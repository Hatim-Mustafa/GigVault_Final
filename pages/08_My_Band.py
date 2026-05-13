import streamlit as st

from components.auth_guard import require_musician
from components.sidebar import render_sidebar
from services.band_service import (
    create_band,
    get_active_band_id,
    get_band_by_id,
    get_band_members,
    get_musician_bands,
    join_band,
    set_active_band_id,
)
from utils import empty_state, format_date

st.set_page_config(
    page_title="My Band — GigVault",
    page_icon="🎶",
    layout="wide",
)

require_musician()
render_sidebar()

user_id = st.session_state["user_id"]
username = st.session_state["username"]
active_band_id = get_active_band_id(user_id)
my_bands = get_musician_bands(user_id)
active_band = get_band_by_id(active_band_id) if active_band_id else None

st.markdown('<div class="page-title">🎶 My Band</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Manage the band you apply and perform with.</div>',
    unsafe_allow_html=True,
)

if active_band:
    members = get_band_members(active_band.id)
    member_names = ", ".join(member.username for member in members) if members else "No members yet"
    st.markdown(
        f'''
        <div class="card">
            <div class="card-row" style="justify-content:space-between;margin-top:0;margin-bottom:0.4rem;">
                <span class="card-title">🎤 {active_band.name}</span>
                <span style="color:#94a3b8;font-size:0.85rem;">Active band</span>
            </div>
            <div class="card-meta">{active_band.genre or 'No genre set'} · {active_band.city or 'City not set'}</div>
            <div style="font-size:0.9rem;color:#cbd5e1;margin-top:0.6rem;">
                {active_band.bio or 'No band description yet.'}
            </div>
            <div style="font-size:0.84rem;color:#94a3b8;margin-top:0.6rem;">
                Leader: <b style="color:#f1f5f9;">{active_band.leader.username if active_band.leader else 'Unknown'}</b>
            </div>
            <div style="font-size:0.84rem;color:#94a3b8;margin-top:0.3rem;">
                Members: {member_names}
            </div>
            <div style="font-size:0.84rem;color:#94a3b8;margin-top:0.3rem;">
                Joined: {format_date(active_band.created_at) if active_band.created_at else 'N/A'}
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
else:
    st.markdown(empty_state("You are not in a band yet. Create one or join an existing band to start applying to gigs.", "🎶"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="section-header">Switch Band</div>', unsafe_allow_html=True)
    if len(my_bands) <= 1:
        st.info("You only have one band membership right now.")
    else:
        options = {f"{band.name} · {band.genre or 'No genre'}": band.id for band in my_bands}
        current_label = next((label for label, value in options.items() if value == active_band_id), list(options.keys())[0])
        selected_label = st.selectbox("Choose active band", list(options.keys()), index=list(options.keys()).index(current_label))
        if st.button("Use This Band", type="primary", use_container_width=True):
            try:
                set_active_band_id(user_id, options[selected_label])
                st.success("Active band updated.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Join Existing Band</div>', unsafe_allow_html=True)
    st.caption("Your primary instrument from your musician profile will be used for this band membership.")
    with st.form("join_band_form"):
        join_band_id = st.number_input("Band ID", min_value=1, step=1)
        joined = st.form_submit_button("➕ Join Band", type="primary", use_container_width=True)
        if joined:
            try:
                band = join_band(user_id, int(join_band_id))
                set_active_band_id(user_id, band.id)
                st.success(f"Joined {band.name}.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

with col_right:
    st.markdown('<div class="section-header">Create New Band</div>', unsafe_allow_html=True)
    with st.form("create_band_form"):
        band_name = st.text_input("Band Name *", placeholder="e.g. Midnight Echo")
        c1, c2 = st.columns(2)
        band_genre = c1.text_input("Genre", placeholder="Jazz, Rock, Pop")
        band_city = c2.text_input("City", placeholder="e.g. New York")
        band_bio = st.text_area("Description", placeholder="Describe your band, vibe and sound...", height=140)
        created = st.form_submit_button("🎸 Create Band", type="primary", use_container_width=True)
        if created:
            try:
                band = create_band(user_id, band_name, genre=band_genre, city=band_city, bio=band_bio)
                set_active_band_id(user_id, band.id)
                st.success(f"Band {band.name} created and set as active.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Your Band Memberships</div>', unsafe_allow_html=True)
    if not my_bands:
        st.info("No memberships yet.")
    else:
        for band in my_bands:
            is_active = band.id == active_band_id
            members = get_band_members(band.id)
            st.markdown(
                f'''
                <div class="card" style="border-color:{'#a78bfa' if is_active else '#2d2d4a'};">
                    <div class="card-row" style="justify-content:space-between;margin-top:0;margin-bottom:0.3rem;">
                        <span class="card-title">{band.name}</span>
                        <span style="color:#94a3b8;font-size:0.84rem;">{'Active' if is_active else 'Member'}</span>
                    </div>
                    <div class="card-meta">{band.genre or 'No genre set'} · {band.city or 'City not set'}</div>
                    <div style="font-size:0.84rem;color:#cbd5e1;margin-top:0.45rem;">{band.bio or 'No description'}</div>
                    <div style="font-size:0.82rem;color:#94a3b8;margin-top:0.45rem;">Members: {len(members)}</div>
                </div>
                ''',
                unsafe_allow_html=True,
            )
