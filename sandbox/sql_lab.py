"""Webová část SQL Labu (blueprint /sql). Sdílí přihlášení (session cookie)
s Pískovištěm a Python Labem. Dotazy se spouštějí a kontrolují na serveru
nad vymyšlenou databází v paměti (sql_engine.py)."""

from flask import Blueprint, jsonify, render_template, request, session

from . import auth, ratelimit
from . import sql_gamification as gamification
from .sql_data import TABLES_INFO
from .sql_engine import QueryError, check_result, run_query
from .sql_tasks import CHAPTERS, EPILOGUE, PROLOGUE, SQL_TASKS, format_sql, get_task
from .routes import SESSION_USER, SESSION_UID, SESSION_SV, _client_ip

bp = Blueprint(
    "sql_lab",
    __name__,
    url_prefix="/sql",
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


# Referenční řešení (hint) a kontrolní pravidla (must) zůstávají na serveru.
_PUBLIC_FIELDS = ("id", "set", "title", "tip", "story", "victory", "goal", "starter")


def _public_tasks():
    tasks = [{k: t[k] for k in _PUBLIC_FIELDS} for t in SQL_TASKS]
    for t in tasks:
        t["starter"] = format_sql(t["starter"])
    return tasks


@bp.get("/")
def page():
    return render_template("sql.html")


@bp.get("/api/state")
def api_state():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401
    return jsonify({
        "ok": True,
        "user": {"username": user.username},
        "tasks": _public_tasks(),
        "chapters": CHAPTERS,
        "prologue": PROLOGUE,
        "epilogue": EPILOGUE,
        "tables": TABLES_INFO,
        "progress": gamification.summary(user),
        "leaderboard": gamification.leaderboard(user),
    })


@bp.get("/api/hint/<int:task_id>")
def api_hint(task_id):
    """Řešení se vydává jen na výslovné přání (tlačítko Ukaž řešení)."""
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401
    task = get_task(task_id)
    if task is None:
        return jsonify({"ok": False, "error": "Úkol neexistuje."}), 404
    return jsonify({"ok": True, "hint": format_sql(task["hint"])})


@bp.post("/api/run")
def api_run():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401
    if ratelimit.check_sql(_client_ip()) is not None:
        return jsonify({"ok": False, "error": "Moc dotazů za sebou. Chvíli počkej a zkus to znovu."}), 429

    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    if not isinstance(query, str):
        return jsonify({"ok": False, "error": "Neplatný dotaz."}), 400
    task_id = data.get("task_id")
    task = None
    if task_id is not None:
        task = get_task(task_id) if isinstance(task_id, int) else None
        if task is None:
            return jsonify({"ok": False, "error": "Neplatný úkol."}), 400

    try:
        result = run_query(query)
    except QueryError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 200

    payload = {
        "ok": True,
        "columns": result["columns"],
        "rows": result["rows"],
        "truncated": result["truncated"],
        "correct": None,
    }
    if task is not None:
        advice = check_result(task, query, result)
        payload["correct"] = advice == ""
        if advice:
            payload["advice"] = advice
        else:
            already_done = bool(gamification.load_progress(user).get(str(task["id"])))
            gamification.mark_complete(user, task["id"])
            payload["newly_completed"] = not already_done
            payload["progress"] = gamification.summary(user)
            payload["leaderboard"] = gamification.leaderboard(user)
    return jsonify(payload)
