"""Simplify left column filter chips — plain labels + section header."""
from pathlib import Path

fp = Path(__file__).resolve().parent / "build_upgraded_preview.py"
src = fp.read_text(encoding="utf-8")

# ── 1. Replace filter chips HTML ─────────────────────────────────────────────
OLD_CHIPS = """        <div class="filter-chips">
          <button class="filter-chip active" onclick="filterByGroup('all')">All (36)</button>
          <button class="filter-chip" onclick="filterByGroup('top10')">Top 10</button>
          <button class="filter-chip" onclick="filterByGroup('group-b')">Grp B (2)</button>
          <button class="filter-chip" onclick="filterByGroup('group-c')">Grp C (13)</button>
          <button class="filter-chip" onclick="filterByGroup('group-a')">Grp A (21)</button>
        </div>"""

NEW_CHIPS = """        <div class="lb-section-header">Filter states by group</div>
        <div class="filter-chips">
          <button class="filter-chip active" onclick="filterByGroup('all')">All States</button>
          <button class="filter-chip" onclick="filterByGroup('top10')">Top 10</button>
          <button class="filter-chip" onclick="filterByGroup('group-b')">Outliers</button>
          <button class="filter-chip" onclick="filterByGroup('group-c')">High Burden</button>
          <button class="filter-chip" onclick="filterByGroup('group-a')">Lower Burden</button>
        </div>"""

assert OLD_CHIPS in src, "HTML chips block not found"
src = src.replace(OLD_CHIPS, NEW_CHIPS, 1)

# ── 2. Add lb-section-header CSS after .filter-chips block ───────────────────
OLD_CSS = "  .filter-chips {{"
NEW_CSS = """  .lb-section-header {{
    font-size: 0.6rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
  }}
  .filter-chips {{"""

assert OLD_CSS in src, "CSS anchor not found"
src = src.replace(OLD_CSS, NEW_CSS, 1)

# ── 3. Slightly open up chip padding for readability ─────────────────────────
src = src.replace(
    "    padding: 3px 8px;\n    font-size: 0.65rem;",
    "    padding: 4px 10px;\n    font-size: 0.63rem;",
)

fp.write_text(src, encoding="utf-8")
print("Done — left column filter chips patched.")
