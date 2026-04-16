import streamlit as st

from home.home_view import render_home_page

if st.session_state.get("authentication_status"):
    st.switch_page("dashboard/dashboard_page.py")

render_home_page()
