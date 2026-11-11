from pathlib import Path

target = Path(r"C:\Users\LENOVO\Desktop\int396 tb project\app\main.py")
code = target.read_text(encoding="utf-8")

old_block = '''if page == "Home":
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

new_block = '''# On analytical sub-pages, show return button at top
if page != "Home":
    st.markdown(
        """
        <a href="/?page=Home" style="display:inline-flex; align-items:center; gap:8px; background:rgba(0,242,254,0.12); border:1px solid rgba(0,242,254,0.3); border-radius:9999px; padding:7px 18px; color:#00f2fe; text-decoration:none; font-weight:700; font-size:0.82rem; margin-bottom:18px;">
          ← Return to AeroTB Command Center
        </a>
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
        st.error("preview.html not found")'''

assert old_block in code, "old_block not found"
code = code.replace(old_block, new_block, 1)
target.write_text(code, encoding="utf-8")
print("Fixed if/elif syntax in app/main.py!")
