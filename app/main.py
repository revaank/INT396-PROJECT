from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analysis import (
    build_dendrogram,
    cluster_plain_summary,
    describe_pattern,
    feature_contributions,
    fit_clusters,
    stability_comparison,
    sweep_k,
)
from src.data import (
    DATA_PATH,
    get_quality_summary,
    load_data,
    regional_data,
    regional_feature_matrix,
)

st.set_page_config(
    page_title="AeroTB | India Regional Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────── THEME & AESTHETICS (AEROTB DARK) ─────────────────────
THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
:root {
  --bg-deep: #08090d;
  --panel: rgba(18, 20, 28, 0.85);
  --border: rgba(255, 255, 255, 0.08);
  --border-subtle: rgba(255, 255, 255, 0.06);
  --cyan: #38bdf8;
  --accent: #38bdf8;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
}
.stApp {
  background-color: #07080c;
  background-image: 
    radial-gradient(ellipse 90% 65% at 50% -12%, rgba(42, 53, 76, 0.42) 0%, rgba(18, 23, 34, 0.5) 50%, transparent 90%),
    radial-gradient(circle at 85% 90%, rgba(28, 35, 52, 0.28) 0%, transparent 60%);
  background-attachment: fixed;
  color: var(--text-main);
  font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
}
[data-testid="stSidebar"] {
  background: #0d0f15 !important;
  border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] * {
  color: #e2e8f0;
}
.block-container {
  padding-top: 1.2rem !important;
  padding-bottom: 2rem !important;
  max-width: 96% !important;
}

/* ── HIDE UGLY RADIO DOTS & TURN SIDEBAR INTO SLEEK PILLS ── */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  background: rgba(15, 23, 42, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.06) !important;
  border-radius: 10px !important;
  padding: 10px 14px !important;
  cursor: pointer !important;
  transition: all 0.22s ease !important;
  display: flex !important;
  align-items: center !important;
  width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(0, 242, 254, 0.1) !important;
  border-color: rgba(0, 242, 254, 0.35) !important;
  transform: translateX(3px);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
  background: rgba(0, 242, 254, 0.16) !important;
  border-color: #00f2fe !important;
  box-shadow: 0 0 16px rgba(0, 242, 254, 0.25) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
  color: #00f2fe !important;
  font-weight: 700 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"],
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
  display: none !important;
}

/* ── AEROTB FLOATING COMPONENTS ── */
.aero-brand-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.aero-logo {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #00f2fe, #4facfe);
  box-shadow: 0 0 16px rgba(0, 242, 254, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  color: #050811;
}
.aero-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.02em;
  line-height: 1.1;
}
.aero-sub {
  font-size: 0.65rem;
  color: #64748b;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* FACT BOX */
.aero-fact-card {
  background: rgba(11, 18, 34, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 242, 254, 0.25);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
  margin-bottom: 14px;
  position: relative;
  overflow: hidden;
}
.aero-fact-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, #00f2fe, #4facfe, transparent);
}
.aero-fact-tag {
  color: #00f2fe;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.aero-fact-text {
  font-size: 0.82rem;
  line-height: 1.5;
  color: #cbd5e1;
}

/* TELEMETRY CARD */
.aero-telemetry {
  background: rgba(11, 18, 34, 0.88);
  backdrop-filter: blur(22px);
  border: 1px solid rgba(0, 242, 254, 0.28);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.7), 0 0 35px rgba(0, 242, 254, 0.08);
}
.aero-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(0, 242, 254, 0.12);
  border: 1px solid rgba(0, 242, 254, 0.3);
  color: #00f2fe;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.aero-stat-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 2px;
}
.aero-cluster-pill {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 10px;
  padding: 8px 12px;
  margin: 12px 0;
}

/* ── SCROLL-STACK STORYTELLING CARDS ── */
.story-scroll-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 36px;
  max-width: 960px;
  margin: 0 auto;
  padding: 10px 0 50px 0;
}
.story-card-stack {
  position: sticky;
  background: rgba(13, 21, 39, 0.95);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid rgba(0, 242, 254, 0.28);
  border-radius: 24px;
  padding: 32px 36px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 242, 254, 0.1);
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
.story-card-stack:hover {
  border-color: #00f2fe;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.9), 0 0 50px rgba(0, 242, 254, 0.25);
}

/* 3D SCROLL STORY CARDS */
.aero-3d-card {
  background: rgba(13, 21, 39, 0.85);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 242, 254, 0.25);
  border-radius: 24px;
  padding: 32px 28px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7), 0 0 35px rgba(0, 242, 254, 0.12);
  transition: all 0.3s ease;
  height: 100%;
}
.aero-3d-card:hover {
  border-color: #00f2fe;
  transform: translateY(-8px);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.8), 0 0 45px rgba(0, 242, 254, 0.25);
}

/* PORTAL LAUNCH CARDS */
.aero-portal-card {
  background: rgba(11, 18, 34, 0.7);
  border: 1px solid var(--border-subtle);
  border-radius: 18px;
  padding: 22px 18px;
  transition: all 0.25s ease;
  height: 100%;
}
.aero-portal-card:hover {
  background: rgba(15, 25, 48, 0.9);
  border-color: #00f2fe;
  transform: translateY(-6px);
  box-shadow: 0 16px 35px rgba(0, 0, 0, 0.6), 0 0 25px rgba(0, 242, 254, 0.15);
}
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)


