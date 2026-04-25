from __future__ import annotations

import unittest
from unittest.mock import patch

from database.models import Feature, RoleFeature
from features.admin.services import user_management_service
from tests.test_helpers import create_test_session_local, seed_user


class UserManagementServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session_local = create_test_session_local()
        self.user_patch = patch.object(
            user_management_service,
            "SessionLocal",
            self.session_local,
        )
        self.user_patch.start()

    def tearDown(self) -> None:
        self.user_patch.stop()

    def test_list_users_returns_users_with_deserialized_features(self) -> None:
        with self.session_local() as db:
            db.add(RoleFeature(role="user", feature_code="dashboard"))
            db.commit()

        seed_user(
            self.session_local,
            username="user@example.com",
            role="user",
            allowed_features='["read_lesson"]',
        )

        users = user_management_service.list_users()

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].allowed_features, ["read_lesson"])
        self.assertEqual(users[0].role_features, ["dashboard"])
        self.assertEqual(users[0].effective_features, ["dashboard", "read_lesson"])

    def test_list_active_features_returns_only_active_features(self) -> None:
        with self.session_local() as db:
            db.add(
                Feature(
                    code="read_lesson",
                    name="Read Lesson",
                    category="lesson",
                    is_active=True,
                )
            )
            db.add(
                Feature(
                    code="old_feature",
                    name="Old Feature",
                    category="lesson",
                    is_active=False,
                )
            )
            db.commit()

        features = user_management_service.list_active_features()

        self.assertEqual([feature.code for feature in features], ["read_lesson"])

    def test_update_user_access_updates_role_verified_and_features(self) -> None:
        user_id = seed_user(
            self.session_local,
            username="user@example.com",
            role="user",
            is_verified=False,
            allowed_features="[]",
        )

        user_management_service.update_user_access(
            user_id,
            role="admin",
            is_verified=True,
            allowed_features=["create_lesson", "read_lesson", "read_lesson"],
        )

        user = user_management_service.get_user_by_id(user_id)
        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_verified)
        self.assertEqual(user.allowed_features, ["create_lesson", "read_lesson"])

    def test_update_role_features_replaces_existing_role_assignments(self) -> None:
        with self.session_local() as db:
            db.add(RoleFeature(role="user", feature_code="dashboard"))
            db.commit()

        user_management_service.update_role_features(
            "user",
            ["read_lesson", "read_lesson"],
        )

        role = user_management_service.get_role("user")
        self.assertEqual(role.feature_codes, ["read_lesson"])


if __name__ == "__main__":
    unittest.main()
