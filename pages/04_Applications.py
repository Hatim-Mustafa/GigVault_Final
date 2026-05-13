import streamlit as st

from components.auth_guard import auth_guard
from components.sidebar import render_sidebar
from services.application_service import (
    get_all_client_pending_applications,
    get_musician_applications,
    withdraw_application,
)
from services.booking_service import accept_application, reject_application
from utils import empty_state, format_currency, format_date, status_badge_html

st.set_page_config(
    page_title="Applications — GigVault",
    page_icon="📋",
    layout="wide",
)

auth_guard()
render_sidebar()

role = st.session_state["role"]
user_id = st.session_state["user_id"]

if role == "Musician":
    st.markdown('<div class="page-title">📋 My Applications</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Track all your gig applications and their statuses.</div>',
        unsafe_allow_html=True,
    )

    apps = get_musician_applications(user_id)

    if not apps:
        st.markdown(
            empty_state("You haven't applied to any gigs yet. Head to Explore Gigs to find opportunities!", "🎵"),
            unsafe_allow_html=True,
        )
    else:
        pending = [a for a in apps if (a.status.value if hasattr(a.status, "value") else a.status) == "Pending"]
        accepted = [a for a in apps if (a.status.value if hasattr(a.status, "value") else a.status) == "Accepted"]
        rejected = [a for a in apps if (a.status.value if hasattr(a.status, "value") else a.status) in ("Rejected", "Withdrawn")]

        tab_pending, tab_accepted, tab_all = st.tabs([
            f"  ⏳ Pending ({len(pending)})  ",
            f"  ✅ Accepted ({len(accepted)})  ",
            f"  📁 All ({len(apps)})  ",
        ])

        def render_application_card(app, show_withdraw=False):
            gig = app.gig
            status_val = app.status.value if hasattr(app.status, "value") else app.status
            applied_str = format_date(app.applied_at) if app.applied_at else "N/A"
            budget_str = format_currency(gig.budget)

            st.markdown(
                f"""
                <div class="card">
                    <div class="card-row" style="justify-content:space-between;margin-top:0;margin-bottom:0.4rem;">
                        <span class="card-title">{gig.title}</span>
                        {status_badge_html(status_val)}
                    </div>
                    <div class="card-meta">📅 {format_date(gig.performance_date)} · 📍 {gig.city} · 🎵 {gig.genre}</div>
                    <div style="display:flex;gap:1.5rem;margin-top:0.4rem;font-size:0.88rem;color:#94a3b8;">
                        <span>💵 Budget: <b style="color:#a78bfa;">{budget_str}</b></span>
                        <span>🗓 Applied: {applied_str}</span>
                    </div>
                    {f'<div style="margin-top:0.5rem;font-size:0.88rem;color:#cbd5e1;"><b>Message:</b> {app.message}</div>' if app.message else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if show_withdraw:
                if st.button(f"↩️ Withdraw", key=f"wd_{app.id}", use_container_width=False):
                    try:
                        withdraw_application(app.id, user_id)
                        st.success("Application withdrawn.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        with tab_pending:
            if not pending:
                st.markdown(empty_state("No pending applications.", "⏳"), unsafe_allow_html=True)
            for app in pending:
                render_application_card(app, show_withdraw=True)

        with tab_accepted:
            if not accepted:
                st.markdown(empty_state("No accepted applications yet. Keep applying!", "🌟"), unsafe_allow_html=True)
            for app in accepted:
                render_application_card(app, show_withdraw=False)
                gig = app.gig
                if gig.booking:
                    b = gig.booking
                    booking_status = b.status.value if hasattr(b.status, "value") else b.status
                    st.markdown(
                        f'<div style="background:#0f2820;border:1px solid #166534;border-radius:8px;'
                        f'padding:0.7rem 1rem;margin-top:-0.5rem;margin-bottom:1rem;font-size:0.88rem;">'
                        f'🤝 Booking confirmed · Agreed: <b style="color:#4ade80;">{format_currency(b.agreed_amount)}</b> · '
                        f'Contract: {status_badge_html(booking_status)}'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        with tab_all:
            for app in apps:
                render_application_card(app, show_withdraw=False)

else:
    st.markdown('<div class="page-title">📥 Manage Applications</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Review and respond to musician applications for your gigs.</div>',
        unsafe_allow_html=True,
    )

    pending_apps = get_all_client_pending_applications(user_id)

    if not pending_apps:
        st.markdown(
            empty_state("No pending applications to review. Create open gigs to start receiving applications!", "📬"),
            unsafe_allow_html=True,
        )
    else:
        from collections import defaultdict
        by_gig = defaultdict(list)
        for app in pending_apps:
            by_gig[app.gig.id].append(app)

        st.markdown(f"**{len(pending_apps)} pending application{'s' if len(pending_apps) != 1 else ''} across {len(by_gig)} gig{'s' if len(by_gig) != 1 else ''}**")
        st.markdown("---")

        for gig_id, apps_for_gig in by_gig.items():
            gig = apps_for_gig[0].gig
            with st.expander(
                f"🎵 {gig.title}  ·  {format_date(gig.performance_date)}  ·  {len(apps_for_gig)} applicant{'s' if len(apps_for_gig) != 1 else ''}",
                expanded=True,
            ):
                for app in apps_for_gig:
                    musician = app.musician
                    profile = musician.musician_profile if musician else None
                    stage_name = profile.stage_name if profile and profile.stage_name else musician.username if musician else "Unknown"
                    genres = profile.genres if profile and profile.genres else "N/A"
                    rate_str = format_currency(gig.budget)

                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="card-row" style="justify-content:space-between;margin-top:0;margin-bottom:0.4rem;">
                                <span class="card-title">🎤 {stage_name}</span>
                                <span style="color:#94a3b8;font-size:0.85rem;">@{musician.username if musician else ''}</span>
                            </div>
                            <div style="display:flex;gap:1.5rem;font-size:0.88rem;color:#94a3b8;">
                                <span>🎵 Genres: {genres}</span>
                                <span>💵 Rate: <b style="color:#a78bfa;">{rate_str}</b></span>
                            </div>
                            {f'<div style="margin-top:0.5rem;font-size:0.88rem;color:#cbd5e1;border-top:1px solid #2d2d4a;padding-top:0.5rem;"><b>Message:</b> {app.message}</div>' if app.message else ''}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    col_a, col_r, _ = st.columns([1, 1, 3])
                    if col_a.button(f"✅ Accept", key=f"acc_{app.id}", type="primary"):
                        try:
                            accept_application(app.id, user_id)
                            st.success(f"🎉 {stage_name} accepted! Booking contract created and gig is now Booked.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                        except Exception as ex:
                            st.error(f"Error: {ex}")

                    if col_r.button(f"❌ Reject", key=f"rej_{app.id}"):
                        try:
                            reject_application(app.id, user_id)
                            st.info("Application rejected.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

                    st.markdown("<br>", unsafe_allow_html=True)
