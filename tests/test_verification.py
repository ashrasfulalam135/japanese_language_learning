from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from unittest.mock import patch

from features.auth.services import verification_service as verification


class FakeSMTP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.started_tls = False
        self.logged_in_with = None
        self.sent_messages: list[EmailMessage] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def ehlo(self):
        return None

    def starttls(self):
        self.started_tls = True

    def login(self, username, password):
        self.logged_in_with = (username, password)

    def send_message(self, message):
        self.sent_messages.append(message)


class VerificationTests(unittest.TestCase):
    def test_generate_verification_token_returns_unique_tokens(self) -> None:
        first = verification.generate_verification_token()
        second = verification.generate_verification_token()

        self.assertTrue(first)
        self.assertTrue(second)
        self.assertNotEqual(first, second)

    def test_verification_expiry_timestamp_returns_future_datetime(
        self,
    ) -> None:
        expiry = verification.verification_expiry_timestamp()

        self.assertIsNotNone(expiry.tzinfo)
        self.assertGreater(expiry, datetime.now(timezone.utc))

    def test_is_verification_token_valid_accepts_unexpired_timestamp(
        self,
    ) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        expires_at = expires_at.isoformat()

        valid = verification.is_verification_token_valid(
            {
                "verification_token": "abc123",
                "verification_expires_at": expires_at,
            },
            "abc123",
        )

        self.assertTrue(valid)

    def test_is_verification_token_valid_rejects_mismatch(self) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        expires_at = expires_at.isoformat()

        valid = verification.is_verification_token_valid(
            {
                "verification_token": "abc123",
                "verification_expires_at": expires_at,
            },
            "nope",
        )

        self.assertFalse(valid)

    def test_build_verification_link_uses_root_url_query_param(
        self,
    ) -> None:
        with patch.object(
            verification,
            "APP_BASE_URL",
            "http://localhost:8501",
        ):
            link = verification.build_verification_link("abc123")

        self.assertEqual(link, "http://localhost:8501/?verify_token=abc123")

    def test_send_verification_email_requires_smtp_config(self) -> None:
        with patch.object(verification, "SMTP_HOST", None):
            with self.assertRaisesRegex(
                RuntimeError,
                "SMTP is not configured",
            ):
                verification.send_verification_email(
                    "user@example.com", "User", "token"
                )

    def test_send_verification_email_sends_message(self) -> None:
        smtp_instance = FakeSMTP("smtp.example.com", 587)

        with (
            patch.object(verification, "SMTP_HOST", "smtp.example.com"),
            patch.object(verification, "SMTP_PORT", 587),
            patch.object(
                verification,
                "SMTP_USERNAME",
                "no-reply@example.com",
            ),
            patch.object(verification, "SMTP_PASSWORD", "secret"),
            patch.object(verification, "SMTP_USE_STARTTLS", True),
            patch.object(verification, "EMAIL_FROM", "no-reply@example.com"),
            patch.object(
                verification,
                "APP_BASE_URL",
                "http://localhost:8501",
            ),
            patch(
                "features.auth.services.verification_service.smtplib.SMTP",
                return_value=smtp_instance,
            ),
        ):
            verification.send_verification_email(
                "user@example.com",
                "User",
                "verify-token",
            )

        self.assertTrue(smtp_instance.started_tls)
        self.assertEqual(
            smtp_instance.logged_in_with,
            ("no-reply@example.com", "secret"),
        )
        self.assertEqual(len(smtp_instance.sent_messages), 1)
        payload = smtp_instance.sent_messages[0].get_content()
        self.assertIn("verify-token", payload)
        self.assertIn("Hello User", payload)


if __name__ == "__main__":
    unittest.main()
