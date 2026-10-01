#!/usr/bin/env python3
"""
Kontrola sandbox/tasks.py - spouští se ručně přes 'make check-tasks' po každé
úpravě úkolů v Pískovišti, než se to nasadí.

Hlídá dvě věci, které se v minulosti ukázaly jako skutečné chyby nahlášené
přímo uživateli (viz historie commitů):

  1. FUNKČNÍ KONTROLA - pro každý úkol spustí jeho "hint" (referenční řešení)
     v čisté kopii sandbox/skel/ a ověří, že všechny jeho "checks" po tomhle
     řešení skutečně projdou. Odhalí chybu "hint neodpovídá kontrole".

  2. SROVNÁNÍ ZADÁNÍ S NÁPOVĚDOU - string "goal" (co vidí dítě) by měl sám
     o sobě stačit k vyřešení úkolu, bez nutnosti otevřít nápovědu. Skript
     porovná, jestli nápověda nepoužívá jméno příkazu, cestu nebo parametr,
     který se v zadání vůbec nezmiňuje. Právě tenhle vzorec byl přesně to,
     na co si stěžovali první skuteční uživatelé webu (úkoly 'ls' do složky
     'data' a 'ls -l', kde zadání mlčelo o složce/parametru, co se ve
     skutečnosti vyžadoval).

Konec s chybovým kódem != 0, pokud cokoliv neprojde - dá se zapojit i do
CI/pre-commit, i když to teď volá jen Makefile cíl 'check-tasks'.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKEL = HERE / "skel"

sys.path.insert(0, str(HERE.parent))
from sandbox.tasks import TASKS  # noqa: E402

# Úkoly, co vyžadují skutečnou síť (ping) - v izolovaném/CI prostředí bez
# sítě ven typicky selžou i se správným řešením, proto se jen nahlásí jako
# přeskočené, ne jako chyba. Na produkčním serveru (kde se kontejnery
# spouští s plnou síťovou izolací mezi sebou, ale smí ven) fungují.
SIT_ZAVISLE = {"ping"}

# Slova/přípony běžné v každém hintu (jméno příkazu, přepínače, přesměrování),
# která by bylo zbytečné vyžadovat doslova v zadání - ta popisují/parafrázují
# příkaz, nemusí ho citovat. Jméno hlavního příkazu (cmd_name) se řeší zvlášť
# jako tvrdé pravidlo níž.
IGNOROVANA_SLOVA = {
    "cd", "ls", "cat", "grep", "mkdir", "touch", "wc", "rm", "cp", "mv", "find",
    "ping", "echo", "head", "tail", "rmdir", "df", "chmod", "ps", "free", "tar",
    "gzip", "alias", "date", "uname", "env", "pgrep", "sleep", "bashrc", "~",
    "home", "dev", "null",
}
IGNOROVANE_TOKENY = {"/dev/null", "2>&1", ">", ">>", "<", "&"}


def pripravit_domov(cilova_slozka: Path) -> None:
    if cilova_slozka.exists():
        shutil.rmtree(cilova_slozka)
    shutil.copytree(SKEL, cilova_slozka)


def over_funkcne(task: dict, domov: Path) -> list[str]:
    """Spustí hint, pak všechny checks. Vrátí seznam chybových hlášek (prázdný = OK)."""
    env = os.environ.copy()
    env["HOME"] = str(domov)
    subprocess.run(
        ["bash", "-c", task.get("hint", "")],
        cwd=domov, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
    )
    chyby = []
    for chk in task.get("checks", []):
        r = subprocess.run(
            ["bash", "-c", chk["test"]],
            cwd=domov, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
        )
        if r.returncode != 0:
            chyby.append(f"kontrola '{chk['label']}' po spuštění hintu neprošla")
    return chyby


def over_zadani_vs_napovedu(task: dict) -> list[str]:
    """Hledá věci, co hint používá, ale zadání o nich mlčí."""
    problemy = []
    goal_lower = task["goal"].lower()

    # tvrdé pravidlo: jméno hlavního příkazu musí být v zadání (kvůli konzistenci
    # a aby šlo zadání vůbec napsat do terminálu bez hádání)
    hlavni_prikaz = task["cmd_name"].split()[0].replace(".sh", "")
    if hlavni_prikaz.lower() not in goal_lower:
        problemy.append(f"zadání nezmiňuje jméno příkazu '{hlavni_prikaz}'")

    # měkké pravidlo: cesty/parametry z hintu, co chybí v zadání
    hint = task["hint"]
    for ignor in IGNOROVANE_TOKENY:
        hint = hint.replace(ignor, " ")
    tokeny = set(re.findall(r"[\w./*-]+", hint))
    for tok in tokeny:
        if tok.lower() in IGNOROVANA_SLOVA or tok.startswith("-"):
            continue
        # cesty se '/' rozděl na části a posuzuj je zvlášť (např.
        # 'hangar1/soubor.txt' je v pořádku, i když zadání zmiňuje
        # 'hangar1' a 'soubor.txt' každé v jiné větě, ne jako spojený řetězec)
        casti = [c for c in tok.split("/") if c]
        for cast in casti:
            if len(cast) > 2 and cast.lower() not in goal_lower:
                problemy.append(f"nápověda používá '{cast}' (z '{tok}'), zadání to nezmiňuje")
    return problemy


def over_duplicitni_vety(task: dict) -> list[str]:
    """Hrubá past na zkopírovanou/zdvojenou větu v zadání (viz oprava #1)."""
    vety = [v.strip() for v in re.split(r"(?<=[.!?])\s+", task["goal"]) if len(v.strip()) > 8]
    if len(vety) != len(set(vety)):
        return ["zadání obsahuje doslova zopakovanou větu"]
    return []


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tasks_check_") as tmp:
        # JEDNA trvalá domovská složka pro všech 90 úkolů po sobě - stejně jako
        # skutečný kadet řeší úkoly postupně v jedné složce (např. úkol #22
        # počítá s tím, že 'hangar1' z úkolu #19 už existuje). Reset před každým
        # úkolem zvlášť by falešně nahlásil chybu u každého navazujícího úkolu.
        domov = Path(tmp) / "kadet_check"
        pripravit_domov(domov)
        celkem_chyb = 0
        preskoceno = 0

        for task in sorted(TASKS, key=lambda t: t["id"]):
            hlavicka = f"#{task['id']:3d} {task['cmd_name']:10s}"

            funkcni_chyby = over_funkcne(task, domov)
            if funkcni_chyby and task["cmd_name"].split()[0] in SIT_ZAVISLE:
                preskoceno += 1
                continue
            for ch in funkcni_chyby:
                print(f"x {hlavicka} FUNKČNĚ: {ch}")
                celkem_chyb += 1

            for ch in over_zadani_vs_napovedu(task):
                print(f"x {hlavicka} ZADÁNÍ: {ch}")
                celkem_chyb += 1

            for ch in over_duplicitni_vety(task):
                print(f"x {hlavicka} ZADÁNÍ: {ch}")
                celkem_chyb += 1

        print()
        print(f"Zkontrolováno úkolů: {len(TASKS)}, přeskočeno (síť): {preskoceno}, chyb: {celkem_chyb}")
        if celkem_chyb:
            print("Někde se nápověda/kontrola rozchází se zadáním, co vidí dítě. Oprav a spusť znovu.")
            return 1
        print("Všechny úkoly: zadání odpovídá nápovědě a kontrola po vyřešení hintem projde.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
