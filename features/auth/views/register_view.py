import streamlit as st

from features.auth.services.user_service import delete_user, register_user
from features.auth.services.verification_service import (
    generate_verification_token,
    send_verification_email,
    verification_expiry_timestamp,
)


def render_register_view(
    authenticator,
    config: dict,
    get_user_record,
) -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stForm"] {
            padding: 1rem;
        }
        div[data-testid="stForm"] button[kind="secondaryFormSubmit"],
        div[data-testid="stForm"] button[kind="primaryFormSubmit"],
        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"],
        div[data-testid="stForm"]
        div[data-testid="stFormSubmitButton"] > button {
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h1 style='text-align: center;'>JLPT Study App</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='text-align: center;'>Register</h3>",
        unsafe_allow_html=True,
    )

    try:
        with st.form("register_form", clear_on_submit=True):
            first_name_col, last_name_col = st.columns(2, gap="small")
            first_name = first_name_col.text_input(
                "First name",
                autocomplete="off",
            )
            last_name = last_name_col.text_input(
                "Last name",
                autocomplete="off",
            )
            email = st.text_input("Email", autocomplete="off")
            password = st.text_input(
                "Password",
                type="password",
                autocomplete="off",
            )
            st.text_input(
                "Confirm password",
                type="password",
                autocomplete="off",
            )
            register_submitted = st.form_submit_button(
                "Create account",
                use_container_width=True,
            )

        email_of_registered_user = None
        username_of_registered_user = None
        if register_submitted:
            verification_token = generate_verification_token()
            verification_expires_at = verification_expiry_timestamp()
            (
                email_of_registered_user,
                username_of_registered_user,
            ) = register_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                verification_token=verification_token,
                verification_expires_at=verification_expires_at,
            )
    except Exception as exc:
        st.error(str(exc))
    else:
        if email_of_registered_user:
            user_record = get_user_record(username_of_registered_user)
            first_name = user_record.get("first_name", "")

            try:
                send_verification_email(
                    recipient_email=email_of_registered_user,
                    first_name=first_name,
                    token=user_record["verification_token"],
                )
            except Exception as exc:
                delete_user(username_of_registered_user)
                st.error(f"Registration failed: {exc}")
            else:
                st.session_state.pop("authenticator", None)
                st.success(
                    f"Account created for {email_of_registered_user}. "
                    "Please verify your email before logging in."
                )

    if st.button(
        "Already have an account? Back to login",
        key="go_to_login",
        type="tertiary",
        use_container_width=True,
    ):
        st.switch_page("features/auth/pages/login.py")
