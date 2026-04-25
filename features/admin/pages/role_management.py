import streamlit as st

from features.admin.services.user_management_service import (
    get_role,
    list_active_features,
    list_roles,
    update_role_features,
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

st.title("Role Management")
st.caption(
    "Assign features to roles so access automatically applies to every user "
    "with that role."
)

roles = list_roles()
features = list_active_features()

role_names = [role.name for role in roles] or ["user", "admin"]
selected_role_name = st.selectbox("Select role", options=role_names)
selected_role = get_role(selected_role_name)

feature_labels = {
    feature.code: f"{feature.name} ({feature.category})" for feature in features
}
feature_options = [feature.code for feature in features]
disabled_for_admin = selected_role.name == "admin"

with st.form("role_management_form"):
    st.subheader("Role Access")
    st.write(f"Role: `{selected_role.name}`")

    assigned_features = st.multiselect(
        "Assigned features",
        options=feature_options,
        default=selected_role.feature_codes,
        format_func=lambda code: feature_labels.get(code, code),
        disabled=disabled_for_admin,
        help=(
            "Admin role automatically has full access."
            if disabled_for_admin
            else "Selected features will apply to all users with this role."
        ),
    )

    submitted = st.form_submit_button(
        "Save role access",
        use_container_width=True,
    )

if submitted:
    try:
        update_role_features(
            selected_role.name,
            feature_options if selected_role.name == "admin" else assigned_features,
        )
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.success("Role access updated successfully.")
        st.rerun()
