import streamlit as st

from utils import STATUS_COLORS, status_badge_html


def badge(status: str) -> None:
    st.markdown(status_badge_html(status), unsafe_allow_html=True)


def inline_badge(status: str) -> str:
    return status_badge_html(status)


def payment_status_indicator(status: str, amount, due_date=None) -> None:
    from utils import format_currency, format_date
    color = STATUS_COLORS.get(status, "#6b7280")
    due_str = f" · Due {format_date(due_date)}" if due_date else ""
    extra_class = "overdue-row" if status == "Overdue" else ""
    st.markdown(
        f'<div class="payment-row {extra_class}">'
        f'<span style="font-weight:700;color:#f1f5f9;">{format_currency(amount)}</span>'
        f'<span style="color:#94a3b8;font-size:0.85rem;">{due_str}</span>'
        f"{status_badge_html(status)}"
        f"</div>",
        unsafe_allow_html=True,
    )
