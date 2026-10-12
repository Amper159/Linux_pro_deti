"""XP, odznaky a žebříček pro SQL Lab - oddělené od Pískoviště i Python Labu,
ale nad stejnými uživatelskými účty (auth.py). Na rozdíl od Python Labu kontroluje
výsledek dotazu server (viz sql_engine.check_result), klient jen zobrazuje."""
import json
from typing import List

from . import auth
from .config import SQL_PROGRESS_DIR
from .python_gamification import _with_me, LEADERBOARD_SIZE
from .sql_tasks import SQL_TASKS

XP_PER_TASK = 50
TOTAL_TASKS = len(SQL_TASKS)

BADGE_TIERS = [
    {"value": 4, "id": "ctenar_archivu", "label": "Čtenář archivu", "icon": "fa-book-open"},
    {"value": 8, "id": "vyslechovac", "label": "Vyslýchač", "icon": "fa-filter"},
    {"value": 12, "id": "stopar", "label": "Stopař", "icon": "fa-magnifying-glass"},
    {"value": 16, "id": "poctar", "label": "Počtář", "icon": "fa-calculator"},
    {"value": 19, "id": "skupinar", "label": "Skupinář", "icon": "fa-layer-group"},
    {"value": 23, "id": "datovy_detektiv", "label": "Datový detektiv", "icon": "fa-user-secret"},
]


def _progress_path(user: auth.SandboxUser):
    return SQL_PROGRESS_DIR / f"{user.uid}.json"


def load_progress(user: auth.SandboxUser) -> dict:
    path = _progress_path(user)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_progress(user: auth.SandboxUser, progress: dict) -> None:
    from .config import ensure_dirs
    ensure_dirs()
    path = _progress_path(user)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(progress, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _completed_ids(progress: dict):
    result = set()
    for key, done in progress.items():
        if not done:
            continue
        try:
            result.add(int(key))
        except (TypeError, ValueError):
            continue
    return result


def completed_count(progress: dict) -> int:
    return len(_completed_ids(progress))


def xp_for(progress: dict) -> int:
    return completed_count(progress) * XP_PER_TASK


def mark_complete(user: auth.SandboxUser, task_id: int) -> dict:
    """Zapíše splnění úkolu (idempotentní)."""
    progress = load_progress(user)
    progress[str(task_id)] = True
    save_progress(user, progress)
    return progress


def badges_for(progress: dict) -> List[dict]:
    done = completed_count(progress)
    return [{**tier, "unlocked": done >= tier["value"]} for tier in BADGE_TIERS]


def summary(user: auth.SandboxUser) -> dict:
    progress = load_progress(user)
    done = completed_count(progress)
    return {
        "completed": done,
        "total_tasks": TOTAL_TASKS,
        "xp": xp_for(progress),
        "completed_ids": sorted(_completed_ids(progress)),
        "badges": badges_for(progress),
    }


def leaderboard(me=None, limit: int = LEADERBOARD_SIZE) -> List[dict]:
    entries = []
    for user in auth.all_users():
        progress = load_progress(user)
        done = completed_count(progress)
        if done == 0:
            continue
        entries.append({"username": user.username, "xp": xp_for(progress), "completed": done})
    entries.sort(key=lambda e: (-e["xp"], e["username"].lower()))
    return _with_me(entries, me, limit)
