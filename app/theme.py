"""Identite visuelle EY pour l'application Streamlit du POC.

Regroupe la charte graphique (couleurs, CSS injecte) et quelques composants
d'interface reutilisables (en-tete, pied de page, badges de statut).
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

EY_YELLOW = "#FFE600"
EY_DARK = "#2E2E38"
EY_BLACK = "#161616"
EY_GRAY = "#747480"
EY_LIGHT_GRAY = "#F6F6FA"
EY_WHITE = "#FFFFFF"
EY_SUCCESS = "#1E7B34"
EY_DANGER = "#C4262E"
EY_WARNING = "#B25000"

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "ey_logo.png"


@st.cache_data(show_spinner=False)
def _logo_base64() -> str | None:
    try:
        if not LOGO_PATH.exists():
            return None
        return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    except Exception:
        return None


def inject_global_css() -> None:
    """Injecte le CSS de la charte EY dans la page Streamlit courante."""
    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        /* Fond principal clair */
        .stApp {{
            background: {EY_LIGHT_GRAY};
            color: {EY_DARK};
        }}
        [data-testid="stAppViewContainer"] {{
            background: {EY_LIGHT_GRAY};
        }}

        /* NE PAS forcer la couleur sur tous les <p>/<span> markdown :
           cela rendait le texte invisible sur les fonds noirs (bandeau / hero). */

        /* ---------- Bandeau de marque EY (haut de page) ---------- */
        .ey-topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: {EY_BLACK} !important;
            border-bottom: 6px solid {EY_YELLOW};
            padding: 18px 28px;
            border-radius: 10px;
            margin-bottom: 28px;
        }}
        .ey-topbar, .ey-topbar * {{
            color: {EY_WHITE} !important;
        }}
        .ey-topbar-left {{
            display: flex;
            align-items: center;
            gap: 18px;
        }}
        .ey-topbar img {{
            height: 40px;
        }}
        .ey-topbar-title {{
            color: {EY_WHITE} !important;
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1.2;
            margin: 0;
        }}
        .ey-topbar-subtitle {{
            color: #D0D0DC !important;
            font-size: 0.85rem;
            margin: 0;
        }}
        .ey-topbar-tag {{
            background: {EY_YELLOW} !important;
            color: {EY_BLACK} !important;
            font-weight: 700;
            font-size: 0.75rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            padding: 6px 14px;
            border-radius: 999px;
        }}

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background: {EY_BLACK};
        }}
        section[data-testid="stSidebar"] * {{
            color: {EY_WHITE} !important;
        }}
        section[data-testid="stSidebar"] .ey-sidebar-logo {{
            display: flex;
            justify-content: center;
            padding: 18px 0 6px 0;
        }}
        section[data-testid="stSidebar"] .ey-sidebar-logo img {{
            height: 46px;
        }}
        section[data-testid="stSidebar"] .ey-sidebar-caption {{
            text-align: center;
            color: #B9B9C6 !important;
            font-size: 0.78rem;
            margin-bottom: 18px;
            padding: 0 12px;
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: #40404C;
        }}
        section[data-testid="stSidebar"] .stRadio > label {{
            font-weight: 700;
            color: {EY_YELLOW} !important;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.06em;
        }}
        section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {{
            padding: 6px 4px;
            border-radius: 6px;
        }}
        section[data-testid="stSidebar"] .ey-phase-item {{
            padding: 5px 0;
        }}
        section[data-testid="stSidebar"] .ey-phase-head {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            white-space: nowrap;
            color: #F2F2F5 !important;
        }}
        section[data-testid="stSidebar"] .ey-phase-dot {{
            display: inline-block;
            width: 9px;
            height: 9px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        section[data-testid="stSidebar"] .ey-phase-label {{
            font-size: 0.78rem;
            color: #B9B9C6 !important;
            padding-left: 17px;
            line-height: 1.3;
        }}

        /* ---------- Cartes / sections ---------- */
        .ey-card {{
            background: {EY_WHITE} !important;
            border: 1px solid #E6E6EC;
            border-radius: 12px;
            padding: 22px 24px;
            box-shadow: 0 1px 3px rgba(22, 22, 22, 0.06);
            margin-bottom: 18px;
            color: {EY_DARK} !important;
        }}
        .ey-card, .ey-card * {{
            color: {EY_DARK} !important;
        }}
        .ey-card b, .ey-card strong {{
            color: {EY_BLACK} !important;
        }}
        .ey-card code {{
            background: #F0F0F5 !important;
            color: {EY_BLACK} !important;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .ey-card .ey-badge-pass {{ color: {EY_SUCCESS} !important; }}
        .ey-card .ey-badge-fail {{ color: {EY_DANGER} !important; }}
        .ey-card .ey-badge-warn {{ color: {EY_WARNING} !important; }}
        .ey-hero {{
            background: linear-gradient(135deg, {EY_BLACK} 0%, #34343F 100%) !important;
            border-radius: 14px;
            padding: 34px 36px;
            margin-bottom: 26px;
            overflow: visible !important;
        }}
        .ey-hero .ey-hero-title {{
            color: #FFFFFF !important;
            font-size: 1.75rem;
            font-weight: 800;
            margin: 10px 0 12px 0;
            line-height: 1.3;
        }}
        .ey-hero .ey-hero-desc {{
            color: #F0F0F5 !important;
            font-size: 1rem;
            max-width: 920px;
            line-height: 1.55;
            margin: 0;
        }}
        div[data-testid="stMarkdownContainer"] .ey-hero .ey-hero-title,
        div[data-testid="stMarkdownContainer"] .ey-hero .ey-hero-desc {{
            color: #FFFFFF !important;
        }}
        div[data-testid="stMarkdownContainer"] .ey-hero .ey-hero-desc {{
            color: #F0F0F5 !important;
        }}
        .ey-hero::after {{
            content: "";
            position: absolute;
            top: -40px;
            right: -40px;
            width: 220px;
            height: 220px;
            background: {EY_YELLOW};
            opacity: 0.12;
            transform: rotate(20deg);
            border-radius: 30px;
            pointer-events: none;
        }}
        .ey-eyebrow {{
            display: inline-block;
            background: {EY_YELLOW} !important;
            color: {EY_BLACK} !important;
            font-weight: 700;
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 14px;
        }}
        div[data-testid="stMarkdownContainer"] .ey-eyebrow {{
            color: {EY_BLACK} !important;
        }}

        .ey-section-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: {EY_BLACK};
            border-left: 5px solid {EY_YELLOW};
            padding-left: 12px;
            margin: 6px 0 14px 0;
        }}

        /* ---------- Badges de statut ---------- */
        .ey-badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }}
        .ey-badge-pass {{ background: #E4F4E7; color: {EY_SUCCESS}; }}
        .ey-badge-fail {{ background: #FBE7E8; color: {EY_DANGER}; }}
        .ey-badge-warn {{ background: #FDECD9; color: {EY_WARNING}; }}

        /* ---------- Boutons ---------- */
        .stButton > button, .stDownloadButton > button {{
            background: {EY_YELLOW};
            color: {EY_BLACK};
            font-weight: 700;
            border: none;
            border-radius: 8px;
            padding: 0.55rem 1.4rem;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background: #E6CE00;
            color: {EY_BLACK};
        }}

        /* ---------- Metrics ---------- */
        div[data-testid="stMetric"] {{
            background: {EY_WHITE} !important;
            border: 1px solid #E6E6EC;
            border-left: 4px solid {EY_YELLOW};
            border-radius: 10px;
            padding: 14px 18px 10px 18px;
            color: {EY_DARK} !important;
        }}
        div[data-testid="stMetric"] * {{
            color: {EY_DARK} !important;
        }}
        div[data-testid="stMetricValue"] {{
            overflow: visible;
            white-space: normal;
            word-break: break-word;
            font-size: 1.6rem;
            color: {EY_BLACK} !important;
        }}
        div[data-testid="stMetricLabel"] {{
            white-space: normal;
            color: {EY_GRAY} !important;
        }}
        div[data-testid="stMetricDelta"] {{
            color: {EY_SUCCESS} !important;
        }}

        /* ---------- Tabs ---------- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: {EY_LIGHT_GRAY} !important;
            color: {EY_DARK} !important;
            border-radius: 8px 8px 0 0;
            padding: 8px 18px;
            font-weight: 600;
        }}
        .stTabs [data-baseweb="tab"] * {{
            color: {EY_DARK} !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: {EY_BLACK} !important;
            color: {EY_WHITE} !important;
        }}
        .stTabs [aria-selected="true"] * {{
            color: {EY_WHITE} !important;
        }}

        .ey-footer {{
            text-align: center;
            color: {EY_GRAY};
            font-size: 0.78rem;
            padding-top: 24px;
            border-top: 1px solid #E6E6EC;
            margin-top: 36px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(title: str, subtitle: str, tag: str = "POC — Stage EY") -> None:
    logo_b64 = _logo_base64()
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="EY" style="height:40px;" />'
        if logo_b64
        else ""
    )
    # components.html : bandeau court, hauteur fixe OK
    html = f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                background:#161616;border-bottom:6px solid #FFE600;
                padding:18px 28px;border-radius:10px;font-family:Segoe UI,Tahoma,sans-serif;">
      <div style="display:flex;align-items:center;gap:18px;">
        {logo_html}
        <div>
          <div style="color:#FFFFFF;font-size:1.25rem;font-weight:700;line-height:1.2;">{title}</div>
          <div style="color:#D0D0DC;font-size:0.85rem;margin-top:4px;">{subtitle}</div>
        </div>
      </div>
      <span style="background:#FFE600;color:#161616;font-weight:700;font-size:0.75rem;
                   letter-spacing:0.04em;text-transform:uppercase;padding:6px 14px;
                   border-radius:999px;">{tag}</span>
    </div>
    """
    components.html(html, height=92)


