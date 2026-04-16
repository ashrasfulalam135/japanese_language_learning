from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from sqlalchemy import inspect
from yaml.loader import SafeLoader

from auth.db_auth import (
    build_credentials,
    get_user_record,
    verify_user_by_token,
)
from database.db import engine
from database.models import Base, User

CONFIG_PATH = Path(__file__).resolve().parents[1] / "auth_config.yaml"


def load_auth_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.load(file, Loader=SafeLoader)


def clear_login_state() -> None:
    st.session_state["authentication_status"] = None
    st.session_state["name"] = None
    st.session_state["username"] = None
    st.session_state["roles"] = None


def ensure_user_table_schema() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        return

    columns = inspector.get_columns("users")
    existing_columns = {column["name"] for column in columns}
    required_columns = {
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "password_hash",
        "role",
        "allowed_features",
        "is_verified",
        "verification_token",
        "verification_expires_at",
        "created_at",
        "updated_at",
    }

    if required_columns.issubset(existing_columns):
        return

    with engine.begin() as connection:
        User.__table__.drop(bind=connection, checkfirst=True)

    Base.metadata.create_all(bind=engine)


def process_verification_link(config: dict) -> bool:
    token = st.query_params.get("verify_token")
    if not token:
        return False

    if verify_user_by_token(token):
        st.query_params.clear()
        st.success("Your email has been verified. You can log in now.")
        return True

    st.query_params.clear()
    st.error("This verification link is invalid or has expired.")
    return False


def build_authenticator(config: dict):
    existing_authenticator = st.session_state.get("authenticator")
    if existing_authenticator is not None:
        return existing_authenticator

    ensure_user_table_schema()

    authenticator = stauth.Authenticate(
        build_credentials(),
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )
    st.session_state["authenticator"] = authenticator
    authenticator.login(location="unrendered")
    return authenticator


def require_login(authenticator, config: dict) -> None:
    if not st.session_state.get("authentication_status"):
        st.switch_page("auth/login_page.py")

    username = st.session_state.get("username")
    user_record = get_user_record(username)
    if not user_record.get("verified", True):
        authenticator.logout(location="unrendered")
        clear_login_state()
        st.switch_page("auth/login_page.py")


def require_role(role: str) -> None:
    roles = st.session_state.get("roles") or []
    if role not in roles:
        st.error("You do not have access to this page.")
        st.stop()
