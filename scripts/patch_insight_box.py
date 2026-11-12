"""Insert plain-English insight box and update JS to populate it dynamically."""
from pathlib import Path

fp = Path(__file__).resolve().parent / "build_upgraded_preview.py"
src = fp.read_text(encoding="utf-8")

# ── 1. Insert insight-box HTML between twins-box and card-action-bar ──────────
OLD_HTML = "        <!-- ACTION BUTTONS -->"
NEW_HTML = """        <!-- PLAIN ENGLISH SUMMARY -->
        <div class="insight-box" id="t-insight">
          <div class="insight-title">💡 What this tells you</div>
          <div class="insight-text" id="t-insight-text">
            Maharashtra reports <strong>significantly more TB cases</strong> than the average Indian state. It is grouped with other high-burden states — meaning its health challenges are <strong>similar to states like Karnataka and Gujarat</strong>. Use "Explore Similarity" below to compare them side by side.
          </div>
        </div>

        <!-- ACTION BUTTONS -->"""
assert OLD_HTML in src, "HTML anchor not found"
src = src.replace(OLD_HTML, NEW_HTML, 1)

# ── 2. Add insight-box CSS after .twins-box strong rule ───────────────────────
OLD_CSS = "  .twins-box strong {{ color: #94a3b8; }}"
NEW_CSS = """  .twins-box strong {{ color: #94a3b8; }}

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
  .insight-text strong {{ color: #94a3b8; }}"""
assert OLD_CSS in src, "CSS anchor not found"
src = src.replace(OLD_CSS, NEW_CSS, 1)

# ── 3. Remove margin-top: auto from card-action-bar (flex:1 on insight-box handles spacing) ──
src = src.replace(
    "  .card-action-bar {{\n    margin-top: auto;\n    padding-top: 10px;",
    "  .card-action-bar {{\n    padding-top: 10px;",
)

# ── 4. Add JS to update insight text when a state is clicked ─────────────────
# Insert after the tTwins block (we'll look for the last tTwins assignment)
OLD_JS = "    else tTwins.innerHTML = 'Most Similar States (Health Twins): Very similar baseline —"
NEW_JS = """    else tTwins.innerHTML = 'Most Similar States (Health Twins): Very similar baseline —"""

# We want to inject insight updater after the whole twins block — find the closing of that block
TWINS_END = "    else tTwins.innerHTML = 'Most Similar States (Health Twins): Very similar baseline —"
# Find it and append insight update after the line
insight_js = """
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
        insightMsg = sName + ' is a <strong>high-burden state</strong> — it has significantly more TB cases than average and shares a similar pattern with other major states. Use "Explore Similarity" to compare.';
      }} else {{
        insightMsg = sName + ' has a <strong>relatively lower TB burden</strong> compared to major states. It is grouped with similar smaller-burden states across India.';
      }}
      tInsightText.innerHTML = insightMsg;
    }}"""

# Find a unique anchor after all tTwins assignments
AFTER_TWINS = "    // Progress Bars"
assert AFTER_TWINS in src, f"JS anchor not found: {AFTER_TWINS}"
src = src.replace(AFTER_TWINS, insight_js + "\n\n    // Progress Bars", 1)

fp.write_text(src, encoding="utf-8")
print("Done — insight-box patch applied.")
