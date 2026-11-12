"""Fix title description interference:
1. Restore .brand-bar to a sleek, compact single-line capsule (zero overlap with header actions or left column boxes).
2. Place the hero tagline cleanly inside col-center as an elegant pill above the layer buttons, so it stays in normal document flow and never interferes with any card.
"""
from pathlib import Path

fp = Path(r"c:\Users\LENOVO\OneDrive\Desktop\int 396 project\scripts\build_upgraded_preview.py")
src = fp.read_text(encoding="utf-8")

# ── 1. Revert .brand-bar and .brand-tagline CSS ──────────────────────────────
OLD_BRAND_CSS = """  .brand-bar {{
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
  }}
  .brand-logo {{
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%);
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 13px;
    color: #ffffff;
  }}
  .brand-name {{
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: #ffffff;
  }}
  .brand-sub {{
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

NEW_BRAND_CSS = """  .brand-bar {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(14, 18, 26, 0.88);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    padding: 7px 18px;
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
    pointer-events: auto;
  }}
  .brand-logo {{
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%);
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 13px;
    color: #ffffff;
  }}
  .brand-name {{
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: #ffffff;
  }}
  .brand-sub {{
    font-size: 0.65rem;
    color: #64748b;
    font-weight: 700;
    letter-spacing: 0.08em;
  }}
  .hero-tagline-bar {{
    font-size: 0.78rem;
    color: #94a3b8;
    text-align: center;
    max-width: 620px;
    line-height: 1.35;
    margin-bottom: 10px;
    background: rgba(14, 18, 26, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px 16px;
    border-radius: 9999px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  }}"""

assert OLD_BRAND_CSS in src, "OLD_BRAND_CSS not found"
src = src.replace(OLD_BRAND_CSS, NEW_BRAND_CSS, 1)

# ── 2. Revert .brand-bar HTML to sleek single line ───────────────────────────
OLD_BRAND_HTML = """    <div class="brand-bar">
      <div class="brand-logo">◈</div>
      <div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="brand-name">AeroTB</span>
          <span class="brand-sub">/ INDIA REGIONAL INTELLIGENCE</span>
        </div>
        <div class="brand-tagline">This tool helps you explore how TB spread differently across India's 36 states, using AI to find hidden patterns.</div>
      </div>
    </div>"""

NEW_BRAND_HTML = """    <div class="brand-bar">
      <div class="brand-logo">◈</div>
      <div class="brand-name">AeroTB</div>
      <span class="brand-sub">/ INDIA REGIONAL INTELLIGENCE</span>
    </div>"""

assert OLD_BRAND_HTML in src, "OLD_BRAND_HTML not found"
src = src.replace(OLD_BRAND_HTML, NEW_BRAND_HTML, 1)

# ── 3. Insert .hero-tagline-bar inside col-center right before layer pills ───
OLD_COL_CENTER = """    <!-- CENTER: LIVING AESTHETIC INDIA MAP -->
    <main class="col-center">

      <!-- FIRST-TIMER ONBOARDING HINT (dismissable) -->"""

NEW_COL_CENTER = """    <!-- CENTER: LIVING AESTHETIC INDIA MAP -->
    <main class="col-center">

      <!-- HERO MISSION TAGLINE (SELF-CONTAINED IN CENTER, NEVER OVERLAPS) -->
      <div class="hero-tagline-bar">
        This tool helps you explore how TB spread differently across India's 36 states, using AI to find hidden patterns.
      </div>

      <!-- FIRST-TIMER ONBOARDING HINT (dismissable) -->"""

assert OLD_COL_CENTER in src, "OLD_COL_CENTER not found"
src = src.replace(OLD_COL_CENTER, NEW_COL_CENTER, 1)

fp.write_text(src, encoding="utf-8")
print("SUCCESS: scripts/build_upgraded_preview.py updated cleanly!")
