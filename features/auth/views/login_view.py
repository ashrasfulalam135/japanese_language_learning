import streamlit as st


def render_login_view(
    authenticator,
    config: dict,
    get_user_record,
    clear_login_state,
) -> None:
    redirect_url = None

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
        "<h3 style='text-align: center;'>Login</h3>",
        unsafe_allow_html=True,
    )

    try:
        with st.form("login_form", clear_on_submit=True):
            email = st.text_input("Email", autocomplete="off")
            password = st.text_input(
                "Password",
                type="password",
                autocomplete="off",
            )
            login_submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if login_submitted:
            if authenticator.authentication_controller.login(
                email,
                password,
            ):
                username = st.session_state.get("username")
                user_record = get_user_record(username)
                if not user_record.get("verified", True):
                    authenticator.logout(location="unrendered")
                    clear_login_state()
                    st.warning("Please verify your email before logging in.")
                    st.stop()

                authenticator.cookie_controller.set_cookie()
                redirect_url = "/dashboard"
    except Exception as exc:
        st.error(str(exc))

    if redirect_url:
        st.success("Login successful. Redirecting to dashboard...")
        st.markdown(
            '<meta http-equiv="refresh" content="1; url=/dashboard">',
            unsafe_allow_html=True,
        )
        st.link_button(
            "Continue to dashboard",
            redirect_url,
            use_container_width=True,
        )
        st.stop()

    if st.button(
        "Not a member? Create account",
        key="go_to_register",
        type="tertiary",
        use_container_width=True,
    ):
        st.switch_page("features/auth/pages/register.py")

    auth_status = st.session_state.get("authentication_status")
    if auth_status:
        username = st.session_state.get("username")
        user_record = get_user_record(username)
        is_verified = user_record.get("verified", True)
        if not is_verified:
            authenticator.logout(location="unrendered")
            clear_login_state()
            st.warning("Please verify your email before logging in.")
            st.stop()
    elif auth_status is False:
        st.error("Email or password is incorrect.")
