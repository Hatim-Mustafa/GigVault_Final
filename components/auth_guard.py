import streamlit as st
from auth import get_current_role, is_authenticated


def auth_guard() -> None:
    if not is_authenticated():
        st.warning("🔒 Please log in to access this page.")
        st.page_link("app.py", label="Go to Login →", icon="🔑")
        st.stop()


def require_role(role: str) -> None:
    auth_guard()
    current = get_current_role()
    if current != role:
        role_label = "Venue Owner / Client" if role == "Venue_Owner" else "Musician"
        st.error(f"⛔ Access Denied — This section is for {role_label}s only.")
        st.stop()


def require_client() -> None:
    require_role("Venue_Owner")


def require_musician() -> None:
    require_role("Musician")
