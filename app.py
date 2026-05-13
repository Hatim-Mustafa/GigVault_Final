import streamlit as st

from auth import is_authenticated, login, register, set_session
from database import init_db
from styles.main import get_main_css

st.set_page_config(
    page_title="GigVault — Music Marketplace",
    initial_sidebar_state="collapsed",
)

init_db()

if is_authenticated():
    st.switch_page("pages/01_Dashboard.py")

st.markdown(get_main_css(), unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">GigVault</div>
        <div class="hero-sub">The music industry's premier freelance marketplace.<br>
        Connect venues with world-class musicians.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_login, tab_register = st.tabs(["Login", "Create Account"])

with tab_login:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button(
            "Login to GigVault", use_container_width=True, type="primary"
        )

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user_data = login(username, password)
                if user_data:
                    set_session(user_data)
                    st.success(f"Welcome back, {user_data['username']}! Redirecting...")
                    st.switch_page("pages/01_Dashboard.py")
                else:
                    st.error("Invalid username or password. Please try again.")

    st.markdown(
        '<p style="text-align:center;color:#64748b;font-size:0.85rem;margin-top:1rem;">'
        "GigVault — Built for musicians and venues.",
        unsafe_allow_html=True,
    )

with tab_register:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("register_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        reg_username = col1.text_input("Username *", placeholder="Choose a username")
        reg_email = col2.text_input("Email *", placeholder="your@email.com")

        col3, col4 = st.columns(2)
        reg_password = col3.text_input("Password *", type="password", placeholder="Min. 6 chars")
        reg_confirm = col4.text_input("Confirm Password *", type="password")

        reg_city = st.text_input("City", placeholder="e.g. New York")

        st.markdown("**I am a:**")
        reg_role = st.radio(
            "Role",
            options=["client", "musician"],
            format_func=lambda x: "🏛 Venue Owner / Client" if x == "client" else "🎵 Musician / Artist",
            horizontal=True,
            label_visibility="collapsed",
        )

        reg_submit = st.form_submit_button(
            "Create My Account", use_container_width=True, type="primary"
        )

        if reg_submit:
            errors = []
            if not reg_username or not reg_email or not reg_password:
                errors.append("Username, email and password are required.")
            if reg_password and len(reg_password) < 6:
                errors.append("Password must be at least 6 characters.")
            if reg_password != reg_confirm:
                errors.append("Passwords do not match.")
            if "@" not in reg_email:
                errors.append("Please enter a valid email address.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                user_data = register(reg_username, reg_email, reg_password, reg_role, reg_city)
                if user_data:
                    set_session(user_data)
                    st.success("Account created! Redirecting to your dashboard...")
                    st.switch_page("pages/01_Dashboard.py")
                else:
                    st.error("Username or email is already registered. Please try another.")