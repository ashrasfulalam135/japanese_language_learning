import streamlit as st

from features.auth.services.session_service import (
    build_authenticator,
    clear_login_state,
    load_auth_config,
    process_verification_link,
)

st.set_page_config(page_title="JLPT Study App", layout="wide")

config = load_auth_config()
process_verification_link(config)
authenticator = build_authenticator(config)
auth_status = st.session_state.get("authentication_status")
roles = st.session_state.get("roles") or []

home_page = st.Page(
    "features/home/pages/home.py",
    title="Home",
    url_path="",
    default=True,
    visibility="hidden",
)
login_page = st.Page(
    "features/auth/pages/login.py",
    title="Login",
    url_path="login",
    visibility="hidden",
)
register_page = st.Page(
    "features/auth/pages/register.py",
    title="Register",
    url_path="register",
    visibility="hidden",
)
dashboard_page = st.Page(
    "features/dashboard/pages/dashboard.py",
    title="Dashboard",
    url_path="dashboard",
    visibility="hidden",
)
read_lesson_page = st.Page(
    "features/lessons/pages/read_lesson.py",
    title="Read Lesson",
    url_path="read-lesson",
    visibility="hidden",
)
create_lesson_page = st.Page(
    "features/lessons/pages/create_lesson.py",
    title="Create Lesson",
    url_path="create-lesson",
    visibility="hidden",
)

if auth_status:
    with st.sidebar:
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlock"]:first-child {
                min-height: 100vh;
            }
            section[data-testid="stSidebar"]
            div[data-testid="stVerticalBlock"]:first-child > div {
                display: flex;
                flex-direction: column;
                min-height: 100%;
            }
            section[data-testid="stSidebar"] .sidebar-spacer {
                margin-top: auto;
                padding-top: 1rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.title("Navigation")
        st.page_link(dashboard_page, label="Dashboard")
        with st.expander("Lesson", expanded=False):
            if "admin" in roles:
                st.page_link(
                    create_lesson_page,
                    label="Create Lesson",
                )
            st.page_link(
                read_lesson_page,
                label="Read Lesson",
            )
        st.markdown(
            '<div class="sidebar-spacer"></div>',
            unsafe_allow_html=True,
        )
        if st.button(
            "Logout",
            key="sidebar_logout",
            use_container_width=True,
        ):
            authenticator.logout(location="unrendered")
            clear_login_state()
            st.switch_page(home_page)

navigation = st.navigation(
    [
        home_page,
        login_page,
        register_page,
        dashboard_page,
        read_lesson_page,
        create_lesson_page,
    ],
)
navigation.run()
