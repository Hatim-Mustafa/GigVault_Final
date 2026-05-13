import datetime

import streamlit as st

from components.auth_guard import require_musician
from components.sidebar import render_sidebar
from config import MUSIC_GENRES_FILTER
from database import get_db
from queries.gig_queries import get_open_gigs_filtered
from services.application_service import apply_to_gig
from utils import empty_state, format_currency, format_date, format_time, status_badge_html

st.set_page_config(
    page_title="Explore Gigs — GigVault",
    page_icon="🔍",
    layout="wide",
)

require_musician()
render_sidebar()

musician_id = st.session_state["user_id"]

st.markdown('<div class="page-title">🔍 Explore Gigs</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Browse open gig listings and apply to perform.</div>',
    unsafe_allow_html=True,
)

with st.expander("🎛 Filter Gigs", expanded=True):
    fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 1.5, 1.5])
    sel_genre = fc1.selectbox("Genre", MUSIC_GENRES_FILTER, key="ex_genre")
    sel_city = fc2.text_input("City", placeholder="e.g. New York", key="ex_city")
    sel_date = fc3.date_input("Performance Date", value=None, key="ex_date", min_value=datetime.date.today())
    sel_min_budget = fc4.number_input("Min Budget ($)", min_value=0, value=0, step=50, key="ex_min")
    sel_max_budget = fc5.number_input("Max Budget ($)", min_value=0, value=0, step=50, key="ex_max")

    col_search, col_reset = st.columns([1, 5])
    search_clicked = col_search.button("Search", type="primary", key="ex_search")
    if col_reset.button("Reset Filters", key="ex_reset"):
        for k in ["ex_genre", "ex_city", "ex_date", "ex_min", "ex_max"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

with get_db() as db:
    gigs = get_open_gigs_filtered(
        db=db,
        genre=sel_genre if sel_genre != "All" else None,
        city=sel_city or None,
        date=sel_date if isinstance(sel_date, datetime.date) else None,
        min_budget=float(sel_min_budget) if sel_min_budget > 0 else None,
        max_budget=float(sel_max_budget) if sel_max_budget > 0 else None,
        musician_id=musician_id,
    )

st.markdown(f"<br>**{len(gigs)} gig{'s' if len(gigs) != 1 else ''} found**", unsafe_allow_html=True)
st.markdown("---")

if not gigs:
    st.markdown(
        empty_state("No open gigs match your filters. Try broadening your search!", "🎶"),
        unsafe_allow_html=True,
    )
else:
    for gig in gigs:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">🎵 {gig.title}</div>
                <div class="card-meta">
                    📅 {format_date(gig.performance_date)}
                    · ⏰ {format_time(gig.start_time)}
                    · 📍 {gig.city}
                    · 🎵 {gig.genre}
                </div>
                <div class="card-budget">{format_currency(gig.budget)}</div>
                <div style="color:#cbd5e1;margin-top:0.6rem;">
                    {gig.description or ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st.form(f"apply_form_{gig.id}"):
            msg = st.text_area("Cover Message", key=f"msg_{gig.id}")
            apply_btn = st.form_submit_button("📩 Apply Now", type="primary")

            if apply_btn:
                apply_to_gig(
                    musician_id=musician_id,
                    gig_id=gig.id,
                    message=msg,
                )
                st.success("✅ Application submitted!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)