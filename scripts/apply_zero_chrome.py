from pathlib import Path

target = Path(r"C:\Users\LENOVO\Desktop\int396 tb project\app\main.py")
code = target.read_text(encoding="utf-8")

# 1. Update navigation to sync with query_params
old_nav = '''pages = [
    "Home",
    "Explore India",
    "Compare States",
    "State Pattern Groups",
    "Research Insights",
    "AI Explainer",
    "TB Knowledge Centre",
    "Find Help & About",
]
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
    page = st.radio("Navigation", pages, label_visibility="collapsed")'''

new_nav = '''pages = [
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
    page = st.radio("Navigation", pages, index=def_idx, label_visibility="collapsed")'''

if old_nav in code:
    code = code.replace(old_nav, new_nav, 1)
    print("Updated navigation with query_params resolution")
else:
    print("old_nav not matched exactly")

# 2. Update Home view to hide Streamlit chrome and render full bleed
old_home_block = '''if page == "Home":
    import streamlit.components.v1 as components
    preview_file = ROOT / "preview.html"
    if preview_file.exists():
        html_code = preview_file.read_text(encoding="utf-8")
        components.html(html_code, height=3200, scrolling=False)
    else:
        st.error("preview.html not found")'''

new_home_block = '''if page == "Home":
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
          background: #050811 !important;
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
          border: none !important;
          width: 100vw !important;
          margin: 0 !important;
          padding: 0 !important;
          display: block !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    import streamlit.components.v1 as components
    preview_file = ROOT / "preview.html"
    if preview_file.exists():
        html_code = preview_file.read_text(encoding="utf-8")
        components.html(html_code, height=3400, scrolling=False)
    else:
        st.error("preview.html not found")
else:
    # On analytical sub-pages, show return button at top
    st.markdown(
        """
        <a href="/?page=Home" style="display:inline-flex; align-items:center; gap:8px; background:rgba(0,242,254,0.12); border:1px solid rgba(0,242,254,0.3); border-radius:9999px; padding:7px 18px; color:#00f2fe; text-decoration:none; font-weight:700; font-size:0.82rem; margin-bottom:18px;">
          ← Return to AeroTB Command Center
        </a>
        """,
        unsafe_allow_html=True,
    )'''

if old_home_block in code:
    code = code.replace(old_home_block, new_home_block, 1)
    print("Updated Home view with zero-chrome CSS and return button")
else:
    print("old_home_block not matched exactly")

target.write_text(code, encoding="utf-8")
print("Finished writing app/main.py")
