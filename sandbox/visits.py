"""
Počítadlo návštěvnosti.

Princip: každému prohlížeči přiřadíme dlouho platící cookie s náhodným ID.
Kdo cookie ještě nemá, je to "nový" návštěvník. Ukládáme jen datum posledního
zobrazení pro každé ID - z toho jde spočítat:
  - kolik různých ID jsme kdy viděli (odhad "kolik lidí stránku navštívilo")
  - kolik z nich mělo poslední návštěvu dnes ("kolik lidí je tu dnes")

Je to odhad, ne přesná unikátní návštěvnost (někdo si cookie může smazat,
někdo přijde z více zařízení) - ale je to výrazně blíž realitě než počítání
každého načtení stránky zvlášť.
"""
from __future__ import annotations

import json
import secrets
from datetime import date
from threading import Lock

from .config import DATA_DIR, VISITS_FILE, ensure_dirs

_LOCK = Lock()
COOKIE_NAME = "lpd_vid"
COOKIE_MAX_AGE = 400 * 24 * 60 * 60  # ~400 dní (maximum, které si prohlížeče vůbec nechají)


def _load() -> dict:
    if not VISITS_FILE.exists():
        return {}
    try:
        return json.loads(VISITS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    ensure_dirs()
    tmp = VISITS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(VISITS_FILE)


def record_visit(visitor_id: str | None) -> tuple[str, dict]:
    """Zapíše návštěvu. Vrátí (visitor_id, statistiky). Pokud visitor_id
    chybí (nová cookie), vygeneruje nové."""
    today = date.today().isoformat()
    is_new_cookie = not visitor_id

    with _LOCK:
        data = _load()
        if not visitor_id or visitor_id not in data:
            visitor_id = visitor_id or secrets.token_hex(16)
            data[visitor_id] = today
        else:
            data[visitor_id] = today
        _save(data)

        total_unique = len(data)
        today_unique = sum(1 for last_seen in data.values() if last_seen == today)

    return visitor_id, {
        "total_unique": total_unique,
        "today_unique": today_unique,
        "is_new": is_new_cookie,
    }


def stats() -> dict:
    """Jen pro čtení (např. na jiných stránkách), bez zápisu nové návštěvy."""
    today = date.today().isoformat()
    with _LOCK:
        data = _load()
    return {
        "total_unique": len(data),
        "today_unique": sum(1 for last_seen in data.values() if last_seen == today),
    }