"""Webová část Python labu - samostatná stránka, ale sdílí přihlášení
(session cookie) s pískovištěm, takže se uživatel přihlašuje jen jednou."""

from flask import Blueprint, jsonify, render_template, request, session

from . import auth
from . import python_gamification as gamification
from .python_tasks import PYTHON_TASKS
from .routes import SESSION_USER, SESSION_UID, SESSION_SV

bp = Blueprint(
    "python_lab",
    __name__,
    url_prefix="/python",
    template_folder="templates",
)


def _current_user():
    username = session.get(SESSION_USER)
    uid = session.get(SESSION_UID)
    if not username or not uid:
        return None
    user = auth.find_user(uid, username)
    if user is None:
        return None
    if session.get(SESSION_SV) != auth.session_version(user):
        return None
    return user


def _public_tasks():
    """Úkoly bez 'check' - ten se posílá zvlášť, až ho kód spustí,
    aby si dítě nemohlo jen otevřít zdroj stránky a přečíst si přesnou
    odpověď (např. 'assert vysledek == 42'). Nejde o bezpečnost - kdokoliv
    technicky zdatný stejně může zavolat /api/complete napřímo - jen o to,
    nekazit hru přes view-source."""
    return [
        {k: v for k, v in t.items() if k != "check"}
        for t in PYTHON_TASKS
    ]


@bp.get("/")
def page():
    return render_template("python.html")


@bp.get("/api/state")
def api_state():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401

    summary = gamification.summary(user)
    return jsonify({
        "ok": True,
        "user": {"username": user.username},
        "tasks": _public_tasks(),
        "progress": summary,
        "leaderboard": gamification.leaderboard(),
    })


@bp.get("/api/task/<int:task_id>/check-code")
def api_task_check_code(task_id):
    """Kontrolní kód se dá teprve po odeslání řešení, ne předem - viz _public_tasks."""
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401
    from .python_tasks import get_task
    task = get_task(task_id)
    if task is None:
        return jsonify({"ok": False, "error": "Úkol neexistuje."}), 404
    return jsonify({"ok": True, "check": task["check"]})


@bp.post("/api/complete")
def api_complete():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401

    data = request.get_json(silent=True) or {}
    task_id = data.get("task_id")
    from .python_tasks import get_task
    if get_task(task_id) is None:
        return jsonify({"ok": False, "error": "Neplatný úkol."}), 400

    already_done = bool(gamification.load_progress(user).get(str(task_id)))
    gamification.mark_complete(user, task_id)
    summary = gamification.summary(user)
    return jsonify({
        "ok": True,
        "newly_completed": not already_done,
        "progress": summary,
        "leaderboard": gamification.leaderboard(),
    })
