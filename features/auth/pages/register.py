import streamlit as st

from features.auth.services.session_service import (
    build_authenticator,
    load_auth_config,
)
from features.auth.services.user_service import get_user_record
from features.auth.views.register_view import render_register_view

config = load_auth_config()
authenticator = build_authenticator(config)

if st.session_state.get("authentication_status"):
    st.switch_page("features/dashboard/pages/dashboard.py")

_, auth_col, _ = st.columns([1, 1.25, 1], gap="large")
with auth_col:
    render_register_view(
        authenticator=authenticator,
        config=config,
        get_user_record=get_user_record,
    )
