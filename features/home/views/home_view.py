import streamlit as st


def render_home_page() -> None:
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        st.markdown(
            "<h1 style='text-align: center;'>JLPT Study App</h1>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Login / Register",
            key="home_auth_link",
            use_container_width=True,
        ):
            st.switch_page("features/auth/pages/login.py")
