"""Remove the extra box under/around the TB + Diabetes (db+tb) layer buttons in col-center."""
from pathlib import Path

fp = Path(r"c:\Users\LENOVO\OneDrive\Desktop\int 396 project\scripts\build_upgraded_preview.py")
src = fp.read_text(encoding="utf-8")

# Target block to clean up: remove #map-hint and the color key caption
OLD_CENTER_BLOCK = """    <!-- CENTER: LIVING AESTHETIC INDIA MAP -->
    <main class="col-center">

      <!-- HERO MISSION TAGLINE (SELF-CONTAINED IN CENTER, NEVER OVERLAPS) -->
      <div class="hero-tagline-bar">
        This tool helps you explore how TB spread differently across India's 36 states, using AI to find hidden patterns.
      </div>

      <!-- FIRST-TIMER ONBOARDING HINT (dismissable) -->
      <div id="map-hint" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.18);border-radius:10px;padding:9px 14px;margin-bottom:10px;font-size:0.82rem;color:#c0d8ff;display:flex;align-items:center;gap:10px;line-height:1.4;">
        <span style="font-size:1.1rem;">👆</span>
        <span><b style="color:#fff;">New here?</b> Pick a topic below, then <b style="color:#fff;">click any state</b> on the map to see its health details on the right →</span>
        <button onclick="document.getElementById('map-hint').style.display='none';localStorage.setItem('map-hint-dismissed','1');" style="margin-left:auto;background:none;border:1px solid rgba(255,255,255,0.3);color:#a0c4ff;border-radius:6px;padding:3px 10px;cursor:pointer;font-size:0.78rem;white-space:nowrap;">Got it ✓</button>
      </div>
      <script>if(localStorage.getItem('map-hint-dismissed')==='1'){{document.getElementById('map-hint').style.display='none';}}</script>

      <div class="map-layer-pills">
        <button class="layer-btn active" id="btn-dia" onclick="setLayer('dia')">🩺 TB + Diabetes</button>
        <button class="layer-btn" id="btn-tob" onclick="setLayer('tob')">🚬 TB + Tobacco</button>
        <button class="layer-btn" id="btn-alc" onclick="setLayer('alc')">🍷 TB + Alcohol</button>
        <button class="layer-btn" id="btn-clust" onclick="setLayer('cluster')">👥 Group Similar States</button>
      </div>

      <!-- COLOR KEY CAPTION -->
      <div style="font-size:0.76rem;color:#8aaabb;text-align:center;margin:4px 0 2px;letter-spacing:0.03em;">
        Lighter shade = fewer patients &nbsp;·&nbsp; Brighter/darker = more patients &nbsp;·&nbsp; Click any state for details
      </div>"""

NEW_CENTER_BLOCK = """    <!-- CENTER: LIVING AESTHETIC INDIA MAP -->
    <main class="col-center">

      <!-- HERO MISSION TAGLINE (SELF-CONTAINED IN CENTER, NEVER OVERLAPS) -->
      <div class="hero-tagline-bar">
        This tool helps you explore how TB spread differently across India's 36 states, using AI to find hidden patterns.
      </div>

      <div class="map-layer-pills">
        <button class="layer-btn active" id="btn-dia" onclick="setLayer('dia')">🩺 TB + Diabetes</button>
        <button class="layer-btn" id="btn-tob" onclick="setLayer('tob')">🚬 TB + Tobacco</button>
        <button class="layer-btn" id="btn-alc" onclick="setLayer('alc')">🍷 TB + Alcohol</button>
        <button class="layer-btn" id="btn-clust" onclick="setLayer('cluster')">👥 Group Similar States</button>
      </div>"""

assert OLD_CENTER_BLOCK in src, "OLD_CENTER_BLOCK not found"
src = src.replace(OLD_CENTER_BLOCK, NEW_CENTER_BLOCK, 1)

fp.write_text(src, encoding="utf-8")
print("SUCCESS: Removed extra boxes around db+tb controls!")
