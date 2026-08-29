"""Běh příkazů v izolovaném kontejneru.

Primárně Docker (jeden malý kontejner na přihlášeného uživatele), jako záloha
bubblewrap (`bwrap`), když Docker na stroji není. V obou případech běží
**skutečný Linux** – výstupy i kontrola úkolů jsou reálné, nic se nesimuluje.

Izolace:
  * bez sítě (--network none)
  * bez rootu (--user <uid hostitele>) a bez capabilities (--cap-drop ALL)
  * read-only rootfs, zapisovatelný je jen domov uživatele a /tmp (tmpfs)
  * limity paměti, CPU a počtu procesů
  * no-new-privileges (sudo/setuid nemá šanci)
"""

import os
import re
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from . import auth
from .config import (
    COMMAND_TIMEOUT,
    CONTAINER_PREFIX,
    CPU_LIMIT,
    DOCKERFILE_DIR,
    IDLE_TIMEOUT,
    IMAGE_NAME,
    MAX_CONTAINERS,
    MAX_OUTPUT_BYTES,
    MEMORY_LIMIT,
    PIDS_LIMIT,
    TMPFS_SIZE,
)

CWD_MARKER = "__LPD_CWD__"
RC_MARKER = "__LPD_RC__"

# Skript, který se pouští uvnitř kontejneru. Příkaz uživatele přichází
# v proměnné prostředí, takže se nikde nelepí do řetězce (žádné uvozovkové peklo).
WRAPPER = f"""
cd "$LPD_CWD" 2>/dev/null || cd "$HOME"
eval "$LPD_CMD" 2>&1
__rc=$?
printf '\\n{CWD_MARKER}%s\\n{RC_MARKER}%s\\n' "$PWD" "$__rc"
"""

_OUTPUT_TAIL = re.compile(
    rf"\n?{CWD_MARKER}(?P<cwd>.*)\n{RC_MARKER}(?P<rc>-?\d+)\n?$", re.DOTALL
)


class SandboxError(Exception):
    """Chyba pískoviště s textem pro uživatele."""


@dataclass
class ExecResult:
    output: str
    cwd: str
    returncode: int
    timed_out: bool = False


# =============================================================================
#  Docker
# =============================================================================

def _docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        return subprocess.run(
            ["docker", "info"], capture_output=True, timeout=10
        ).returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


_BUILD_LOCK = threading.Lock()


def ensure_image() -> None:
    """Postaví obraz pískoviště, pokud ještě neexistuje."""
    with _BUILD_LOCK:
        exists = subprocess.run(
            ["docker", "image", "inspect", IMAGE_NAME],
            capture_output=True,
        ).returncode == 0
        if exists:
            return
        build = subprocess.run(
            ["docker", "build", "-t", IMAGE_NAME, str(DOCKERFILE_DIR)],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if build.returncode != 0:
            raise SandboxError(
                "Nepodařilo se postavit obraz pískoviště:\n"
                + build.stderr.strip()[-800:]
            )


def _container_name(user: auth.SandboxUser) -> str:
    return CONTAINER_PREFIX + user.uid


def _container_state(name: str) -> Optional[str]:
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Status}}", name],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _running_containers() -> int:
    result = subprocess.run(
        ["docker", "ps", "-q", "--filter", f"name=^{CONTAINER_PREFIX}"],
        capture_output=True,
        text=True,
    )
    return len([line for line in result.stdout.splitlines() if line.strip()])