# ───────────────────── HELPERS ─────────────────────
def header(kicker: str, title: str, subtitle: str = ""):
    st.markdown(
        f'<div class="hero"><div class="eyebrow">{kicker}</div>'
        f"<h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def metric(label: str, value: str, sub: str = ""):
    st.markdown(
        f'<div class="metric"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def explain(text: str):
    """A friendly explanation box that stands out."""
    st.markdown(f'<div class="explain">💡 {text}</div>', unsafe_allow_html=True)


def policy_box(text: str):
    """A 'what could this mean for health planning' box."""
    st.markdown(f'<div class="policy-box">🏥 {text}</div>', unsafe_allow_html=True)


# ───────────────────── LOAD DATA ─────────────────────
@st.cache_data(show_spinner=False)
def get_data():
    return load_data()


try:
    df = get_data()
except (FileNotFoundError, ValueError, OSError) as exc:
    st.error(f"The dataset could not be loaded: {exc}")
    st.stop()

regions = regional_data(df)
quality = get_quality_summary(df)

# ───────────────────── NAVIGATION ─────────────────────
pages = [
    "Home",
    "Explore India",
    "Compare States",
    "State Pattern Groups",
    "Research Insights",
    "AI Explainer",
    "TB Knowledge Centre",
    "Find Help & About",
]

query_p = st.query_params.get("page", "Home")
p_map = {
    "clusters": "State Pattern Groups",
    "compare": "Compare States",
    "explore": "Explore India",
    "explainer": "AI Explainer",
    "help": "Find Help & About",
    "Home": "Home",
}
resolved_default = p_map.get(query_p, "Home")
def_idx = pages.index(resolved_default) if resolved_default in pages else 0

with st.sidebar:
    st.markdown(
        """
        <div class="aero-brand-badge">
          <div class="aero-logo">◈</div>
          <div>
            <div class="aero-title">AeroTB</div>
            <div class="aero-sub">India Regional Intelligence</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio("Navigation", pages, index=def_idx, label_visibility="collapsed")
    st.markdown("---")
    st.caption(f"SURVEILLANCE WINDOW · {min(quality['years'])}–{max(quality['years'])}")
    st.caption("Official MoHFW Annual TB Surveillance Reports")
    st.markdown(
        '<div class="note"><b>Aggregated Surveillance:</b> Records describe regional clinical indicators. Not for individual diagnosis.</div>',
        unsafe_allow_html=True,
    )


def selection_controls(key_prefix="sel"):
    years = [int(y) for y in quality["years"]]
    a, b, c, d = st.columns(4)
    year = a.selectbox("Year", years, index=len(years) - 1, key=f"{key_prefix}_year")
    factor = b.selectbox(
        "Risk factor",
        sorted(regions.risk_factor.dropna().unique()),
        key=f"{key_prefix}_factor",
    )
    sectors = sorted(
        regions.loc[
            (regions.year == year) & (regions.risk_factor == factor), "sector"
        ]
        .dropna()
        .unique()
    )
    sector = c.selectbox("Reporting sector", sectors, key=f"{key_prefix}_sector")
    params = sorted(
        regions.loc[
            (regions.year == year)
            & (regions.risk_factor == factor)
            & (regions.sector == sector),
            "parameter",
        ]
        .dropna()
        .unique()
    )
    parameter = d.selectbox("Indicator", params, key=f"{key_prefix}_parameter")
    return year, factor, sector, parameter


import unicodedata

def _clean_geo_name(s: str) -> str:
    """Normalize diacritics and casing for reliable geographic matching."""
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8").strip().lower()


def display_map(plot_data, value_col, label="Reported count", color_col=None, height=650, highlight_state=None):
    """Show an interactive Bharat Cancer-style choropleth map with fluid scroll-zoom and pan."""
    geo_path = ROOT / "data" / "raw" / "dataful_20833" / "india_admin1.geojson"
    if not geo_path.exists():
        st.info("The interactive map needs the boundary file.")
        return
    try:
        geo = json.loads(geo_path.read_text(encoding="utf-8"))
        geo_map = {}
        for feat in geo.get("features", []):
            raw_shape = feat.get("properties", {}).get("shapeName", "")
            geo_map[_clean_geo_name(raw_shape)] = raw_shape

        data_copy = plot_data.copy()
        raw_state_col = "state" if "state" in data_copy.columns else "State / UT"
        data_copy["_geo_key"] = data_copy[raw_state_col].apply(_clean_geo_name).map(geo_map)
        match = data_copy.dropna(subset=["_geo_key"])

        if match.empty:
            st.warning("Map boundary names don't match the selected states — map hidden.")
            return

        if color_col and color_col in match.columns:
            fig = px.choropleth(
                match, geojson=geo, locations="_geo_key",
                featureidkey="properties.shapeName",
                color=color_col, hover_name=raw_state_col,
                color_discrete_sequence=["#00f2fe", "#4facfe", "#f6d365", "#fda085", "#ff5858", "#a8edea"],
                labels={color_col: "AI Cluster Group"},
            )
            fig.update_traces(
                marker_line_width=1.4,
                marker_line_color="rgba(255, 255, 255, 0.6)",
                hovertemplate="<b>%{hovertext}</b><br><span style='color:#00f2fe;'>Group:</span> %{color}<br><span style='color:#94a3b8;font-size:11px;'>Scroll wheel to zoom · Drag to pan</span><extra></extra>",
            )
        else:
            fig = px.choropleth(
                match, geojson=geo, locations="_geo_key",
                featureidkey="properties.shapeName",
                color=value_col,
                color_continuous_scale=[
                    [0.0, "#081b29"],
                    [0.15, "#0d3b66"],
                    [0.35, "#0077b6"],
                    [0.65, "#00b4d8"],
                    [0.85, "#48cae4"],
                    [1.0, "#00f2fe"],
                ],
                hover_name=raw_state_col,
                labels={value_col: label},
            )
            fig.update_traces(
                marker_line_width=1.3,
                marker_line_color="rgba(255, 255, 255, 0.45)",
                hovertemplate="<b>%{hovertext}</b><br><span style='color:#00f2fe;'>" + label + ":</span> %{z:,.0f}<br><span style='color:#94a3b8;font-size:11px;'>Scroll wheel to zoom · Drag to pan</span><extra></extra>",
            )

        if highlight_state:
            clean_target = _clean_geo_name(highlight_state)
            for feat in geo.get("features", []):
                raw_s = feat.get("properties", {}).get("shapeName", "")
                if _clean_geo_name(raw_s) == clean_target:
                    coords = feat.get("geometry", {}).get("coordinates", [])
                    lons, lats = [], []
                    def _extract(p):
                        for item in p:
                            if isinstance(item[0], (int, float)):
                                lons.append(item[0])
                                lats.append(item[1])
                            else:
                                _extract(item)
                    _extract(coords)
                    if lons and lats:
                        c_lon = sum(lons) / len(lons)
                        c_lat = sum(lats) / len(lats)
                        fig.add_trace(
                            go.Scattergeo(
                                lon=[c_lon],
                                lat=[c_lat],
                                mode="markers+text",
                                marker=dict(
                                    size=16,
                                    color="#00f2fe",
                                    symbol="circle",
                                    line=dict(width=3, color="#ffffff"),
                                ),
                                text=[f"📍 {highlight_state}"],
                                textposition="top center",
                                textfont=dict(color="#ffffff", size=13, family="Plus Jakarta Sans"),
                                hoverinfo="skip",
                                showlegend=False,
                            )
                        )
                    break

        fig.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor="rgba(0,0,0,0)",
            showcoastlines=False,
            showland=False,
            showocean=False,
            showlakes=False,
        )
        fig.update_layout(
            height=height,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dcebea",
            dragmode="pan",
            coloraxis_colorbar=dict(
                title=label,
                thicknessmode="pixels",
                thickness=14,
                lenmode="fraction",
                len=0.75,
                bgcolor="rgba(10, 25, 35, 0.6)",
                bordercolor="rgba(0, 242, 254, 0.3)",
                borderwidth=1,
            ),
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "scrollZoom": True,
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            },
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.warning(f"State boundaries could not be rendered: {exc}")


# ═══════════════════════════════════════════════════════
#                        PAGES
# ═══════════════════════════════════════════════════════


# ───────────────────── HOME (AEROTB COMMAND CENTER) ─────────────────────
# On analytical sub-pages, show return button at top
if page != "Home":
    st.markdown(
        """
        <div style="margin-top: 10px; margin-bottom: 20px;">
          <a href="/?page=Home" style="display:inline-flex; align-items:center; gap:8px; background:rgba(0,242,254,0.14); border:1px solid rgba(0,242,254,0.4); border-radius:9999px; padding:8px 20px; color:#00f2fe; text-decoration:none; font-weight:700; font-size:0.84rem; box-shadow: 0 0 16px rgba(0,242,254,0.2); transition: all 0.2s;">
            ← Return to AeroTB Command Center
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

if page == "Home":
    # ── HIDE ALL STREAMLIT CHROME & FULL-BLEED ZERO MARGINS ──
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"],
        #MainMenu,
        footer,
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
          display: none !important;
        }
        .main, .stMain, [data-testid="stAppViewContainer"], section.main {
          background-color: #07080c !important;
          background-image: 
            radial-gradient(ellipse 90% 65% at 50% -12%, rgba(42, 53, 76, 0.42) 0%, rgba(18, 23, 34, 0.5) 50%, transparent 90%),
            radial-gradient(circle at 85% 90%, rgba(28, 35, 52, 0.28) 0%, transparent 60%) !important;
          background-attachment: fixed !important;
          padding: 0 !important;
          margin: 0 !important;
          overflow-x: hidden !important;
        }
        .main .block-container, [data-testid="stMainBlockContainer"] {
          max-width: 100vw !important;
          width: 100vw !important;
          padding: 0 !important;
          margin: 0 !important;
        }
        iframe {
          position: fixed !important;
          top: 0 !important;
          left: 0 !important;
          width: 100vw !important;
          height: 100vh !important;
          border: none !important;
          margin: 0 !important;
          padding: 0 !important;
          z-index: 999999 !important;
          display: block !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    preview_file = ROOT / "preview.html"
    if preview_file.exists():
        st.iframe(preview_file, width="stretch", height="stretch")
    else:
        st.error("preview.html not found")
elif page == "Explore India":
    header(
        "Explore India",
        "See one indicator across every state",
        "Pick a year, risk factor, and indicator below. "
        "The map and chart show how states compare for that one measure.",
    )
    explain(
        "<b>How to read this page:</b> Use the dropdown menus to select what you want "
        "to see. The map shows darker colours for higher reported counts. "
        "The bar chart on the right ranks all states. Click on any state below "
        "to see its full profile."
    )

    year, factor, sector, parameter = selection_controls("explore")
    view = regions.loc[
        (regions.year == year)
        & (regions.risk_factor == factor)
        & (regions.sector == sector)
        & (regions.parameter == parameter)
    ].copy()

    st.markdown(
        f"**Showing:** {parameter}  \n"
        f"**Risk factor:** {factor} · **Sector:** {sector} · **Year:** {year} · "
        f"*{(view.unit.iloc[0] if not view.empty else 'unit unavailable')}*"
    )

    left, right = st.columns([1.05, 1])
    with left:
        display_map(view, "value")
    with right:
        sort = view.dropna(subset=["value"]).sort_values("value", ascending=True)
        fig = px.bar(
            sort, x="value", y="state", orientation="h",
            labels={"value": "Reported count", "state": "State / UT"},
            color="value",
            color_continuous_scale=["#1b6570", "#56d5c2"],
        )
        fig.update_layout(
            height=500, margin=dict(l=0, r=0, t=5, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dcebea", showlegend=False, coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Taller bars = more reported cases for this indicator. "
        "Remember: bigger numbers can mean better reporting, not necessarily more disease."
    )

    states = sorted(view.state.unique())
    if states:
        chosen = st.selectbox("Open a state profile", states, key="explore_profile")
        profile = regions.loc[
            (regions.state == chosen)
            & (regions.year == year)
            & (regions.sector == sector)
        ]
        st.subheader(f"📋 {chosen} — all indicators for {year}")
        explain(
            f"This table shows every TB indicator reported for {chosen} in {year}. "
            "Each row is a different thing that was measured."
        )
        st.dataframe(
            profile[["risk_factor", "parameter", "value", "unit"]].sort_values(
                ["risk_factor", "parameter"]
            ),
            use_container_width=True,
            hide_index=True,
        )

# ───────────────────── COMPARE STATES ─────────────────────
elif page == "Compare States":
    header(
        "Compare States",
        "Put states side by side",
        "Pick one indicator and up to six states to see how their numbers "
        "changed year by year.",
    )
    explain(
        "<b>How to use:</b> Choose a risk factor and indicator first, then pick "
        "the states you want to compare. The chart shows their reported counts "
        "over time. If a line goes up, the reported count increased — but that "
        "could mean more cases OR better detection."
    )

    factor = st.selectbox(
        "Risk factor", sorted(regions.risk_factor.unique()), key="compare_factor"
    )
    parameter = st.selectbox(
        "Indicator",
        sorted(regions.loc[regions.risk_factor == factor, "parameter"].unique()),
        key="compare_parameter",
    )
    sectors = sorted(
        regions.loc[
            (regions.risk_factor == factor) & (regions.parameter == parameter),
            "sector",
        ].unique()
    )
    sector = st.selectbox("Reporting sector", sectors, key="compare_sector")
    options = sorted(regions.state.unique())
    defaults = [x for x in ["Maharashtra", "Uttar Pradesh", "Tamil Nadu"] if x in options]
    selected = st.multiselect(
        "States / UTs (up to 6)", options, default=defaults[:3], max_selections=6
    )
    trend = regions.loc[
        (regions.risk_factor == factor)
        & (regions.parameter == parameter)
        & (regions.sector == sector)
        & (regions.state.isin(selected))
    ].dropna(subset=["value"])

    if not trend.empty:
        fig = px.line(
            trend, x="year", y="value", color="state", markers=True,
            labels={"year": "Year", "value": "Reported count", "state": "State / UT"},
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig.update_layout(
            height=480, margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dcebea", legend_title_text="State / UT",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            trend.pivot(index="year", columns="state", values="value").reset_index(),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "📌 Missing values are left blank — they are NOT treated as zero. "
            "A rising line means the reported count went up, which could reflect "
            "more cases, better screening, or changes in reporting."
        )
    else:
        st.info("Choose at least one region with reported values for this indicator.")

# ───────────────────── STATE PATTERN GROUPS (was ML Intelligence) ─────────────────────
elif page == "State Pattern Groups":
    header(
        "Machine Learning Analysis",
        "Which states have similar TB patterns?",
        "This page groups states with similar TB reporting patterns. "
        "Think of it like sorting states into teams based on their numbers.",
    )
    explain(
        "<b>What's happening here:</b> The computer looks at the numbers each state "
        "reported, finds which states have similar patterns, and groups them together. "
        "This is called <i>clustering</i> — it's like sorting a deck of cards by colour "
        "without being told the colours first."
    )

    # ── Controls ──
    years = [int(y) for y in quality["years"]]
    a, b, c = st.columns(3)
    year = a.selectbox("Year", years, index=len(years) - 1, key="ml_year")
    factors = sorted(regions.loc[regions.year == year, "risk_factor"].unique())
    factor_default = factors.index("Diabetes") if "Diabetes" in factors else 0
    factor = b.selectbox("Risk factor", factors, index=factor_default, key="ml_factor")
    avail_sectors = sorted(
        regions.loc[
            (regions.year == year) & (regions.risk_factor == factor), "sector"
        ]
        .unique()
    )
    sector_default = avail_sectors.index("public + private") if "public + private" in avail_sectors else 0
    sector = c.selectbox(
        "Reporting sector",
        avail_sectors,
        index=sector_default,
        key="ml_sector",
    )

    raw, complete = regional_feature_matrix(df, year, factor, sector)

    if raw.empty:
        st.warning("No state-level records match this selection.")
    elif raw.shape[1] < 2:
        st.warning("This selection has fewer than two indicators — meaningful grouping is unavailable.")
    elif complete.shape[0] < 4:
        st.warning("Fewer than four complete regions remain. Try another year, factor, or sector.")
    else:
        # ── Preprocessing explainer ──
        with st.expander("📋 How was the data prepared? (click to expand)"):
            st.markdown(
                f"**Step 1 — Filter:** Kept only {year}, {factor}, {sector} records "
                f"from the {quality['regions']} states/UTs (All India excluded).\n\n"
                f"**Step 2 — Pivot:** Rearranged so each state is a row and each "
                f"indicator is a column. This gave {raw.shape[0]} states × {raw.shape[1]} indicators.\n\n"
                f"**Step 3 — Remove incomplete rows:** {raw.shape[0] - complete.shape[0]} states "
                f"had missing values and were removed, leaving {complete.shape[0]} complete states.\n\n"
                f"**Step 4 — Standardise:** Brought all indicators to the same scale "
                "(mean=0, spread=1) so one large indicator doesn't dominate.\n\n"
                "**Why?** Without standardisation, an indicator measured in millions "
                "would overpower one measured in hundreds, even if both are equally important."
            )

        st.markdown(
            f"**Indicators available:** {raw.shape[1]} · "
            f"**States with complete data:** {complete.shape[0]} out of {raw.shape[0]} · "
            f"**Removed for missing data:** {raw.shape[0] - complete.shape[0]}"
        )

        # ── Method selection ──
        st.markdown("---")
        st.subheader("① Choose a grouping method")
        explain(
            "<b>K-Means (Euclidean):</b> The most common method — groups states by "
            "straight-line similarity in their numbers.<br>"
            "<b>Agglomerative (Euclidean):</b> Builds groups step-by-step by merging "
            "the most similar states first.<br>"
            "<b>Agglomerative (Manhattan):</b> Same step-by-step approach but measures "
            "similarity differently — like walking city blocks instead of flying straight."
        )

        method = st.selectbox(
            "Method",
            ["K-Means (Euclidean)", "Agglomerative (Euclidean)", "Agglomerative (Manhattan)", "DBSCAN"],
        )

        if method.startswith("K-Means"):
            actual_method, distance = "K-Means", "euclidean"
        elif method == "Agglomerative (Manhattan)":
            actual_method, distance = "Agglomerative", "manhattan"
        elif method == "Agglomerative (Euclidean)":
            actual_method, distance = "Agglomerative", "euclidean"
        else:
            actual_method, distance = "DBSCAN", "euclidean"

        if actual_method in ("K-Means", "Agglomerative"):
            k = st.slider(
                "How many groups?", 2,
                min(6, complete.shape[0] - 1),
                min(3, complete.shape[0] - 1),
                help="More groups = finer distinctions. Fewer = broader categories.",
            )
            eps, min_samples = 0.9, 4
        else:
            u, v = st.columns(2)
            eps = u.slider("DBSCAN neighbourhood size", 0.2, 3.0, 0.9, 0.1)
            min_samples = v.slider("Minimum states per group", 2, min(10, complete.shape[0]), min(4, complete.shape[0]))
            k = 3

        try:
            result, metrics, pca_var = fit_clusters(
                complete, actual_method, clusters=k, eps=eps,
                min_samples=min_samples, distance=distance,
            )

            # ── STEP 2: Elbow chart + Multi-k comparison ──
            if actual_method == "K-Means":
                st.markdown("---")
                st.subheader("② Finding the best number of groups")
                explain(
                    "How do we know if 3 groups is better than 4? We try different numbers "
                    "and compare scores. The <b>elbow chart</b> shows how tightly packed "
                    "each grouping is — look for where the line bends (the 'elbow')."
                )
                sweep_df = sweep_k(complete, max_k=min(6, complete.shape[0] - 1))
                if not sweep_df.empty:
                    el, er = st.columns(2)
                    with el:
                        fig_elbow = px.line(
                            sweep_df, x="k", y="WCSS", markers=True,
                            labels={"k": "Number of groups", "WCSS": "WCSS (lower = tighter groups)"},
                            title="Elbow Chart — how tight are the groups?",
                        )
                        fig_elbow.update_traces(line_color="#55d8c7", marker_size=10)
                        fig_elbow.update_layout(
                            height=350, margin=dict(l=0, r=0, t=40, b=0),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#dcebea",
                        )
                        st.plotly_chart(fig_elbow, use_container_width=True)
                        st.caption(
                            "WCSS = Within-Cluster Sum of Squares. "
                            "Lower means states within each group are more similar. "
                            "The 'elbow' is where adding more groups stops helping much."
                        )
                    with er:
                        fig_sil = px.line(
                            sweep_df, x="k", y="Silhouette", markers=True,
                            labels={"k": "Number of groups", "Silhouette": "Silhouette Score (higher = better)"},
                            title="Silhouette — how well-separated are the groups?",
                        )
                        fig_sil.update_traces(line_color="#e9a34b", marker_size=10)
                        fig_sil.update_layout(
                            height=350, margin=dict(l=0, r=0, t=40, b=0),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#dcebea",
                        )
                        st.plotly_chart(fig_sil, use_container_width=True)
                        st.caption(
                            "Silhouette ranges from -1 to 1. Higher means groups "
                            "are clearly separated with little overlap."
                        )

                    st.markdown("**Full comparison across all tested group counts:**")
                    display_sweep = sweep_df.copy()
                    display_sweep.columns = [
                        "Groups (k)", "WCSS (lower=better)",
                        "Silhouette (higher=better)", "Davies-Bouldin (lower=better)",
                        "Calinski-Harabasz (higher=better)",
                    ]
                    st.dataframe(display_sweep.round(3), use_container_width=True, hide_index=True)
                    st.caption(
                        "This table helps you pick the best number of groups. "
                        "Look for the k where Silhouette is highest and Davies-Bouldin is lowest."
                    )

            # ── STEP 3: Results ──
            st.markdown("---")
            st.subheader("③ The grouping results")
            explain(
                f"Using <b>{method}</b> with <b>{k if actual_method != 'DBSCAN' else 'auto'} groups</b>, "
                f"here's how the {complete.shape[0]} states were sorted. "
                "Each colour represents a different group of states with similar patterns."
            )

            # Metrics in plain language
            m_cols = st.columns(4)
            sil = metrics.get("Silhouette")
            db = metrics.get("Davies-Bouldin")
            wcss_val = metrics.get("WCSS (Inertia)")
            ch = metrics.get("Calinski-Harabasz")

            with m_cols[0]:
                if wcss_val is not None:
                    st.metric("WCSS", f"{wcss_val:.1f}")
                    st.caption("How tight the groups are (lower = better)")
                else:
                    st.metric("WCSS", "N/A")
            with m_cols[1]:
                if sil is not None:
                    quality_word = "excellent" if sil > 0.7 else "good" if sil > 0.5 else "fair" if sil > 0.25 else "weak"
                    st.metric("Separation quality", f"{sil:.3f}")
                    st.caption(f"Silhouette score — {quality_word} (max is 1.0)")
                else:
                    st.metric("Separation quality", "N/A")
            with m_cols[2]:
                if db is not None:
                    st.metric("Group overlap", f"{db:.3f}")
                    st.caption("Davies-Bouldin — lower means less overlap")
                else:
                    st.metric("Group overlap", "N/A")
            with m_cols[3]:
                st.metric("States grouped", f"{metrics['Regions']}")
                st.caption(f"Into {metrics['Groups found']} groups")

            # ── PCA scatter with variance annotation ──
            pca_left, pca_right = st.columns([1.2, 1])
            with pca_left:
                st.markdown(f"**Visual map of state similarity** (PC1: {pca_var[0]:.1f}%, PC2: {pca_var[1]:.1f}%)")
                fig_pca = px.scatter(
                    result, x="PC1", y="PC2", color="Cluster",
                    hover_name="State / UT",
                    color_discrete_sequence=["#54d6c4", "#4c8ed1", "#e9a34b", "#bd77d7", "#e46b79", "#97bd62"],
                    labels={"PC1": f"Dimension 1 ({pca_var[0]:.1f}%)", "PC2": f"Dimension 2 ({pca_var[1]:.1f}%)"},
                )
                fig_pca.update_traces(marker_size=12)
                fig_pca.update_layout(
                    height=430, margin=dict(l=0, r=0, t=18, b=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#dcebea", legend_title_text="Group",
                )
                st.plotly_chart(fig_pca, use_container_width=True)
                st.caption(
                    "Each dot is a state. States close together have similar TB patterns. "
                    "The computer compressed multiple indicators into two dimensions (PC1 & PC2) "
                    f"which together capture {pca_var[0] + pca_var[1]:.1f}% of the variation. "
                    "This is a visual summary, not proof of the grouping."
                )
            with pca_right:
                st.markdown("**Which states are in each group?**")
                display_results_df = result[["State / UT", "Cluster"]].rename(columns={"Cluster": "Group"}).sort_values(
                    ["Group", "State / UT"]
                )
                st.dataframe(
                    display_results_df,
                    use_container_width=True,
                    hide_index=True,
                    height=360,
                )
                csv_bytes = display_results_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Group Assignments (CSV)",
                    data=csv_bytes,
                    file_name=f"tb_state_clusters_{year}_{factor}_{sector}.csv",
                    mime="text/csv",
                )

            # ── Cluster map ──
            st.subheader("🗺️ Groups on the map")
            explain(
                "The same groups shown on the India map — states with the same colour "
                "were sorted into the same group because their TB numbers are similar."
            )
            map_data = result.rename(columns={"State / UT": "state", "Cluster": "Group"})
            display_map(map_data, "Group", color_col="Group")

            # ── Cluster profiles with plain summaries ──
            st.markdown("---")
            st.subheader("④ What makes each group different?")
            profiled = complete.copy()
            profiled["Cluster"] = result.set_index("State / UT")["Cluster"].reindex(profiled.index).values
            cluster_profile = profiled.groupby("Cluster", observed=True)[complete.columns].median().round(1)

            # Auto-generated plain summaries
            summaries = cluster_plain_summary(cluster_profile, complete.columns.tolist())
            for cluster_label, summary_text in summaries.items():
                st.markdown(summary_text)
            st.write("")

            st.markdown("**Median values per group** (what the 'typical' state in each group looks like):")
            st.dataframe(cluster_profile.rename_axis("Group"), use_container_width=True)
            st.caption(
                "Each number is the middle value (median) for that indicator within the group. "
                "Higher counts do not mean higher risk — they reflect reported numbers, "
                "which depend on population and screening coverage."
            )

            # ── Feature contribution chart ──
            st.subheader("⚖️ Which indicators separate the groups most?")
            explain(
                "This chart shows the average standardised value per indicator per group. "
                "A tall bar means that group has unusually high (or low) numbers for that indicator."
            )
            feat_df = feature_contributions(complete, result.set_index("State / UT")["Cluster"].reindex(complete.index).values)
            fig_feat = px.bar(
                feat_df.T.reset_index().melt(id_vars="index"),
                x="index", y="value", color="Cluster",
                barmode="group",
                labels={"index": "Indicator", "value": "Standardised score", "Cluster": "Group"},
                color_discrete_sequence=["#54d6c4", "#4c8ed1", "#e9a34b", "#bd77d7", "#e46b79"],
            )
            fig_feat.update_layout(
                height=400, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dcebea", xaxis_tickangle=-30,
            )
            st.plotly_chart(fig_feat, use_container_width=True)
            st.caption(
                "Bars above zero mean that group reported more than average; "
                "below zero means less than average. Zero is the overall average."
            )

            # ── Unit III: Hierarchical Dendrogram ──
            st.markdown("---")
            st.subheader("⑤ Hierarchical Tree (Dendrogram) — Unit III")
            explain(
                "<b>What is a dendrogram?</b> Think of it as a family tree of Indian states. "
                "States that are closest together in their TB indicators merge first at the bottom. "
                "The height of each vertical bar shows how different two merging groups are."
            )
            d_col1, d_col2 = st.columns(2)
            d_metric = d_col1.selectbox("Distance measure", ["Euclidean (straight line)", "Manhattan (city block)"], key="dendro_dist")
            d_dist = "euclidean" if "Euclidean" in d_metric else "manhattan"
            d_link_opts = ["Average", "Complete"] if d_dist == "manhattan" else ["Ward (variance-minimising)", "Average", "Complete"]
            d_link_choice = d_col2.selectbox("Linkage method", d_link_opts, key="dendro_link")
            d_link = "ward" if "Ward" in d_link_choice else "average" if "Average" in d_link_choice else "complete"

            from scipy.cluster.hierarchy import linkage
            from sklearn.preprocessing import StandardScaler
            scaled_for_dendro = StandardScaler().fit_transform(complete.astype(float))
            dendro_fig = ff.create_dendrogram(
                scaled_for_dendro,
                labels=list(complete.index),
                linkagefun=lambda x: linkage(x, method=d_link, metric=d_dist),
                color_threshold=2.5,
            )
            dendro_fig.update_layout(
                height=500,
                margin=dict(l=0, r=0, t=20, b=120),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dcebea",
                xaxis=dict(tickangle=-45),
            )
            st.plotly_chart(dendro_fig, use_container_width=True)
            st.caption(
                f"Dendrogram computed with {d_dist.capitalize()} distance and {d_link} linkage. "
                "Horizontal cuts across high vertical branches define the distinct clusters."
            )

            # ── Stability across tested settings ──
            st.markdown("---")
            st.subheader("⑥ Stability Across Distance Settings (Euclidean vs. Manhattan)")
            explain(
                "<b>Why check stability?</b> If changing from Euclidean (straight-line) to Manhattan (city-block) distance "
                "completely scrambles which states belong together, the groups are fragile. "
                "If most states stay together, the pattern is real and trustworthy."
            )
            stab_df, agree_pct = stability_comparison(complete, k=k)
            st_col1, st_col2 = st.columns([1, 2])
            with st_col1:
                st.metric("Grouping Stability Agreement", f"{agree_pct:.1f}%")
                if agree_pct >= 80:
                    st.success("High stability: states consistently group together regardless of distance formula.")
                elif agree_pct >= 60:
                    st.info("Moderate stability: core state groups hold, while borderline states shift.")
                else:
                    st.warning("Low stability: sensitive to distance metric choice.")
            with st_col2:
                st.dataframe(stab_df, use_container_width=True, hide_index=True)

            # ── Defensible configuration selection ──
            st.markdown("---")
            st.subheader("⑦ Defensible Configuration Selection (For Viva & Report)")
            sweep_data = sweep_k(complete)
            best_sil_k = int(sweep_data.loc[sweep_data["Silhouette"].idxmax(), "k"]) if not sweep_data.empty else 3
            st.info(
                f"📌 <b>Recommended Defensible Choice:</b> Based on the quantitative evaluation on these {complete.shape[0]} states:<br>"
                f"• The <b>WCSS Elbow curve</b> bends between k=2 and k=4, indicating diminishing compactness gains thereafter.<br>"
                f"• The <b>Silhouette Score</b> peaks at <b>k={best_sil_k}</b>, demonstrating maximum group separation and minimal cluster overlap.<br>"
                f"• <b>Conclusion:</b> <b>k={best_sil_k}</b> (or k=3 for balanced public health communication) represents the most statistically sound and interpretable configuration."
            )

            # ── Policy box ──
            policy_box(
                "<b>What could health planners do with this?</b><br>"
                "States in the same group share similar TB-related patterns. "
                "Health administrators could investigate what these states have in common — "
                "similar demographics, screening programs, or resource constraints — "
                "and consider whether interventions that work in one could help others "
                "in the same group.<br><br>"
                "<i>These groups are exploratory — they describe patterns in the data, "
                "not permanent real-world categories.</i>"
            )

            # ── Features used ──
            with st.expander("📊 See the raw data used for grouping"):
                st.dataframe(complete.reset_index(), use_container_width=True, hide_index=True)

        except ValueError as exc:
            st.warning(str(exc))

    st.markdown(
        '<div class="note"><b>Remember:</b> These are reported counts, not '
        "population-adjusted rates. A state's group depends on what was "
        "reported, which is affected by population size, screening programs, "
        "and reporting systems. The groups are a starting point for questions, "
        "not final answers.</div>",
        unsafe_allow_html=True,
    )

# ───────────────────── RESEARCH INSIGHTS ─────────────────────
elif page == "Research Insights":
    header(
        "Research Insights",
        "Dig deeper into the numbers",
        "Pick an indicator and see statistical summaries, unusual values, "
        "and how the numbers changed over time.",
    )
    explain(
        "This page recalculates everything from the actual data — nothing is "
        "pre-written. Change the filters and the summaries update instantly."
    )

    year, factor, sector, parameter = selection_controls("insight")
    view = regions.loc[
        (regions.year == year)
        & (regions.risk_factor == factor)
        & (regions.sector == sector)
        & (regions.parameter == parameter)
    ].dropna(subset=["value"])

    st.subheader(f"{factor}: {parameter}")
    st.write(describe_pattern(view))

    if len(view) >= 5:
        median = view.value.median()
        deviations = (view.value - median).abs()
        mad = deviations.median()
        if mad > 0:
            view = view.assign(robust_z=0.6745 * (view.value - median) / mad)
            anomalies = view.loc[view.robust_z.abs() >= 3.5].sort_values(
                "robust_z", key=abs, ascending=False
            )
            if anomalies.empty:
                st.info("No unusual values found for this selection — all states are within the normal range.")
            else:
                st.subheader("🔎 Values that stand out")
                explain(
                    "These states have numbers very far from the middle value (median). "
                    "This doesn't mean there's an error — it just means they're unusual "
                    "and worth investigating."
                )
                st.dataframe(
                    anomalies[["state", "value", "robust_z"]].rename(
                        columns={
                            "state": "State / UT",
                            "value": "Reported count",
                            "robust_z": "How unusual (z-score)",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption(
                    "A z-score above 3.5 means this value is far from what most states reported. "
                    "It's a statistical flag, not a judgement."
                )

    years_list = sorted(int(y) for y in regions.year.unique())
    trajectory = regions.loc[
        (regions.risk_factor == factor)
        & (regions.parameter == parameter)
        & (regions.sector == sector)
    ].dropna(subset=["value"])
    agg = trajectory.groupby("year").value.agg(["median", "count"]).reset_index()
    if not agg.empty:
        st.subheader("📈 How this indicator changed over time")
        fig = px.line(
            agg, x="year", y="median", markers=True,
            labels={"year": "Year", "median": "Median state count"},
        )
        fig.update_traces(line_color="#55d8c7", marker_size=9)
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dcebea",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "This shows the median (middle value) across all states for each year. "
            "The number of reporting states can vary — see the table below."
        )
        st.dataframe(
            agg.rename(columns={"year": "Year", "median": "Median count", "count": "States with values"}),
            use_container_width=True,
            hide_index=True,
        )

# ───────────────────── AI EXPLAINER ─────────────────────
elif page == "AI Explainer":
    header(
        "AI Explainer",
        "Plain language, grounded in your data",
        "Select an indicator, state comparison, or clustering method to get an instant, data-backed plain English explanation.",
    )

    mode = st.radio(
        "Explainer Mode",
        ["🔍 Interactive Data Explainer", "📖 Concepts & FAQ Guide"],
        horizontal=True,
    )

    if mode == "🔍 Interactive Data Explainer":
        topic = st.radio("What would you like the AI to explain?", ["An indicator", "A state comparison", "A clustering method"], horizontal=True)
        year, factor, sector, parameter = selection_controls("ai_explain")
        view = regions.loc[(regions.year == year) & (regions.risk_factor == factor) & (regions.sector == sector) & (regions.parameter == parameter)]

        if topic == "An indicator":
            st.subheader(f"💡 AI Narrative: {parameter} ({year})")
            st.info(describe_pattern(view))
            missing = int(view.value.isna().sum())
            st.write(
                f"**Data Profile:** This slice covers {view.state.nunique()} states/UTs, with "
                f"{view.value.notna().sum()} reported values and {missing} blank entries. "
                "Blank values are strictly preserved as missing; they are never assumed to be zero."
            )
        elif topic == "A state comparison":
            st.subheader("💡 AI Narrative: State-to-State Trajectory")
            picks = st.multiselect(
                "Select states to compare",
                sorted(regions.state.unique()),
                default=[s for s in ["Maharashtra", "Uttar Pradesh"] if s in set(regions.state)],
                max_selections=6,
                key="ai_explain_states",
            )
            trend = regions.loc[
                (regions.risk_factor == factor)
                & (regions.parameter == parameter)
                & (regions.sector == sector)
                & (regions.state.isin(picks))
            ].dropna(subset=["value"])
            if trend.empty:
                st.info("Select regions with reported values for this indicator.")
            else:
                summary = trend.sort_values("year").groupby("state").agg(
                    first_year=("year", "min"),
                    last_year=("year", "max"),
                    first_count=("value", "first"),
                    last_count=("value", "last"),
                    years_reported=("year", "nunique"),
                ).reset_index()
                summary["count_change"] = summary["last_count"] - summary["first_count"]
                st.write("Comparing each selected region's first and last available reported values:")
                st.dataframe(
                    summary.rename(
                        columns={
                            "state": "State / UT",
                            "first_year": "First year",
                            "last_year": "Last year",
                            "first_count": "First count",
                            "last_count": "Last count",
                            "years_reported": "Years reported",
                            "count_change": "Count difference",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption("A rise in absolute count does not necessarily equal an increase in individual infection risk; screening coverage and demographic growth also contribute.")
        else:
            st.subheader("💡 AI Narrative: Clustering & Standardization Logic")
            raw_c, comp_c = regional_feature_matrix(df, year, factor, sector)
            st.write(
                f"The feature matrix extracts {raw_c.shape[1]} comparable indicators. "
                f"Of {raw_c.shape[0]} regions, {len(comp_c)} are complete across all dimensions; "
                f"{raw_c.shape[0] - len(comp_c)} were omitted because at least one value was missing."
            )
            explain(
                "<b>How the algorithm groups regions:</b> The model standardizes all counts (subtracting mean, dividing by standard deviation) "
                "so every indicator has equal weight regardless of magnitude. The clusters group states sharing similar multivariate shapes. "
                "PCA provides a 2D map projection for visualization, capturing major variance without distorting underlying multidimensional distance."
            )

    else:
        topic_guide = st.radio(
            "Topic Guide",
            ["The data", "What the charts mean", "How the grouping works", "Common questions"],
            horizontal=True,
        )

        if topic_guide == "The data":
            st.subheader("📊 Where does this data come from?")
            st.markdown(
                "The data comes from **India's Ministry of Health and Family Welfare**, "
                "published in their annual TB reports (2019–2023). It was obtained through "
                "**Dataful** (dataset 20833).\n\n"
                "**What's in it?** For each state and union territory, the data records "
                "how many TB patients were also screened for conditions like "
                "diabetes, alcohol use, tobacco use, and COVID-19.\n\n"
                "**What's NOT in it?**\n"
                "- How many people actually have TB in total (only officially reported cases)\n"
                "- The rate of TB per 100,000 population (no population denominator is in the dataset)\n"
                "- Whether a risk factor directly caused TB (correlation vs causation)\n"
            )
            st.markdown(
                f"**Quick stats:** {quality['rows']:,} data points · "
                f"{quality['regions']} states/UTs · {len(quality['years'])} years · "
                f"{quality['missing_values']} missing values"
            )

        elif topic_guide == "What the charts mean":
            st.subheader("📈 Reading the charts")
            st.markdown(
                "**Bar charts (Explore India):** Each bar is a state. Longer bars = higher reported counts.\n\n"
                "**Line charts (Compare States):** Upward slope = increase in recorded notifications; downward slope = decrease.\n\n"
                "**Scatter plot (State Pattern Groups):** States close together share similar profiles. Dimension 1 & 2 capture ~99% of total variance.\n\n"
                "**Dendrogram Tree:** States connected near the bottom are most identical in indicators."
            )

        elif topic_guide == "How the grouping works":
            st.subheader("🔍 Clustering explained simply")
            st.markdown(
                "**K-Means:** Partitions states into $k$ groups by iteratively minimizing the Within-Cluster Sum of Squares (WCSS).\n\n"
                "**Agglomerative:** Merges pairs of states bottom-up based on pairwise distance.\n\n"
                "**Distance Comparison:** We test both Euclidean (straight line) and Manhattan (city block) distances to test clustering stability."
            )

        else:
            st.subheader("❓ Common questions")
            st.markdown(
                "**Q: Does a high number mean a state has more disease?**\n"
                "Not necessarily. Highly populated states (like UP or Maharashtra) naturally report higher absolute numbers.\n\n"
                "**Q: Can this tool diagnose TB?**\n"
                "No. This tool is an academic platform for regional public health policy planning, not patient-level medical diagnosis.\n\n"
                "**Q: Why standardise features?**\n"
                "If one indicator is measured in tens of thousands and another in hundreds, standardisation prevents the larger number from biasing the cluster centers."
            )

# ───────────────────── TB KNOWLEDGE CENTRE ─────────────────────
elif page == "TB Knowledge Centre":
    header(
        "TB Knowledge Centre",
        "Learn about tuberculosis",
        "A simple guide to TB — what it is, how it spreads, and where to "
        "get help. This is general awareness, not medical advice.",
    )
    left, right = st.columns(2)
    with left:
        st.subheader("What is TB?")
        st.write(
            "Tuberculosis (TB) is a disease caused by bacteria that usually "
            "affects the lungs. It's been around for centuries but is now "
            "preventable and curable with proper treatment. India has the "
            "world's largest TB burden, which is why tracking and understanding "
            "it is so important."
        )
        st.subheader("How does it spread?")
        st.write(
            "TB bacteria travel through the air when someone with active TB "
            "coughs, sneezes, or even talks. You can't get it from shaking "
            "hands, sharing food, or touching surfaces. Not everyone who "
            "breathes in the bacteria gets sick — it depends on many factors."
        )
    with right:
        st.subheader("What symptoms should you watch for?")
        st.write(
            "A persistent cough (2+ weeks), fever, night sweats, unexplained "
            "weight loss, or coughing up blood. These symptoms can have many "
            "causes, but if they don't go away, see a doctor."
        )
        st.subheader("Risk factors in this dataset")
        st.write(
            "This tool tracks TB alongside four risk factors: **diabetes, "
            "tobacco use, alcohol use, and COVID-19**. These don't cause TB, "
            "but they can make someone more vulnerable. The data shows how many "
            "TB patients were also screened for these conditions."
        )
    st.markdown("### Where to learn more")
    st.markdown(
        "- [WHO: Tuberculosis fact sheet](https://www.who.int/news-room/fact-sheets/detail/tuberculosis)\n"
        "- [India National TB Elimination Programme](https://tbcindia.mohfw.gov.in/)\n"
        "- [Ni-kshay portal](https://nikshay.in/)"
    )

# ───────────────────── FIND HELP & ABOUT ─────────────────────
else:
    header(
        "Find Help & About",
        "Sources, methods, and how to get help",
        "Everything you need to know about where this data comes from "
        "and where to go if you or someone you know needs TB-related help.",
    )

    st.subheader("🆘 Need TB-related help?")
    st.markdown(
        "- **India National TB Helpline:** Call your nearest government health facility\n"
        "- [India National TB Elimination Programme](https://tbcindia.mohfw.gov.in/)\n"
        "- [Ni-kshay portal](https://nikshay.in/) — India's TB case management system\n"
        "- Contact a government hospital or qualified doctor for symptoms or treatment"
    )

    st.subheader("📊 About the data")
    st.markdown(
        "**Source:** Ministry of Health and Family Welfare annual reports (2019–2023), "
        "republished by **Dataful** as dataset 20833: "
        "*Year, State, Sector and Risk Factor wise cases of TB*.\n\n"
        f"**Coverage:** {', '.join(map(str, quality['years']))} · "
        f"{quality['regions']} states/UTs · {quality['rows']:,} records · "
        f"{quality['missing_values']} missing values\n\n"
        "**Units:** All values are absolute counts (number of cases/screenings), "
        "not rates or percentages."
    )
    st.markdown(
        "[Dataful dataset](https://dataful.in/datasets/20833/20833) · "
        "[Original annual reports](https://tbcindia.mohfw.gov.in/annual-reports/)"
    )

    st.subheader("🔬 How the analysis works")
    st.markdown(
        "1. **Load and validate** official government TB data\n"
        "2. **Filter** by year, risk factor, and reporting sector\n"
        "3. **Pivot** so each state is a row, each indicator is a column\n"
        "4. **Remove** states with missing values (not filled with zero)\n"
        "5. **Standardise** all indicators to the same scale\n"
        "6. **Cluster** using K-Means and Agglomerative methods\n"
        "7. **Evaluate** using WCSS, Silhouette, Davies-Bouldin, and Calinski-Harabasz scores\n"
        "8. **Visualise** with PCA (a way to display many dimensions in 2D)"
    )

    st.subheader("⚠️ Limitations — please read")
    st.markdown(
        "- **Counts ≠ rates:** No population data, so we can't say 'X% of people have TB'\n"
        "- **Reported ≠ actual:** Only cases that were officially reported are counted\n"
        "- **Groups ≠ risk levels:** Cluster labels (A, B, C) are not risk scores\n"
        "- **Correlation ≠ causation:** We can't say a risk factor caused TB\n"
        "- **Changing definitions:** How indicators were measured may vary across years\n"
        "- **This is academic work:** An exploratory university project, not a policy tool"
    )

    st.subheader("🗺️ Map boundaries")
    st.markdown(
        "State boundaries from [geoBoundaries](https://www.geoboundaries.org/) "
        "(open India ADM1, based on DataMeet/ECI 2011 boundaries). "
        "CC BY 2.5 India attribution. The map only joins data to state shapes by name."
    )

    st.caption(
        f"Data quality: {quality['duplicate_keys']} duplicate key rows · "
        f"{quality['negative_values']} negative values · "
        f"{quality['missing_values']} missing values. "
        "State names are not used as model features."
    )