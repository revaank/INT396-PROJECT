"""Patch build_upgraded_preview.py with the 3 requested landing page improvements:
1. Hero tagline below AeroTB brand
2. Map legend updated labels for Group Similar States
3. Leaderboard column header with unit label 'Patients screened (2023, Diabetes)'
"""
from pathlib import Path

fp = Path(r"c:\Users\LENOVO\OneDrive\Desktop\int 396 project\scripts\build_upgraded_preview.py")
src = fp.read_text(encoding="utf-8")

# ── 1. Hero Tagline in .brand-bar CSS & HTML ────────────────────────────────
OLD_BRAND_CSS = """  .brand-sub {{
    font-size: 0.65rem;
    color: #64748b;
    font-weight: 700;
    letter-spacing: 0.08em;
  }}"""

NEW_BRAND_CSS = """  .brand-sub {{
    font-size: 0.65rem;
    color: #64748b;
    font-weight: 700;
    letter-spacing: 0.08em;
  }}
  .brand-tagline {{
    font-size: 0.68rem;
    color: #94a3b8;
    font-weight: 500;
    margin-top: 2px;
    letter-spacing: 0.01em;
    max-width: 540px;
    line-height: 1.35;
  }}"""

assert OLD_BRAND_CSS in src, "OLD_BRAND_CSS not found"
src = src.replace(OLD_BRAND_CSS, NEW_BRAND_CSS, 1)

OLD_BRAND_BAR_CSS = """  .brand-bar {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(14, 18, 26, 0.88);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    padding: 7px 18px;
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
    pointer-events: auto;
  }}"""

NEW_BRAND_BAR_CSS = """  .brand-bar {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(14, 18, 26, 0.88);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    padding: 8px 18px;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
    pointer-events: auto;
  }}"""

assert OLD_BRAND_BAR_CSS in src, "OLD_BRAND_BAR_CSS not found"
src = src.replace(OLD_BRAND_BAR_CSS, NEW_BRAND_BAR_CSS, 1)

OLD_BRAND_HTML = """    <div class="brand-bar">
      <div class="brand-logo">◈</div>
      <div>
        <div class="brand-name">AeroTB</div>
      </div>
      <span class="brand-sub">/ INDIA NATIONAL INTELLIGENCE</span>
    </div>"""

NEW_BRAND_HTML = """    <div class="brand-bar">
      <div class="brand-logo">◈</div>
      <div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="brand-name">AeroTB</span>
          <span class="brand-sub">/ INDIA REGIONAL INTELLIGENCE</span>
        </div>
        <div class="brand-tagline">This tool helps you explore how TB spread differently across India's 36 states, using AI to find hidden patterns.</div>
      </div>
    </div>"""

assert OLD_BRAND_HTML in src, "OLD_BRAND_HTML not found"
src = src.replace(OLD_BRAND_HTML, NEW_BRAND_HTML, 1)

# ── 2. Map Legend Updates for Group Similar States ─────────────────────────
OLD_LEGEND_JS = """          <span class="legend-item"><span class="legend-swatch" style="background:#38bdf8; box-shadow:0 0 6px rgba(56,189,248,0.5);"></span>Team B: Mega-Epicenters (2)</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#818cf8;"></span>Team C: High-Burden States (13)</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#222a3d; border:1px solid rgba(255,255,255,0.2);"></span>Team A: Baseline/UTs (21)</span>"""

NEW_LEGEND_JS = """          <span class="legend-item"><span class="legend-swatch" style="background:#38bdf8; box-shadow:0 0 6px rgba(56,189,248,0.5);"></span>Team B: Outlier scale (2 states)</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#818cf8;"></span>Team C: High burden (13 states)</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#222a3d; border:1px solid rgba(255,255,255,0.2);"></span>Team A: Lower burden (21 states)</span>"""

assert OLD_LEGEND_JS in src, "OLD_LEGEND_JS not found"
src = src.replace(OLD_LEGEND_JS, NEW_LEGEND_JS, 1)

# ── 3. Leaderboard Unit Header CSS & HTML ──────────────────────────────────
OLD_LB_CSS = "  .state-list {{"
NEW_LB_CSS = """  .lb-col-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 10px 6px;
    font-size: 0.58rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 4px;
  }}
  .lb-col-header span:last-child {{
    text-align: right;
    color: #38bdf8;
  }}
  .state-list {{"""

assert OLD_LB_CSS in src, "OLD_LB_CSS not found"
src = src.replace(OLD_LB_CSS, NEW_LB_CSS, 1)

OLD_LB_HTML = """        <div class="search-wrap">
          <input type="text" class="search-input" id="state-search" placeholder="🔍 Search any state...">
        </div>

        <div class="state-list" id="leader-list">"""

NEW_LB_HTML = """        <div class="search-wrap">
          <input type="text" class="search-input" id="state-search" placeholder="🔍 Search any state...">
        </div>

        <div class="lb-col-header">
          <span>Rank &amp; State</span>
          <span>Patients screened (2023, Diabetes)</span>
        </div>

        <div class="state-list" id="leader-list">"""

assert OLD_LB_HTML in src, "OLD_LB_HTML not found"
src = src.replace(OLD_LB_HTML, NEW_LB_HTML, 1)

fp.write_text(src, encoding="utf-8")
print("SUCCESS: scripts/build_upgraded_preview.py updated cleanly!")