def _start_container(user: auth.SandboxUser) -> None:
    name = _container_name(user)
    state = _container_state(name)

    if state == "running":
        return
    if state is not None:  # existuje, ale je zastavený
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)

    if _running_containers() >= MAX_CONTAINERS:
        raise SandboxError(
            "Pískoviště je právě plné (běží maximum kontejnerů). Zkus to za chvíli."
        )

    ensure_image()
    passwd_file, group_file = auth.passwd_files(user)
    uid, gid = os.getuid(), os.getgid()

    cmd = [
        "docker", "run", "-d",
        "--name", name,
        "--hostname", f"tux-{user.uid[:6]}",
        "--network", "none",
        "--user", f"{uid}:{gid}",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        # Bez CAP_NET_RAW by 'ping' (úkoly 40-42) hlásil "Operation not permitted".
        # Tenhle sysctl povolí ping přes obyčejný ("unprivileged") ICMP socket
        # bez nutnosti vracet capability - funguje jen na loopbacku, síť je stále "none".
        "--sysctl", "net.ipv4.ping_group_range=0 2147483647",
        "--read-only",
        "--tmpfs", f"/tmp:rw,noexec,nosuid,size={TMPFS_SIZE}",
        "--memory", MEMORY_LIMIT,
        "--memory-swap", MEMORY_LIMIT,
        "--cpus", CPU_LIMIT,
        "--pids-limit", PIDS_LIMIT,
        "--restart", "no",
        "-v", f"{user.home}:{user.container_home}:rw",
        "-v", f"{passwd_file}:/etc/passwd:ro",
        "-v", f"{group_file}:/etc/group:ro",
        "-w", user.container_home,
        "-e", f"HOME={user.container_home}",
        "-e", f"USER={user.login}",
        "-e", "PS1=$ ",
        IMAGE_NAME,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise SandboxError(
            "Kontejner se nepodařilo spustit:\n" + result.stderr.strip()[-500:]
        )


def _docker_exec(user: auth.SandboxUser, command: str, cwd: str) -> ExecResult:
    _start_container(user)
    name = _container_name(user)

    proc_cmd = [
        "docker", "exec",
        "-e", f"LPD_CMD={command}",
        "-e", f"LPD_CWD={cwd}",
        "-e", f"HOME={user.container_home}",
        name,
        "/bin/bash", "--noprofile", "--norc", "-c", WRAPPER,
    ]
    try:
        result = subprocess.run(
            proc_cmd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=COMMAND_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        # Příkaz se zasekl (nekonečná smyčka) – kontejner restartujeme,
        # domovská složka je na disku, takže se nic neztratí.
        subprocess.run(["docker", "restart", "-t", "1", name], capture_output=True)
        return ExecResult(
            output="⏱ Příkaz běžel moc dlouho a byl ukončen. Pískoviště je zase v pořádku.",
            cwd=user.container_home,
            returncode=124,
            timed_out=True,
        )

    return _parse_output(result.stdout, result.stderr, fallback_cwd=cwd)


# =============================================================================
#  Bubblewrap (záloha, když Docker chybí)
# =============================================================================

def _bwrap_available() -> bool:
    return bool(shutil.which("bwrap"))


def _bwrap_exec(user: auth.SandboxUser, command: str, cwd: str) -> ExecResult:
    shell = shutil.which("bash") or "/bin/sh"
    args = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session"]
    for path in ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc"):
        if os.path.exists(path):
            args += ["--ro-bind", path, path]
    args += [
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/tmp",
        "--bind", str(user.home), user.container_home,
        "--chdir", user.container_home,
        "--setenv", "HOME", user.container_home,
        "--setenv", "USER", user.login,
        "--setenv", "LPD_CMD", command,
        "--setenv", "LPD_CWD", cwd,
        "--setenv", "PATH", "/usr/local/bin:/usr/bin:/bin",
        shell, "-c", WRAPPER,
    ]
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, errors="replace",
            timeout=COMMAND_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return ExecResult(
            output="⏱ Příkaz běžel moc dlouho a byl ukončen.",
            cwd=user.container_home,
            returncode=124,
            timed_out=True,
        )
    return _parse_output(result.stdout, result.stderr, fallback_cwd=cwd)


# =============================================================================
#  Společná část
# =============================================================================

def _parse_output(stdout: str, stderr: str, fallback_cwd: str) -> ExecResult:
    """Oddělí uživatelský výstup od koncových značek (nová složka + návratový kód).

    Výstup uživatelova příkazu chodí celý na stdout (wrapper dělá 2>&1), takže
    značky jsou vždycky až úplně na konci. Na stderr zbude nanejvýš chyba Dockeru.
    """
    match = _OUTPUT_TAIL.search(stdout)
    if match:
        body = stdout[: match.start()]
        cwd = match.group("cwd").strip() or fallback_cwd
        rc = int(match.group("rc"))
    else:
        body, cwd, rc = stdout, fallback_cwd, 0

    if stderr.strip():
        body = (body + "\n" + stderr) if body.strip() else stderr

    if len(body.encode("utf-8")) > MAX_OUTPUT_BYTES:
        body = body.encode("utf-8")[:MAX_OUTPUT_BYTES].decode("utf-8", "ignore")
        body += "\n… (výstup byl zkrácen)"

    return ExecResult(output=body.rstrip("\n"), cwd=cwd, returncode=rc)


_ENGINE_CACHE: Dict[str, str] = {}


def engine_name() -> str:
    """'docker', 'bwrap' nebo 'none' – zjišťuje se jednou za běh."""
    if "name" not in _ENGINE_CACHE:
        if _docker_available():
            _ENGINE_CACHE["name"] = "docker"
        elif _bwrap_available():
            _ENGINE_CACHE["name"] = "bwrap"
        else:
            _ENGINE_CACHE["name"] = "none"
    return _ENGINE_CACHE["name"]


# Poslední aktivita uživatele – kvůli uklízení nečinných kontejnerů.
_LAST_SEEN: Dict[str, float] = {}
_LAST_SEEN_LOCK = threading.Lock()


def run(user: auth.SandboxUser, command: str, cwd: Optional[str] = None) -> ExecResult:
    """Spustí příkaz v pískovišti uživatele a vrátí výstup + novou složku."""
    cwd = cwd or user.container_home
    engine = engine_name()

    with _LAST_SEEN_LOCK:
        _LAST_SEEN[user.uid] = time.time()

    if engine == "docker":
        return _docker_exec(user, command, cwd)
    if engine == "bwrap":
        return _bwrap_exec(user, command, cwd)
    raise SandboxError(
        "Na tomhle serveru není Docker ani bubblewrap – pískoviště nelze bezpečně spustit."
    )


def stop(user: auth.SandboxUser) -> None:
    """Zastaví a smaže kontejner. Data v domovské složce zůstávají."""
    if engine_name() != "docker":
        return
    subprocess.run(
        ["docker", "rm", "-f", _container_name(user)], capture_output=True
    )
    with _LAST_SEEN_LOCK:
        _LAST_SEEN.pop(user.uid, None)


def container_info(user: auth.SandboxUser) -> Tuple[str, Optional[str]]:
    engine = engine_name()
    if engine != "docker":
        return engine, None
    return engine, _container_state(_container_name(user))


def _reaper() -> None:
    """Na pozadí uklízí kontejnery, do kterých se dlouho nic nepsalo."""
    while True:
        time.sleep(60)
        if engine_name() != "docker":
            continue
        now = time.time()
        with _LAST_SEEN_LOCK:
            stale = [uid for uid, seen in _LAST_SEEN.items() if now - seen > IDLE_TIMEOUT]
            for uid in stale:
                _LAST_SEEN.pop(uid, None)
        for uid in stale:
            subprocess.run(
                ["docker", "rm", "-f", CONTAINER_PREFIX + uid], capture_output=True
            )


def start_reaper() -> None:
    thread = threading.Thread(target=_reaper, daemon=True, name="sandbox-reaper")
    thread.start()