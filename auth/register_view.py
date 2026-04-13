import streamlit as st

from auth.verification import (
    generate_verification_token,
    send_verification_email,
    verification_expiry_timestamp,
)


def render_register_view(
    authenticator, config: dict, get_user_record, set_view
) -> None:
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
            confirm_password = st.text_input(
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
            (
                email_of_registered_user,
                username_of_registered_user,
                _,
            ) = authenticator.authentication_controller.register_user(
                new_first_name=first_name,
                new_last_name=last_name,
                new_email=email,
                new_username=email,
                new_password=password,
                new_password_repeat=confirm_password,
                password_hint="",
                roles=["user"],
                captcha=False,
            )
    except Exception as exc:
        st.error(str(exc))
    else:
        if email_of_registered_user:
            user_record = get_user_record(config, username_of_registered_user)
            first_name = user_record.get("first_name", "")
            verification_token = generate_verification_token()

            user_record["roles"] = ["user"]
            user_record["allowed_features"] = []
            user_record["verified"] = False
            user_record["verification_token"] = verification_token
            verification_expires_at = verification_expiry_timestamp()
            user_record["verification_expires_at"] = verification_expires_at

            try:
                send_verification_email(
                    recipient_email=email_of_registered_user,
                    first_name=first_name,
                    token=verification_token,
                )
            except Exception as exc:
                config["credentials"]["usernames"].pop(
                    username_of_registered_user, None
                )
                st.error(f"Registration failed: {exc}")
            else:
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
        set_view("login")
