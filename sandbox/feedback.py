"""
Zpětná vazba od návštěvníků.

Jednosměrné - návštěvník napíše, uloží se to do souboru, nikde na webu se to
veřejně nezobrazuje (na rozdíl od otevřeného chatu, kde by cizí lidi viděli
zprávy od sebe navzájem - to je přesně to, čemu jsme se u dětského webu
záměrně vyhnuli).

Majitel webu si zprávy přečte přímo na serveru:
    cat sandbox_data/feedback.json | python3 -m json.tool
"""
from __future__ import annotations

import json
import re
import secrets
from datetime import datetime
from threading import Lock

from .config import FEEDBACK_FILE, ensure_dirs

_LOCK = Lock()

MAX_JMENO_DELKA = 40
MAX_ZPRAVA_DELKA = 2000
MAX_KONTAKT_DELKA = 100
POVOLENE_TYPY = {"libi", "nelibi", "navrh", "skola", "dotaz"}
# U těchhle typů je kontakt povinný - bez něj by se na zprávu nedalo odpovědět.
KONTAKT_POVINNY = {"skola", "dotaz"}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_TELEFON_RE = re.compile(r"^[+\d\s()./-]{6,}$")


def _jedna_radka(text: str, limit: int) -> str:
    """Zalomení řádků a nadbytečné mezery pryč - hodnota se dostane do e-mailu."""
    return " ".join((text or "").split())[:limit]


def kontakt_ok(kontakt: str) -> bool:
    """Kontakt musí vypadat jako e-mail nebo telefon (aspoň 6 číslic)."""
    if _EMAIL_RE.match(kontakt):
        return True
    return bool(_TELEFON_RE.match(kontakt)) and sum(c.isdigit() for c in kontakt) >= 6


def _load() -> list:
    if not FEEDBACK_FILE.exists():
        return []
    try:
        return json.loads(FEEDBACK_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(data: list) -> None:
    ensure_dirs()
    tmp = FEEDBACK_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(FEEDBACK_FILE)


def ulozit(jmeno: str, typ: str, zprava: str, kontakt: str = "") -> dict | None:
    """Vrátí None při neplatném vstupu, jinak uložený záznam.

    Kontakt je nepovinný, u typů z KONTAKT_POVINNY povinný. Ukládá se jen
    to, co návštěvník sám vyplní, a jen kvůli odpovědi na tu jednu zprávu."""
    jmeno = _jedna_radka(jmeno, MAX_JMENO_DELKA)
    zprava = (zprava or "").strip()[:MAX_ZPRAVA_DELKA]
    kontakt = _jedna_radka(kontakt, MAX_KONTAKT_DELKA)
    if typ not in POVOLENE_TYPY or not zprava:
        return None
    if typ in KONTAKT_POVINNY and not kontakt:
        return None
    if kontakt and not kontakt_ok(kontakt):
        return None

    zaznam = {
        "id": secrets.token_hex(6),
        "cas": datetime.now().isoformat(timespec="seconds"),
        "jmeno": jmeno or "Anonym",
        "typ": typ,
        "zprava": zprava,
    }
    if kontakt:
        zaznam["kontakt"] = kontakt
    with _LOCK:
        data = _load()
        data.append(zaznam)
        _save(data)
    return zaznam
