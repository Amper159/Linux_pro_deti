"""Filtr nebezpečných příkazů.

Kontejner sám je zamčený (bez sítě, bez rootu, read-only rootfs, limity paměti
a procesů), tohle je druhá vrstva: zachytí nebezpečný příkaz dřív, než se vůbec
spustí, a dítěti hezky česky vysvětlí, proč se to nedělá.
"""

import re
from typing import Optional

from .config import MAX_COMMAND_LENGTH

# Příkaz -> přátelské vysvětlení, proč ho radši nezkoušet (text vidí dítě).
BLOCKED_COMMANDS = {
    # práva a identita
    "sudo": "Tohle by ti dalo práva správce, a ty je tu ještě nepotřebuješ. Zkus úkol bez toho 🙂",
    "su": "Přepínání na jiného uživatele si necháme na jindy.",
    "doas": "Přepínání na jiného uživatele si necháme na jindy.",
    "chown": "Změna vlastníka souborů patří správci lodi, ne kadetovi.",
    "chroot": "Tohle je pokročilá operace se zbytečným rizikem – přeskoč ji.",
    "passwd": "Heslo si měnit nemusíš, funguje ti pořád stejné.",
    "useradd": "Nové uživatele tu zakládat nepotřebuješ.",
    "adduser": "Nové uživatele tu zakládat nepotřebuješ.",
    "userdel": "Mazání uživatelů necháme na jindy.",
    "usermod": "Úpravu uživatelů necháme na jindy.",
    # disky a souborové systémy
    "mount": "Připojování disků by mohlo pískoviště pěkně rozhodit.",
    "umount": "Odpojování disků by mohlo pískoviště pěkně rozhodit.",
    "mkfs": "Whoa, tohle by smazalo celý souborový systém! Radši ne 😅",
    "mkfs.ext4": "Whoa, tohle by smazalo celý souborový systém! Radši ne 😅",
    "fdisk": "Práce s diskovými oddíly je na pískoviště moc velké kafe.",
    "parted": "Práce s diskovými oddíly je na pískoviště moc velké kafe.",
    "dd": "'dd' umí jedním překlepem přepsat celý disk – radši se mu vyhni.",
    "shred": "Nenávratné mazání dat necháme na jindy.",
    "swapoff": "Do odkládacího prostoru radši nesahej.",
    "sync": "Tahle systémová operace tu není potřeba.",
    # běh systému
    "shutdown": "Vypínání kontejneru necháme na tlačítku 'Vyčistit'.",
    "reboot": "Restart necháme na tlačítku 'Vyčistit'.",
    "halt": "Vypínání kontejneru necháme na tlačítku 'Vyčistit'.",
    "poweroff": "Vypínání kontejneru necháme na tlačítku 'Vyčistit'.",
    "init": "Zásahy do startu systému jsou nad rámec pískoviště.",
    "systemctl": "Správa služeb je nad rámec pískoviště.",
    "service": "Správa služeb je nad rámec pískoviště.",
    "sysctl": "Ladění jádra necháme na jindy.",
    "insmod": "Práce s moduly jádra necháme na jindy.",
    "rmmod": "Práce s moduly jádra necháme na jindy.",
    "modprobe": "Práce s moduly jádra necháme na jindy.",
    # procesy
    "kill": "Ukončování procesů si zkusíš přímo ve hře – tady zatím ne.",
    "killall": "Hromadné ukončování procesů necháme na jindy.",
    "pkill": "Hromadné ukončování procesů necháme na jindy.",
    "fork": "Vytváření procesů ve smyčce by zahltilo pískoviště.",
    # síť (kontejner ji stejně nemá)
    "curl": "Pískoviště je bez internetu, takže tenhle příkaz by stejně nic nestáhl.",
    "wget": "Pískoviště je bez internetu, takže tenhle příkaz by stejně nic nestáhl.",
    "nc": "Pískoviště je bez internetu – síťové příkazy tu nefungují.",
    "netcat": "Pískoviště je bez internetu – síťové příkazy tu nefungují.",
    "ssh": "Připojování na jiné počítače tu nefunguje.",
    "scp": "Přenos souborů po síti tu nefunguje.",
    "ftp": "Přenos souborů po síti tu nefunguje.",
    "telnet": "Připojování na jiné počítače tu nefunguje.",
    "iptables": "Nastavení firewallu necháme na jindy.",
    "ip": "Nastavení sítě necháme na jindy.",
    "ifconfig": "Nastavení sítě necháme na jindy.",
    # instalace balíčků
    "apk": "Instalovat nové programy tu bohužel nejde.",
    "apt": "Instalovat nové programy tu bohužel nejde.",
    "apt-get": "Instalovat nové programy tu bohužel nejde.",
    "dnf": "Instalovat nové programy tu bohužel nejde.",
    "yum": "Instalovat nové programy tu bohužel nejde.",
    "pacman": "Instalovat nové programy tu bohužel nejde.",
    "pip": "Instalovat nové programy tu bohužel nejde.",
    # plánování a démoni
    "crontab": "Plánované úlohy necháme na jindy.",
    "at": "Plánované úlohy necháme na jindy.",
    "nohup": "Spouštění na pozadí necháme na jindy.",
    # interaktivní programy, které by v okně terminálu zůstaly viset
    "vi": "Editory na celou obrazovku tu bohužel nefungují – zkus 'echo text > soubor'.",
    "vim": "Editory na celou obrazovku tu bohužel nefungují – zkus 'echo text > soubor'.",
    "nano": "Editory na celou obrazovku tu bohužel nefungují – zkus 'echo text > soubor'.",
    "top": "Programy na celou obrazovku tu nefungují – zkus radši 'ps'.",
    "htop": "Programy na celou obrazovku tu nefungují – zkus radši 'ps'.",
    "less": "Stránkovače tu nefungují – zkus 'cat' nebo 'head'.",
    "more": "Stránkovače tu nefungují – zkus 'cat' nebo 'head'.",
    "man": "Manuálové stránky tu nejsou, ale nápovědu najdeš v zadání úkolu.",
}

# Nebezpečné vzory (fork bomba, mazání kořene, přepis zařízení…).
DANGEROUS_PATTERNS = [
    (re.compile(r":\s*\(\s*\)\s*\{.*\|.*&.*\}"), "Tohle je 'fork bomba' – zahltila by celé pískoviště. Radši ne!"),
    (re.compile(r"\brm\b[^|;&]*\s(-[a-zA-Z]*[rRf][a-zA-Z]*\s+)*/(\s|$)"), "Mazání celého kořenového adresáře '/' by smazalo úplně všechno."),
    (re.compile(r"\brm\b[^|;&]*\s/(bin|etc|usr|lib|sbin|var|boot|dev|proc|sys)\b"), "Mazání systémových složek by pískoviště rozbilo."),
    (re.compile(r">\s*/dev/(sd|nvme|hd|mmc)"), "Zápis přímo na disk je moc riskantní."),
    (re.compile(r">\s*/(etc|bin|usr|lib|sbin|boot|proc|sys)/"), "Zápis do systémových složek by pískoviště rozbil."),
    (re.compile(r"\bwhile\s+true\b|\bwhile\s+:\s*;"), "Nekonečná smyčka by ti zablokovala terminál."),
    (re.compile(r"/dev/(zero|urandom|random)\b[^|]*>"), "Zaplňování disku náhodnými daty by pískoviště zahltilo."),
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
            return f"'{name}' si tu zatím nezkoušej. {reason}"

    return None
