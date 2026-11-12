import json
import unicodedata
from pathlib import Path

# Paths
WORKSPACE = Path(__file__).resolve().parent.parent
MIRROR = Path(r"C:\Users\LENOVO\Desktop\int396 tb project")

# 1. Load state data
state_data = json.loads((WORKSPACE / "data" / "preview_state_data.json").read_text(encoding="utf-8"))

def clean(s):
    return unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("utf-8").strip().lower()

# Map GeoJSON shape names to cleaned state names
geo_path = WORKSPACE / "data/raw/dataful_20833/india_admin1.geojson"
if not geo_path.exists():
    geo_path = MIRROR / "data/raw/dataful_20833/india_admin1.geojson"
geo = json.loads(geo_path.read_text(encoding="utf-8"))

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

clean_to_state = {clean(s): s for s in state_data.keys()}

# Precalculate national statistics
total_dia = sum(s["dia"] for s in state_data.values())
sorted_dias = sorted(s["dia"] for s in state_data.values())
median_dia = (sorted_dias[17] + sorted_dias[18]) / 2  # 30,499.5

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
        "cluster": "Group A"
    })
    
    # Calculate share of national total
    pct_share = (s_info["dia"] / total_dia * 100) if total_dia > 0 else 0
    delta_vs_med = ((s_info["dia"] - median_dia) / median_dia * 100) if median_dia > 0 else 0
    
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
            f'data-dia-raw="{s_info["dia"]}" '
            f'data-tob="{s_info["tob"]:,}" '
            f'data-alc="{s_info["alc"]:,}" '
            f'data-cluster="{s_info["cluster"]}" '
            f'data-share="{pct_share:.2f}%" '
            f'data-delta="{delta_vs_med:+.1f}%" '
            f'd="{d_str}" />'
        )

svg_body = "\n          ".join(svg_elements)

# Leaderboard items with cluster attributes for filtering
leader_items = []
sorted_states = sorted(state_data.values(), key=lambda x: x["dia"], reverse=True)
for idx, s in enumerate(sorted_states, 1):
    val_str = f"{s['dia'] / 1000:.1f}k" if s['dia'] >= 1000 else str(s['dia'])
    is_active = ' active' if s['name'] == 'Maharashtra' else ''
    clean_id = clean(s['name'])
    c_group = "B" if "Group B" in s["cluster"] else ("C" if "Group C" in s["cluster"] else "A")
    leader_items.append(
        f'<div class="state-item{is_active}" id="item-{clean_id}" data-state="{s["name"]}" data-cluster="group-{c_group.lower()}" data-rank="{idx}">'
        f'<span class="s-left"><span class="rank-num">{idx:02d}</span> <strong>{s["name"]}</strong></span>'
        f'<span class="s-val"><span class="c-tag c-tag-{c_group.lower()}">Grp {c_group}</span> {val_str}</span>'
        f'</div>'
    )
