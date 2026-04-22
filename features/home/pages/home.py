import streamlit as st

from features.home.views.home_view import render_home_page

if st.session_state.get("authentication_status"):
    st.switch_page("features/dashboard/pages/dashboard.py")

render_home_page()
