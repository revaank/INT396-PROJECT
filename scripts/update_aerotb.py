import sys
from pathlib import Path

target_file = Path(r"C:\Users\LENOVO\Desktop\int396 tb project\app\main.py")
code = target_file.read_text(encoding="utf-8")

# 1. Update display_map signature to support highlight_state
old_def = 'def display_map(plot_data, value_col, label="Reported count", color_col=None, height=650):'
new_def = 'def display_map(plot_data, value_col, label="Reported count", color_col=None, height=650, highlight_state=None):'
if old_def in code:
    code = code.replace(old_def, new_def)
    print("Updated display_map signature")
else:
    print("display_map signature already updated or not matched")

# 2. Add centroid extraction & scattergeo beacon to display_map
old_trace_end = '''        fig.update_geos(
            fitbounds="locations",'''

beacon_code = '''        if highlight_state:
            clean_target = _clean_geo_name(highlight_state)
            for feat in geo.get("features", []):
                raw_s = feat.get("properties", {}).get("shapeName", "")
                if _clean_geo_name(raw_s) == clean_target:
                    coords = feat.get("geometry", {}).get("coordinates", [])
                    lons, lats = [], []
                    def _extract(p):
                        for item in p:
                            if isinstance(item[0], (int, float)):
                                lons.append(item[0])
                                lats.append(item[1])
                            else:
                                _extract(item)
                    _extract(coords)
                    if lons and lats:
                        c_lon = sum(lons) / len(lons)
                        c_lat = sum(lats) / len(lats)
                        fig.add_trace(
                            go.Scattergeo(
                                lon=[c_lon],
                                lat=[c_lat],
                                mode="markers+text",
                                marker=dict(
                                    size=16,
                                    color="#00f2fe",
                                    symbol="circle",
                                    line=dict(width=3, color="#ffffff"),
                                ),
                                text=[f"📍 {highlight_state}"],
                                textposition="top center",
                                textfont=dict(color="#ffffff", size=13, family="Plus Jakarta Sans"),
                                hoverinfo="skip",
                                showlegend=False,
                            )
                        )
                    break

        fig.update_geos(
            fitbounds="locations",'''

if "if highlight_state:" not in code and old_trace_end in code:
    code = code.replace(old_trace_end, beacon_code, 1)
    print("Added beacon code to display_map")

# 3. Add CSS for scroll-stack storytelling
old_css_anchor = '/* 3D SCROLL STORY CARDS */'
new_css = '''/* ── SCROLL-STACK STORYTELLING CARDS ── */
.story-scroll-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 36px;
  max-width: 960px;
  margin: 0 auto;
  padding: 10px 0 50px 0;
}
.story-card-stack {
  position: sticky;
  background: rgba(13, 21, 39, 0.95);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid rgba(0, 242, 254, 0.28);
  border-radius: 24px;
  padding: 32px 36px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(0, 242, 254, 0.1);
  transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
.story-card-stack:hover {
  border-color: #00f2fe;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.9), 0 0 50px rgba(0, 242, 254, 0.25);
}
'''
if ".story-scroll-wrap" not in code and old_css_anchor in code:
    code = code.replace(old_css_anchor, new_css + "\n" + old_css_anchor, 1)
    print("Added CSS for scroll-stack")

# 4. Update Home layer calls to pass highlight_state=active_state
home_map_calls = [
    ('display_map(home_map_df, "AI Cluster Group", color_col="AI Cluster Group", height=580)',
     'display_map(home_map_df, "AI Cluster Group", color_col="AI Cluster Group", height=580, highlight_state=active_state)'),
    ('display_map(alc_slice, "value", label=f"Reported {first_param}", height=580)',
     'display_map(alc_slice, "value", label=f"Reported {first_param}", height=580, highlight_state=active_state)'),
    ('display_map(tob_slice, "value", label=f"Reported {first_param}", height=580)',
     'display_map(tob_slice, "value", label=f"Reported {first_param}", height=580, highlight_state=active_state)'),
    ('display_map(dia_slice, "value", label=f"Reported {first_param}", height=580)',
     'display_map(dia_slice, "value", label=f"Reported {first_param}", height=580, highlight_state=active_state)'),
]
for old_call, new_call in home_map_calls:
    if old_call in code:
        code = code.replace(old_call, new_call)
        print(f"Updated call: {old_call[:35]}...")