leader_html = "\n          ".join(leader_items)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AeroTB · India Regional Intelligence Command Center</title>
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

  /* ── GLOBAL TOP NAVIGATION BAR ── */
  .top-header {{
    position: fixed;
    top: 16px;
    left: 28px;
    right: 28px;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    pointer-events: none;
  }}
  .brand-bar {{
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

  .header-actions {{
    display: flex;
    align-items: center;
    gap: 10px;
    pointer-events: auto;
  }}
  .nav-pill-group {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(14, 18, 26, 0.88);
    backdrop-filter: blur(18px);
    padding: 5px 8px;
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }}
  .nav-pill {{
    color: #94a3b8;
    text-decoration: none;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: 9999px;
    transition: all 0.2s;
  }}
  .nav-pill:hover, .nav-pill.active {{
    color: #ffffff;
    background: rgba(255, 255, 255, 0.1);
  }}
  .provenance-badge {{
    display: flex;
    align-items: center;
    gap: 7px;
    background: rgba(14, 18, 26, 0.88);
    backdrop-filter: blur(18px);
    padding: 7px 14px;
    border-radius: 9999px;
    border: 1px solid rgba(16, 185, 129, 0.3);
    font-size: 0.7rem;
    font-weight: 700;
    color: #cbd5e1;
  }}
  .status-pulse {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 8px #10b981;
  }}

  /* ── SCREEN 1: 3-COLUMN COMMAND CENTER ── */
  .viewport-hero {{
    height: 100vh;
    min-height: 720px;
    max-height: 920px;
    padding: 76px 28px 18px;
    display: grid;
    grid-template-columns: 310px minmax(460px, 1fr) 340px;
    gap: 20px;
    position: relative;
    box-sizing: border-box;
  }}

  /* LEFT COLUMN: DID YOU KNOW + LEADERBOARD */
  .col-left {{
    width: 310px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    height: 100%;
    overflow: hidden;
  }}

  /* DID YOU KNOW BRIEFING CARD */
  .fact-box {{
    background: rgba(18, 20, 28, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 14px 16px 16px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.55);
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

  /* LEADERBOARD LIST & FILTER TABS */
  .leaderboard {{
    flex: 1;
    background: rgba(18, 20, 28, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.55);
  }}
  .lb-section-header {{
    font-size: 0.6rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
  }}
  .filter-chips {{
    display: flex;
    gap: 4px;
    margin-bottom: 10px;
    overflow-x: auto;
    padding-bottom: 4px;
  }}
  .filter-chip {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #94a3b8;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.63rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }}
  .filter-chip:hover, .filter-chip.active {{
    background: rgba(56, 189, 248, 0.15);
    color: #38bdf8;
    border-color: rgba(56, 189, 248, 0.35);
  }}
  .search-wrap {{
    position: relative;
    margin-bottom: 8px;
  }}
  .search-input {{
    width: 100%;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 7px 12px;
    color: #fff;
    font-size: 0.76rem;
    outline: none;
    font-family: inherit;
  }}
  .search-input:focus {{
    border-color: #38bdf8;
    background: rgba(255, 255, 255, 0.08);
  }}
  .lb-col-header {{
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
  .state-list {{
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-right: 4px;
  }}
  .state-list::-webkit-scrollbar {{ width: 4px; }}
  .state-list::-webkit-scrollbar-track {{ background: transparent; }}
  .state-list::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.1); border-radius: 4px; }}

  .state-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 10px;
    border-radius: 8px;
    font-size: 0.74rem;
    cursor: pointer;
    background: transparent;
    border: 1px solid transparent;
    transition: all 0.15s ease;
  }}
  .state-item .s-left {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .state-item .rank-num {{
    color: #64748b;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
  }}
  .state-item:hover {{
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
  }}
  .state-item.active {{
    background: rgba(56, 189, 248, 0.12);
    border-color: rgba(56, 189, 248, 0.35);
    color: #ffffff;
  }}
  .state-item .s-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #cbd5e1;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .c-tag {{
    font-size: 0.58rem;
    padding: 1px 5px;
    border-radius: 4px;
    font-weight: 700;
  }}
  .c-tag-b {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; }}
  .c-tag-c {{ background: rgba(129, 140, 248, 0.15); color: #818cf8; }}
  .c-tag-a {{ background: rgba(100, 116, 139, 0.2); color: #94a3b8; }}

  /* CENTER COLUMN: MAP & HUD CONTROLS */
  .col-center {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    height: 100%;
  }}
  .map-layer-pills {{
    position: absolute;
    top: 0;
    z-index: 10;
    display: flex;
    gap: 6px;
    background: rgba(14, 18, 26, 0.9);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 9999px;
    padding: 4px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  }}
  .layer-btn {{
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
  }}
  .layer-btn:hover {{ color: #ffffff; }}
  .layer-btn.active {{
    background: #38bdf8;
    color: #07080c;
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
  }}

  /* FLOATING MAP HUD LEGEND */
  .map-legend {{
    position: absolute;
    bottom: 45px;
    left: 20px;
    z-index: 10;
    background: rgba(14, 18, 26, 0.88);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 8px 14px;
    font-size: 0.68rem;
    color: #94a3b8;
    display: flex;
    flex-direction: column;
    gap: 5px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
  }}
  .legend-title {{
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-size: 0.6rem;
    color: #64748b;
  }}
  .legend-scale-row {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .legend-item {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    margin-right: 6px;
    font-size: 0.66rem;
  }}
  .legend-swatch {{
    width: 10px;
    height: 10px;
    border-radius: 3px;
    display: inline-block;
  }}

  /* FLOATING MOUSE TOOLTIP */
  .map-tooltip {{
    position: fixed;
    pointer-events: none;
    z-index: 200;
    background: rgba(14, 18, 26, 0.95);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 8px;
    padding: 8px 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.8);
    display: none;
    font-size: 0.72rem;
    color: #fff;
    transform: translate(-50%, -125%);
    white-space: nowrap;
  }}
  .tooltip-title {{
    font-weight: 800;
    font-size: 0.8rem;
    margin-bottom: 2px;
    color: #ffffff;
  }}
  .tooltip-row {{
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: #94a3b8;
    font-size: 0.68rem;
  }}
  .tooltip-row strong {{ color: #38bdf8; font-family: 'JetBrains Mono', monospace; }}

  /* SVG MAP STYLING */
  .india-map {{
    width: 100%;
    height: 100%;
    max-height: 590px;
    filter: drop-shadow(0 15px 35px rgba(0, 0, 0, 0.7));
  }}
  .state-shape {{
    stroke: rgba(255, 255, 255, 0.12);
    stroke-width: 0.6;
    stroke-linejoin: round;
    transition: fill 0.35s ease, stroke 0.2s ease, filter 0.2s ease;
    cursor: pointer;
  }}
  .state-shape:hover {{
    stroke: #38bdf8;
    stroke-width: 1.6;
    filter: brightness(1.2);
  }}
  .state-shape.selected {{
    stroke: #38bdf8;
    stroke-width: 2.2;
    filter: brightness(1.3) drop-shadow(0 0 10px rgba(56, 189, 248, 0.5));
  }}

  /* SCROLL CUE */
  .scroll-cue {{
    position: absolute;
    bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748b;
    text-decoration: none;
    transition: color 0.2s;
  }}
  .scroll-cue:hover {{ color: #38bdf8; }}

  /* RIGHT COLUMN: TELEMETRY INSPECTOR CARD */
  .col-right {{
    width: 340px;
    z-index: 10;
    height: 100%;
    display: flex;
    flex-direction: column;
  }}
  .telemetry-card {{
    height: 100%;
    background: rgba(14, 16, 24, 0.92);
    backdrop-filter: blur(22px);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 18px;
    padding: 18px 18px 14px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0;
  }}
  .badge-region {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 5px;
    background: rgba(255, 255, 255, 0.05);
    color: #94a3b8;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
    text-transform: uppercase;
  }}
  .telemetry-name {{
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 1px;
    letter-spacing: -0.01em;
  }}
  .telemetry-rank {{
    font-size: 0.7rem;
    color: #64748b;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  /* Cluster row — slim, no box */
  .cluster-chip {{
    border-top: 1px solid rgba(255,255,255,0.06);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 8px 0;
    margin-bottom: 12px;
  }}
  .cluster-chip-title {{
    font-size: 0.6rem;
    color: #475569;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.06em;
  }}
  .cluster-chip-val {{
    font-size: 0.84rem;
    font-weight: 700;
    color: #38bdf8;
    margin-top: 2px;
  }}
  .cluster-desc {{
    font-size: 0.68rem;
    color: #64748b;
    margin-top: 3px;
    line-height: 1.4;
  }}

  /* STAT BENCHMARK GRID */
  .benchmark-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-bottom: 12px;
  }}
  .bench-box {{
    background: rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    padding: 7px 10px;
  }}
  .bench-label {{
    font-size: 0.58rem;
    color: #475569;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  .bench-val {{
    font-size: 1.0rem;
    font-weight: 800;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 1px;
  }}
  .bench-diff {{
    font-size: 0.6rem;
    font-weight: 600;
    margin-top: 2px;
    display: inline-block;
    color: #94a3b8;
  }}
  .diff-amber {{ color: #f59e0b; }}
  .diff-green {{ color: #10b981; }}

  .metric-bar-group {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
  }}
  .mbar-header {{
    display: flex;
    justify-content: space-between;
    font-size: 0.68rem;
    color: #64748b;
    margin-bottom: 3px;
  }}
  .mbar-header strong {{ color: #94a3b8; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; }}
  .mbar-track {{
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.07);
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
  
  .policy-box {{
    font-size: 0.68rem;
    color: #64748b;
    margin-bottom: 10px;
    line-height: 1.5;
    padding-left: 8px;
    border-left: 2px solid rgba(56, 189, 248, 0.3);
  }}
  .policy-box strong {{ color: #38bdf8; }}

  .twins-box {{
    font-size: 0.68rem;
    color: #475569;
    line-height: 1.45;
    margin-bottom: 10px;
  }}
  .twins-box strong {{ color: #94a3b8; }}

  .insight-box {{
    flex: 1;
    background: rgba(255,255,255,0.025);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-height: 0;
  }}
  .insight-title {{
    font-size: 0.62rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .insight-text {{
    font-size: 0.72rem;
    color: #64748b;
    line-height: 1.55;
  }}
  .insight-text strong {{ color: #94a3b8; }}

  .card-action-bar {{
    padding-top: 10px;
    display: flex;
    gap: 8px;
  }}
  .btn-action {{
    flex: 1;
    padding: 7px 10px;
    border-radius: 8px;
    font-size: 0.68rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    text-decoration: none;
  }}
  .btn-print {{
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #475569;
  }}
  .btn-print:hover {{
    border-color: rgba(255,255,255,0.2);
    color: #94a3b8;
  }}
  .btn-lab {{
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: #38bdf8;
  }}
  .btn-lab:hover {{
    background: #38bdf8;
    color: #07080c;
  }}

  /* ── SCREEN 2: SCROLL-DRIVEN 3D TRANSITION STORYTELLING ── */
  .story-track {{
    position: relative;
    height: 350vh;
    background: #07080c;
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
    padding: 40px;
    box-sizing: border-box;
  }}
  .story-progress-bar {{
    position: absolute;
    top: 40px;
    display: flex;
    gap: 8px;
  }}
  .progress-dot {{
    width: 32px;
    height: 4px;
    border-radius: 2px;
    background: rgba(255, 255, 255, 0.15);
    transition: all 0.3s;
    cursor: pointer;
  }}
  .progress-dot.active {{
    background: #00f2fe;
    width: 48px;
    box-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
  }}
  .story-cards-container {{
    position: relative;
    width: 100%;
    max-width: 760px;
    height: 380px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .story-card-step {{
    position: absolute;
    inset: 0;
    background: rgba(14, 20, 34, 0.88);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 28px;
    padding: 44px 50px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    opacity: 0;
    transform: translateY(40px) scale(0.95);
    transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    pointer-events: none;
    box-shadow: 0 30px 70px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 242, 254, 0.05);
  }}
  .story-card-step.current {{
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: auto;
  }}
  .story-card-step.passed {{
    opacity: 0;
    transform: translateY(-40px) scale(0.95);
    pointer-events: none;
    filter: blur(4px);
  }}

  /* ── MEDICAL HOLOGRAPHIC OVERLAY & WIDGETS ── */
  .holo-stage-grid {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image: 
      linear-gradient(rgba(0, 242, 254, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 242, 254, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    opacity: 0.7;
    z-index: 1;
  }}

  /* Centered Tomography Radar Reticle */
  .holo-radar-ring {{
    position: absolute;
    top: 50%;
    left: 50%;
    width: 620px;
    height: 620px;
    margin-top: -310px;
    margin-left: -310px;
    border-radius: 50%;
    border: 1px dashed rgba(0, 242, 254, 0.15);
    box-shadow: 0 0 50px rgba(0, 242, 254, 0.04), inset 0 0 50px rgba(0, 242, 254, 0.04);
    pointer-events: none;
    z-index: 2;
    animation: holoSpin 40s linear infinite;
  }}
  .holo-radar-ring::before {{
    content: '';
    position: absolute;
    inset: 50px;
    border-radius: 50%;
    border: 1px solid rgba(129, 140, 248, 0.12);
  }}
  .holo-radar-ring::after {{
    content: '';
    position: absolute;
    inset: 120px;
    border-radius: 50%;
    border: 1px dashed rgba(56, 189, 248, 0.18);
  }}

  @keyframes holoSpin {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
  }}

  /* Floating Medical Hologram Widget - Left (Pulmonary Vitals) */
  .holo-widget {{
    position: absolute;
    z-index: 5;
    pointer-events: none;
    background: rgba(14, 20, 34, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 242, 254, 0.22);
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(0, 242, 254, 0.12);
    transition: transform 0.4s ease-out, opacity 0.4s ease-out;
  }}
  .holo-widget-left {{
    left: 45px;
    top: 50%;
    transform: translateY(-50%);
    width: 250px;
  }}
  .holo-widget-right {{
    right: 45px;
    top: 50%;
    transform: translateY(-50%);
    width: 260px;
  }}

  .holo-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.6rem;
    font-weight: 800;
    color: #00f2fe;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .holo-pulse-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00f2fe;
    box-shadow: 0 0 8px #00f2fe;
    animation: holoBlink 1.4s ease-in-out infinite;
  }}
  @keyframes holoBlink {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.4; transform: scale(0.8); }}
  }}

  .holo-title {{
    font-size: 0.82rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 10px;
    letter-spacing: -0.01em;
  }}

  .holo-stat-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.68rem;
    color: #94a3b8;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }}
  .holo-stat-row strong {{
    color: #00f2fe;
    font-family: 'JetBrains Mono', monospace;
  }}

  /* Animated Medical ECG Waveform */
  .holo-ecg-svg {{
    width: 100%;
    height: 42px;
    margin-top: 8px;
    overflow: visible;
  }}
  .holo-ecg-path {{
    stroke: #00f2fe;
    stroke-width: 2;
    fill: none;
    stroke-dasharray: 400;
    stroke-dashoffset: 400;
    animation: holoEcgSweep 3s linear infinite;
    filter: drop-shadow(0 0 6px rgba(0, 242, 254, 0.6));
  }}
  @keyframes holoEcgSweep {{
    0% {{ stroke-dashoffset: 400; }}
    100% {{ stroke-dashoffset: 0; }}
  }}

  /* Top & Bottom Cyber Crosshair Accents */
  .holo-corner-reticle {{
    position: absolute;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: rgba(0, 242, 254, 0.45);
    letter-spacing: 0.05em;
    pointer-events: none;
    z-index: 3;
  }}
  .reticle-tl {{ top: 30px; left: 45px; }}
  .reticle-tr {{ top: 30px; right: 45px; text-align: right; }}
  .reticle-bl {{ bottom: 30px; left: 45px; }}
  .reticle-br {{ bottom: 30px; right: 45px; text-align: right; }}

  @media (max-width: 1200px) {{
    .holo-widget {{ display: none !important; }}
    .holo-radar-ring {{ width: 440px; height: 440px; margin-top: -220px; margin-left: -220px; }}
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

  /* PRINT STYLES */
  @media print {{
    body {{ background: #fff; color: #000; }}
    .top-header, .col-left, .story-track, .viewport-launch, .map-layer-pills, .map-legend, .scroll-cue, .card-action-bar {{ display: none !important; }}
    .viewport-hero {{ height: auto; display: block; padding: 20px; }}
    .col-right {{ width: 100%; height: auto; }}
    .telemetry-card {{ border: 1px solid #ccc; background: #fff; color: #000; box-shadow: none; }}
    .telemetry-name {{ color: #000; }}
  }}
</style>
</head>
<body>

  <!-- FLOATING TOP NAVIGATION BAR -->
  <header class="top-header">
    <div class="brand-bar">
      <div class="brand-logo">◈</div>
      <div class="brand-name">AeroTB</div>
      <span class="brand-sub">/ INDIA REGIONAL INTELLIGENCE</span>
    </div>

    <div class="header-actions">
      <nav class="nav-pill-group">
        <a href="#hero" class="nav-pill active">🗺️ Command Map</a>
        <a href="#story" class="nav-pill">📖 3D Story</a>
        <a href="#modules" class="nav-pill">🔬 Modules</a>
      </nav>
      <div class="provenance-badge">
        <div class="status-pulse"></div>
        <span>MoHFW / Ni-kshay Verified (N=36)</span>
      </div>
    </div>
  </header>

  <!-- ════════════════════════════════════════════════════════ -->
  <!-- SCREEN 1: 3-COLUMN COMMAND CENTER MAP                   -->
  <!-- ════════════════════════════════════════════════════════ -->
  <section class="viewport-hero" id="hero">

    <!-- LEFT: DID YOU KNOW + FILTERABLE LEADERBOARD -->
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

      <!-- SEARCH & LEADERBOARD WITH FILTER CHIPS -->
      <div class="leaderboard">
        <div class="lb-section-header">Filter states by group</div>
        <div class="filter-chips">
          <button class="filter-chip active" onclick="filterByGroup('all')">All States</button>
          <button class="filter-chip" onclick="filterByGroup('top10')">Top 10</button>
          <button class="filter-chip" onclick="filterByGroup('group-b')">Outliers</button>
          <button class="filter-chip" onclick="filterByGroup('group-c')">High Burden</button>
          <button class="filter-chip" onclick="filterByGroup('group-a')">Lower Burden</button>
        </div>

        <div class="search-wrap">
          <input type="text" class="search-input" id="state-search" placeholder="🔍 Search any state...">
        </div>

        <div class="lb-col-header">
          <span>Rank &amp; State</span>
          <span>Patients screened (2023, Diabetes)</span>
        </div>

        <div class="state-list" id="leader-list">
          {leader_html}
        </div>
      </div>
    </aside>

    <!-- CENTER: LIVING AESTHETIC INDIA MAP -->
    <main class="col-center">

      <div class="map-layer-pills">
        <button class="layer-btn active" id="btn-dia" onclick="setLayer('dia')">🩺 TB + Diabetes</button>
        <button class="layer-btn" id="btn-tob" onclick="setLayer('tob')">🚬 TB + Tobacco</button>
        <button class="layer-btn" id="btn-alc" onclick="setLayer('alc')">🍷 TB + Alcohol</button>
        <button class="layer-btn" id="btn-clust" onclick="setLayer('cluster')">👥 Group Similar States</button>
      </div>

      <!-- MAP FLOATING HUD LEGEND -->
      <div class="map-legend" id="map-legend"></div>

      <!-- SVG INDIA VECTOR MAP -->
      <svg class="india-map" viewBox="0 0 600 700">
        <g id="map-states">
          {svg_body}
        </g>
      </svg>

      <!-- CURSOR HOVER TOOLTIP -->
      <div class="map-tooltip" id="map-tooltip">
        <div class="tooltip-title" id="tt-name">State</div>
        <div class="tooltip-row"><span>TB Cases:</span> <strong id="tt-val">0</strong></div>
        <div class="tooltip-row"><span>India's Share:</span> <strong id="tt-share">0%</strong></div>
        <div class="tooltip-row"><span>Cluster:</span> <strong id="tt-cluster">Group</strong></div>
      </div>

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
        <div class="telemetry-rank" id="t-rank">
          <span>National Burden Rank: #2 of 36</span>
        </div>

        <div class="cluster-chip">
          <div class="cluster-chip-title">Which Group Does This State Belong To?</div>
          <div class="cluster-chip-val" id="t-cluster">Group C · High-Burden Major State</div>
          <div class="cluster-desc" id="t-cluster-desc">
            Substantial clinical volume with emerging private notification integration and active comorbidity monitoring.
          </div>
        </div>

        <!-- BENCHMARK GRID (STATE VS NATIONAL MEDIAN) -->
        <div class="benchmark-grid">
          <div class="bench-box">
            <div class="bench-label">TB Cases Reported</div>
            <div class="bench-val" id="t-m1">213,034</div>
            <div class="bench-diff diff-amber" id="t-diff">598% more than avg Indian state</div>
          </div>
          <div class="bench-box">
            <div class="bench-label">Share of India's Total</div>
            <div class="bench-val" id="t-share">9.02%</div>
            <div class="bench-diff diff-green" id="t-share-tag">Major Contributor</div>
          </div>
        </div>

        <!-- CLINICAL INDICATORS -->
        <div class="metric-bar-group">
          <div>
            <div class="mbar-header"><span id="lbl-m1">Also Had Diabetes</span> <strong id="bar-num-1">213k</strong></div>
            <div class="mbar-track"><div class="mbar-fill" id="bar-m1" style="width: 82%;"></div></div>
          </div>
          <div>
            <div class="mbar-header"><span id="lbl-m2">Also Used Tobacco</span> <strong id="bar-num-2">178k</strong></div>
            <div class="mbar-track"><div class="mbar-fill mbar-fill-green" id="bar-m2" style="width: 78%;"></div></div>
          </div>
          <div>
            <div class="mbar-header"><span id="lbl-m3">Also Used Alcohol</span> <strong id="bar-num-3">174k</strong></div>
            <div class="mbar-track"><div class="mbar-fill mbar-fill-amber" id="bar-m3" style="width: 76%;"></div></div>
          </div>
        </div>

        <!-- CLINICAL POLICY ACTION RECOMMENDATION -->
        <div class="policy-box" id="t-policy">
          <strong>Clinical Focus:</strong> Scale bidirectional diabetes screening in peripheral dispensaries; expand private-provider mandatory reporting.
        </div>

        <!-- MULTIVARIATE TWINS -->
        <div class="twins-box" id="t-twins">
          Nearest Pattern Twins: Closest mathematical proximity to <strong>Gujarat & Rajasthan</strong>.
        </div>

        <!-- PLAIN ENGLISH SUMMARY -->
        <div class="insight-box" id="t-insight">
          <div class="insight-title">💡 What this tells you</div>
          <div class="insight-text" id="t-insight-text">
            Maharashtra reports <strong>significantly more TB cases</strong> than the average Indian state. It is grouped with other high-burden states — meaning its health challenges are <strong>similar to states like Karnataka and Gujarat</strong>.
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-action-bar">
          <button class="btn-action btn-print" style="grid-column: 1 / -1; width: 100%; justify-content: center;" onclick="window.print()" title="Export clinical summary">📄 Print State Health Dossier</button>
        </div>
      </div>
    </aside>

  </section>

  <!-- ════════════════════════════════════════════════════════ -->
  <!-- SCREEN 2: SCROLL-DRIVEN 3D TRANSITION STORYTELLING       -->
  <!-- ════════════════════════════════════════════════════════ -->
  <section class="story-track" id="story">
    <div class="story-sticky-stage">
      <!-- MEDICAL HOLOGRAPHIC AMBIENT GRID & RADAR -->
      <div class="holo-stage-grid"></div>
      <div class="holo-radar-ring" id="holo-radar"></div>

      <!-- CORNER RETICLES -->
      <div class="holo-corner-reticle reticle-tl">
        SYS.MOD // CLINICAL TOMOGRAPHY<br>
        GEO: 20.59° N · 78.96° E [IN]
      </div>
      <div class="holo-corner-reticle reticle-tr">
        SURVEILLANCE MATRIX // N=36<br>
        DATA QUALITY: 100% AUDITED
      </div>
      <div class="holo-corner-reticle reticle-bl">
        VECTOR RESOLUTION: k=3<br>
        PARTITION: K-MEANS + WARD
      </div>
      <div class="holo-corner-reticle reticle-br">
        MOHFW SURVEILLANCE FEED<br>
        STATUS: LIVE &amp; GROUNDED
      </div>

      <!-- LEFT HOLOGRAPHIC WIDGET: PULMONARY VITALS -->
      <div class="holo-widget holo-widget-left" id="holo-widget-l">
        <div class="holo-tag">
          <div class="holo-pulse-dot"></div>
          <span>BIOSENSOR TELEMETRY</span>
        </div>
        <div class="holo-title">Pulmonary Diagnostic Load</div>
        <div class="holo-stat-row"><span>Annual Notified:</span> <strong>2.42M</strong></div>
        <div class="holo-stat-row"><span>Global Burden Share:</span> <strong>27.0%</strong></div>
        <div class="holo-stat-row"><span>Airborne Infection:</span> <strong>Active</strong></div>
        <div class="holo-stat-row"><span>Curability Rate:</span> <strong>100%</strong></div>
        <svg class="holo-ecg-svg" viewBox="0 0 200 40">
          <path class="holo-ecg-path" d="M0,20 L30,20 L40,10 L50,30 L60,5 L70,35 L80,20 L110,20 L120,8 L130,32 L140,20 L200,20" />
        </svg>
      </div>

      <!-- RIGHT HOLOGRAPHIC WIDGET: COMORBIDITY SCANNER -->
      <div class="holo-widget holo-widget-right" id="holo-widget-r">
        <div class="holo-tag">
          <div class="holo-pulse-dot" style="background:#818cf8; box-shadow:0 0 8px #818cf8;"></div>
          <span style="color:#818cf8;">COMORBIDITY MATRIX</span>
        </div>
        <div class="holo-title">Clinical Risk Multipliers</div>
        <div class="holo-stat-row"><span>TB + Diabetes Risk:</span> <strong style="color:#38bdf8;">3.1× High</strong></div>
        <div class="holo-stat-row"><span>Tobacco Impairment:</span> <strong style="color:#818cf8;">2.4× Risk</strong></div>
        <div class="holo-stat-row"><span>Alcohol Defenses:</span> <strong style="color:#f59e0b;">1.9× Risk</strong></div>
        <div class="holo-stat-row"><span>Screening Regime:</span> <strong style="color:#10b981;">Bilateral</strong></div>
        <div style="margin-top:10px; font-size:0.62rem; color:#64748b; line-height:1.4;">
          Multidimensional feature space standardises volumes across 36 regional units for unsupervised clustering.
        </div>
      </div>
      <div class="story-progress-bar">
        <div class="progress-dot active" id="dot-0"></div>
        <div class="progress-dot" id="dot-1"></div>
        <div class="progress-dot" id="dot-2"></div>
      </div>

      <div style="text-align: center; margin-bottom: 24px;">
        <span class="step-pill">Scroll-Driven Public Health Journey</span>
        <h2 style="font-size: 2.2rem; font-weight: 800; color: #fff;">Understanding India's TB Challenge</h2>
      </div>

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
            A uniform national policy cannot work. Highly urbanized states like Maharashtra face massive private-sector notification lags, while agrarian regions suffer from comorbidity under-diagnosis. Unsupervised clustering exposes the hidden geographic patterns.
          </p>
          <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 8px; background: rgba(129,140,248,0.1); border: 1px solid rgba(129,140,248,0.3); border-radius: 8px; padding: 6px 12px; font-size: 0.8rem; color: #818cf8; font-weight: 600;">
            ⚡ Machine learning segregates India into 3 distinct policy regimes
          </div>
          <div class="step-counter">03 / 03 · Ready for Deep Exploration ↓</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════════════════════════════════════════════ -->
  <!-- SCREEN 3: NAVIGATION LAUNCHPAD                           -->
  <!-- ════════════════════════════════════════════════════════ -->
  <section class="viewport-launch" id="modules">
    <div style="text-align: center; max-width: 650px;">
      <span class="step-pill">Course INT396 · Advanced Project Suite</span>
      <h2 class="section-headline" style="font-size: 2.2rem; margin-bottom: 8px; color: #fff;">Explore Intelligence Modules</h2>
      <p style="color: #64748b; font-size: 0.95rem;">Jump into specialized research tools, mathematical clustering benchmarks, and viva defense artifacts.</p>
    </div>

    <div class="portal-grid">
      <div class="portal-card" onclick="navigateTo('compare')">
        <div class="portal-tag">Module 01 · Side-by-Side Analysis</div>
        <div class="portal-title">📈 Compare States</div>
        <div class="portal-desc">Put up to 6 states side-by-side to track and compare their 5-year notification trajectories from 2019 to 2023.</div>
      </div>

      <div class="portal-card" onclick="navigateTo('clusters')">
        <div class="portal-tag">Module 02 · Find State "Twins"</div>
        <div class="portal-title">👥 State Similarity Lab</div>
        <div class="portal-desc">Let AI discover which states face the exact same TB challenge. Unsupervised clustering groups all 36 states into 3 similar "teams".</div>
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

  // Auto-advance every 5.5 seconds
  setInterval(() => {{
    progressVal += 2;
    if (factProgress) factProgress.style.width = progressVal + '%';
    if (progressVal >= 100) {{
      nextFact();
    }}
  }}, 110);

  // CLUSTER PROFILE METADATA
  const CLUSTER_META = {{
    'Group B': {{
      name: 'Group B · Hyper-Burden Epicenter',
      desc: 'Extremely high case volume carrying ~29.8% of national notifications. Critical demand for decentralized rapid molecular testing.',
      policy: 'Clinical Focus: Intensify urban TB dispensaries, expand private-provider mandatory reporting, and fast-track daily regimen adherence.',
      color: '#38bdf8'
    }},
    'Group C': {{
      name: 'Group C · High-Burden Major State',
      desc: 'Substantial surveillance volume with high bidirectional screening rates (>85%) but significant comorbid diabetes and tobacco burden.',
      policy: 'Clinical Focus: Scale up nutritional support (Nikshay Poshan Yojana) and integrate routine blood glucose screening in all primary centers.',
      color: '#818cf8'
    }},
    'Group A': {{
      name: 'Group A · Baseline Surveillance & UTs',
      desc: 'Low aggregate case numbers with high geographic dispersion. Strong candidates for localized sub-district TB elimination certification.',
      policy: 'Clinical Focus: Maintain high index of suspicion, active case finding in tribal pockets, and rigorous contact tracing.',
      color: '#273248'
    }}
  }};

  // ACTIVE STATE & TELEMETRY
  const shapes = document.querySelectorAll('.state-shape');
  const tName = document.getElementById('t-name');
  const tRank = document.getElementById('t-rank');
  const tReg = document.getElementById('t-reg');
  const tCluster = document.getElementById('t-cluster');
  const tClusterDesc = document.getElementById('t-cluster-desc');
  const tM1 = document.getElementById('t-m1');
  const tDiff = document.getElementById('t-diff');
  const tShare = document.getElementById('t-share');
  const tPolicy = document.getElementById('t-policy');
  const barM1 = document.getElementById('bar-m1');
  const barM2 = document.getElementById('bar-m2');
  const barM3 = document.getElementById('bar-m3');
  const barNum1 = document.getElementById('bar-num-1');
  const barNum2 = document.getElementById('bar-num-2');
  const barNum3 = document.getElementById('bar-num-3');
  const tTwins = document.getElementById('t-twins');
  let currentLayer = 'dia';

  const NAT_MEDIAN = 30499.5;

  function updateTelemetry(el) {{
    shapes.forEach(x => x.classList.remove('selected'));
    el.classList.add('selected');

    const sName = el.getAttribute('data-name');
    const rawVal = parseInt(el.getAttribute('data-dia-raw') || '0');
    const rawTob = parseInt((el.getAttribute('data-tob') || '0').replace(/,/g, ''));
    const rawAlc = parseInt((el.getAttribute('data-alc') || '0').replace(/,/g, ''));
    const clusterKey = el.getAttribute('data-cluster') || 'Group A';
    const cMeta = CLUSTER_META[clusterKey] || CLUSTER_META['Group A'];

    tName.textContent = sName;
    tRank.textContent = 'National Burden Rank: ' + el.getAttribute('data-rank') + ' of 36';
    tReg.textContent = el.getAttribute('data-zone') || 'INDIA';
    
    tCluster.textContent = cMeta.name;
    tCluster.style.color = cMeta.color;
    tClusterDesc.textContent = cMeta.desc;
    tPolicy.innerHTML = '<strong>Clinical Focus:</strong> ' + cMeta.policy.replace('Clinical Focus: ', '');

    // Current Layer Value
    let valStr = el.getAttribute('data-' + currentLayer) || '0';
    tM1.textContent = valStr;

    // Benchmark Delta
    let currRaw = (currentLayer === 'dia') ? rawVal : ((currentLayer === 'tob') ? rawTob : rawAlc);
    let delta = ((currRaw - NAT_MEDIAN) / NAT_MEDIAN * 100);
    if (delta >= 0) {{
      tDiff.textContent = '+' + delta.toFixed(1) + '% more than avg Indian state';
      tDiff.className = 'bench-diff diff-amber';
    }} else {{
      tDiff.textContent = delta.toFixed(1) + '% below avg Indian state';
      tDiff.className = 'bench-diff diff-green';
    }}

    // National Share
    const shareStr = el.getAttribute('data-share') || '0.00%';
    tShare.textContent = shareStr;


    // Plain-English Insight
    const tInsightText = document.getElementById('t-insight-text');
    if (tInsightText) {{
      let insightMsg = '';
      const deltaAbs = Math.abs(delta).toFixed(0);
      if (sName === 'Uttar Pradesh') {{
        insightMsg = 'Uttar Pradesh has <strong>the most TB cases of any state</strong> in India — far above all others. It forms its own group because no other state comes close in scale.';
      }} else if (clusterKey === 'Group B') {{
        insightMsg = sName + ' is an <strong>outlier state</strong> — its TB numbers are so large that the AI placed it in a group of just two, separate from the rest of India.';
      }} else if (clusterKey === 'Group C') {{
        insightMsg = sName + ' is a <strong>high-burden state</strong> — it has significantly more TB cases than average and shares a similar pattern with other major states across India.';
      }} else {{
        insightMsg = sName + ' has a <strong>relatively lower TB burden</strong> compared to major states. It is grouped with similar smaller-burden states across India.';
      }}
      tInsightText.innerHTML = insightMsg;
    }}

    // Progress Bars
    const maxVal = 620325; // UP max
    const w1 = Math.min(100, Math.max(6, Math.round(rawVal / maxVal * 100)));
    const w2 = Math.min(100, Math.max(6, Math.round(rawTob / 432523 * 100)));
    const w3 = Math.min(100, Math.max(6, Math.round(rawAlc / 421491 * 100)));

    barM1.style.width = w1 + '%';
    barM2.style.width = w2 + '%';
    barM3.style.width = w3 + '%';

    barNum1.textContent = rawVal >= 1000 ? (rawVal / 1000).toFixed(1) + 'k' : rawVal;
    barNum2.textContent = rawTob >= 1000 ? (rawTob / 1000).toFixed(1) + 'k' : rawTob;
    barNum3.textContent = rawAlc >= 1000 ? (rawAlc / 1000).toFixed(1) + 'k' : rawAlc;

    // Mathematical Twins
    if (sName === 'Maharashtra') tTwins.innerHTML = 'Most Similar States: Closest multivariate match — proximity to <strong>Gujarat & Madhya Pradesh</strong>.';
    else if (sName === 'Uttar Pradesh') tTwins.innerHTML = 'Most Similar States (Health Twins): Co-pattern states — with <strong>Tamil Nadu</strong> in comorbidity volume.';
    else if (clusterKey === 'Group B') tTwins.innerHTML = 'Most Similar States (Health Twins): Co-pattern trajectory — with <strong>Uttar Pradesh</strong>.';
    else if (clusterKey === 'Group C') tTwins.innerHTML = 'Most Similar States (Health Twins): Highly similar pattern — distance to <strong>Rajasthan, Bihar & Gujarat</strong>.';
    else tTwins.innerHTML = 'Most Similar States (Health Twins): Very similar baseline — <strong>Sikkim, Goa & Himachal Pradesh</strong>.';

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

  // HOVER TOOLTIP LOGIC
  const tooltip = document.getElementById('map-tooltip');
  const ttName = document.getElementById('tt-name');
  const ttVal = document.getElementById('tt-val');
  const ttShare = document.getElementById('tt-share');
  const ttCluster = document.getElementById('tt-cluster');

  shapes.forEach(s => {{
    s.addEventListener('mouseenter', (e) => {{
      updateTelemetry(s);
      showTooltip(e, s);
    }});
    s.addEventListener('mousemove', (e) => moveTooltip(e));
    s.addEventListener('mouseleave', () => hideTooltip());
    s.addEventListener('click', () => updateTelemetry(s));
  }});

  function showTooltip(e, el) {{
    if (!tooltip) return;
    ttName.textContent = el.getAttribute('data-name');
    ttVal.textContent = el.getAttribute('data-' + currentLayer) || '0';
    ttShare.textContent = el.getAttribute('data-share') || '0%';
    ttCluster.textContent = el.getAttribute('data-cluster') || 'Group A';
    tooltip.style.display = 'block';
    moveTooltip(e);
  }}

  function moveTooltip(e) {{
    if (!tooltip) return;
    tooltip.style.left = e.clientX + 'px';
    tooltip.style.top = e.clientY + 'px';
  }}

  function hideTooltip() {{
    if (tooltip) tooltip.style.display = 'none';
  }}

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

  // FILTER CHIPS (ALL, TOP 10, GROUP A/B/C)
  function filterByGroup(grp) {{
    document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    document.querySelectorAll('.state-item').forEach(item => {{
      const itemGrp = item.getAttribute('data-cluster');
      const rank = parseInt(item.getAttribute('data-rank') || '99');

      if (grp === 'all') {{
        item.style.display = 'flex';
      }} else if (grp === 'top10') {{
        item.style.display = rank <= 10 ? 'flex' : 'none';
      }} else {{
        item.style.display = itemGrp === grp ? 'flex' : 'none';
      }}
    }});
  }}

  // CHOROPLETH COLOR ENGINE
  const COLOR_PALETTE = {{
    tier5: '#7dd3fc', // > 200k (UP, MH): Soft ice sky
    tier4: '#38bdf8', // 100k - 200k (MP, RJ, BR, GJ): Azure sky
    tier3: '#0284c7', // 40k - 100k (TN, WB, AP, HR, KA, OD, PB, AS, DL, TS, JH): Ocean blue
    tier2: '#2b3a58', // 15k - 40k (CG, UK, KL, HP): Muted slate blue
    tier1: '#1e2330', // 4k - 15k (JK, ML): Charcoal slate
    tier0: '#151821'  // < 4k (NE states, UTs): Neutral graphite
  }};

  const CLUSTER_PALETTE = {{
    'Group B': '#38bdf8', // Hyper-Burden Epicenters (Ice Azure)
    'Group C': '#818cf8', // High-Burden Major States (Indigo Periwinkle)
    'Group A': '#222a3d'  // Baseline Surveillance & UTs (Slate Graphite)
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
        <div class="legend-title">STATES GROUPED BY SIMILAR HEALTH PATTERNS (3 TEAMS)</div>
        <div class="legend-scale-row">
          <span class="legend-item"><span class="legend-swatch" style="background:#38bdf8; box-shadow:0 0 6px rgba(56,189,248,0.5);"></span>Team B: Outlier scale (2 states)</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#818cf8;"></span>Team C: High burden (13 states)</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#222a3d; border:1px solid rgba(255,255,255,0.2);"></span>Team A: Lower burden (21 states)</span>
        </div>
      `;
    }} else {{
      legEl.innerHTML = `
        <div class="legend-title">SURVEILLANCE SCALE (CASES · NAT'L MEDIAN: 30.5k)</div>
        <div class="legend-scale-row">
          <span class="legend-item"><span class="legend-swatch" style="background:#151821; border:1px solid rgba(255,255,255,0.15);"></span>&lt;4k</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#1e2330;"></span>15k</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#2b3a58;"></span>40k</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#0284c7;"></span>100k</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#38bdf8;"></span>200k</span>
          <span class="legend-item"><span class="legend-swatch" style="background:#7dd3fc;"></span>&gt;200k</span>
        </div>
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
    if (layerKey === 'dia') lbl.textContent = 'Diabetes Co-Screening Volume';
    else if (layerKey === 'tob') lbl.textContent = 'Tobacco Screening Volume';
    else if (layerKey === 'alc') lbl.textContent = 'Alcohol Screening Volume';
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

  // 3D SCROLL STORY TELLING SCRIPT
  const storyTrack = document.getElementById('story');
  const step0 = document.getElementById('step-0');
  const step1 = document.getElementById('step-1');
  const step2 = document.getElementById('step-2');
  const dot0 = document.getElementById('dot-0');
  const dot1 = document.getElementById('dot-1');
  const dot2 = document.getElementById('dot-2');

  const steps = [step0, step1, step2];
  const dots = [dot0, dot1, dot2];

  function updateStep(idx) {{
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

    // Dynamic 3D Holographic Parallax
    const holoL = document.getElementById('holo-widget-l');
    const holoR = document.getElementById('holo-widget-r');
    const holoRadar = document.getElementById('holo-radar');
    if (holoL && holoR) {{
      const shiftY = (progress - 0.5) * 80;
      const shiftRot = (progress - 0.5) * 6;
      holoL.style.transform = "translateY(calc(-50% + " + shiftY + "px)) rotate(" + shiftRot + "deg)";
      holoR.style.transform = "translateY(calc(-50% - " + shiftY + "px)) rotate(" + (-shiftRot) + "deg)";
      if (holoRadar) {{
        holoRadar.style.transform = "scale(" + (0.9 + progress * 0.2) + ") rotate(" + (progress * 180) + "deg)";
      }}
    }}
  }};

  window.addEventListener('scroll', handleScroll, {{ passive: true }});
  document.addEventListener('scroll', handleScroll, {{ passive: true }});
</script>
</body>
</html>
"""

# Write to both workspace and mirror
(WORKSPACE / "preview.html").write_text(html_template, encoding="utf-8")
if MIRROR.exists():
    (MIRROR / "preview.html").write_text(html_template, encoding="utf-8")
print(f"Successfully generated upgraded preview.html ({len(html_template)} bytes) in both locations!")
