import smtplib
from email.message import EmailMessage
from typing import Iterable

from app.core.config import settings


def _normalize_recipients(recipients: str | Iterable[str]) -> list[str]:
    if isinstance(recipients, str):
        items = [recipients]
    else:
        items = list(recipients)
    return [item for item in items if item]


def send_email(recipients: str | Iterable[str], subject: str, body: str) -> None:
    to_emails = _normalize_recipients(recipients)
    if not to_emails:
        return

    if not settings.SMTP_HOST:
        raise RuntimeError("SMTP_HOST no configurado")

    from_address = settings.SMTP_FROM or settings.SMTP_USER or "no-reply@example.com"

    message = EmailMessage()
    message["From"] = from_address
    message["To"] = ", ".join(to_emails)
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)
