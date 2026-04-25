import streamlit as st

from features.admin.services.user_management_service import (
    get_user_by_id,
    list_active_features,
    list_users,
    update_user_access,
)
from features.auth.services.session_service import (
    build_authenticator,
    load_auth_config,
    require_login,
    require_role,
)

config = load_auth_config()
authenticator = build_authenticator(config)
require_login(authenticator, config)
require_role("admin")

st.title("User Management")
st.caption("Manage user roles, verification, and user-specific feature access.")

users = list_users()
features = list_active_features()

if not users:
    st.info("No users found.")
    st.stop()

user_options = {
    f"{user.first_name} {user.last_name} ({user.email})": user.id for user in users
}
selected_label = st.selectbox(
    "Select user",
    options=list(user_options.keys()),
)
selected_user = get_user_by_id(user_options[selected_label])

if selected_user is None:
    st.error("Selected user could not be loaded.")
    st.stop()

feature_labels = {
    feature.code: f"{feature.name} ({feature.category})" for feature in features
}
feature_options = [feature.code for feature in features]
disabled_for_admin = selected_user.role == "admin"

with st.form("user_management_form"):
    st.subheader("User Details")
    st.write(f"Email: `{selected_user.email}`")
    st.write(f"Username: `{selected_user.username}`")
    st.write(f"Role features: `{', '.join(selected_user.role_features) or 'None'}`")
    st.write(
        "Effective features: "
        f"`{', '.join(selected_user.effective_features) or 'None'}'"
    )

    role = st.selectbox(
        "Role",
        options=["user", "admin"],
        index=1 if selected_user.role == "admin" else 0,
    )
    is_verified = st.checkbox("Verified", value=selected_user.is_verified)
    allowed_features = st.multiselect(
        "Allowed features",
        options=feature_options,
        default=selected_user.allowed_features,
        format_func=lambda code: feature_labels.get(code, code),
        disabled=disabled_for_admin,
        help=(
            "Admin users automatically have full access. "
            "For normal users, these are extra features on top of role features."
            if disabled_for_admin
            else "These are user-specific features in addition to role features.",
        ),
    )
    submitted = st.form_submit_button("Save access", use_container_width=True)

if submitted:
    try:
        effective_features = feature_options if role == "admin" else allowed_features
        update_user_access(
            selected_user.id,
            role=role,
            allowed_features=effective_features,
            is_verified=is_verified,
        )
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.success("User access updated successfully.")
        st.rerun()
