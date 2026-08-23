"""Účty pískoviště.

Uživatel zadá jméno + heslo. Z hesla se spočítá:
  * ověřovač (scrypt se solí) – ten se ukládá, heslo samotné nikdy,
  * otisk účtu `uid` (16 hex znaků) – z něj se odvozuje jméno uživatele
    uvnitř kontejneru i složka na disku, která se do kontejneru mountuje.

Žádná databáze není potřeba, stačí jeden JSON soubor.
"""

import hashlib
import hmac
import json
import os
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

from .config import (
    CONTAINER_USER_PREFIX,
    HOMES_DIR,
    PROGRESS_DIR,
    SKEL_DIR,
    USERS_FILE,
    ensure_dirs,
)

_LOCK = Lock()

USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]{3,24}$")
MIN_PASSWORD_LENGTH = 4

# Parametry scryptu – rychlé dost na dětské pískoviště, pomalé dost na útok.
_SCRYPT = {"n": 2 ** 14, "r": 8, "p": 1, "dklen": 32}


class AuthError(Exception):
    """Chyba přihlášení/registrace, text je určený uživateli."""


class SandboxUser:
    def __init__(self, username: str, uid: str):
        self.username = username          # co zadal uživatel
        self.uid = uid                    # otisk účtu (16 hex)
        self.login = CONTAINER_USER_PREFIX + uid[:8]   # jméno uvnitř kontejneru
        self.home = HOMES_DIR / uid       # složka na hostiteli
        self.container_home = f"/home/{self.login}"

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "uid": self.uid,
            "login": self.login,
            "home": self.container_home,
        }


# --- ukládání ----------------------------------------------------------------

def _load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict) -> None:
    ensure_dirs()
    tmp = USERS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(USERS_FILE)


def _normalize(username: str) -> str:
    """Malá písmena bez diakritiky – 'Honza' i 'honza' je stejný účet."""
    stripped = unicodedata.normalize("NFKD", username.strip())
    return "".join(c for c in stripped if not unicodedata.combining(c)).lower()


def _verifier(password: str, salt: str) -> str:
    return hashlib.scrypt(
        password.encode("utf-8"), salt=bytes.fromhex(salt), **_SCRYPT
    ).hex()


def _derive_uid(key: str, salt: str) -> str:
    """Otisk účtu = základ jména uživatele i mountované složky."""
    return hashlib.sha256(f"{key}:{salt}".encode("utf-8")).hexdigest()[:16]


# --- veřejné API -------------------------------------------------------------

def login_or_register(username: str, password: str) -> SandboxUser:
    """Přihlásí existující účet, jinak založí nový (a jeho domovskou složku)."""
    username = username.strip()
    password = password or ""

    if not USERNAME_RE.match(_normalize(username) or ""):
        raise AuthError(
            "Jméno smí mít 3–24 znaků a jen písmena, číslice, tečku, pomlčku nebo podtržítko."
        )
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AuthError(f"Heslo musí mít aspoň {MIN_PASSWORD_LENGTH} znaky.")

    key = _normalize(username)

    with _LOCK:
        users = _load_users()
        record = users.get(key)

        if record is None:
            salt = os.urandom(16).hex()
            record = {
                "username": username,
                "salt": salt,
                "verifier": _verifier(password, salt),
                "uid": _derive_uid(key, salt),
                "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            users[key] = record
            _save_users(users)
        else:
            if not hmac.compare_digest(
                _verifier(password, record["salt"]), record["verifier"]
            ):
                raise AuthError("Špatné heslo. Zkus to ještě jednou.")

    user = SandboxUser(record["username"], record["uid"])
    prepare_home(user)
    return user


def prepare_home(user: SandboxUser, reset: bool = False) -> None:
    """Vytvoří (nebo obnoví) domovskou složku, která se mountuje do kontejneru."""
    ensure_dirs()
    if reset and user.home.exists():
        shutil.rmtree(user.home)

    if not user.home.exists():
        shutil.copytree(SKEL_DIR, user.home)
    else:
        # Chybějící soubory ze vzoru doplníme (např. když si někdo smaže
        # start.sh a nemohl by dodělat 3. úkol). Vlastní soubory necháváme být.
        for source in SKEL_DIR.rglob("*"):
            target = user.home / source.relative_to(SKEL_DIR)
            if source.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    # start.sh je schválně bez práva spouštění – povolit ho je úkol č. 3.
    script = user.home / "start.sh"
    if script.exists() and not (user.home / "starty.log").exists():
        script.chmod(0o644)

    # /etc/passwd pro kontejner: bez něj by se uživatel jmenoval "I have no name!"
    passwd_file = user.home.parent / f"{user.uid}.passwd"
    passwd_file.write_text(
        "root:x:0:0:root:/root:/bin/bash\n"
        f"{user.login}:x:{_host_uid()}:{_host_gid()}:Kadet:{user.container_home}:/bin/bash\n"
        "nobody:x:65534:65534:nobody:/:/sbin/nologin\n",
        encoding="utf-8",
    )
    group_file = user.home.parent / f"{user.uid}.group"
    group_file.write_text(
        "root:x:0:\n"
        f"{user.login}:x:{_host_gid()}:\n"
        "nobody:x:65534:\n",
        encoding="utf-8",
    )


def passwd_files(user: SandboxUser):
    return (
        user.home.parent / f"{user.uid}.passwd",
        user.home.parent / f"{user.uid}.group",
    )


def _host_uid() -> int:
    """Kontejner běží pod UID hostitele, aby soubory v mountu patřily nám."""
    return os.getuid()


def _host_gid() -> int:
    return os.getgid()


# --- pokrok v úkolech --------------------------------------------------------

def progress_path(user: SandboxUser) -> Path:
    return PROGRESS_DIR / f"{user.uid}.json"


def load_progress(user: SandboxUser) -> dict:
    path = progress_path(user)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_progress(user: SandboxUser, progress: dict) -> None:
    ensure_dirs()
    progress_path(user).write_text(
        json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def find_user(uid: str, username: str) -> Optional[SandboxUser]:
    """Obnoví uživatele ze session cookie."""
    users = _load_users()
    record = users.get(_normalize(username))
    if record and hmac.compare_digest(record["uid"], uid):
        return SandboxUser(record["username"], record["uid"])
    return None
