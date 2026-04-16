import streamlit as st

from auth.register_view import render_register_view
from core.auth_state import (
    build_authenticator,
    get_user_record,
    load_auth_config,
)

config = load_auth_config()
authenticator = build_authenticator(config)

if st.session_state.get("authentication_status"):
    st.switch_page("dashboard/dashboard_page.py")

_, auth_col, _ = st.columns([1, 1.25, 1], gap="large")
with auth_col:
    render_register_view(
        authenticator=authenticator,
        config=config,
        get_user_record=get_user_record,
    )
