import streamlit as st

from utils import format_currency, format_date, format_time, status_badge_html, truncate_text


def render_gig_card(gig, show_apply_btn: bool = False, on_apply=None) -> None:
    genre_tag = (
        f'<span style="background:#1e1b4b;color:#a78bfa;padding:2px 10px;'
        f'border-radius:20px;font-size:11px;font-weight:600;">{gig.genre}</span>'
    )
    city_tag = (
        f'<span style="background:#0c4a6e;color:#7dd3fc;padding:2px 10px;'
        f'border-radius:20px;font-size:11px;font-weight:600;">📍 {gig.city}</span>'
    )
    date_str = format_date(gig.performance_date)
    time_str = ""
    if gig.start_time:
        time_str = f" · {format_time(gig.start_time)}"
        if gig.end_time:
            time_str += f" – {format_time(gig.end_time)}"

    venue_name = ""
    if hasattr(gig, "client") and gig.client and gig.client.client_profile:
        venue_name = gig.client.client_profile.venue_name

    st.markdown(
        f"""
        <div class="card">
            <div class="card-row" style="justify-content:space-between;margin-top:0;margin-bottom:0.4rem;">
                <span class="card-title">{gig.title}</span>
                {status_badge_html(gig.status.value if hasattr(gig.status, 'value') else gig.status)}
            </div>
            {f'<div style="color:#64748b;font-size:0.8rem;margin-bottom:0.3rem;">🏛 {venue_name}</div>' if venue_name else ''}
            <div class="card-meta">📅 {date_str}{time_str}</div>
            <div class="card-row" style="margin-top:0.3rem;margin-bottom:0.6rem;">
                {genre_tag}
                {city_tag}
            </div>
            <div class="card-budget">{format_currency(gig.budget)}</div>
            {f'<div style="color:#94a3b8;font-size:0.88rem;margin-top:0.5rem;">{truncate_text(gig.description or "", 160)}</div>' if gig.description else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if show_apply_btn and on_apply is not None:
        on_apply(gig)


def render_gig_summary_row(gig) -> None:
    status_val = gig.status.value if hasattr(gig.status, "value") else gig.status
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:0.7rem 1rem;background:#1a1a2e;border:1px solid #2d2d4a;'
        f'border-radius:10px;margin-bottom:0.5rem;">'
        f'<span style="color:#f1f5f9;font-weight:600;">{gig.title}</span>'
        f'<span style="color:#94a3b8;font-size:0.85rem;">{format_date(gig.performance_date)}</span>'
        f'<span style="color:#a78bfa;font-weight:700;">{format_currency(gig.budget)}</span>'
        f"{status_badge_html(status_val)}"
        f"</div>",
        unsafe_allow_html=True,
    )
