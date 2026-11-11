import json
import unicodedata
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\LENOVO\Desktop\int396 tb project")

# 1. Load state data
state_data = json.loads((ROOT / "data" / "preview_state_data.json").read_text(encoding="utf-8"))

def clean(s):
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8").strip().lower()

# Map GeoJSON shape names to cleaned state names
geo = json.loads((ROOT / "data/raw/dataful_20833/india_admin1.geojson").read_text(encoding="utf-8"))

# Projection bounds for India map
min_lon, max_lon = 68.0, 97.5
min_lat, max_lat = 7.5, 37.5

def pt_to_svg(lon, lat):
    x = (lon - min_lon) / (max_lon - min_lon) * 520 + 40
    y = (max_lat - lat) / (max_lat - min_lat) * 620 + 40
    return f"{int(round(x))},{int(round(y))}"

def simplify_ring(ring, min_dist=0.22):
    if len(ring) <= 8:
        return ring
    res = [ring[0]]
    for p in ring[1:-1]:
        if not isinstance(p[0], (int, float)):
            continue
        d = ((p[0] - res[-1][0]) ** 2 + (p[1] - res[-1][1]) ** 2) ** 0.5
        if d >= min_dist:
            res.append(p)
    res.append(ring[-1])
    if len(res) < 3:
        return ring
    return res

# Clean name mapping
clean_to_state = {clean(s): s for s in state_data.keys()}

# Generate SVG paths for all shapes
svg_elements = []
for feat in geo["features"]:
    raw_name = feat["properties"]["shapeName"]
    c_name = clean(raw_name)
    matched_state = clean_to_state.get(c_name, raw_name)
    s_info = state_data.get(matched_state, {
        "name": matched_state,
        "rank": "#--",
        "zone": "INDIA",
        "dia": 0,
        "tob": 0,
        "alc": 0,
        "cluster": "Group B · Standard"
    })
    
    geom = feat["geometry"]
    coords = geom["coordinates"]
    gtype = geom["type"]
    polys = [coords] if gtype == "Polygon" else coords
    
    d_parts = []
    for poly in polys:
        ring = poly[0] if isinstance(poly[0][0], (list, tuple)) else poly
        simp = simplify_ring(ring, 0.22)
        pts = [pt_to_svg(p[0], p[1]) for p in simp if isinstance(p[0], (int, float))]
        if len(pts) >= 3:
            d_parts.append("M" + " L".join(pts) + " Z")
            
    if d_parts:
        d_str = " ".join(d_parts)
        is_selected = ' selected' if matched_state == 'Maharashtra' else ''
        svg_elements.append(
            f'<path class="state-shape{is_selected}" id="shape-{c_name}" '
            f'data-name="{s_info["name"]}" '
            f'data-rank="{s_info["rank"]}" '
            f'data-zone="{s_info["zone"]}" '
            f'data-dia="{s_info["dia"]:,}" '
            f'data-tob="{s_info["tob"]:,}" '
            f'data-alc="{s_info["alc"]:,}" '
            f'data-cluster="{s_info["cluster"]}" '
            f'd="{d_str}" />'
        )

svg_body = "\n          ".join(svg_elements)

# Leaderboard items
leader_items = []
sorted_states = sorted(state_data.values(), key=lambda x: x["dia"], reverse=True)
for idx, s in enumerate(sorted_states, 1):
    val_str = f"{s['dia'] / 1000:.1f}k" if s['dia'] >= 1000 else str(s['dia'])
    is_active = ' active' if s['name'] == 'Maharashtra' else ''
    clean_id = clean(s['name'])
    leader_items.append(
        f'<div class="state-item{is_active}" id="item-{clean_id}" data-state="{s["name"]}">'
        f'<span>{idx:02d}. <strong>{s["name"]}</strong></span>'
        f'<span>{val_str}</span>'
        f'</div>'
    )
