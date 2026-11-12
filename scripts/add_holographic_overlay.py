"""Add medical aesthetic holographic overlay and floating diagnostic widgets to the scroll story section."""
from pathlib import Path

fp = Path(r"c:\Users\LENOVO\OneDrive\Desktop\int 396 project\scripts\build_upgraded_preview.py")
src = fp.read_text(encoding="utf-8")

# ── 1. Holographic HUD CSS ───────────────────────────────────────────────────
HOLO_CSS = """
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
"""

# Insert HOLO_CSS right after .step-pill rule
OLD_CSS_ANCHOR = "  .step-pill {{"
assert OLD_CSS_ANCHOR in src, "OLD_CSS_ANCHOR not found"
src = src.replace(OLD_CSS_ANCHOR, HOLO_CSS + "\n" + OLD_CSS_ANCHOR, 1)

# ── 2. Holographic HTML Overlay ──────────────────────────────────────────────
HOLO_HTML = """    <div class="story-sticky-stage">
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
      </div>"""

OLD_STAGE_HTML = "    <div class=\"story-sticky-stage\">"
assert OLD_STAGE_HTML in src, "OLD_STAGE_HTML not found"
src = src.replace(OLD_STAGE_HTML, HOLO_HTML, 1)

# ── 3. Scroll Parallax Script ────────────────────────────────────────────────
OLD_SCROLL_SCRIPT = """    if (progress < 0.35) {{
      updateStep(0);
    }} else if (progress < 0.70) {{
      updateStep(1);
    }} else {{
      updateStep(2);
    }}"""

NEW_SCROLL_SCRIPT = """    if (progress < 0.35) {{
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
      holoL.style.transform = `translateY(calc(-50% + ${shiftY}px)) rotate(${shiftRot}deg)`;
      holoR.style.transform = `translateY(calc(-50% - ${shiftY}px)) rotate(${-shiftRot}deg)`;
      if (holoRadar) {{
        holoRadar.style.transform = `scale(${0.9 + progress * 0.2}) rotate(${progress * 180}deg)`;
      }}
    }}"""

assert OLD_SCROLL_SCRIPT in src, "OLD_SCROLL_SCRIPT not found"
src = src.replace(OLD_SCROLL_SCRIPT, NEW_SCROLL_SCRIPT, 1)

fp.write_text(src, encoding="utf-8")
print("SUCCESS: scripts/build_upgraded_preview.py updated with medical holographic overlays!")
