from __future__ import annotations

import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from config import (
    APP_BASE_URL,
    EMAIL_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_STARTTLS,
    VERIFICATION_EXPIRY_HOURS,
)


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def verification_expiry_timestamp() -> str:
    expiry_delta = timedelta(hours=VERIFICATION_EXPIRY_HOURS)
    expires_at = datetime.now(timezone.utc) + expiry_delta
    return expires_at.isoformat()


def is_verification_token_valid(user_record: dict, token: str) -> bool:
    stored_token = user_record.get("verification_token")
    expires_at = user_record.get("verification_expires_at")

    if not stored_token or not expires_at or stored_token != token:
        return False

    try:
        expiry_time = datetime.fromisoformat(expires_at)
    except ValueError:
        return False

    return datetime.now(timezone.utc) <= expiry_time


def build_verification_link(token: str) -> str:
    return f"{APP_BASE_URL.rstrip('/')}/?verify_token={token}"


def send_verification_email(
    recipient_email: str,
    first_name: str,
    token: str,
) -> None:
    if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
            "SMTP_PASSWORD, EMAIL_FROM, and APP_BASE_URL in your environment."
        )

    verification_link = build_verification_link(token)
    display_name = first_name or "there"

    message = EmailMessage()
    message["Subject"] = "Verify your JLPT Study App account"
    message["From"] = EMAIL_FROM
    message["To"] = recipient_email
    message.set_content(
        "\n".join(
            [
                f"Hello {display_name},",
                "",
                "Thank you for registering for JLPT Study App.",
                "Please verify your email by opening the link below:",
                verification_link,
                "",
                f"This link will expire in {VERIFICATION_EXPIRY_HOURS} hours.",
            ]
        )
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        if SMTP_USE_STARTTLS:
            server.starttls()
            server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)