# 5. Update Screen 2 (Story cards) to use sticky scroll stack
old_story_section = """    # ── SCREEN 2: 3D SCROLL STORY SECTION ──
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.08);'><br>", unsafe_allow_html=True)
    st.markdown(
        \"\"\"
        <div style="text-align: center; margin-bottom: 30px;">
          <div class="hero-badge">Public Health Reality · The 3D Story</div>
          <h2 style="font-size: 2.2rem; font-weight: 800; color: #fff; letter-spacing: -0.02em;">Understanding India's Regional TB Challenge</h2>
          <p style="color: #94a3b8; max-width: 650px; margin: 8px auto 0; font-size: 0.95rem;">
            India's tuberculosis epidemic is not one single crisis — it is 36 distinct regional stories governed by population density, comorbidities, and healthcare reporting capacity.
          </p>
        </div>
        \"\"\",
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            \"\"\"
            <div class="aero-3d-card">
              <div style="font-size: 2.2rem; margin-bottom: 12px;">🫁</div>
              <h3 style="font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 10px;">Ancient, Airborne & 100% Curable</h3>
              <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.6;">
                TB bacteria have infected humans for over 9,000 years, spreading simply through the air when someone speaks or coughs. It is completely curable with antibiotics — yet <strong>India carries 27% of the entire world's cases</strong>.
              </p>
              <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 6px; background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.3); border-radius: 8px; padding: 5px 10px; font-size: 0.72rem; color: #00f2fe; font-weight: 700;">
                ⚡ Over 2.4 million Indians notified annually
              </div>
            </div>
            \"\"\",
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            \"\"\"
            <div class="aero-3d-card">
              <div style="font-size: 2.2rem; margin-bottom: 12px;">🔬</div>
              <h3 style="font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 10px;">The Secret Multipliers</h3>
              <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.6;">
                TB rarely attacks alone. <strong>Diabetes triples a patient's risk</strong> of developing active TB, while Tobacco and Alcohol destroy lung defenses and cause patients to drop out of treatment before being cured.
              </p>
              <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 6px; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); border-radius: 8px; padding: 5px 10px; font-size: 0.72rem; color: #38bdf8; font-weight: 700;">
                ⚡ 1 in 5 TB patients has co-occurring conditions
              </div>
            </div>
            \"\"\",
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            \"\"\"
            <div class="aero-3d-card">
              <div style="font-size: 2.2rem; margin-bottom: 12px;">⚖️</div>
              <h3 style="font-size: 1.25rem; font-weight: 800; color: #fff; margin-bottom: 10px;">36 States · 36 Crises</h3>
              <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.6;">
                Treating Kerala's aging, high-diabetes TB population with the exact same budget as Uttar Pradesh's dense young workforce guarantees failure. <strong>One size does not fit all.</strong>
              </p>
              <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 6px; background: rgba(168,237,234,0.1); border: 1px solid rgba(168,237,234,0.3); border-radius: 8px; padding: 5px 10px; font-size: 0.72rem; color: #a8edea; font-weight: 700;">
                ⚡ AI clusters states for tailored policy funding
              </div>
            </div>
            \"\"\",
            unsafe_allow_html=True,
        )"""

