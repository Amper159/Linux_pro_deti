"""Odesílání e-mailů z aplikace: obnova zapomenutého hesla a upozornění na
novou zprávu ze zpětné vazby.

Dokud není nastavené SMTP_HOST (viz config.py / .env), e-mail se doopravdy
neposílá - obsah se jen vypíše do logu, aby šla funkce vyzkoušet i na
vývojářském stroji bez poštovního serveru.
"""

import logging
import re
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from . import config

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _send(message: EmailMessage) -> None:
    """Sdílená logika odeslání - použitá pro obnovu hesla i pro upozornění."""
    if config.SMTP_USE_SSL:
        with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as smtp:
            if config.SMTP_USER:
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            if config.SMTP_USER:
                smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.send_message(message)


def send_reset_email(to_email: str, username: str, reset_link: str) -> None:
    if not config.SMTP_HOST:
        logger.warning(
            "SMTP není nastavené - odkaz na obnovu hesla pro '%s' (%s): %s",
            username, to_email, reset_link,
        )
        return

    message = EmailMessage()
    message["Subject"] = "Obnova hesla – Linux pro děti"
    message["From"] = config.SMTP_FROM
    message["To"] = to_email
    minutes = config.PASSWORD_RESET_TTL_SECONDS // 60
    message.set_content(
        f"Ahoj {username},\n\n"
        "někdo (doufejme, že ty) požádal o nové heslo do Pískoviště na linuxhrou.cz.\n\n"
        f"Nastav si nové heslo tady (odkaz platí {minutes} minut):\n"
        f"{reset_link}\n\n"
        "Pokud jsi o nic nežádal(a), tenhle e-mail prostě ignoruj - heslo zůstane, jaké bylo.\n"
    )

    try:
        _send(message)
    except (smtplib.SMTPException, OSError):
        # Odpověď API je schválně stejná ať e-mail dorazí nebo ne (viz routes.py),
        # takže případnou chybu jen zalogujeme a uživateli nic nespadne.
        logger.exception("Nepodařilo se odeslat e-mail s obnovou hesla na %s", to_email)


def send_feedback_notification(zaznam: dict) -> None:
    """Upozornění provozovateli, že přišla nová zpráva ze zpětné vazby na homepage.
    Selhání odeslání nikdy nesmí shodit uložení zprávy samotné (viz volání v app.py)."""
    if not config.FEEDBACK_NOTIFY_EMAIL:
        return
    if not config.SMTP_HOST:
        logger.warning(
            "SMTP není nastavené - zpětná vazba od '%s' (%s): %s",
            zaznam["jmeno"], zaznam["typ"], zaznam["zprava"],
        )
        return

    typ_popis = {
        "libi": "👍 Líbí se mi", "nelibi": "👎 Nelíbí se mi",
        "navrh": "💡 Návrh", "skola": "🏫 Škola / kroužek", "dotaz": "❓ Dotaz / jiné",
    }.get(zaznam["typ"], zaznam["typ"])
    kontakt = zaznam.get("kontakt", "")

    message = EmailMessage()
    # Předmět obsahuje typ i jméno, ať je v doručené poště hned vidět, od koho zpráva je.
    message["Subject"] = f"Linuxhrou.cz – {typ_popis} – {zaznam['jmeno']}"
    message["From"] = config.SMTP_FROM
    message["To"] = config.FEEDBACK_NOTIFY_EMAIL
    # Když je kontakt e-mail, půjde odpovědět rovnou tlačítkem "Odpovědět".
    if _EMAIL_RE.match(kontakt):
        try:
            jmeno = zaznam["jmeno"]
            message["Reply-To"] = kontakt if jmeno == "Anonym" else formataddr((jmeno, kontakt))
        except ValueError:
            message["Reply-To"] = kontakt
    message.set_content(
        f"Od: {zaznam['jmeno']}\n"
        f"Typ: {typ_popis}\n"
        + (f"Kontakt: {kontakt}\n" if kontakt else "")
        + f"Čas: {zaznam['cas']}\n\n"
        f"{zaznam['zprava']}\n"
    )

    try:
        _send(message)
    except (smtplib.SMTPException, OSError):
        logger.exception("Nepodařilo se odeslat upozornění na zpětnou vazbu")
