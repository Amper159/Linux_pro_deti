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
import secrets
from datetime import datetime
from threading import Lock

from .config import FEEDBACK_FILE, ensure_dirs

_LOCK = Lock()

MAX_JMENO_DELKA = 40
MAX_ZPRAVA_DELKA = 2000
POVOLENE_TYPY = {"libi", "nelibi", "navrh"}


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


def ulozit(jmeno: str, typ: str, zprava: str) -> dict | None:
    """Vrátí None při neplatném vstupu, jinak uložený záznam."""
    jmeno = (jmeno or "").strip()[:MAX_JMENO_DELKA]
    zprava = (zprava or "").strip()[:MAX_ZPRAVA_DELKA]
    if typ not in POVOLENE_TYPY or not zprava:
        return None

    zaznam = {
        "id": secrets.token_hex(6),
        "cas": datetime.now().isoformat(timespec="seconds"),
        "jmeno": jmeno or "Anonym",
        "typ": typ,
        "zprava": zprava,
    }
    with _LOCK:
        data = _load()
        data.append(zaznam)
        _save(data)
    return zaznam
