"""Odesílání e-mailu s odkazem na obnovu zapomenutého hesla.

Dokud není nastavené SMTP_HOST (viz config.py / .env), e-mail se doopravdy
neposílá - odkaz se jen vypíše do logu, aby šla funkce vyzkoušet i na
vývojářském stroji bez poštovního serveru.
"""

import logging
import smtplib
from email.message import EmailMessage

from . import config

logger = logging.getLogger(__name__)


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
    except (smtplib.SMTPException, OSError):
        # Odpověď API je schválně stejná ať e-mail dorazí nebo ne (viz routes.py),
        # takže případnou chybu jen zalogujeme a uživateli nic nespadne.
        logger.exception("Nepodařilo se odeslat e-mail s obnovou hesla na %s", to_email)
