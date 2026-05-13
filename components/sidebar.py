import streamlit as st

from auth import clear_session, get_current_role, get_current_username, is_authenticated
from styles.main import get_main_css
from utils import role_badge_html


def inject_css() -> None:
    st.markdown("""
    <style>
        /* Hide Streamlit default multipage nav */
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        div[class*="st-emotion-cache"] > ul {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(get_main_css(), unsafe_allow_html=True)


def render_sidebar() -> None:
    inject_css()
    with st.sidebar:
        st.markdown(
            '<div style="font-size:1.6rem;font-weight:900;'
            'background:linear-gradient(135deg,#a78bfa,#f472b6);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
            'background-clip:text;padding:0.5rem 0;">🎵 GigVault</div>',
            unsafe_allow_html=True,
        )

        if not is_authenticated():
            return

        role = get_current_role()
        username = get_current_username() or ""

        st.markdown(
            f'<div style="margin:0.5rem 0;">'
            f'<span style="color:#f1f5f9;font-weight:700;font-size:0.95rem;">👤 {username}</span>'
            f"</div>"
            f'<div style="margin-bottom:1rem;">{role_badge_html(role or "")}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            '<p style="color:#64748b;font-size:0.75rem;font-weight:700;'
            'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Navigation</p>',
            unsafe_allow_html=True,
        )

        st.page_link("pages/01_Dashboard.py", label="🏠  Dashboard")

        if role == "Musician":
            st.page_link("pages/02_Explore_Gigs.py", label="🔍  Explore Gigs")
            st.page_link("pages/08_My_Band.py", label="🎶  My Band")
            st.page_link("pages/04_Applications.py", label="📋  My Applications")
        else:
            st.page_link("pages/03_My_Gigs.py", label="🎸  My Gigs")
            st.page_link("pages/04_Applications.py", label="📥  Manage Applications")

        st.page_link("pages/05_Payments.py", label="💰  Payments")
        st.page_link("pages/06_Profile.py", label="👤  Profile")
        st.page_link("pages/07_History.py", label="📜  History")

        st.markdown("---")
        if st.button("🚪  Logout", use_container_width=True, type="secondary"):
            clear_session()
            st.switch_page("app.py")
