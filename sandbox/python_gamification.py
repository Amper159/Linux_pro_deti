"""XP, odznaky a žebříček pro Python lab – oddělené od pískoviště, ale nad
stejnými uživatelskými účty (auth.py). Úkoly se kontrolují v prohlížeči přes
Pyodide (viz sandbox/templates/python.html); server jen důvěryhodně zapisuje
výsledek "task_id byl splněn", stejně jako by to udělal kdokoliv jiný, kdo
klientovi věří o kus víc než u pískoviště (tady nejde o reálný systém, jen
o cvičné programování, takže nižší riziko podvádění nevadí).
"""
import json
from typing import List

from . import auth
from .config import PYTHON_PROGRESS_DIR
from .python_tasks import PYTHON_TASKS

XP_PER_TASK = 50
TOTAL_TASKS = len(PYTHON_TASKS)

BADGE_TIERS = [
    {"value": 3, "id": "prvni_radky", "label": "První řádky", "icon": "fa-code"},
    {"value": 6, "id": "logika", "label": "Logika", "icon": "fa-diagram-project"},
    {"value": 10, "id": "smyckar", "label": "Smyčkář", "icon": "fa-rotate"},
    {"value": 15, "id": "pythonista", "label": "Pythonista", "icon": "fa-hat-wizard"},
    {"value": 20, "id": "textovy_mag", "label": "Textový mág", "icon": "fa-wand-magic-sparkles"},
    {"value": 25, "id": "datovy_architekt", "label": "Datový architekt", "icon": "fa-database"},
    {"value": 30, "id": "mistr_pythonu", "label": "Mistr Pythonu", "icon": "fa-crown"},
]


def _progress_path(user: auth.SandboxUser):
    return PYTHON_PROGRESS_DIR / f"{user.uid}.json"


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
    """Zapíše splnění úkolu (idempotentní - druhé volání nic nerozbije)."""
    progress = load_progress(user)
    progress[str(task_id)] = True
    save_progress(user, progress)
    return progress


def badges_for(progress: dict) -> List[dict]:
    done = completed_count(progress)
    result = []
    for tier in BADGE_TIERS:
        result.append({**tier, "unlocked": done >= tier["value"]})
    return result


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


def leaderboard(limit: int = 10) -> List[dict]:
    entries = []
    for user in auth.all_users():
        progress = load_progress(user)
        done = completed_count(progress)
        if done == 0:
            continue
        entries.append({
            "username": user.username,
            "xp": xp_for(progress),
            "completed": done,
        })
    entries.sort(key=lambda e: (-e["xp"], e["username"].lower()))
    return entries[:limit]