new_story_section = """    # ── SCREEN 2: SCROLL-DRIVEN 3D STORYTELLING SECTION ──
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.08);'><br>", unsafe_allow_html=True)
    st.markdown(
        \"\"\"
        <div style="text-align: center; margin-bottom: 34px;">
          <div class="hero-badge" style="margin-bottom: 10px;">Public Health Reality · Continuous Scroll Transitions</div>
          <h2 style="font-size: 2.3rem; font-weight: 800; color: #fff; letter-spacing: -0.02em;">Understanding India's Regional TB Challenge</h2>
          <p style="color: #94a3b8; max-width: 680px; margin: 8px auto 0; font-size: 0.95rem; line-height: 1.6;">
            India's tuberculosis epidemic is not one single crisis — scroll down to explore how clinical multipliers and regional heterogeneity shape the national landscape before reaching the analytical suites.
          </p>
        </div>

        <div class="story-scroll-wrap">
          <!-- CARD 1: STICKY AT 100px -->
          <div class="story-card-stack" style="top: 100px; z-index: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <span class="hero-badge" style="margin-bottom: 0;">Discovery 01 · Biological Reality</span>
              <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #64748b; font-weight: 700;">01 / 03 · AIRBORNE TRANSMISSION</span>
            </div>
            <h3 style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; margin-bottom: 12px;">🫁 Ancient, Airborne & 100% Curable</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px;">
              <div style="background: rgba(15,23,42,0.65); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px 16px;">
                <div style="color: #00f2fe; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">Ancient Pathogen</div>
                <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.55;">
                  Mycobacterium tuberculosis has infected humans for over 9,000 years — genetic traces exist in ancient Egyptian mummies.
                </div>
              </div>
              <div style="background: rgba(15,23,42,0.65); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px 16px;">
                <div style="color: #38bdf8; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">Silent Droplets</div>
                <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.55;">
                  Spreads silently through microscopic air droplets when someone speaks, coughs, or laughs. Anyone breathing air can be exposed.
                </div>
              </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,242,254,0.08); border: 1px solid rgba(0,242,254,0.25); border-radius: 12px; padding: 12px 18px;">
              <div style="font-size: 0.85rem; color: #cbd5e1;"><strong style="color: #fff;">100% Curable:</strong> A disciplined 6-month first-line antibiotic course fully cures the patient.</div>
              <div style="font-size: 0.78rem; font-weight: 800; color: #00f2fe;">India: 27% of World TB Burden (>2.4M cases/yr)</div>
            </div>
          </div>

          <!-- CARD 2: STICKY AT 140px (SLIDES OVER CARD 1) -->
          <div class="story-card-stack" style="top: 140px; z-index: 2;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <span class="hero-badge" style="margin-bottom: 0; color: #38bdf8; border-color: rgba(56,189,248,0.35); background: rgba(56,189,248,0.1);">Discovery 02 · Clinical Comorbidity</span>
              <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #64748b; font-weight: 700;">02 / 03 · IMMUNITY SUPPRESSION</span>
            </div>
            <h3 style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; margin-bottom: 12px;">🔬 The Secret Multipliers</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px;">
              <div style="background: rgba(15,23,42,0.65); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px 16px;">
                <div style="color: #38bdf8; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">Diabetes Multiplier (3x)</div>
                <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.55;">
                  Diabetes triples active TB contraction risk and delays lung sputum conversion. Blood sugar control is indispensable.
                </div>
              </div>
              <div style="background: rgba(15,23,42,0.65); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px 16px;">
                <div style="color: #f6d365; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">Tobacco & Alcohol</div>
                <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.55;">
                  Smoking doubles relapse risk; heavy alcohol consumption triggers treatment abandonment before bacterial eradication.
                </div>
              </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(56,189,248,0.08); border: 1px solid rgba(56,189,248,0.25); border-radius: 12px; padding: 12px 18px;">
              <div style="font-size: 0.85rem; color: #cbd5e1;"><strong style="color: #fff;">Bidirectional Screening:</strong> Mandatory national testing for Diabetes in every TB patient.</div>
              <div style="font-size: 0.78rem; font-weight: 800; color: #38bdf8;">Metabolic + Infectious Health Strategy</div>
            </div>
          </div>

          <!-- CARD 3: STICKY AT 180px (SLIDES OVER CARD 2) -->
          <div class="story-card-stack" style="top: 180px; z-index: 3;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
              <span class="hero-badge" style="margin-bottom: 0; color: #a8edea; border-color: rgba(168,237,234,0.35); background: rgba(168,237,234,0.1);">Discovery 03 · Regional Intelligence</span>
              <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #64748b; font-weight: 700;">03 / 03 · PATTERN CLUSTERING</span>
            </div>
            <h3 style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; margin-bottom: 12px;">⚖️ 36 States · 36 Unique Crises</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 18px;">
              <div style="background: rgba(15,23,42,0.65); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px 16px;">
                <div style="color: #a8edea; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">Demographic Variance</div>
                <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.55;">
                  Kerala manages an aging demographic with high diabetes; Uttar Pradesh handles immense absolute volume across dense districts.
                </div>
              </div>
              <div style="background: rgba(15,23,42,0.65); border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 14px 16px;">
                <div style="color: #fda085; font-size: 0.72rem; font-weight: 800; text-transform: uppercase; margin-bottom: 4px;">Northeastern Hotspots</div>
                <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.55;">
                  Mizoram and Nagaland exhibit specialized tobacco-linked notification patterns requiring localized district initiatives.
                </div>
              </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(168,237,234,0.08); border: 1px solid rgba(168,237,234,0.25); border-radius: 12px; padding: 12px 18px;">
              <div style="font-size: 0.85rem; color: #cbd5e1;"><strong style="color: #fff;">Unsupervised AI:</strong> Clustering states by multivariate similarity rather than administrative borders.</div>
              <div style="font-size: 0.78rem; font-weight: 800; color: #a8edea;">AeroTB Pattern Intelligence</div>
            </div>
          </div>
        </div>
        \"\"\",
        unsafe_allow_html=True,
    )"""

if old_story_section in code:
    code = code.replace(old_story_section, new_story_section)
    print("Replaced story section with scroll-stack scrollytelling")
else:
    print("Could not match exact old_story_section, checking partial match")

target_file.write_text(code, encoding="utf-8")
print("Finished writing app/main.py")