def render_sidebar_brand(caption: str) -> None:
    logo_b64 = _logo_base64()
    if logo_b64:
        st.sidebar.markdown(
            f"""
            <div class="ey-sidebar-logo"><img src="data:image/png;base64,{logo_b64}" alt="EY" /></div>
            <p class="ey-sidebar-caption">{caption}</p>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(f"### EY\n{caption}")


def hero(eyebrow: str, title: str, description: str) -> None:
    """Hero en markdown (hauteur auto) — plus de coupure de texte."""
    st.markdown(
        f"""
        <div class="ey-hero">
            <div class="ey-eyebrow">{eyebrow}</div>
            <div class="ey-hero-title">{title}</div>
            <div class="ey-hero-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(f'<div class="ey-section-title">{text}</div>', unsafe_allow_html=True)


def badge(status: str) -> str:
    status_upper = (status or "").upper()
    css_class = {
        "PASS": "ey-badge-pass",
        "FAIL": "ey-badge-fail",
        "WARN": "ey-badge-warn",
    }.get(status_upper, "ey-badge-warn")
    return f'<span class="ey-badge {css_class}">{status_upper}</span>'


def footer() -> None:
    st.markdown(
        """
        <div class="ey-footer">
            POC IA pour l'automatisation ETL &amp; Power BI — Stage EY, 2026 ·
            Document interne de démonstration, à usage pédagogique.
        </div>
        """,
        unsafe_allow_html=True,
    )
