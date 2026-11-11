import json
import re
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(r"C:\Users\LENOVO\Desktop\int396 tb project")
sys.path.insert(0, str(ROOT))
from src.analysis import fit_clusters
from src.data import load_data, regional_data, regional_feature_matrix

df = load_data()
regions = regional_data(df)

# 1. Clusters (2023 Diabetes public + private, k=3)
raw, comp = regional_feature_matrix(df, 2023, "Diabetes", "public + private")
res, _, _ = fit_clusters(comp, "K-Means", clusters=3)
cluster_map = dict(zip(res["State / UT"], res["Cluster"]))

# 2. Diabetes notifications
dia = regions[(regions.year == 2023) & (regions.risk_factor == "Diabetes") & (regions.sector == "public + private")]
dia_p = dia["parameter"].iloc[0]
dia_dict = dict(zip(dia[dia.parameter == dia_p]["state"], dia[dia.parameter == dia_p]["value"]))

# Screened & diagnosed for Diabetes
dia_screen = regions[(regions.year == 2023) & (regions.risk_factor == "Diabetes") & (regions.sector == "public + private")]
dia_diag_p = [p for p in dia_screen.parameter.unique() if "diagnosed" in p.lower()]
dia_diag_dict = {}
if dia_diag_p:
    sub = dia_screen[dia_screen.parameter == dia_diag_p[0]]
    dia_diag_dict = dict(zip(sub["state"], sub["value"]))

# 3. Tobacco notifications (sector: 'total')
tob = regions[(regions.year == 2023) & (regions.risk_factor == "Tobacco") & (regions.sector == "total")]
if tob.empty:
    tob = regions[(regions.year == 2023) & (regions.risk_factor == "Tobacco")]
tob_p = tob["parameter"].iloc[0]
tob_dict = dict(zip(tob[tob.parameter == tob_p]["state"], tob[tob.parameter == tob_p]["value"]))

# 4. Alcohol notifications
alc = regions[(regions.year == 2023) & (regions.risk_factor == "Alcohol") & (regions.sector == "public + private")]
if alc.empty:
    alc = regions[(regions.year == 2023) & (regions.risk_factor == "Alcohol")]
alc_p = alc["parameter"].iloc[0]
alc_dict = dict(zip(alc[alc.parameter == alc_p]["state"], alc[alc.parameter == alc_p]["value"]))

# Build states master list sorted by Diabetes volume
all_states = sorted(regions["state"].unique())
ranked_states = sorted(all_states, key=lambda s: dia_dict.get(s, 0), reverse=True)

state_data = {}
for rank_idx, s in enumerate(ranked_states, 1):
    d_val = int(dia_dict.get(s, 0))
    t_val = int(tob_dict.get(s, 0))
    a_val = int(alc_dict.get(s, 0))
    c_grp = cluster_map.get(s, "Group B · Standard")
    
    # Regional zones
    zone = "NORTH INDIA"
    if s in ["Kerala", "Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Puducherry"]:
        zone = "SOUTH INDIA"
    elif s in ["Maharashtra", "Gujarat", "Goa", "Dadra & Nagar Haveli and Daman & Diu"]:
        zone = "WEST INDIA"
    elif s in ["Madhya Pradesh", "Chhattisgarh"]:
        zone = "CENTRAL INDIA"
    elif s in ["Bihar", "West Bengal", "Odisha", "Jharkhand"]:
        zone = "EAST INDIA"
    elif s in ["Assam", "Meghalaya", "Tripura", "Mizoram", "Manipur", "Nagaland", "Arunachal Pradesh", "Sikkim"]:
        zone = "NORTHEAST"

    state_data[s] = {
        "name": s,
        "rank": f"#{rank_idx}",
        "zone": zone,
        "dia": d_val,
        "tob": t_val,
        "alc": a_val,
        "cluster": c_grp,
    }

print(f"Extracted {len(state_data)} state records.")
output_json = ROOT / "data" / "preview_state_data.json"
output_json.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
print(f"Saved {output_json}")
