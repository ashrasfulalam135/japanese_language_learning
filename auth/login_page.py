import streamlit as st

from auth.login_view import render_login_view
from core.auth_state import (
    build_authenticator,
    clear_login_state,
    get_user_record,
    load_auth_config,
    process_verification_link,
)

config = load_auth_config()
process_verification_link(config)
authenticator = build_authenticator(config)

if st.session_state.get("authentication_status"):
    st.switch_page("dashboard/dashboard_page.py")

_, auth_col, _ = st.columns([1, 1.25, 1], gap="large")
with auth_col:
    render_login_view(
        authenticator=authenticator,
        config=config,
        get_user_record=get_user_record,
        clear_login_state=clear_login_state,
    )
