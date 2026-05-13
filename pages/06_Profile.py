import streamlit as st

from components.auth_guard import auth_guard
from components.sidebar import render_sidebar
from config import VENUE_TYPES
from services.user_service import get_client_profile, get_musician_profile, get_user_by_id, update_client_profile, update_musician_profile
from utils import format_date, role_badge_html

st.set_page_config(page_title="Profile — GigVault", page_icon="👤", layout="wide")
auth_guard(); render_sidebar()
role = st.session_state["role"]; user_id = st.session_state["user_id"]; username = st.session_state["username"]
user = get_user_by_id(user_id)

st.markdown('<div class="page-title">👤 My Profile</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-subtitle">{role_badge_html(role)} &nbsp; @{username}</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if role == "Venue_Owner":
    profile = get_client_profile(user_id)
    col_view, col_edit = st.columns([1, 2])
    with col_view:
        st.markdown('<div class="section-header">Current Venue Profile</div>', unsafe_allow_html=True)
        if profile:
            st.markdown(f'''
            <div class="card"><div class="card-title">🏛 {profile.venue_name or 'No venue name'}</div>
            <div class="card-meta">@{username}</div>
            <div style="font-size:0.88rem;color:#94a3b8;margin-top:0.5rem;">
            <div>📍 {profile.city or 'City not set'}</div><div>🏷️ {profile.venue_type or 'Venue type not set'}</div>
            <div>🎵 {profile.genre_specialization or 'No genre specified'}</div>
            {f'<div>🗺️ {profile.address}</div>' if profile.address else ''}
            {f'<div>👥 Capacity: {profile.capacity}</div>' if profile.capacity else ''}
            {f'<div>🌐 {profile.website}</div>' if profile.website else ''}</div>
            {f'<div style="margin-top:0.7rem;font-size:0.88rem;color:#cbd5e1;">{profile.description}</div>' if profile.description else ''}</div>
            ''', unsafe_allow_html=True)
        else:
            st.info("No profile set up yet. Fill out the form to complete your profile.")
        if user: st.caption(f"✉️ {user.email} · Member since {format_date(user.created_at)}")
    with col_edit:
        st.markdown('<div class="section-header">Edit Venue Profile</div>', unsafe_allow_html=True)
        with st.form("client_profile_form"):
            venue_name = st.text_input("Venue Name *", value=profile.venue_name if profile else "")
            c1, c2 = st.columns(2)
            venue_type = c1.selectbox("Venue Type", VENUE_TYPES, index=VENUE_TYPES.index(profile.venue_type) if profile and profile.venue_type in VENUE_TYPES else 0)
            city = c2.text_input("City *", value=profile.city if profile else "")
            genre_spec = st.text_input("Genre Specialization", value=profile.genre_specialization if profile else "")
            address = st.text_input("Address", value=profile.address if profile else "")
            c3, c4 = st.columns(2)
            capacity = c3.number_input("Venue Capacity", min_value=0, value=profile.capacity if profile and profile.capacity else 0)
            website = c4.text_input("Website", value=profile.website if profile else "")
            description = st.text_area("Venue Description", value=profile.description if profile else "", height=120)
            if st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True):
                if not venue_name.strip() or not city.strip(): st.error("Venue name and city are required.")
                else:
                    update_client_profile(user_id, venue_name, venue_type, genre_spec, city, address, int(capacity) if capacity > 0 else None, description, website)
                    st.success("✅ Profile updated successfully!"); st.rerun()
else:
    profile = get_musician_profile(user_id)
    col_view, col_edit = st.columns([1, 2])
    with col_view:
        st.markdown('<div class="section-header">Current Musician Profile</div>', unsafe_allow_html=True)
        if profile:
            st.markdown(f'''
            <div class="card"><div class="card-title">🎤 {profile.stage_name or username}</div><div class="card-meta">@{username}</div>
            <div style="font-size:0.88rem;color:#94a3b8;margin-top:0.5rem;">
            <div>📍 {user.city if user and user.city else 'City not set'}</div><div>🎵 {profile.genres or 'Genres not set'}</div>
            <div>🎸 {profile.instruments or 'Instruments not set'}</div><div>💵 ${float(profile.hourly_rate or 0):,.2f}/hr</div>
            <div>⭐ {profile.years_experience or 0} years experience</div>
            {f'<div>☁️ {profile.soundcloud_url}</div>' if profile.soundcloud_url else ''}
            {f'<div>🟢 {profile.spotify_url}</div>' if profile.spotify_url else ''}</div>
            {f'<div style="margin-top:0.7rem;font-size:0.88rem;color:#cbd5e1;">{user.bio}</div>' if user and user.bio else ''}</div>
            ''', unsafe_allow_html=True)
        else:
            st.info("No profile set up yet. Fill out the form to complete your profile.")
        if user: st.caption(f"✉️ {user.email} · Member since {format_date(user.created_at)}")
    with col_edit:
        st.markdown('<div class="section-header">Edit Musician Profile</div>', unsafe_allow_html=True)
        with st.form("musician_profile_form"):
            stage_name = st.text_input("Stage Name *", value=profile.stage_name if profile else username)
            genres = st.text_input("Genres", value=profile.genres if profile else "", placeholder="Jazz, Pop, Rock")
            instruments = st.text_input("Instruments", value=profile.instruments if profile else "", placeholder="Vocals, Guitar, Piano")
            c1, c2 = st.columns(2)
            hourly_rate = c1.number_input("Hourly Rate ($)", min_value=0.0, value=float(profile.hourly_rate or 0) if profile else 0.0, step=10.0)
            years_experience = c2.number_input("Years Experience", min_value=0, value=profile.years_experience if profile and profile.years_experience else 0)
            bio = st.text_area("Bio", value=user.bio if user and user.bio else "", height=120)
            soundcloud_url = st.text_input("SoundCloud URL", value=profile.soundcloud_url if profile and profile.soundcloud_url else "")
            spotify_url = st.text_input("Spotify URL", value=profile.spotify_url if profile and profile.spotify_url else "")
            if st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True):
                if not stage_name.strip(): st.error("Stage name is required.")
                else:
                    update_musician_profile(user_id, stage_name, genres, instruments, hourly_rate, int(years_experience), bio, soundcloud_url, spotify_url)
                    st.success("✅ Profile updated successfully!"); st.rerun()
