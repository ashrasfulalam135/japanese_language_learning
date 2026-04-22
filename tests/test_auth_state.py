from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from features.auth.services import session_service as auth_state


class AuthStateTests(unittest.TestCase):
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
