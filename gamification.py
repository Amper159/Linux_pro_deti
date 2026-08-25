"""XP, odznaky a žebříček – postavené nad *skutečným* pokrokem v pískovišti.

Žádná falešná hra: XP se počítá z úkolů, které opravdu prošly kontrolou proti
souborovému systému v kontejneru (viz `tasks.verify`). Streak se počítá z toho,
kolik dní po sobě se hráč do pískoviště přihlásil (viz `auth.record_login`).
"""

from typing import List

from . import auth
from .tasks import TASKS

XP_PER_TASK = 100

# Odznaky se váží buď na počet dokončených úkolů ("task"), nebo na délku
# přihlašovací série ("streak"). Díky tomu má smysl odznaky mít, i když jsou
# v pískovišti zatím jen tři úkoly.
BADGES = [
    {
        "id": "prvni_krok",
        "label": "První krok",
        "desc": "Dokonči svůj první úkol v pískovišti.",
        "icon": "fa-shoe-prints",
        "kind": "task",
        "value": 1,
    },
    {
        "id": "stavitel",
        "label": "Stavitel",
        "desc": "Dokonči aspoň dva úkoly.",
        "icon": "fa-hammer",
        "kind": "task",
        "value": 2,
    },
    {
        "id": "mistr_piskoviste",
        "label": "Mistr pískoviště",
        "desc": "Dokonči úplně všechny úkoly.",
        "icon": "fa-crown",
        "kind": "task",
        "value": len(TASKS),
    },
    {
        "id": "verny_kadet",
        "label": "Věrný kadet",
        "desc": "Přihlas se 3 dny v řadě.",
        "icon": "fa-fire",
        "kind": "streak",
        "value": 3,
    },
    {
        "id": "tydenni_hrdina",
        "label": "Týdenní hrdina",
        "desc": "Přihlas se 7 dní v řadě.",
        "icon": "fa-bolt",
        "kind": "streak",
        "value": 7,
    },
]


def completed_count(progress: dict) -> int:
    return sum(1 for done in progress.values() if done)


def xp_for(progress: dict) -> int:
    return completed_count(progress) * XP_PER_TASK


def badges_for(progress: dict, stats: dict) -> List[dict]:
    done = completed_count(progress)
    streak = stats.get("streak", 0)
    result = []
    for badge in BADGES:
        threshold = badge["value"]
        earned = done >= threshold if badge["kind"] == "task" else streak >= threshold
        result.append({**badge, "earned": earned})
    return result


def player_summary(user: auth.SandboxUser) -> dict:
    """Kompletní gamifikační stav jednoho hráče (pro hlavičku a odznaky)."""
    progress = auth.load_progress(user)
    stats = auth.load_stats(user)
    return {
        "xp": xp_for(progress),
        "completed": completed_count(progress),
        "total_tasks": len(TASKS),
        "streak": stats.get("streak", 0),
        "best_streak": stats.get("best_streak", 0),
        "badges": badges_for(progress, stats),
    }


def leaderboard(limit: int = 10) -> List[dict]:
    """Žebříček všech registrovaných hráčů podle XP (pak podle streaku)."""
    entries = []
    for user in auth.all_users():
        progress = auth.load_progress(user)
        stats = auth.load_stats(user)
        entries.append(
            {
                "username": user.username,
                "xp": xp_for(progress),
                "completed": completed_count(progress),
                "streak": stats.get("streak", 0),
            }
        )
    entries.sort(key=lambda e: (-e["xp"], -e["streak"], e["username"].lower()))
    return entries[:limit]
