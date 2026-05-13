import datetime

import streamlit as st

from components.auth_guard import require_client
from components.sidebar import render_sidebar
from config import MUSIC_GENRES_SELECT, VENUE_TYPES
from services.gig_service import (
    cancel_gig,
    complete_gig,
    create_gig,
    get_client_gigs,
    update_gig,
)
from utils import empty_state, format_currency, format_date, format_time, status_badge_html

st.set_page_config(
    page_title="My Gigs — GigVault",
    page_icon="🎸",
    layout="wide",
)

require_client()
render_sidebar()

client_id = st.session_state["user_id"]

st.markdown('<div class="page-title">🎸 My Gigs</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Create, manage and track all your venue gig listings.</div>',
    unsafe_allow_html=True,
)

tab_list, tab_create = st.tabs(["  📋  My Listings  ", "  ➕  Create New Gig  "])

with tab_create:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("create_gig_form", clear_on_submit=True):
        st.markdown('<div class="section-header">New Gig Details</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        title = c1.text_input("Gig Title *", placeholder="e.g. Jazz Night at The Blue Note")
        genre = c2.selectbox("Genre *", MUSIC_GENRES_SELECT)

        c3, c4 = st.columns(2)
        city = c3.text_input("City *", placeholder="e.g. New York")
        perf_date = c4.date_input(
            "Performance Date *",
            min_value=datetime.date.today() + datetime.timedelta(days=1),
        )

        c5, c6, c7 = st.columns(3)
        start_t = c5.time_input("Start Time", value=datetime.time(20, 0))
        end_t = c6.time_input("End Time", value=datetime.time(23, 0))
        duration = c7.number_input("Duration (hours)", min_value=0.5, max_value=12.0, value=3.0, step=0.5)

        budget = st.number_input("Budget ($) *", min_value=50.0, value=500.0, step=50.0)
        description = st.text_area("Description", placeholder="Describe the gig, audience, venue vibe...", height=100)
        requirements = st.text_area(
            "Musician Requirements",
            placeholder="e.g. Must have own equipment, jazz experience required...",
            height=80,
        )

        submitted = st.form_submit_button("🚀 Publish Gig Listing", type="primary", use_container_width=True)

        if submitted:
            if not title or not city:
                st.error("Title and city are required.")
            elif budget < 50:
                st.error("Minimum budget is $50.")
            else:
                try:
                    gig = create_gig(
                        client_id=client_id,
                        title=title,
                        description=description,
                        genre=genre,
                        city=city,
                        performance_date=perf_date,
                        start_time=start_t,
                        end_time=end_t,
                        budget=budget,
                        requirements=requirements,
                        duration_hours=duration,
                    )
                    st.success(f"✅ Gig **{gig.title}** published successfully for {format_date(gig.performance_date)}!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
                except Exception as err:
                    st.error(f"Failed to create gig: {err}")

with tab_list:
    gigs = get_client_gigs(client_id)

    if not gigs:
        st.markdown(empty_state("You haven't created any gigs yet. Use the 'Create New Gig' tab to get started!", "🎸"), unsafe_allow_html=True)
    else:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Open", "Filled", "Completed", "Cancelled"],
            key="mg_filter",
        )
        filtered = gigs if filter_status == "All" else [g for g in gigs if (g.status.value if hasattr(g.status, "value") else g.status) == filter_status]

        st.markdown(f"**{len(filtered)} gig{'s' if len(filtered) != 1 else ''}**")
        st.markdown("---")

        for gig in filtered:
            status_val = gig.status.value if hasattr(gig.status, "value") else gig.status

            with st.expander(
                f"{gig.title}  ·  {format_date(gig.performance_date)}  ·  {format_currency(gig.budget)}",
                expanded=False,
            ):
                col_det, col_act = st.columns([3, 1])

                with col_det:
                    st.markdown(
                        f'<div style="margin-bottom:0.5rem;">{status_badge_html(status_val)}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Genre:** {gig.genre}  &nbsp;&nbsp; **City:** {gig.city}")
                    st.markdown(f"**Date:** {format_date(gig.performance_date)}")
                    if gig.start_time:
                        st.markdown(f"**Time:** {format_time(gig.start_time)} – {format_time(gig.end_time) if gig.end_time else ''}")
                    st.markdown(f"**Budget:** {format_currency(gig.budget)}")
                    if gig.description:
                        st.markdown(f"**Description:** {gig.description}")
                    if gig.requirements:
                        st.markdown(f"**Requirements:** {gig.requirements}")

                    if gig.booking:
                        b = gig.booking
                        musician_name = b.musician.username if b.musician else "Unknown"
                        st.markdown("---")
                        st.markdown(f"🎤 **Booked Musician:** {musician_name}")
                        booking_status = b.status.value if hasattr(b.status, "value") else b.status
                        st.markdown(
                            f"📄 **Contract Status:** {status_badge_html(booking_status)}",
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"💵 **Agreed Amount:** {format_currency(b.agreed_amount)}")

                with col_act:
                    st.markdown("<br>", unsafe_allow_html=True)

                    if status_val == "Open":
                        with st.expander("✏️ Edit Gig"):
                            with st.form(f"edit_form_{gig.id}"):
                                new_title = st.text_input("Title", value=gig.title, key=f"et_{gig.id}")
                                new_genre = st.selectbox(
                                    "Genre",
                                    MUSIC_GENRES_SELECT,
                                    index=MUSIC_GENRES_SELECT.index(gig.genre) if gig.genre in MUSIC_GENRES_SELECT else 0,
                                    key=f"eg_{gig.id}",
                                )
                                new_city = st.text_input("City", value=gig.city, key=f"ec_{gig.id}")
                                new_budget = st.number_input(
                                    "Budget ($)", min_value=50.0, value=float(gig.budget), step=50.0, key=f"eb_{gig.id}"
                                )
                                new_desc = st.text_area("Description", value=gig.description or "", key=f"ed_{gig.id}")
                                new_req = st.text_area("Requirements", value=gig.requirements or "", key=f"er_{gig.id}")
                                save = st.form_submit_button("💾 Save Changes", use_container_width=True)
                                if save:
                                    try:
                                        update_gig(
                                            gig_id=gig.id,
                                            client_id=client_id,
                                            title=new_title,
                                            description=new_desc,
                                            genre=new_genre,
                                            city=new_city,
                                            start_time=gig.start_time,
                                            end_time=gig.end_time,
                                            budget=new_budget,
                                            requirements=new_req,
                                            duration_hours=float(gig.duration_hours) if gig.duration_hours else None,
                                        )
                                        st.success("Gig updated!")
                                        st.rerun()
                                    except ValueError as ve:
                                        st.error(str(ve))

                        if st.button("❌ Cancel Gig", key=f"cancel_{gig.id}", use_container_width=True):
                            try:
                                cancel_gig(gig_id=gig.id, client_id=client_id)
                                st.success("Gig cancelled.")
                                st.rerun()
                            except ValueError as ve:
                                st.error(str(ve))

                    elif status_val == "Filled":
                        if st.button("✅ Mark Completed", key=f"comp_{gig.id}", use_container_width=True, type="primary"):
                            try:
                                complete_gig(gig_id=gig.id, client_id=client_id)
                                st.success("Gig marked as completed!")
                                st.rerun()
                            except ValueError as ve:
                                st.error(str(ve))
                    else:
                        st.markdown(
                            f'<div style="color:#64748b;font-size:0.9rem;text-align:center;padding:0.5rem;">'
                            f"No actions available for {status_val} gigs.</div>",
                            unsafe_allow_html=True,
                        )
