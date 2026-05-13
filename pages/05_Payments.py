import streamlit as st

from components.auth_guard import auth_guard
from components.sidebar import render_sidebar
from database import get_db
from queries.payment_queries import (
    get_client_payment_summary,
    get_client_payments_with_details,
    get_musician_payment_summary,
    get_musician_payments_with_details,
)
from services.payment_service import mark_payment_paid
from utils import empty_state, format_currency, format_date, status_badge_html

st.set_page_config(
    page_title="Payments — GigVault",
    page_icon="💰",
    layout="wide",
)

auth_guard()
render_sidebar()

role = st.session_state["role"]
user_id = st.session_state["user_id"]

if role == "Venue_Owner":
    st.markdown('<div class="page-title">💰 Payment Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Track all outgoing payments to your booked musicians.</div>',
        unsafe_allow_html=True,
    )

    with get_db() as db:
        summary = get_client_payment_summary(db, user_id)
        rows = get_client_payments_with_details(db, user_id)

    c1, c2, c3 = st.columns(3)
    c1.metric("⏳ Pending", f"{summary['pending_count']} · {format_currency(summary['pending_amount'])}")
    c2.metric("✅ Paid", f"{summary['completed_count']} · {format_currency(summary['completed_amount'])}")
    c3.metric("💸 Total Committed", format_currency(summary["total_amount"]))

    st.markdown("---")

    if not rows:
        st.markdown(empty_state("No payment records yet. Accept a musician application to generate a booking and payment.", "💳"), unsafe_allow_html=True)
    else:
        tab_pending, tab_paid, tab_all = st.tabs([
            f"  ⏳ Pending ({summary['pending_count']})  ",
            f"  ✅ Paid ({summary['completed_count']})  ",
            f"  📁 All ({len(rows)})  ",
        ])

        def render_client_payment(payment, musician_user, gig, show_pay_btn=False):
            status_val = payment.status.value if hasattr(payment.status, "value") else payment.status
            musician_profile = musician_user.musician_profile
            stage_name = musician_profile.stage_name if musician_profile and musician_profile.stage_name else musician_user.username

            st.markdown(
                f"""
                <div style="background:#1a1a2e;border:1px solid #2d2d4a;border-radius:10px;
                padding:1rem 1.2rem;margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                        <span style="color:#f1f5f9;font-weight:700;font-size:1rem;">{gig.title}</span>
                        {status_badge_html(status_val)}
                    </div>
                    <div style="display:flex;gap:1.5rem;font-size:0.86rem;color:#94a3b8;flex-wrap:wrap;">
                        <span>🎤 {stage_name}</span>
                        <span>📅 {format_date(gig.performance_date)}</span>
                        <span>💵 <b style="color:#a78bfa;">{format_currency(payment.amount)}</b></span>
                        {f'<span style="color:#4ade80;">✅ Paid: {format_date(payment.paid_at)}</span>' if payment.paid_at else ''}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if show_pay_btn:
                col_btn, _ = st.columns([1, 4])
                if col_btn.button(f"💸 Mark Paid", key=f"pay_{payment.id}", type="primary"):
                    try:
                        mark_payment_paid(payment.id, user_id)
                        st.success("Payment marked as paid!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        with tab_pending:
            pending_rows = [(p, u, g) for p, u, g in rows if (p.status.value if hasattr(p.status, "value") else p.status) == "Pending"]
            if not pending_rows:
                st.markdown(empty_state("No pending payments.", "✅"), unsafe_allow_html=True)
            for p, u, g in pending_rows:
                render_client_payment(p, u, g, show_pay_btn=True)

        with tab_paid:
            paid_rows = [(p, u, g) for p, u, g in rows if (p.status.value if hasattr(p.status, "value") else p.status) == "Completed"]
            if not paid_rows:
                st.markdown(empty_state("No completed payments yet.", "💳"), unsafe_allow_html=True)
            for p, u, g in paid_rows:
                render_client_payment(p, u, g, show_pay_btn=False)

        with tab_all:
            for p, u, g in rows:
                render_client_payment(p, u, g, show_pay_btn=(p.status.value if hasattr(p.status, "value") else p.status) == "Pending")

else:
    st.markdown('<div class="page-title">💵 My Earnings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Track payments owed to you for completed and upcoming performances.</div>',
        unsafe_allow_html=True,
    )

    with get_db() as db:
        summary = get_musician_payment_summary(db, user_id)
        rows = get_musician_payments_with_details(db, user_id)

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Earned", format_currency(summary["total_earned"]))
    c2.metric("⏳ Pending Payout", f"{summary['pending_count']} · {format_currency(summary['pending_amount'])}")
    c3.metric("✅ Paid", f"{summary['completed_count']} payments")

    st.markdown("---")

    if not rows:
        st.markdown(empty_state("No payment records yet. Apply to gigs to get booked and earn!", "🎵"), unsafe_allow_html=True)
    else:
        tab_unpaid, tab_paid, tab_all = st.tabs([
            f"  💸 Unpaid ({summary['pending_count']})  ",
            f"  ✅ Paid ({summary['completed_count']})  ",
            f"  📁 All ({len(rows)})  ",
        ])

        def render_musician_payment(payment, client_user, gig):
            status_val = payment.status.value if hasattr(payment.status, "value") else payment.status
            venue_name = client_user.client_profile.venue_name if client_user.client_profile else client_user.username

            st.markdown(
                f"""
                <div style="background:#1a1a2e;border:1px solid #2d2d4a;border-radius:10px;
                padding:1rem 1.2rem;margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                        <span style="color:#f1f5f9;font-weight:700;">{gig.title}</span>
                        {status_badge_html(status_val)}
                    </div>
                    <div style="display:flex;gap:1.5rem;font-size:0.86rem;color:#94a3b8;flex-wrap:wrap;">
                        <span>🏛 {venue_name}</span>
                        <span>📅 {format_date(gig.performance_date)}</span>
                        <span>💵 <b style="color:#4ade80;">{format_currency(payment.amount)}</b></span>
                        {f'<span style="color:#4ade80;">✅ Received: {format_date(payment.paid_at)}</span>' if payment.paid_at else ''}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with tab_unpaid:
            unpaid = [(p, u, g) for p, u, g in rows if (p.status.value if hasattr(p.status, "value") else p.status) == "Pending"]
            if not unpaid:
                st.markdown(empty_state("All payments received! Nothing outstanding.", "🎉"), unsafe_allow_html=True)
            for p, u, g in unpaid:
                render_musician_payment(p, u, g)

        with tab_paid:
            paid = [(p, u, g) for p, u, g in rows if (p.status.value if hasattr(p.status, "value") else p.status) == "Completed"]
            if not paid:
                st.markdown(empty_state("No paid payments yet.", "💳"), unsafe_allow_html=True)
            for p, u, g in paid:
                render_musician_payment(p, u, g)

        with tab_all:
            for p, u, g in rows:
                render_musician_payment(p, u, g)
