from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from features.auth.services import session_service as auth_state


class AuthStateTests(unittest.TestCase):
    def test_restore_authentication_from_cookie_reruns_after_cookie_login(self) -> None:
        authenticator = MagicMock()

        def login_side_effect(*args, **kwargs):
            auth_state.st.session_state["authentication_status"] = True
            auth_state.st.session_state["username"] = "admin@jlpt.local"

        authenticator.login.side_effect = login_side_effect
        auth_state.st.session_state["authentication_status"] = None
        auth_state.st.session_state["username"] = None

        with patch.object(
            auth_state.st,
            "rerun",
            side_effect=RuntimeError("rerun"),
        ) as rerun_mock:
            with self.assertRaisesRegex(RuntimeError, "rerun"):
                auth_state.restore_authentication_from_cookie(authenticator)

        rerun_mock.assert_called_once()
        self.assertEqual(
            auth_state.st.session_state["_auth_cookie_restored"],
            ("admin@jlpt.local", True),
        )

    def test_restore_authentication_from_cookie_skips_rerun_if_already_restored(
        self,
    ) -> None:
        authenticator = MagicMock()
        auth_state.st.session_state["authentication_status"] = None
        auth_state.st.session_state["username"] = None
        auth_state.st.session_state["_auth_cookie_restored"] = (
            "admin@jlpt.local",
            True,
        )

        def login_side_effect(*args, **kwargs):
            auth_state.st.session_state["authentication_status"] = True
            auth_state.st.session_state["username"] = "admin@jlpt.local"

        authenticator.login.side_effect = login_side_effect

        with patch.object(auth_state.st, "rerun") as rerun_mock:
            auth_state.restore_authentication_from_cookie(authenticator)

        rerun_mock.assert_not_called()

    def test_build_authenticator_refreshes_existing_authenticator_from_cookie(
        self,
    ) -> None:
        authenticator = MagicMock()
        auth_state.st.session_state["authenticator"] = authenticator

        with patch.object(
            auth_state, "restore_authentication_from_cookie"
        ) as restore_mock:
            result = auth_state.build_authenticator(
                {
                    "cookie": {
                        "name": "cookie-name",
                        "key": "cookie-key",
                        "expiry_days": 1,
                    }
                }
            )

        self.assertIs(result, authenticator)
        restore_mock.assert_called_once_with(authenticator)

    def test_build_authenticator_creates_authenticator_and_restores_cookie(
        self,
    ) -> None:
        auth_state.st.session_state.pop("authenticator", None)
        authenticator = MagicMock()

        with (
            patch.object(auth_state, "ensure_user_table_schema"),
            patch.object(auth_state.stauth, "Authenticate", return_value=authenticator),
            patch.object(
                auth_state, "build_credentials", return_value={"usernames": {}}
            ),
            patch.object(
                auth_state, "restore_authentication_from_cookie"
            ) as restore_mock,
        ):
            result = auth_state.build_authenticator(
                {
                    "cookie": {
                        "name": "cookie-name",
                        "key": "cookie-key",
                        "expiry_days": 1,
                    }
                }
            )

        self.assertIs(result, authenticator)
        restore_mock.assert_called_once_with(authenticator)
        self.assertIs(auth_state.st.session_state["authenticator"], authenticator)

    def test_clear_login_state_resets_session_values(self) -> None:
        auth_state.st.session_state["authentication_status"] = True
        auth_state.st.session_state["name"] = "Admin"
        auth_state.st.session_state["username"] = "admin@example.com"
        auth_state.st.session_state["roles"] = ["admin"]

        auth_state.clear_login_state()

        self.assertIsNone(auth_state.st.session_state["authentication_status"])
        self.assertIsNone(auth_state.st.session_state["name"])
        self.assertIsNone(auth_state.st.session_state["username"])
        self.assertIsNone(auth_state.st.session_state["roles"])

    def test_process_verification_link_returns_false_without_token(
        self,
    ) -> None:
        with patch.object(
            auth_state.st,
            "query_params",
            {},
            create=True,
        ):
            processed = auth_state.process_verification_link({})

        self.assertFalse(processed)

    def test_process_verification_link_verifies_valid_token(self) -> None:
        query_params = {"verify_token": "abc123"}

        with (
            patch.object(
                auth_state.st,
                "query_params",
                query_params,
                create=True,
            ),
            patch.object(
                auth_state,
                "verify_user_by_token",
                return_value=True,
            ),
            patch.object(auth_state.st, "success") as success_mock,
        ):
            processed = auth_state.process_verification_link({})

        self.assertTrue(processed)
        success_mock.assert_called_once()
        self.assertEqual(query_params, {})

    def test_process_verification_link_rejects_invalid_token(self) -> None:
        query_params = {"verify_token": "bad-token"}

        with (
            patch.object(
                auth_state.st,
                "query_params",
                query_params,
                create=True,
            ),
            patch.object(
                auth_state,
                "verify_user_by_token",
                return_value=False,
            ),
            patch.object(auth_state.st, "error") as error_mock,
        ):
            processed = auth_state.process_verification_link({})

        self.assertFalse(processed)
        error_mock.assert_called_once()
        self.assertEqual(query_params, {})

    def test_require_role_allows_matching_role(self) -> None:
        auth_state.st.session_state["roles"] = ["admin"]

        auth_state.require_role("admin")

    def test_require_role_blocks_non_matching_role(self) -> None:
        auth_state.st.session_state["roles"] = ["user"]

        with (
            patch.object(auth_state.st, "error") as error_mock,
            patch.object(
                auth_state.st,
                "stop",
                side_effect=RuntimeError("stopped"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "stopped"):
                auth_state.require_role("admin")

        expected_message = "You do not have access to this page."
        error_mock.assert_called_once_with(expected_message)

    def test_require_feature_allows_admin_without_feature_assignment(self) -> None:
        auth_state.st.session_state["roles"] = ["admin"]

        auth_state.require_feature("read_lesson")

    def test_require_feature_allows_assigned_feature_for_user(self) -> None:
        auth_state.st.session_state["roles"] = ["user"]
        auth_state.st.session_state["username"] = "user@example.com"

        with patch.object(
            auth_state,
            "get_user_record",
            return_value={"allowed_features": ["read_lesson"]},
        ):
            auth_state.require_feature("read_lesson")

    def test_require_feature_blocks_unassigned_feature(self) -> None:
        auth_state.st.session_state["roles"] = ["user"]
        auth_state.st.session_state["username"] = "user@example.com"

        with (
            patch.object(
                auth_state,
                "get_user_record",
                return_value={"allowed_features": []},
            ),
            patch.object(auth_state.st, "error") as error_mock,
            patch.object(auth_state.st, "stop", side_effect=RuntimeError("stopped")),
        ):
            with self.assertRaisesRegex(RuntimeError, "stopped"):
                auth_state.require_feature("read_lesson")

        error_mock.assert_called_once_with("You do not have access to this page.")

    def test_require_login_redirects_when_not_authenticated(self) -> None:
        authenticator = MagicMock()
        auth_state.st.session_state["authentication_status"] = None

        with patch.object(
            auth_state.st,
            "switch_page",
            side_effect=RuntimeError("redirected"),
        ) as switch_mock:
            with self.assertRaisesRegex(RuntimeError, "redirected"):
                auth_state.require_login(authenticator, {})

        switch_mock.assert_called_once_with("features/auth/pages/login.py")

    def test_require_login_logs_out_unverified_user(self) -> None:
        authenticator = MagicMock()
        auth_state.st.session_state["authentication_status"] = True
        auth_state.st.session_state["username"] = "user@example.com"

        with (
            patch.object(
                auth_state,
                "get_user_record",
                return_value={"verified": False},
            ),
            patch.object(
                auth_state.st,
                "switch_page",
                side_effect=RuntimeError("redirected"),
            ) as switch_mock,
        ):
            with self.assertRaisesRegex(RuntimeError, "redirected"):
                auth_state.require_login(authenticator, {})

        authenticator.logout.assert_called_once_with(location="unrendered")
        switch_mock.assert_called_once_with("features/auth/pages/login.py")


if __name__ == "__main__":
    unittest.main()
