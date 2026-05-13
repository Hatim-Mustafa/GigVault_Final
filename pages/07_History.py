import streamlit as st
from components.auth_guard import auth_guard
from components.sidebar import render_sidebar
from database import get_db
from queries.booking_queries import get_all_bookings_for_client, get_all_bookings_for_musician
from queries.payment_queries import get_client_payments_with_details, get_musician_payments_with_details
from utils import empty_state, format_currency, format_date, status_badge_html

st.set_page_config(page_title="History — GigVault", page_icon="📜", layout="wide")
auth_guard(); render_sidebar()
role = st.session_state["role"]; user_id = st.session_state["user_id"]
st.markdown('<div class="page-title">📜 History</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Review booking and payment history.</div>', unsafe_allow_html=True)
with get_db() as db:
    if role == "Venue_Owner":
        bookings = get_all_bookings_for_client(db, user_id); payments = get_client_payments_with_details(db, user_id)
    else:
        bookings = get_all_bookings_for_musician(db, user_id); payments = get_musician_payments_with_details(db, user_id)

tab_bookings, tab_payments = st.tabs([f"  📁 Bookings ({len(bookings)})  ", f"  💰 Payments ({len(payments)})  "])
with tab_bookings:
    if not bookings: st.markdown(empty_state("No booking history yet.", "📁"), unsafe_allow_html=True)
    else:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Completed", "Cancelled"], key="hist_booking_filter")
        shown = bookings if status_filter == "All" else [(b,g,u) for b,g,u in bookings if (b.status.value if hasattr(b.status,"value") else b.status)==status_filter]
        for booking, gig, other_user in shown:
            status_val = booking.status.value if hasattr(booking.status, "value") else booking.status
            other_label = "Musician" if role == "Venue_Owner" else "Venue"; other_name = other_user.username
            if role == "Musician" and getattr(other_user, "client_profile", None): other_name = other_user.client_profile.venue_name or other_user.username
            st.markdown(f'''<div class="card"><div class="card-row" style="justify-content:space-between;margin-top:0;margin-bottom:0.3rem;"><span class="card-title">{gig.title}</span>{status_badge_html(status_val)}</div><div class="card-meta">📅 {format_date(gig.performance_date)} · 📍 {gig.city} · 🎵 {gig.genre}</div><div style="display:flex;gap:1.5rem;font-size:0.87rem;color:#94a3b8;margin-top:0.4rem;flex-wrap:wrap;"><span>{other_label}: {other_name}</span><span>💵 <b style="color:#a78bfa;">{format_currency(booking.agreed_amount)}</b></span><span>🗓 Booked: {format_date(booking.booked_at)}</span></div></div>''', unsafe_allow_html=True)
with tab_payments:
    if not payments: st.markdown(empty_state("No payment history yet.", "💰"), unsafe_allow_html=True)
    else:
        pay_filter = st.selectbox("Filter by Payment Status", ["All", "Pending", "Completed", "Failed", "Refunded"], key="hist_payment_filter")
        shown = payments if pay_filter == "All" else [(p,u,g) for p,u,g in payments if (p.status.value if hasattr(p.status,"value") else p.status)==pay_filter]
        for payment, other_user, gig in shown:
            status_val = payment.status.value if hasattr(payment.status, "value") else payment.status
            other_label = "Musician" if role == "Venue_Owner" else "Venue"; other_name = other_user.username
            if role == "Musician" and getattr(other_user, "client_profile", None): other_name = other_user.client_profile.venue_name or other_user.username
            paid_line = f" · Paid: {format_date(payment.paid_at)}" if payment.paid_at else ""
            note = f'<div style="margin-top:0.5rem;color:#cbd5e1;font-size:0.85rem;">Notes: {payment.notes}</div>' if payment.notes else ''
            st.markdown(f'''<div class="card"><div class="card-row" style="justify-content:space-between;margin-top:0;margin-bottom:0.3rem;"><span class="card-title">{gig.title}</span>{status_badge_html(status_val)}</div><div class="card-meta">{other_label}: {other_name}</div><div style="display:flex;gap:1.5rem;font-size:0.87rem;color:#94a3b8;margin-top:0.4rem;flex-wrap:wrap;"><span>💵 <b style="color:#a78bfa;">{format_currency(payment.amount)}</b></span>{paid_line}</div>{note}</div>''', unsafe_allow_html=True)
