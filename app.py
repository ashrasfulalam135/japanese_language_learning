from copy import deepcopy
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from auth.login_view import render_login_view
from auth.register_view import render_register_view
from auth.verification import (
    is_verification_token_valid,
)
from dashboard.dashboard_view import render_dashboard
from home.home_view import render_home_page
from yaml.loader import SafeLoader

CONFIG_PATH = Path(__file__).resolve().parent / "auth_config.yaml"


def load_auth_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.load(file, Loader=SafeLoader)


def save_auth_config(config: dict) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)


def get_user_record(config: dict, username: str | None) -> dict:
    if not username:
        return {}
    return config["credentials"]["usernames"].get(username, {})


def clear_login_state() -> None:
    st.session_state["authentication_status"] = None
    st.session_state["name"] = None
    st.session_state["username"] = None
    st.session_state["roles"] = None


def process_verification_link(config: dict) -> bool:
    token = st.query_params.get("verify_token")
    if not token:
        return False

    for user_record in config["credentials"]["usernames"].values():
        if is_verification_token_valid(user_record, token):
            user_record["verified"] = True
            user_record["verification_token"] = None
            user_record["verification_expires_at"] = None
            save_auth_config(config)
            st.query_params.clear()
            st.success("Your email has been verified. You can log in now.")
            return True

    st.query_params.clear()
    st.error("This verification link is invalid or has expired.")
    return False


def get_view() -> str:
    return st.query_params.get("view", "home")


def set_view(view: str) -> None:
    st.query_params["view"] = view
    st.rerun()


def render_auth_navigation(active_view: str) -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stForm"] {
            padding: 1rem;
        }
        div[data-testid="stForm"] button[kind="secondaryFormSubmit"],
        div[data-testid="stForm"] button[kind="primaryFormSubmit"],
        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"],
        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"]
        > button {
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
    if active_view == "login":
        st.markdown(
            "<h3 style='text-align: center;'>Login</h3>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<h3 style='text-align: center;'>Register</h3>",
            unsafe_allow_html=True,
        )


st.set_page_config(page_title="JLPT Study App", layout="wide")

config = load_auth_config()
original_config = deepcopy(config)
process_verification_link(config)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)
st.session_state["authenticator"] = authenticator

auth_status = st.session_state.get("authentication_status")

if not auth_status:
    current_view = get_view()

    if current_view == "home":
        render_home_page(set_view)
    else:
        _, auth_col, _ = st.columns([1, 1.25, 1], gap="large")
        with auth_col:
            render_auth_navigation(current_view)

            if current_view == "login":
                render_login_view(
                    authenticator=authenticator,
                    config=config,
                    get_user_record=get_user_record,
                    clear_login_state=clear_login_state,
                    set_view=set_view,
                )
            else:
                render_register_view(
                    authenticator=authenticator,
                    config=config,
                    get_user_record=get_user_record,
                    set_view=set_view,
                )

auth_status = st.session_state.get("authentication_status")

if auth_status:
    st.subheader("Login")
    render_dashboard(config, get_user_record)
    try:
        authenticator.logout("Logout", key="logout_button")
    except Exception as exc:
        st.error(str(exc))

    read_lesson_page = st.Page(
        "lesson_pages/read_lesson.py", title="Read Lesson", default=True
    )
    pages = [read_lesson_page]

    roles = st.session_state.get("roles") or []
    if "admin" in roles:
        create_lesson_page = st.Page(
            "lesson_pages/create_lesson.py", title="Create Lesson"
        )
        pages.insert(1, create_lesson_page)

    navigation = st.navigation(pages)
    navigation.run()

if config != original_config:
    save_auth_config(config)
