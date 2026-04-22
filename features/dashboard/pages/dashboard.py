import streamlit as st

from features.auth.services.session_service import (
    build_authenticator,
    load_auth_config,
    require_login,
)
from features.auth.services.user_service import get_user_record
from features.dashboard.views.dashboard_view import render_dashboard

config = load_auth_config()
authenticator = build_authenticator(config)
require_login(authenticator, config)

st.subheader("Dashboard")
render_dashboard(get_user_record)
