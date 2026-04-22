from __future__ import annotations

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from features.auth.services import user_service as db_auth
from tests.test_helpers import create_test_session_local, seed_user


class DbAuthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session_local = create_test_session_local()
        self.session_patcher = patch.object(
            db_auth,
            "SessionLocal",
            self.session_local,
        )
        self.session_patcher.start()

    def tearDown(self) -> None:
        self.session_patcher.stop()

    def test_get_user_record_returns_expected_shape(self) -> None:
        seed_user(self.session_local, username="user@example.com", role="user")

        record = db_auth.get_user_record("user@example.com")

        self.assertEqual(record["username"], "user@example.com")
        self.assertEqual(record["roles"], ["user"])
        self.assertEqual(
            record["allowed_features"],
            ["read_lesson", "create_lesson"],
        )
        self.assertTrue(record["verified"])

    def test_build_credentials_returns_streamlit_authenticator_shape(
        self,
    ) -> None:
        seed_user(
            self.session_local,
            username="learner@example.com",
            first_name="Learner",
            last_name="One",
            role="user",
        )

        credentials = db_auth.build_credentials()

        self.assertIn("usernames", credentials)
        self.assertIn("learner@example.com", credentials["usernames"])
        learner = credentials["usernames"]["learner@example.com"]
        self.assertEqual(learner["name"], "Learner One")
        self.assertEqual(learner["roles"], ["user"])

    def test_register_user_persists_new_unverified_user(self) -> None:
        expires_at = datetime.utcnow() + timedelta(hours=24)

        email, username = db_auth.register_user(
            first_name="New",
            last_name="User",
            email="new@example.com",
            password="Secret123!",
            verification_token="token-123",
            verification_expires_at=expires_at,
        )

        self.assertEqual(email, "new@example.com")
        self.assertEqual(username, "new@example.com")

        record = db_auth.get_user_record("new@example.com")
        self.assertEqual(record["email"], "new@example.com")
        self.assertEqual(record["roles"], ["user"])
        self.assertFalse(record["verified"])
        self.assertEqual(record["verification_token"], "token-123")

    def test_register_user_rejects_duplicate_email(self) -> None:
        expires_at = datetime.utcnow() + timedelta(hours=24)
        seed_user(
            self.session_local,
            username="taken@example.com",
            email="taken@example.com",
        )

        with self.assertRaisesRegex(ValueError, "Email already registered"):
            db_auth.register_user(
                first_name="Taken",
                last_name="User",
                email="taken@example.com",
                password="Secret123!",
                verification_token="token-123",
                verification_expires_at=expires_at,
            )

    def test_delete_user_removes_user(self) -> None:
        seed_user(self.session_local, username="remove@example.com")

        db_auth.delete_user("remove@example.com")

        self.assertEqual(db_auth.get_user_record("remove@example.com"), {})

    def test_verify_user_by_token_marks_user_verified(self) -> None:
        expires_at = datetime.utcnow() + timedelta(hours=24)
        seed_user(
            self.session_local,
            username="verify@example.com",
            is_verified=False,
            verification_token="verify-me",
            verification_expires_at=expires_at,
        )

        verified = db_auth.verify_user_by_token("verify-me")

        self.assertTrue(verified)
        record = db_auth.get_user_record("verify@example.com")
        self.assertTrue(record["verified"])
        self.assertIsNone(record["verification_token"])
        self.assertIsNone(record["verification_expires_at"])

    def test_verify_user_by_token_rejects_expired_token(self) -> None:
        expires_at = datetime.utcnow() - timedelta(hours=1)
        seed_user(
            self.session_local,
            username="expired@example.com",
            is_verified=False,
            verification_token="expired-token",
            verification_expires_at=expires_at,
        )

        verified = db_auth.verify_user_by_token("expired-token")

        self.assertFalse(verified)
        record = db_auth.get_user_record("expired@example.com")
        self.assertFalse(record["verified"])


if __name__ == "__main__":
    unittest.main()
