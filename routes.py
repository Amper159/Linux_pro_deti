"""Webová část pískoviště – stránka a její API."""

from flask import Blueprint, jsonify, render_template, request, session

from . import auth, engine, gamification, policy, tasks

bp = Blueprint(
    "sandbox",
    __name__,
    url_prefix="/piskoviste",
    template_folder="templates",
)

SESSION_USER = "sandbox_user"
SESSION_UID = "sandbox_uid"
SESSION_CWD = "sandbox_cwd"


def _current_user():
    username = session.get(SESSION_USER)
    uid = session.get(SESSION_UID)
    if not username or not uid:
        return None
    return auth.find_user(uid, username)


def _state(user: auth.SandboxUser) -> dict:
    engine_kind, container_state = engine.container_info(user)
    return {
        "user": user.to_dict(),
        "cwd": session.get(SESSION_CWD, user.container_home),
        "progress": auth.load_progress(user),
        "engine": engine_kind,
        "container": container_state,
        "gamification": gamification.player_summary(user),
        "leaderboard": gamification.leaderboard(),
    }


@bp.route("/")
def page():
    return render_template("piskoviste.html", tasks=tasks.public_tasks())


@bp.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    try:
        user = auth.login_or_register(
            data.get("username", ""), data.get("password", "")
        )
    except auth.AuthError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    session.clear()
    session[SESSION_USER] = user.username
    session[SESSION_UID] = user.uid
    session[SESSION_CWD] = user.container_home
    session.permanent = True

    auth.record_login(user)
    return jsonify({"ok": True, **_state(user)})


@bp.post("/api/logout")
def api_logout():
    user = _current_user()
    if user:
        engine.stop(user)
    session.clear()
    return jsonify({"ok": True})


@bp.get("/api/state")
def api_state():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401
    auth.record_login(user)
    return jsonify({"ok": True, "tasks": tasks.public_tasks(), **_state(user)})


@bp.post("/api/exec")
def api_exec():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401

    command = (request.get_json(silent=True) or {}).get("command", "")
    cwd = session.get(SESSION_CWD, user.container_home)

    if not command.strip():
        return jsonify({"ok": True, "output": "", "cwd": cwd, "blocked": False})

    reason = policy.check_command(command)
    if reason is not None:
        return jsonify(
            {
                "ok": True,
                "blocked": True,
                "output": f"⛔ {reason}",
                "cwd": cwd,
                "returncode": 126,
            }
        )

    try:
        result = engine.run(user, command, cwd)
    except engine.SandboxError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503

    session[SESSION_CWD] = result.cwd
    return jsonify(
        {
            "ok": True,
            "blocked": False,
            "output": result.output,
            "cwd": result.cwd,
            "returncode": result.returncode,
        }
    )


@bp.post("/api/check")
def api_check():
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401

    task_id = (request.get_json(silent=True) or {}).get("task_id", "")
    try:
        result = tasks.verify(user, task_id)
    except engine.SandboxError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    progress = auth.load_progress(user)
    newly_passed = result["passed"] and not progress.get(task_id)
    if result["passed"]:
        progress[task_id] = True
        auth.save_progress(user, progress)

    return jsonify(
        {
            "ok": True,
            "progress": progress,
            "newly_passed": newly_passed,
            "gamification": gamification.player_summary(user),
            "leaderboard": gamification.leaderboard(),
            **result,
        }
    )


@bp.post("/api/reset")
def api_reset():
    """Vyčistí domovskou složku do původního stavu a restartuje kontejner."""
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401

    engine.stop(user)
    auth.prepare_home(user, reset=True)
    auth.save_progress(user, {})
    session[SESSION_CWD] = user.container_home
    return jsonify(
        {
            "ok": True,
            "cwd": user.container_home,
            "progress": {},
            "gamification": gamification.player_summary(user),
            "leaderboard": gamification.leaderboard(),
        }
    )
