import streamlit as st

from features.auth.services.session_service import (
    build_authenticator,
    load_auth_config,
    require_feature,
    require_login,
)

config = load_auth_config()
authenticator = build_authenticator(config)
require_login(authenticator, config)
require_feature("read_lesson")

st.title("Read Lesson")
st.info("Read lesson page is ready for future content.")
