"""XP, odznaky, sady a žebříček – nad *skutečným* pokrokem v pískovišti.

Žádná falešná hra: XP se počítá z úkolů, které opravdu prošly kontrolou proti
souborovému systému / procesům v kontejneru (viz `tasks.verify`). Streak se
počítá z toho, kolik dní po sobě se hráč do pískoviště přihlásil
(viz `auth.record_login`).

90 úkolů je rozdělených do 3 sad po 30 (viz `tasks.py`). Sady se odemykají
popořadě – druhá a třetí jsou zamčené, dokud není ta předchozí hotová na
100 %. Odznaky se udílí po každých 5 splněných úkolech v *aktuálně
odemčené* sadě.
"""

from typing import List

from . import auth
from .tasks import SET_SIZE, TOTAL_SETS, TASKS

XP_PER_TASK = 100

# Kolikátý úkol (v rámci JEDNÉ sady) daný odznak odemyká + jak vypadá.
SET_BADGE_TIERS = [
    {"value": 5, "id": "pruzkumnik", "label": "Průzkumník", "icon": "fa-compass"},
    {"value": 10, "id": "gamer", "label": "Gamer", "icon": "fa-gamepad"},
    {"value": 15, "id": "technik", "label": "Technik", "icon": "fa-wrench"},
    {"value": 20, "id": "pokrocily", "label": "Pokročilý", "icon": "fa-user-ninja"},
    {"value": 25, "id": "guru", "label": "Guru", "icon": "fa-bolt"},
    {"value": 30, "id": "mistr_sady", "label": "Mistr sady", "icon": "fa-crown"},
]

STREAK_BADGES = [
    {"value": 3, "id": "verny_kadet", "label": "Věrný kadet", "icon": "fa-fire", "desc": "Přihlas se 3 dny v řadě."},
    {"value": 7, "id": "tydenni_hrdina", "label": "Týdenní hrdina", "icon": "fa-meteor", "desc": "Přihlas se 7 dní v řadě."},
    {"value": 30, "id": "mesicni_legenda", "label": "Měsíční legenda", "icon": "fa-star", "desc": "Přihlas se 30 dní v řadě."},
]

_TASK_SET = {t["id"]: t["set"] for t in TASKS}


def _completed_ids(progress: dict):
    """ID úkolů, které hráč opravdu splnil (klíče v progress jsou stringy)."""
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


def completed_in_set(progress: dict, set_no: int) -> int:
    ids = _completed_ids(progress)
    return sum(1 for task_id in ids if _TASK_SET.get(task_id) == set_no)


def xp_for(progress: dict) -> int:
    return completed_count(progress) * XP_PER_TASK


def active_set(progress: dict) -> int:
    """První sada, která ještě není hotová na 100 % (nebo poslední, když je vše hotovo)."""
    for set_no in range(1, TOTAL_SETS + 1):
        if completed_in_set(progress, set_no) < SET_SIZE:
            return set_no
    return TOTAL_SETS


def sets_overview(progress: dict) -> List[dict]:
    """Přehled všech sad – kolikátá je aktivní, kolik je v každé hotovo."""
    active = active_set(progress)
    overview = []
    for set_no in range(1, TOTAL_SETS + 1):
        done = completed_in_set(progress, set_no)
        overview.append({
            "set": set_no,
            "done": done,
            "total": SET_SIZE,
            "complete": done >= SET_SIZE,
            "locked": set_no > active,
            "active": set_no == active,
        })
    return overview


def badges_for(progress: dict, stats: dict) -> List[dict]:
    done_in_active = completed_in_set(progress, active_set(progress))
    streak = stats.get("streak", 0)

    badges = []
    for tier in SET_BADGE_TIERS:
        badges.append({**tier, "kind": "set", "earned": done_in_active >= tier["value"]})
    for tier in STREAK_BADGES:
        badges.append({**tier, "kind": "streak", "earned": streak >= tier["value"]})
    badges.append({
        "id": "mistr_linuxu",
        "label": "Mistr Linuxu",
        "icon": "fa-trophy",
        "desc": "Dokonči úplně všech 90 úkolů.",
        "kind": "overall",
        "earned": completed_count(progress) >= len(TASKS),
    })
    return badges


def player_summary(user: auth.SandboxUser) -> dict:
    """Kompletní gamifikační stav jednoho hráče (hlavička, odznaky, sady)."""
    progress = auth.load_progress(user)
    stats = auth.load_stats(user)
    return {
        "xp": xp_for(progress),
        "completed": completed_count(progress),
        "total_tasks": len(TASKS),
        "streak": stats.get("streak", 0),
        "best_streak": stats.get("best_streak", 0),
        "active_set": active_set(progress),
        "sets": sets_overview(progress),
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
