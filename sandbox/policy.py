"""Filtr nebezpečných příkazů.

Kontejner sám je zamčený (bez sítě, bez rootu, read-only rootfs, limity paměti
a procesů), tohle je druhá vrstva: zachytí nebezpečný příkaz dřív, než se vůbec
spustí, a dítěti hezky česky vysvětlí, proč se to nedělá.
"""

import re
from typing import Optional

from .config import MAX_COMMAND_LENGTH

# Příkaz -> proč je zakázaný (text vidí uživatel).
BLOCKED_COMMANDS = {
    # práva a identita
    "sudo": "Tímhle se získávají práva správce – v pískovišti nejsou potřeba.",
    "su": "Přepnutí na jiného uživatele je zakázané.",
    "doas": "Přepnutí na jiného uživatele je zakázané.",
    "chown": "Změna vlastníka souborů je vyhrazená správci systému.",
    "chroot": "Změna kořene systému je nebezpečná operace.",
    "passwd": "Hesla se v pískovišti nemění.",
    "useradd": "Uživatelé se v pískovišti nezakládají.",
    "adduser": "Uživatelé se v pískovišti nezakládají.",
    "userdel": "Mazání uživatelů je zakázané.",
    "usermod": "Úprava uživatelů je zakázaná.",
    # disky a souborové systémy
    "mount": "Připojování disků může rozbít systém.",
    "umount": "Odpojování disků může rozbít systém.",
    "mkfs": "Formátování disku by smazalo celý souborový systém!",
    "mkfs.ext4": "Formátování disku by smazalo celý souborový systém!",
    "fdisk": "Práce s tabulkou oddílů je pro pískoviště moc nebezpečná.",
    "parted": "Práce s tabulkou oddílů je pro pískoviště moc nebezpečná.",
    "dd": "'dd' umí jedním překlepem přepsat celý disk.",
    "shred": "Nenávratné přepisování dat je zakázané.",
    "swapoff": "Zásahy do odkládacího prostoru jsou zakázané.",
    "sync": "Systémové operace s disky jsou zakázané.",
    # běh systému
    "shutdown": "Vypínání počítače je zakázané.",
    "reboot": "Restart počítače je zakázaný.",
    "halt": "Vypínání počítače je zakázané.",
    "poweroff": "Vypínání počítače je zakázané.",
    "init": "Zásahy do startu systému jsou zakázané.",
    "systemctl": "Správa systémových služeb je zakázaná.",
    "service": "Správa systémových služeb je zakázaná.",
    "sysctl": "Ladění jádra je zakázané.",
    "insmod": "Načítání modulů jádra je zakázané.",
    "rmmod": "Práce s moduly jádra je zakázaná.",
    "modprobe": "Práce s moduly jádra je zakázaná.",
    # procesy
    "kill": "Ukončování cizích procesů si zkusíš až ve hře, tady ne.",
    "killall": "Ukončování cizích procesů je zakázané.",
    "pkill": "Ukončování cizích procesů je zakázané.",
    "fork": "Vytváření procesů ve smyčce by zahltilo počítač.",
    # síť (kontejner ji stejně nemá)
    "curl": "Pískoviště je bez internetu – síťové příkazy nefungují.",
    "wget": "Pískoviště je bez internetu – síťové příkazy nefungují.",
    "nc": "Pískoviště je bez internetu – síťové příkazy nefungují.",
    "netcat": "Pískoviště je bez internetu – síťové příkazy nefungují.",
    "ssh": "Připojování na jiné počítače je zakázané.",
    "scp": "Přenos souborů po síti je zakázaný.",
    "ftp": "Přenos souborů po síti je zakázaný.",
    "telnet": "Připojování na jiné počítače je zakázané.",
    "iptables": "Nastavení firewallu je zakázané.",
    "ip": "Nastavení sítě je zakázané.",
    "ifconfig": "Nastavení sítě je zakázané.",
    # instalace balíčků
    "apk": "Instalovat programy v pískovišti nejde.",
    "apt": "Instalovat programy v pískovišti nejde.",
    "apt-get": "Instalovat programy v pískovišti nejde.",
    "dnf": "Instalovat programy v pískovišti nejde.",
    "yum": "Instalovat programy v pískovišti nejde.",
    "pacman": "Instalovat programy v pískovišti nejde.",
    "pip": "Instalovat programy v pískovišti nejde.",
    # plánování a démoni
    "crontab": "Plánované úlohy jsou zakázané.",
    "at": "Plánované úlohy jsou zakázané.",
    "nohup": "Spouštění procesů na pozadí je zakázané.",
    # interaktivní programy, které by v okně terminálu zůstaly viset
    "vi": "Textové editory na celou obrazovku tu bohužel nefungují – zkus 'echo text > soubor'.",
    "vim": "Textové editory na celou obrazovku tu bohužel nefungují – zkus 'echo text > soubor'.",
    "nano": "Textové editory na celou obrazovku tu bohužel nefungují – zkus 'echo text > soubor'.",
    "top": "Programy na celou obrazovku tu nefungují – zkus 'ps'.",
    "htop": "Programy na celou obrazovku tu nefungují – zkus 'ps'.",
    "less": "Stránkovače tu nefungují – zkus 'cat' nebo 'head'.",
    "more": "Stránkovače tu nefungují – zkus 'cat' nebo 'head'.",
    "man": "Manuálové stránky tu nejsou – nápovědu najdeš v úkolu.",
}