leader_html = "\n          ".join(leader_items)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AeroTB · India Regional Intelligence</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; scroll-behavior: smooth; }}
  body {{
    background-color: #07080c;
    background-image: 
      radial-gradient(ellipse 90% 65% at 50% -12%, rgba(42, 53, 76, 0.42) 0%, rgba(18, 23, 34, 0.5) 50%, transparent 90%),
      radial-gradient(circle at 85% 90%, rgba(28, 35, 52, 0.28) 0%, transparent 60%);
    background-attachment: fixed;
    color: #f1f5f9;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    overflow-x: hidden;
  }}

  /* ── MINIMAL FLOATING BRAND HEADER ── */
  .brand-bar {{
    position: fixed;
    top: 20px;
    left: 36px;
    z-index: 100;
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(18, 20, 28, 0.9);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    padding: 8px 18px;
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
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

  /* ── SCREEN 1: 3-COLUMN COMMAND CENTER ── */
  .viewport-hero {{
    height: 100vh;
    min-height: 680px;
    max-height: 880px;
    padding: 72px 28px 20px;
    display: grid;
    grid-template-columns: 290px minmax(460px, 1fr) 320px;
    gap: 20px;
    position: relative;
    box-sizing: border-box;
  }}

  /* LEFT COLUMN: DID YOU KNOW + LEADERBOARD */
  .col-left {{
    width: 290px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    z-index: 10;
    height: 100%;
    min-height: 0;
  }}

  /* DYNAMIC "DID YOU KNOW" CARD */
  .fact-box {{
    background: rgba(18, 20, 28, 0.92);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 14px 16px 12px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
    flex-shrink: 0;
  }}
  .fact-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }}
  .fact-tag {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 9999px;
    padding: 3px 8px;
    font-size: 0.62rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #38bdf8;
    text-transform: uppercase;
  }}
  .fact-tag .pulse-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #38bdf8;
    box-shadow: 0 0 6px #38bdf8;
    animation: blink 2s infinite;
  }}
  @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
  .fact-nav {{
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .fact-btn {{
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #94a3b8;
    width: 20px;
    height: 20px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
    line-height: 1;
    padding: 0;
  }}
  .fact-btn:hover {{
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    border-color: rgba(255, 255, 255, 0.25);
  }}
  .fact-counter {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    color: #64748b;
    min-width: 26px;
    text-align: center;
  }}
  .fact-title {{
    font-size: 0.92rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.01em;
    margin-bottom: 4px;
    transition: opacity 0.25s ease, transform 0.25s ease;
  }}
  .fact-content {{
    font-size: 0.77rem;
    line-height: 1.48;
    color: #94a3b8;
    min-height: 46px;
    transition: opacity 0.25s ease, transform 0.25s ease;
  }}
  .fact-content strong {{
    color: #f1f5f9;
    font-weight: 700;
  }}
  .fact-progress-track {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: rgba(255, 255, 255, 0.06);
  }}
  .fact-progress-fill {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #0284c7, #38bdf8);
    transition: width 0.1s linear;
  }}

  /* LEADERBOARD LIST */
  .leaderboard {{
    flex: 1;
    background: rgba(18, 20, 28, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .search-input {{
    width: 100%;
    background: rgba(24, 27, 36, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #f8fafc;
    padding: 9px 14px;
    border-radius: 10px;
    font-size: 0.78rem;
    outline: none;
    margin-bottom: 12px;
    transition: border 0.2s, box-shadow 0.2s;
  }}
  .search-input:focus {{
    border-color: rgba(255, 255, 255, 0.3);
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
  }}
  .state-list {{
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-right: 4px;
    max-height: 380px;
  }}
  .state-list::-webkit-scrollbar {{ width: 4px; }}
  .state-list::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.18); border-radius: 4px; }}
  .state-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    border-radius: 8px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.2s;
    color: #94a3b8;
  }}
  .state-item:hover, .state-item.active {{
    background: rgba(255, 255, 255, 0.08);
    color: #38bdf8;
    border-left: 2px solid #38bdf8;
    transform: translateX(3px);
  }}
  .state-item strong {{ color: #ffffff; }}

  /* CENTER MAP CONTAINER */
  .col-center {{
    height: 100%;
    min-height: 0;
    background: radial-gradient(circle at 50% 50%, #131622 0%, #0c0e14 75%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 70px rgba(0, 0, 0, 0.85), 0 20px 45px rgba(0, 0, 0, 0.65);
  }}
  .map-layer-pills {{
    position: absolute;
    top: 18px;
    left: 20px;
    display: flex;
    gap: 8px;
    z-index: 10;
  }}
  .layer-btn {{
    background: #161822;
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #94a3b8;
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.22s;
  }}
  .layer-btn:hover, .layer-btn.active {{
    background: rgba(255, 255, 255, 0.12);
    border-color: #cbd5e1;
    color: #ffffff;
    box-shadow: none;
  }}
  svg.india-map {{
    width: 100%;
    max-width: 520px;
    height: 510px;
    max-height: 70vh;
    display: block;
    margin: 6px 0 auto;
  }}
  .state-shape {{
    stroke: rgba(255, 255, 255, 0.15);
    stroke-width: 0.9px;
    cursor: pointer;
    transition: fill 0.25s ease, stroke 0.2s ease, filter 0.2s ease, opacity 0.2s ease;
  }}
  .state-shape:hover {{
    stroke: #ffffff;
    stroke-width: 1.8px;
    filter: brightness(1.22);
  }}
  .state-shape.selected {{
    stroke: #ffffff !important;
    stroke-width: 2.4px !important;
    filter: brightness(1.28) drop-shadow(0 0 6px rgba(255, 255, 255, 0.55)) !important;
  }}

  /* MAP LEGEND */
  .map-legend {{
    position: absolute;
    bottom: 56px;
    left: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(18, 20, 28, 0.9);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 6px 12px;
    font-size: 0.68rem;
    color: #94a3b8;
    z-index: 10;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 5px;
  }}
  .legend-swatch {{
    width: 9px;
    height: 9px;
    border-radius: 2px;
    display: inline-block;
  }}

  /* RIGHT COLUMN: TELEMETRY INSPECTOR CARD */
  .col-right {{
    width: 320px;
    z-index: 10;
    height: 100%;
    display: flex;
    flex-direction: column;
  }}
  .telemetry-card {{
    height: 100%;
    background: rgba(18, 20, 28, 0.9);
    backdrop-filter: blur(22px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.7);
    overflow-y: auto;
  }}
  .badge-region {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #cbd5e1;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
    text-transform: uppercase;
  }}
  .telemetry-name {{
    font-size: 1.65rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 2px;
  }}
  .telemetry-rank {{
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 18px;
  }}
  .cluster-chip {{
    background: rgba(24, 27, 36, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 16px;
  }}
  .cluster-chip-title {{
    font-size: 0.68rem;
    color: #64748b;
    text-transform: uppercase;
    font-weight: 700;
  }}
  .cluster-chip-val {{
    font-size: 0.88rem;
    font-weight: 700;
    color: #38bdf8;
    margin-top: 2px;
  }}
  .metric-bar-group {{
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }}
  .mbar-header {{
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-bottom: 4px;
  }}
  .mbar-header strong {{ color: #fff; font-family: 'JetBrains Mono', monospace; }}
  .mbar-track {{
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    overflow: hidden;
  }}
  .mbar-fill {{
    height: 100%;
    border-radius: 9999px;
    background: linear-gradient(90deg, #0284c7, #38bdf8);
    transition: width 0.4s ease;
  }}
  .mbar-fill-green {{
    background: linear-gradient(90deg, #059669, #10b981) !important;
  }}
  .mbar-fill-amber {{
    background: linear-gradient(90deg, #d97706, #f59e0b) !important;
  }}
  .twins-box {{
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 12px;
    font-size: 0.75rem;
    color: #94a3b8;
    line-height: 1.5;
  }}
  .twins-box strong {{ color: #f1f5f9; }}

  /* SCROLL INDICATOR */
  .scroll-cue {{
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #00f2fe;
    text-decoration: none;
    animation: float 2.5s ease-in-out infinite;
  }}
  @keyframes float {{
    0%, 100% {{ transform: translate(-50%, 0); }}
    50% {{ transform: translate(-50%, 8px); }}
  }}

  /* ── SCREEN 2: SCROLL-DRIVEN 3D TRANSITION STORYTELLING ── */
  .story-track {{
    position: relative;
    min-height: 280vh;
    background: radial-gradient(circle at 50% 30%, #0d1a33 0%, #050811 80%);
  }}
  .story-sticky-stage {{
    position: sticky;
    top: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 0 40px;
  }}
  .story-progress-bar {{
    position: absolute;
    top: 40px;
    display: flex;
    gap: 8px;
    z-index: 20;
  }}
  .progress-dot {{
    width: 36px;
    height: 4px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 9999px;
    transition: all 0.3s ease;
  }}
  .progress-dot.active {{
    background: #00f2fe;
    box-shadow: 0 0 12px #00f2fe;
    width: 56px;
  }}
  .story-cards-container {{
    perspective: 1200px;
    width: 100%;
    max-width: 820px;
    height: 380px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .story-card-step {{
    position: absolute;
    width: 100%;
    background: rgba(13, 21, 39, 0.88);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(0, 242, 254, 0.28);
    border-radius: 28px;
    padding: 44px 48px;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 242, 254, 0.12);
    transform-style: preserve-3d;
    opacity: 0;
    transform: translateY(60px) scale(0.92) rotateX(-10deg);
    transition: opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), filter 0.5s;
    pointer-events: none;
    filter: blur(4px);
  }}
  .story-card-step.current {{
    opacity: 1;
    transform: translateY(0) scale(1) rotateX(0deg);
    pointer-events: auto;
    filter: blur(0px);
    z-index: 5;
  }}
  .story-card-step.passed {{
    opacity: 0;
    transform: translateY(-60px) scale(0.92) rotateX(10deg);
    pointer-events: none;
    filter: blur(4px);
  }}
  .step-pill {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    background: rgba(0, 242, 254, 0.12);
    border: 1px solid rgba(0, 242, 254, 0.35);
    color: #00f2fe;
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 14px;
  }}
  .step-title {{
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 14px;
  }}
  .step-body {{
    color: #94a3b8;
    font-size: 1.05rem;
    line-height: 1.65;
  }}
  .step-counter {{
    position: absolute;
    bottom: 24px;
    right: 36px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #475569;
  }}

  /* ── SCREEN 3: NAVIGATION LAUNCHPAD ── */
  .viewport-launch {{
    min-height: 90vh;
    padding: 90px 60px;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #050811;
  }}
  .portal-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    max-width: 1200px;
    width: 100%;
    margin-top: 40px;
  }}
  .portal-card {{
    background: rgba(11, 18, 34, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 28px 24px;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
  }}
  .portal-card:hover {{
    background: rgba(15, 25, 48, 0.9);
    border-color: #00f2fe;
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 242, 254, 0.15);
  }}
  .portal-tag {{
    font-size: 0.68rem;
    font-weight: 800;
    color: #00f2fe;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 14px;
  }}
  .portal-title {{
    font-size: 1.15rem;
    font-weight: 800;
    color: #fff;
    margin-bottom: 8px;
  }}
  .portal-desc {{
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.5;
  }}
</style>
</head>
<body>

  <!-- FLOATING BRAND LOGO -->
  <div class="brand-bar">
    <div class="brand-logo">◈</div>
    <div>
      <div class="brand-name">AeroTB</div>
    </div>
    <span class="brand-sub">/ INDIA NATIONAL INTELLIGENCE</span>
  </div>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- SCREEN 1: 3-COLUMN COMMAND CENTER MAP                   -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section class="viewport-hero">

    <!-- LEFT: DID YOU KNOW + LEADERBOARD -->
    <aside class="col-left">
      <!-- DYNAMIC TRANSITIONING "DID YOU KNOW" -->
      <div class="fact-box">
        <div class="fact-header">
          <div class="fact-tag">
            <div class="pulse-dot"></div>
            <span id="fact-cat">SURVEILLANCE</span>
          </div>
          <div class="fact-nav">
            <button class="fact-btn" onclick="prevFact()" title="Previous fact">‹</button>
            <span class="fact-counter" id="fact-counter">1 / 5</span>
            <button class="fact-btn" onclick="nextFact()" title="Next fact">›</button>
          </div>
        </div>
        <div class="fact-title" id="fact-title">2.4M Cases Annually</div>
        <div class="fact-content" id="fact-text">
          India notifies over 2.4 million TB patients each year — carrying <strong>27% of global burden</strong> across 36 states.
        </div>
        <div class="fact-progress-track">
          <div class="fact-progress-fill" id="fact-progress"></div>
        </div>
      </div>

      <!-- SEARCH & LEADERBOARD -->
      <div class="leaderboard">
        <input type="text" class="search-input" id="state-search" placeholder="🔍 Search any state...">
        <div class="state-list" id="leader-list">
          {leader_html}
        </div>
      </div>
    </aside>

    <!-- CENTER: LIVING AESTHETIC INDIA MAP -->
    <main class="col-center">
      <div class="map-layer-pills">
        <button class="layer-btn active" id="btn-dia" onclick="setLayer('dia')">🩺 Diabetes in TB</button>
        <button class="layer-btn" id="btn-tob" onclick="setLayer('tob')">🚬 Tobacco Users in TB</button>
        <button class="layer-btn" id="btn-alc" onclick="setLayer('alc')">🍷 Alcohol Users in TB</button>
        <button class="layer-btn" id="btn-clust" onclick="setLayer('cluster')">🤖 AI State Groups</button>
      </div>

      <div class="map-legend" id="map-legend"></div>

      <svg class="india-map" viewBox="0 0 600 700">
        <g id="map-states">
          {svg_body}
        </g>
      </svg>

      <a href="#story" class="scroll-cue">
        <span>Scroll To Uncover The Story</span>
        <span>↓</span>
      </a>
    </main>

    <!-- RIGHT: LIVE STATE TELEMETRY CARD -->
    <aside class="col-right">
      <div class="telemetry-card">
        <span class="badge-region" id="t-reg">WEST INDIA</span>
        <h2 class="telemetry-name" id="t-name">Maharashtra</h2>
        <div class="telemetry-rank" id="t-rank">National Burden Rank: #2 of 36</div>

        <div class="cluster-chip">
          <div class="cluster-chip-title">AI Discovered Pattern Group</div>
          <div class="cluster-chip-val" id="t-cluster">Group B · High-Volume Epicenter</div>
        </div>

        <div class="metric-bar-group">
          <div>
            <div class="mbar-header"><span id="lbl-m1">Annual Notifications</span> <strong id="t-m1">213,034</strong></div>
            <div class="mbar-track"><div class="mbar-fill" id="bar-m1" style="width: 82%;"></div></div>
          </div>
          <div>
            <div class="mbar-header"><span id="lbl-m2">Diabetes Co-Screening</span> <strong id="t-m2">91.4%</strong></div>
            <div class="mbar-track"><div class="mbar-fill mbar-fill-green" id="bar-m2" style="width: 91%;"></div></div>
          </div>
          <div>
            <div class="mbar-header"><span id="lbl-m3">Intervention Compliance</span> <strong id="t-m3">64.2%</strong></div>
            <div class="mbar-track"><div class="mbar-fill mbar-fill-amber" id="bar-m3" style="width: 64%;"></div></div>
          </div>
        </div>

        <div class="twins-box" id="t-twins">
          Pattern Twins: Closest multivariate similarity with <strong>Gujarat & Rajasthan</strong>.
        </div>
      </div>
    </aside>

  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- SCREEN 2: SCROLL-DRIVEN 3D TRANSITION STORYTELLING       -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section class="story-track" id="story">
    <div class="story-sticky-stage">
      <!-- PROGRESS INDICATORS -->
      <div class="story-progress-bar">
        <div class="progress-dot active" id="dot-0"></div>
        <div class="progress-dot" id="dot-1"></div>
        <div class="progress-dot" id="dot-2"></div>
      </div>

      <div style="text-align: center; margin-bottom: 24px;">
        <span class="step-pill">Scroll-Driven Public Health Journey</span>
        <h2 style="font-size: 2.2rem; font-weight: 800; color: #fff;">Understanding India's TB Challenge</h2>
      </div>

      <!-- CARDS THAT TRANSITION AS YOU SCROLL -->
      <div class="story-cards-container">
        <!-- STEP 1 -->
        <div class="story-card-step current" id="step-0">
          <div style="font-size: 2.2rem; margin-bottom: 10px;">🫁</div>
          <h3 class="step-title">Ancient, Airborne & 100% Curable</h3>
          <p class="step-body">
            TB bacteria have infected humans for over 9,000 years, spreading simply through the air when an infected person speaks or coughs. It is completely curable with antibiotics — yet <strong>India carries 27% of the entire world's cases</strong>.
          </p>
          <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 8px; background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.3); border-radius: 8px; padding: 6px 12px; font-size: 0.8rem; color: #00f2fe; font-weight: 600;">
            ⚡ Over 2.4 million Indians are officially notified every year
          </div>
          <div class="step-counter">01 / 03 · Scroll to continue ↓</div>
        </div>

        <!-- STEP 2 -->
        <div class="story-card-step" id="step-1">
          <div style="font-size: 2.2rem; margin-bottom: 10px;">🔬</div>
          <h3 class="step-title">The Secret Multipliers</h3>
          <p class="step-body">
            TB rarely attacks alone. <strong>Diabetes triples a patient's risk</strong> of developing active TB, while Tobacco and Alcohol destroy lung defenses and cause patients to drop out of treatment before being cured.
          </p>
          <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 8px; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); border-radius: 8px; padding: 6px 12px; font-size: 0.8rem; color: #38bdf8; font-weight: 600;">
            ⚡ 1 in 5 TB patients in India also suffers from diabetes or tobacco dependence
          </div>
          <div class="step-counter">02 / 03 · Scroll to continue ↓</div>
        </div>

        <!-- STEP 3 -->
        <div class="story-card-step" id="step-2">
          <div style="font-size: 2.2rem; margin-bottom: 10px;">⚖️</div>
          <h3 class="step-title">36 States · 36 Different Crises</h3>
          <p class="step-body">
            Treating Kerala's aging, high-diabetes TB population with the exact same budget as Uttar Pradesh's dense young workforce guarantees failure. <strong>One size does not fit all.</strong>
          </p>
          <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 8px; background: rgba(168,237,234,0.1); border: 1px solid rgba(168,237,234,0.3); border-radius: 8px; padding: 6px 12px; font-size: 0.8rem; color: #a8edea; font-weight: 600;">
            ⚡ Our AI groups states sharing identical patterns so tailored funding follows
          </div>
          <div class="step-counter">03 / 03 · Reaching Navigation Modules ↓</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- SCREEN 3: CLEAN NAVIGATION LAUNCHPAD                    -->
  <!-- ═══════════════════════════════════════════════════════ -->
  <section class="viewport-launch" id="modules">
    <div style="text-align: center;">
      <span class="step-pill" style="border-color: #38bdf8; color: #38bdf8;">Next Steps</span>
      <h2 class="section-headline" style="font-size: 2.2rem; margin-bottom: 8px; color: #fff;">Explore Intelligence Modules</h2>
      <p style="color: #64748b; font-size: 0.92rem;">Select a specialized suite below to begin your analysis.</p>
    </div>

    <div class="portal-grid">
      <div class="portal-card" onclick="navigateTo('clusters')">
        <div class="portal-tag">Module 01</div>
        <div class="portal-title">🤖 AI Cluster Lab</div>
        <div class="portal-desc">Run K-Means, Manhattan distance tests, WCSS elbow plots, and interactive dendrograms across all states.</div>
      </div>

      <div class="portal-card" onclick="navigateTo('compare')">
        <div class="portal-tag">Module 02</div>
        <div class="portal-title">📈 Compare States</div>
        <div class="portal-desc">Put up to 6 neighboring states side-by-side to track their 5-year notification trajectories from 2019 to 2023.</div>
      </div>

      <div class="portal-card" onclick="navigateTo('explainer')">
        <div class="portal-tag">Module 03</div>
        <div class="portal-title">💡 AI Data Explainer</div>
        <div class="portal-desc">Get instant plain-language translations of data points and understand how standardization works without jargon.</div>
      </div>

      <div class="portal-card" onclick="window.open('https://nikshay.in/', '_blank')">
        <div class="portal-tag">Module 04</div>
        <div class="portal-title">🆘 Official Helplines</div>
        <div class="portal-desc">Direct access to the Government of India Ni-kshay national portal and official healthcare support routes.</div>
      </div>
    </div>
  </section>

<script>
  // DYNAMIC "DID YOU KNOW" INTELLIGENCE ROTATOR
  const facts = [
    {{
      cat: "SURVEILLANCE",
      title: "2.4M Cases Annually",
      text: "India notifies over 2.4 million TB patients each year — carrying <strong>27% of global burden</strong> across 36 states."
    }},
    {{
      cat: "COMORBIDITY",
      title: "The 3× Diabetes Risk",
      text: "Diabetes triples the risk of active TB. All Indian states now mandate <strong>100% bidirectional screening</strong>."
    }},
    {{
      cat: "DATA INSIGHT",
      title: "High Counts ≠ Disease",
      text: "Higher state notifications often reflect <strong>superior hospital screening & reporting</strong>, not higher disease rates."
    }},
    {{
      cat: "ADHERENCE",
      title: "The Tobacco Trap",
      text: "Tobacco users are <strong>twice as likely to drop out</strong> of their 6-month antibiotic regimen before being cured."
    }},
    {{
      cat: "AI CLUSTERS",
      title: "Precision Allocation",
      text: "Treating Kerala like UP fails. Our unsupervised AI <strong>groups states sharing identical clinical traits</strong>."
    }}
  ];
  let factIdx = 0;
  let progressVal = 0;
  const factCat = document.getElementById('fact-cat');
  const factTitle = document.getElementById('fact-title');
  const factEl = document.getElementById('fact-text');
  const factCounter = document.getElementById('fact-counter');
  const factProgress = document.getElementById('fact-progress');

  function renderFact(idx) {{
    if (!factEl) return;
    factTitle.style.opacity = '0';
    factEl.style.opacity = '0';
    factTitle.style.transform = 'translateY(4px)';
    factEl.style.transform = 'translateY(4px)';
    setTimeout(() => {{
      const f = facts[idx];
      factCat.textContent = f.cat;
      factTitle.textContent = f.title;
      factEl.innerHTML = f.text;
      factCounter.textContent = (idx + 1) + ' / ' + facts.length;
      factTitle.style.opacity = '1';
      factEl.style.opacity = '1';
      factTitle.style.transform = 'translateY(0)';
      factEl.style.transform = 'translateY(0)';
      progressVal = 0;
      if (factProgress) factProgress.style.width = '0%';
    }}, 200);
  }}

  function nextFact() {{
    factIdx = (factIdx + 1) % facts.length;
    renderFact(factIdx);
  }}

  function prevFact() {{
    factIdx = (factIdx - 1 + facts.length) % facts.length;
    renderFact(factIdx);
  }}

  // Auto-advance every 5.5 seconds with smooth progress fill
  setInterval(() => {{
    progressVal += 2;
    if (factProgress) factProgress.style.width = progressVal + '%';
    if (progressVal >= 100) {{
      nextFact();
    }}
  }}, 110);

  // ACTIVE STATE & TELEMETRY
  const shapes = document.querySelectorAll('.state-shape');
  const tName = document.getElementById('t-name');
  const tRank = document.getElementById('t-rank');
  const tReg = document.getElementById('t-reg');
  const tCluster = document.getElementById('t-cluster');
  const tM1 = document.getElementById('t-m1');
  const barM1 = document.getElementById('bar-m1');
  let currentLayer = 'dia';

  function updateTelemetry(el) {{
    shapes.forEach(x => x.classList.remove('selected'));
    el.classList.add('selected');

    const sName = el.getAttribute('data-name');
    tName.textContent = sName;
    tRank.textContent = 'National Burden Rank: ' + el.getAttribute('data-rank') + ' of 36';
    tReg.textContent = el.getAttribute('data-zone') || 'INDIA';
    tCluster.textContent = el.getAttribute('data-cluster') || 'Group B · Standard';

    let val = el.getAttribute('data-' + currentLayer) || '0';
    tM1.textContent = val;

    // highlight in leaderboard
    document.querySelectorAll('.state-item').forEach(it => {{
      if (it.getAttribute('data-state') === sName) {{
        it.classList.add('active');
        it.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }} else {{
        it.classList.remove('active');
      }}
    }});
  }}

  shapes.forEach(s => {{
    s.addEventListener('mouseenter', () => updateTelemetry(s));
    s.addEventListener('click', () => updateTelemetry(s));
  }});

  // LEADERBOARD CLICK & SEARCH
  document.querySelectorAll('.state-item').forEach(item => {{
    item.addEventListener('click', () => {{
      const stName = item.getAttribute('data-state');
      shapes.forEach(s => {{
        if (s.getAttribute('data-name') === stName) {{
          updateTelemetry(s);
        }}
      }});
    }});
  }});

  const searchInput = document.getElementById('state-search');
  if (searchInput) {{
    searchInput.addEventListener('input', (e) => {{
      const query = e.target.value.toLowerCase();
      document.querySelectorAll('.state-item').forEach(item => {{
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? 'flex' : 'none';
      }});
    }});
  }}

  // REFINED BALANCED CHOROPLETH (NEUTRAL GRAPHITE BASE + CRISP SKY ACCENTS)
  const COLOR_PALETTE = {{
    tier5: '#7dd3fc', // > 200k (UP, MH): Soft ice sky
    tier4: '#38bdf8', // 100k - 200k (MP, RJ, BR, GJ): Azure sky
    tier3: '#0284c7', // 40k - 100k (TN, WB, AP, HR, KA, OD, PB, AS, DL, TS, JH): Ocean blue
    tier2: '#2b3a58', // 15k - 40k (CG, UK, KL, HP): Muted slate blue
    tier1: '#1e2330', // 4k - 15k (JK, ML): Charcoal slate
    tier0: '#151821'  // < 4k (NE states, UTs): Neutral graphite
  }};

  const CLUSTER_PALETTE = {{
    'Group B': '#7dd3fc', // High-Volume Epicenters (ice-cyan)
    'Group C': '#0284c7', // Standard Burden (ocean blue)
    'Group A': '#1e2330'  // Low Burden Monitoring (neutral charcoal slate)
  }};

  function getChoroplethColor(raw) {{
    if (raw >= 200000) return COLOR_PALETTE.tier5;
    if (raw >= 100000) return COLOR_PALETTE.tier4;
    if (raw >= 40000)  return COLOR_PALETTE.tier3;
    if (raw >= 15000)  return COLOR_PALETTE.tier2;
    if (raw >= 4000)   return COLOR_PALETTE.tier1;
    return COLOR_PALETTE.tier0;
  }}

  function updateLegend(layerKey) {{
    const legEl = document.getElementById('map-legend');
    if (!legEl) return;
    if (layerKey === 'cluster') {{
      legEl.innerHTML = `
        <span style="font-weight:700; color:#94a3b8; margin-right:4px;">Clusters:</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#1e2330; border:1px solid rgba(255,255,255,0.15);"></span>Group A (Low)</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#0284c7;"></span>Group C (Standard)</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#7dd3fc;"></span>Group B (Epicenters)</span>
      `;
    }} else {{
      legEl.innerHTML = `
        <span style="font-weight:700; color:#94a3b8; margin-right:4px;">Scale:</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#151821; border:1px solid rgba(255,255,255,0.15);"></span>&lt;4k</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#1e2330;"></span>15k</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#2b3a58;"></span>40k</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#0284c7;"></span>100k</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#38bdf8;"></span>200k</span>
        <span class="legend-item"><span class="legend-swatch" style="background:#7dd3fc;"></span>&gt;200k</span>
      `;
    }}
  }}

  // DYNAMIC MAP LAYER SWITCHER
  function setLayer(layerKey) {{
    currentLayer = layerKey;
    document.querySelectorAll('.layer-btn').forEach(b => b.classList.remove('active'));
    
    if (layerKey === 'dia') document.getElementById('btn-dia').classList.add('active');
    else if (layerKey === 'tob') document.getElementById('btn-tob').classList.add('active');
    else if (layerKey === 'alc') document.getElementById('btn-alc').classList.add('active');
    else if (layerKey === 'cluster') document.getElementById('btn-clust').classList.add('active');

    // Label update
    const lbl = document.getElementById('lbl-m1');
    if (layerKey === 'dia') lbl.textContent = 'TB Diabetes Screened';
    else if (layerKey === 'tob') lbl.textContent = 'TB Tobacco Users';
    else if (layerKey === 'alc') lbl.textContent = 'TB Alcohol Users';
    else if (layerKey === 'cluster') lbl.textContent = 'Cluster Membership';

    // Recolor all state shapes
    shapes.forEach(s => {{
      if (layerKey === 'cluster') {{
        const c = s.getAttribute('data-cluster') || '';
        if (c.includes('Group B')) s.style.fill = CLUSTER_PALETTE['Group B'];
        else if (c.includes('Group C')) s.style.fill = CLUSTER_PALETTE['Group C'];
        else s.style.fill = CLUSTER_PALETTE['Group A'];
      }} else {{
        const raw = parseInt((s.getAttribute('data-' + layerKey) || '0').replace(/,/g, ''));
        s.style.fill = getChoroplethColor(raw);
      }}
    }});

    updateLegend(layerKey);

    // Update active telemetry value
    const sel = document.querySelector('.state-shape.selected') || shapes[0];
    if (sel) updateTelemetry(sel);
  }}

  // INITIAL MAP RECOLOR
  setLayer('dia');

  function navigateTo(pageKey) {{
    try {{
      if (window.parent && window.parent !== window) {{
        window.parent.location.href = '/?page=' + encodeURIComponent(pageKey);
      }} else {{
        window.location.href = '/?page=' + encodeURIComponent(pageKey);
      }}
    }} catch(e) {{
      window.location.href = '/?page=' + encodeURIComponent(pageKey);
    }}
  }}

  // ── STORY CARDS 3D SCROLL ENGINE ──
  const storyTrack = document.getElementById('story');
  const step0 = document.getElementById('step-0');
  const step1 = document.getElementById('step-1');
  const step2 = document.getElementById('step-2');
  const dot0 = document.getElementById('dot-0');
  const dot1 = document.getElementById('dot-1');
  const dot2 = document.getElementById('dot-2');

  function updateStep(idx) {{
    const steps = [step0, step1, step2];
    const dots = [dot0, dot1, dot2];
    steps.forEach((s, i) => {{
      if (!s) return;
      if (i === idx) s.className = 'story-card-step current';
      else if (i < idx) s.className = 'story-card-step passed';
      else s.className = 'story-card-step';
    }});
    dots.forEach((d, i) => {{
      if (!d) return;
      d.classList.toggle('active', i === idx);
    }});
  }}

  if (dot0) dot0.onclick = () => updateStep(0);
  if (dot1) dot1.onclick = () => updateStep(1);
  if (dot2) dot2.onclick = () => updateStep(2);

  const handleScroll = () => {{
    if (!storyTrack) return;
    const rect = storyTrack.getBoundingClientRect();
    const vHeight = window.innerHeight || 800;
    const trackHeight = storyTrack.offsetHeight - vHeight;
    if (trackHeight <= 0) return;
    const progress = Math.max(0, Math.min(1, -rect.top / trackHeight));

    if (progress < 0.35) {{
      updateStep(0);
    }} else if (progress < 0.70) {{
      updateStep(1);
    }} else {{
      updateStep(2);
    }}
  }};

  window.addEventListener('scroll', handleScroll, {{ passive: true }});
  document.addEventListener('scroll', handleScroll, {{ passive: true }});
</script>
</body>
</html>
"""

(ROOT / "preview.html").write_text(html_template, encoding="utf-8")
print(f"Generated clean fast preview.html ({len(html_template)} bytes)!")
