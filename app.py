import streamlit as st

from features.auth.services.user_service import get_user_record
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
user_record = get_user_record(st.session_state.get("username")) if auth_status else {}
allowed_features = user_record.get("allowed_features", [])


def logout():
    authenticator.logout(location="unrendered")
    clear_login_state()
    st.switch_page(home_page)


home_page = st.Page(
    "features/home/pages/home.py",
    title="Home",
    url_path="",
    default=True,
)
login_page = st.Page(
    "features/auth/pages/login.py",
    title="Login",
    url_path="login",
)
register_page = st.Page(
    "features/auth/pages/register.py",
    title="Register",
    url_path="register",
)
dashboard_page = st.Page(
    "features/dashboard/pages/dashboard.py",
    title="Dashboard",
    url_path="dashboard",
    icon=":material/dashboard:",
)
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
role_management_page = st.Page(
    "features/admin/pages/role_management.py",
    title="Role Management",
    url_path="role-management",
    icon=":material/verified_user:",
)
read_lesson_page = st.Page(
    "features/lessons/pages/read_lesson.py",
    title="Read Lesson",
    url_path="read-lesson",
    icon=":material/book:",
)
create_lesson_page = st.Page(
    "features/lessons/pages/create_lesson.py",
    title="Create Lesson",
    url_path="create-lesson",
    icon=":material/note_add:",
)

common_pages = [dashboard_page, logout_page]
management_pages = [
    role_management_page,
]
lesson_pages = [
    read_lesson_page,
    create_lesson_page,
]

pages = {}
if auth_status:
    with st.sidebar:
        if "user" in roles:
            pages["Lesson"] = [read_lesson_page]
        if "admin" in roles:
            pages["Management"] = management_pages
            pages["Lesson"] = lesson_pages

if len(pages) > 0:
    navigation = st.navigation(
        {f"{st.session_state.get('name')}": common_pages} | pages
    )
else:
    navigation = st.navigation(
        [home_page, login_page, register_page], position="hidden"
    )

navigation.run()