# Nebezpečné vzory (fork bomba, mazání kořene, přepis zařízení…).
DANGEROUS_PATTERNS = [
    (re.compile(r":\s*\(\s*\)\s*\{.*\|.*&.*\}"), "Tohle je 'fork bomba' – zahltila by celý počítač."),
    (re.compile(r"\brm\b[^|;&]*\s(-[a-zA-Z]*[rRf][a-zA-Z]*\s+)*/(\s|$)"), "Mazání kořenového adresáře '/' je zakázané."),
    (re.compile(r"\brm\b[^|;&]*\s/(bin|etc|usr|lib|sbin|var|boot|dev|proc|sys)\b"), "Mazání systémových složek je zakázané."),
    (re.compile(r">\s*/dev/(sd|nvme|hd|mmc)"), "Zápis přímo na disk je zakázaný."),
    (re.compile(r">\s*/(etc|bin|usr|lib|sbin|boot|proc|sys)/"), "Zápis do systémových složek je zakázaný."),
    (re.compile(r"\bwhile\s+true\b|\bwhile\s+:\s*;"), "Nekonečná smyčka by zablokovala terminál."),
    (re.compile(r"/dev/(zero|urandom|random)\b[^|]*>"), "Zaplňování disku náhodnými daty je zakázané."),
]

# Oddělovače, za kterými začíná nový příkaz.
_SEGMENT_SPLIT = re.compile(r"(?:\|\||&&|[|;&\n])")
# Přiřazení proměnné na začátku segmentu (FOO=bar prikaz).
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _binaries(raw: str):
    """Vytáhne z příkazové řádky jména spouštěných programů."""
    for segment in _SEGMENT_SPLIT.split(raw):
        tokens = segment.strip().split()
        while tokens and _ASSIGNMENT.match(tokens[0]):
            tokens.pop(0)
        if not tokens:
            continue
        name = tokens[0].strip("\"'()")
        # /usr/bin/sudo i ./sudo se počítají jako sudo
        yield name.rsplit("/", 1)[-1]


def check_command(raw: str) -> Optional[str]:
    """Vrátí důvod zamítnutí, nebo None když je příkaz v pořádku."""
    cmd = raw.strip()
    if not cmd:
        return None

    if len(cmd) > MAX_COMMAND_LENGTH:
        return f"Příkaz je moc dlouhý (max {MAX_COMMAND_LENGTH} znaků)."

    if "\x00" in cmd:
        return "Příkaz obsahuje neplatné znaky."

    for pattern, reason in DANGEROUS_PATTERNS:
        if pattern.search(cmd):
            return reason

    for name in _binaries(cmd):
        reason = BLOCKED_COMMANDS.get(name)
        if reason:
            return f"Příkaz '{name}' je v pískovišti zakázaný. {reason}"

    return None
