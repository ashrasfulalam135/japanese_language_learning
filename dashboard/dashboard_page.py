import streamlit as st

from core.auth_state import (
    build_authenticator,
    get_user_record,
    load_auth_config,
    require_login,
)
from dashboard.dashboard_view import render_dashboard

config = load_auth_config()
authenticator = build_authenticator(config)
require_login(authenticator, config)

st.subheader("Dashboard")
render_dashboard(get_user_record)
