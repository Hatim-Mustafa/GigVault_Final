import streamlit as st

from components.auth_guard import auth_guard
from components.sidebar import render_sidebar
from services.analytics_service import get_client_analytics, get_musician_analytics
from services.band_service import get_active_band_id, get_band_by_id
from utils import format_currency, format_date, status_badge_html

st.set_page_config(
    page_title="Dashboard — GigVault",
    page_icon="🏠",
    layout="wide",
)

auth_guard()
render_sidebar()

role = st.session_state["role"]
user_id = st.session_state["user_id"]
username = st.session_state["username"]

if role == "Venue_Owner":
    st.markdown(f'<div class="page-title">🏠 Welcome back, {username}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your venue dashboard — manage gigs, bookings and payments.</div>', unsafe_allow_html=True)

    stats = get_client_analytics(user_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Gigs Created", stats["total_gigs"])
    c2.metric("Open Listings", stats["open_gigs"])
    c3.metric("Active Bookings", stats["booked_gigs"])
    c4.metric("Gigs Completed", stats["completed_gigs"])

    st.markdown("<br>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("💬 Pending Applications", stats["pending_applications"])
    c6.metric("🎤 Upcoming Performances", stats["upcoming_performances"])
    c7.metric("💸 Total Committed", format_currency(stats["total_committed"]))
    c8.metric("⏳ Pending Payments", stats.get("pending_payments", 0))
    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-header">📊 Gig Status Overview</div>', unsafe_allow_html=True)
        breakdown = {
            "Open": stats["open_gigs"],
            "Booked": stats["booked_gigs"],
            "Completed": stats["completed_gigs"],
            "Cancelled": stats["cancelled_gigs"],
        }
        for status, count in breakdown.items():
            if count > 0:
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:0.6rem 1rem;background:#1a1a2e;border:1px solid #2d2d4a;'
                    f'border-radius:8px;margin-bottom:0.4rem;">'
                    f"{status_badge_html(status)}"
                    f'<span style="color:#f1f5f9;font-weight:700;">{count} gig{"s" if count != 1 else ""}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
        if stats["total_gigs"] == 0:
            st.info("You haven't created any gigs yet. Head to **My Gigs** to get started!")

    with col_right:
        st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
        if st.button("➕ Create New Gig", use_container_width=True, type="primary"):
            st.switch_page("pages/03_My_Gigs.py")
        if st.button("📥 Review Applications", use_container_width=True):
            st.switch_page("pages/04_Applications.py")
        if st.button("💰 View Payments", use_container_width=True):
            st.switch_page("pages/05_Payments.py")
        if st.button("📜 View History", use_container_width=True):
            st.switch_page("pages/07_History.py")

else:
    st.markdown(f'<div class="page-title">🎵 Welcome back, {username}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your musician dashboard — find gigs, track applications and earnings.</div>', unsafe_allow_html=True)

    band_id = get_active_band_id(user_id)
    band = get_band_by_id(band_id) if band_id else None

    if band:
        st.markdown(
            f'<div style="margin:0.5rem 0 1rem;color:#cbd5e1;">'
            f'Current band: <b style="color:#f1f5f9;">{band.name}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("You are not currently in a band. Create or join one from My Band before applying to gigs.")

    stats = get_musician_analytics(band_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applications Sent", stats["total_applications"])
    c2.metric("Accepted Bookings", stats["accepted_applications"])
    c3.metric("Upcoming Gigs", stats["upcoming_gigs"])
    c4.metric("Total Earned", format_currency(stats["total_earned"]))

    st.markdown("<br>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("⏳ Pending Applications", stats["pending_applications"])
    c6.metric("❌ Rejected", stats["rejected_applications"])
    c7.metric("💵 Pending Payout", format_currency(stats["pending_payment"]))
    c8.metric("⏳ Pending Payments", stats.get("overdue_payments", 0))

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-header">📊 Application Overview</div>', unsafe_allow_html=True)
        breakdown = {
            "Pending": stats["pending_applications"],
            "Accepted": stats["accepted_applications"],
            "Rejected": stats["rejected_applications"],
        }
        for status, count in breakdown.items():
            if count >= 0:
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:0.6rem 1rem;background:#1a1a2e;border:1px solid #2d2d4a;'
                    f'border-radius:8px;margin-bottom:0.4rem;">'
                    f"{status_badge_html(status)}"
                    f'<span style="color:#f1f5f9;font-weight:700;">{count}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
        if st.button("🔍 Browse Open Gigs", use_container_width=True, type="primary"):
            st.switch_page("pages/02_Explore_Gigs.py")
        if st.button("📋 My Applications", use_container_width=True):
            st.switch_page("pages/04_Applications.py")
        if st.button("💰 View Payments", use_container_width=True):
            st.switch_page("pages/05_Payments.py")
        if st.button("📜 View History", use_container_width=True):
            st.switch_page("pages/07_History.py")
