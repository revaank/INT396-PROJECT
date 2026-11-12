"""Patch plain-language label changes into build_upgraded_preview.py"""
from pathlib import Path

fp = Path(__file__).resolve().parent / "build_upgraded_preview.py"
src = fp.read_text(encoding="utf-8")

# 1. Simplify static twins-box default text
src = src.replace(
    "Nearest Pattern Twins: Closest mathematical proximity to <strong>Gujarat &amp; Rajasthan</strong>.",
    "Most Similar States (Health Twins): Closest match to <strong>Gujarat &amp; Rajasthan</strong>.",
)

# 2. Simplify JS dynamic twins strings
src = src.replace(
    "tTwins.innerHTML = 'Nearest Pattern Twins: Closest multivariate proximit",
    "tTwins.innerHTML = 'Most Similar States: Closest multivariate match — proximit",
)
# More surgical: just replace the leading "Nearest Pattern Twins:" everywhere in JS
src = src.replace(
    "'Nearest Pattern Twins: Closest multivariate proximit",
    "'Most Similar States (Health Twins): Closest match — proximit",
)
src = src.replace(
    "'Nearest Pattern Twins: Co-outlier alignment w",
    "'Most Similar States (Health Twins): Co-pattern states — w",
)
src = src.replace(
    "'Nearest Pattern Twins: Co-outlier trajectory w",
    "'Most Similar States (Health Twins): Co-pattern trajectory — w",
)
src = src.replace(
    "'Nearest Pattern Twins: Highly cohesive distanc",
    "'Most Similar States (Health Twins): Highly similar pattern — distanc",
)
src = src.replace(
    "'Nearest Pattern Twins: Homogeneous baseline distance to",
    "'Most Similar States (Health Twins): Very similar baseline —",
)

# 3. Simplify cluster chip title
src = src.replace(
    "<div class=\"cluster-chip-title\">Assigned Health Team (AI Similarity)</div>",
    "<div class=\"cluster-chip-title\">Which Group Does This State Belong To?</div>",
)

fp.write_text(src, encoding="utf-8")
print("Done — patch applied.")
