import streamlit as st


def render_dashboard(config: dict, get_user_record) -> None:
    roles = st.session_state.get("roles") or []
    username = st.session_state.get("username")
    user_record = get_user_record(config, username)
    allowed_features = user_record.get("allowed_features", [])

    st.success(f"Welcome {st.session_state.get('name')}")
    if roles:
        st.write(f"Role: `{roles[0]}`")
    if "admin" in roles:
        st.write("Access: `All features`")
    elif allowed_features:
        st.write("Allowed features:")
        for feature in allowed_features:
            st.write(f"- {feature}")
    else:
        st.write("Allowed features: `None assigned yet`")
