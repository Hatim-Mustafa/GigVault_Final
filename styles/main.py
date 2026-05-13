def get_main_css() -> str:
    return """
<style>
    /* ── Global ─────────────────────────────────────────── */
    [data-testid="stAppViewContainer"] {
        background: #0f0f1a;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ── Sidebar ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #0c0c18 !important;
        border-right: 1px solid #1f1f35;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #cbd5e1;
    }

    /* ── Headings ─────────────────────────────────────────── */
    h1, h2, h3 {
        color: #f1f5f9;
        font-weight: 700;
    }
    .page-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 0.25rem;
    }
    .page-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    /* ── Metric Cards ────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: #1a1a2e !important;
        border: 1px solid #2d2d4a !important;
        border-radius: 14px !important;
        padding: 1.1rem 1.3rem !important;
    }
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
    }

    /* ── Gig / Info Cards ────────────────────────────────── */
    .card {
        background: #1a1a2e;
        border: 1px solid #2d2d4a;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .card:hover {
        border-color: #7c3aed;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.2rem;
    }
    .card-meta {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.6rem;
    }
    .card-budget {
        font-size: 1.3rem;
        font-weight: 800;
        color: #a78bfa;
    }
    .card-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-top: 0.5rem;
    }

    /* ── Buttons ─────────────────────────────────────────── */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        border: none;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background: #1e1e3a;
        color: #cbd5e1;
        border: 1px solid #3d3d5c;
    }

    /* ── Forms ───────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background: #1a1a2e !important;
        border: 1px solid #2d2d4a !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
    }

    /* ── Tabs ────────────────────────────────────────────── */
    [data-testid="stTabs"] [role="tablist"] {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border-bottom: none;
    }
    [data-testid="stTabs"] button[role="tab"] {
        border-radius: 8px;
        font-weight: 600;
        color: #94a3b8 !important;
        padding: 0.5rem 1.2rem;
        border: none;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #7c3aed !important;
        color: white !important;
    }

    /* ── Expanders ───────────────────────────────────────── */
    [data-testid="stExpander"] {
        background: #1a1a2e;
        border: 1px solid #2d2d4a;
        border-radius: 12px;
    }
    [data-testid="stExpander"] summary {
        color: #f1f5f9;
        font-weight: 600;
    }

    /* ── Divider ─────────────────────────────────────────── */
    hr {
        border: none;
        border-top: 1px solid #2d2d4a;
        margin: 1.2rem 0;
    }

    /* ── DataFrames ──────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Alerts ──────────────────────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* ── Auth page hero ──────────────────────────────────── */
    .hero {
        text-align: center;
        padding: 0rem 1rem 2rem;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-top: 0.5rem;
    }

    /* ── Section header ──────────────────────────────────── */
    .section-header {
        font-size: 1rem;
        font-weight: 700;
        color: #a78bfa;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.8rem;
    }

    /* ── Payment row ─────────────────────────────────────── */
    .payment-row {
        background: #1a1a2e;
        border: 1px solid #2d2d4a;
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .overdue-row {
        border-color: #7f1d1d !important;
        background: #1c0a0a !important;
    }
</style>
"""
