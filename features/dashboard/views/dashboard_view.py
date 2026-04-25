import streamlit as st


def render_dashboard(get_user_record) -> None:
    roles = st.session_state.get("roles") or []
    username = st.session_state.get("username")
    user_record = get_user_record(username)
    effective_features = user_record.get("effective_features", [])
    role_features = user_record.get("role_features", [])
    allowed_features = user_record.get("allowed_features", [])

    st.success(f"Welcome {st.session_state.get('name')}")
    if roles:
        st.write(f"Role: `{roles[0]}`")
    if "admin" in roles:
        st.write("Access: `All features`")
    elif effective_features:
        st.write("Role features:")
        if role_features:
            for feature in role_features:
                st.write(f"- {feature}")
        else:
            st.write("- None assigned to role")

        st.write("User-specific features:")
        if allowed_features:
            for feature in allowed_features:
                st.write(f"- {feature}")
        else:
            st.write("- None assigned directly")

        st.write("Effective access:")
        for feature in effective_features:
            st.write(f"- {feature}")
    else:
        st.write("Allowed features: `None assigned yet`")
