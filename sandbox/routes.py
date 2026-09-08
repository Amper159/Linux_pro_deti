"""Webová část pískoviště – stránka a její API."""

from flask import Blueprint, jsonify, render_template, request, session, url_for

from . import auth, engine, gamification, policy, ratelimit, tasks
from .mailer import send_reset_email

bp = Blueprint(
    "sandbox",
    __name__,
    url_prefix="/piskoviste",
    template_folder="templates",
)

SESSION_USER = "sandbox_user"
SESSION_UID = "sandbox_uid"
SESSION_CWD = "sandbox_cwd"
SESSION_SV = "sandbox_sv"


def _current_user():
    username = session.get(SESSION_USER)
    uid = session.get(SESSION_UID)
    if not username or not uid:
        return None
    user = auth.find_user(uid, username)
    if user is None:
        return None
    # Cookie musí nést aktuální "verzi" session, jinak byla zneplatněna
    # odhlášením (viz auth.bump_session_version) - i kdyby byla jinak platná.
    if session.get(SESSION_SV) != auth.session_version(user):
        return None
    return user


def _client_ip() -> str:
    """IP klienta - aplikace běží za Caddy reverzní proxy, takže reálná IP
    je v X-Forwarded-For (Caddy ji nastavuje sama, nejde ji z venku podvrhnout,
    protože Flask vidí jen to, co pošle Caddy)."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


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
    ip = _client_ip()
    retry_after = ratelimit.check_ip(ip)
    if retry_after is not None:
        return jsonify({
            "ok": False,
            "error": "Moc pokusů o přihlášení najednou. Zkus to za chvíli znovu.",
        }), 429

    data = request.get_json(silent=True) or {}
    username_key = auth.normalize_username(data.get("username", ""))

    lock_remaining = ratelimit.check_username_lock(username_key)
    if lock_remaining is not None:
        minutes = max(1, int(lock_remaining // 60) + 1)
        return jsonify({
            "ok": False,
            "error": f"Moc špatných pokusů o heslo. Zkus to prosím za {minutes} min.",
        }), 429

    try:
        user = auth.login_or_register(
            data.get("username", ""), data.get("password", ""), data.get("email", "")
        )
    except auth.WrongPassword as exc:
        ratelimit.record_failed_password(username_key)
        return jsonify({"ok": False, "error": str(exc)}), 400
    except auth.AuthError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    ratelimit.record_success(username_key)

    session.clear()
    session[SESSION_USER] = user.username
    session[SESSION_UID] = user.uid
    session[SESSION_CWD] = user.container_home
    session[SESSION_SV] = auth.session_version(user)
    session.permanent = True

    auth.record_login(user)
    return jsonify({"ok": True, **_state(user)})


@bp.post("/api/forgot-password")
def api_forgot_password():
    ip = _client_ip()
    retry_after = ratelimit.check_ip(ip)
    if retry_after is not None:
        return jsonify({
            "ok": False,
            "error": "Moc pokusů najednou. Zkus to za chvíli znovu.",
        }), 429

    username = (request.get_json(silent=True) or {}).get("username", "")
    result = auth.request_password_reset(username)
    if result is not None:
        user, token, email = result
        reset_link = url_for("sandbox.reset_password_page", token=token, _external=True)
        send_reset_email(email, user.username, reset_link)

    # Odpověď je schválně vždycky stejná - jinak by šlo poznat, jestli dané
    # jméno/e-mail vůbec existuje (viz auth.request_password_reset).
    return jsonify({
        "ok": True,
        "message": "Pokud účet s tímhle jménem existuje a má nastavený e-mail, poslali jsme na něj odkaz na obnovu hesla.",
    })


@bp.get("/reset-heslo")
def reset_password_page():
    return render_template("reset_password.html", token=request.args.get("token", ""))


@bp.post("/api/reset-password")
def api_reset_password():
    ip = _client_ip()
    retry_after = ratelimit.check_ip(ip)
    if retry_after is not None:
        return jsonify({
            "ok": False,
            "error": "Moc pokusů najednou. Zkus to za chvíli znovu.",
        }), 429

    data = request.get_json(silent=True) or {}
    try:
        auth.reset_password(data.get("token", ""), data.get("password", ""))
    except auth.AuthError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True})


@bp.post("/api/logout")
def api_logout():
    user = _current_user()
    if user:
        engine.stop(user)
        auth.bump_session_version(user)
    session.clear()
    return jsonify({"ok": True})


@bp.post("/api/delete-account")
def api_delete_account():
    """Trvale smaže účet i všechna jeho data - právo na výmaz."""
    user = _current_user()
    if user is None:
        return jsonify({"ok": False, "error": "Nejsi přihlášený."}), 401

    engine.stop(user)
    auth.delete_account(user)
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

    raw_task_id = (request.get_json(silent=True) or {}).get("task_id", "")
    task_id = str(raw_task_id)
    try:
        result = tasks.verify(user, raw_task_id)
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