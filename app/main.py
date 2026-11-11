from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analysis import describe_pattern, fit_clusters
from src.data import DATA_PATH, get_quality_summary, load_data, regional_data, regional_feature_matrix


st.set_page_config(page_title="TB Insight | India", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --navy:#07151e; --panel:#0d202b; --panel2:#112a36; --teal:#49d3c1; --muted:#91a7b1; }
.stApp { background: radial-gradient(ellipse at 84% 0%, #123a43 0%, #07151e 42%); color:#eff7f6; font-family:'DM Sans',sans-serif; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#081922,#0c202b); border-right:1px solid #203c46; }
[data-testid="stSidebar"] * { color:#e6f0ee; }
h1,h2,h3 { font-family:'Manrope',sans-serif!important; letter-spacing:-.035em; }
h1 { font-weight:800!important; } h2,h3 { font-weight:700!important; }
.hero { padding:34px 38px; border:1px solid #22414a; border-radius:24px; background:linear-gradient(120deg,rgba(19,56,66,.93),rgba(10,29,39,.83)); margin:8px 0 22px; position:relative; overflow:hidden; }
.hero:after { content:'◈'; position:absolute; right:36px; top:-50px; font-size:230px; color:rgba(73,211,193,.08); }
.eyebrow { color:#65dfcf; text-transform:uppercase; letter-spacing:.18em; font-size:.72rem; font-weight:700; }
.hero h1 { font-size:2.5rem; margin:.35rem 0; color:#f3fbf9; }
.hero p { color:#b0c4c8; max-width:720px; font-size:1.03rem; margin:0; }
.metric { background:linear-gradient(145deg,#102732,#0b1d27); border:1px solid #23424b; padding:20px 22px; border-radius:18px; min-height:108px; }
.metric-label { color:#9bb1b8; font-size:.78rem; text-transform:uppercase; letter-spacing:.09em; }
.metric-value { color:#ecfaf7; font:800 1.75rem 'Manrope'; margin-top:7px; }
.metric-sub { color:#63dccc; font-size:.78rem; margin-top:3px; }
.section-kicker {color:#63dccc; font-size:.75rem; text-transform:uppercase; letter-spacing:.15em; font-weight:700; margin:20px 0 4px;}
.note { border-left:3px solid #45cdbc; background:#102832; padding:12px 16px; border-radius:4px 12px 12px 4px; color:#bfd0d2; }
.stButton>button { border:1px solid #347c7b; background:#133c43; color:#effcf9; border-radius:10px; }
div[data-testid="stMetric"] { background:#0d202b; border:1px solid #23424b; padding:14px; border-radius:14px; }
div[data-testid="stMetricLabel"] { color:#9bb1b8; }
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)


def header(kicker: str, title: str, subtitle: str = ""):
    st.markdown(f'<div class="hero"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def metric(label: str, value: str, sub: str = ""):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_data():
    return load_data()


try:
    df = get_data()
except (FileNotFoundError, ValueError, OSError) as exc:
    st.error(f"The dataset could not be loaded: {exc}")
    st.stop()

regions = regional_data(df)
quality = get_quality_summary(df)
pages = ["Home", "Explore India", "Compare States", "ML Intelligence", "Research Insights", "AI Explainer", "TB Knowledge Centre", "Find Help & About"]
with st.sidebar:
    st.markdown("## ◈ TB Insight")
    st.caption("REGIONAL PATTERN INTELLIGENCE")
    page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.markdown("---")
    st.caption(f"DATA WINDOW · {min(quality['years'])}–{max(quality['years'])}")
    st.caption("Exploratory public health analytics")
    st.markdown('<div class="note">Aggregated notifications only. This platform does not assess any person\'s TB status.</div>', unsafe_allow_html=True)


def selection_controls(key_prefix="sel"):
    years = [int(y) for y in quality["years"]]
    a, b, c, d = st.columns(4)
    year = a.selectbox("Year", years, index=len(years)-1, key=f"{key_prefix}_year")
    factor = b.selectbox("Risk factor", sorted(regions.risk_factor.dropna().unique()), key=f"{key_prefix}_factor")
    sectors = sorted(regions.loc[(regions.year == year) & (regions.risk_factor == factor), "sector"].dropna().unique())
    sector = c.selectbox("Reporting sector", sectors, key=f"{key_prefix}_sector")
    params = sorted(regions.loc[(regions.year == year) & (regions.risk_factor == factor) & (regions.sector == sector), "parameter"].dropna().unique())
    parameter = d.selectbox("Indicator", params, key=f"{key_prefix}_parameter")
    return year, factor, sector, parameter


def display_map(plot_data, value, label="Reported count"):
    geo_path = ROOT / "data" / "raw" / "dataful_20833" / "india_admin1.geojson"
    if not geo_path.exists():
        st.info("The interactive state map needs the boundary file. Run `START_TB_INSIGHT.bat` with an internet connection; it downloads the attributed 2011 geoBoundaries state boundaries once.")
        return
    try:
        geo = json.loads(geo_path.read_text(encoding="utf-8"))
        geo_names = {feature.get("properties", {}).get("shapeName", "") for feature in geo.get("features", [])}
        match = plot_data[plot_data.state.isin(geo_names)]
        if match.empty:
            st.warning("The downloaded map boundaries do not match the selected state names, so the map is hidden.")
            return
        fig = px.choropleth(match, geojson=geo, locations="state", featureidkey="properties.shapeName", color=value,
                            color_continuous_scale=[[0,"#143c48"],[.5,"#278f91"],[1,"#8df2d7"]],
                            hover_name="state", hover_data={value:":,.0f"}, labels={value:label})
        fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
        fig.update_layout(height=500, margin=dict(l=0,r=0,t=5,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dcebea", coloraxis_colorbar=dict(title=label))
        st.plotly_chart(fig, use_container_width=True)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.warning(f"State boundaries could not be rendered: {exc}")


if page == "Home":
    header("India · State & Union Territory Patterns", "TB Insight", "A clear, data-grounded view of reported tuberculosis indicators across India's regions. Designed for exploration, comparison, and careful interpretation.")
    cols = st.columns(4)
    with cols[0]: metric("Regions in dataset", f"{quality['regions']}", "State and UT labels; All India excluded")
    with cols[1]: metric("Years available", f"{len(quality['years'])}", f"{min(quality['years'])}–{max(quality['years'])}")
    with cols[2]: metric("Reported indicators", f"{regions.parameter.nunique()}", "Across four factor groups")
    with cols[3]: metric("Source records", f"{quality['rows']:,}", "Purchased Dataful extract")
    st.markdown('<div class="section-kicker">A platform for careful exploration</div>', unsafe_allow_html=True)
    left, right = st.columns([1.3,1])
    with left:
        st.subheader("What you can explore")
        st.markdown("**Explore India** to inspect reported counts for one indicator, see its geographic pattern, and open a state profile.  \n**Compare States** to view like-for-like indicator trends across selected regions.  \n**ML Intelligence** to group regions by their pattern across a selected risk-factor group, with preprocessing and evaluation shown alongside the result.")
    with right:
        st.subheader("At a glance")
        years = regions.groupby("year", as_index=False).agg(regions_reporting=("state","nunique"), nonmissing=("value","count"))
        fig = px.line(years,x="year",y="regions_reporting",markers=True,labels={"year":"Year","regions_reporting":"Regions with records"})
        fig.update_traces(line_color="#55d8c7",marker_size=9)
        fig.update_layout(height=250,margin=dict(l=0,r=0,t=10,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#dcebea")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="note">Notifications are not the same as true incidence or prevalence. All dataset values are absolute counts, not population-adjusted rates. Larger counts do not by themselves mean higher risk.</div>',unsafe_allow_html=True)

elif page == "Explore India":
    header("Explore India", "One indicator. Every region.", "Filter by year, reporting sector, factor, and indicator. The map displays reported counts only.")
    year, factor, sector, parameter = selection_controls("explore")
    view = regions.loc[(regions.year == year) & (regions.risk_factor == factor) & (regions.sector == sector) & (regions.parameter == parameter)].copy()
    st.markdown(f"**{parameter}** · {factor} · {sector} · {year} · *{(view.unit.iloc[0] if not view.empty else 'unit unavailable')}*")
    left, right = st.columns([1.05,1])
    with left:
        display_map(view, "value")
    with right:
        sort = view.dropna(subset=["value"]).sort_values("value",ascending=True)
        fig = px.bar(sort,x="value",y="state",orientation="h",labels={"value":"Reported count","state":"State / UT"},color="value",color_continuous_scale=["#1b6570","#56d5c2"])
        fig.update_layout(height=500,margin=dict(l=0,r=0,t=5,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#dcebea",showlegend=False,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    states = sorted(view.state.unique())
    if states:
        chosen = st.selectbox("Open a state profile", states, key="explore_profile")
        profile = regions.loc[(regions.state==chosen)&(regions.year==year)&(regions.sector==sector)]
        st.subheader(chosen)
        st.dataframe(profile[["risk_factor","parameter","value","unit"]].sort_values(["risk_factor","parameter"]),use_container_width=True,hide_index=True)

elif page == "Compare States":
    header("Compare States", "Compare like with like", "Select one measure and up to six regions. The trend preserves the dataset's sector and unit definitions.")
    factor=st.selectbox("Risk factor",sorted(regions.risk_factor.unique()),key="compare_factor")
    parameter=st.selectbox("Indicator",sorted(regions.loc[regions.risk_factor==factor,"parameter"].unique()),key="compare_parameter")
    sectors=sorted(regions.loc[(regions.risk_factor==factor)&(regions.parameter==parameter),"sector"].unique())
    sector=st.selectbox("Reporting sector",sectors,key="compare_sector")
    options=sorted(regions.state.unique())
    defaults=[x for x in ["Maharashtra","Uttar Pradesh","Tamil Nadu"] if x in options]
    selected=st.multiselect("States / UTs (up to 6)",options,default=defaults[:3],max_selections=6)
    trend=regions.loc[(regions.risk_factor==factor)&(regions.parameter==parameter)&(regions.sector==sector)&(regions.state.isin(selected))].dropna(subset=["value"])
    if not trend.empty:
        fig=px.line(trend,x="year",y="value",color="state",markers=True,labels={"year":"Year","value":"Reported count","state":"State / UT"},color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(height=480,margin=dict(l=0,r=0,t=20,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#dcebea",legend_title_text="State / UT")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(trend.pivot(index="year",columns="state",values="value").reset_index(),use_container_width=True,hide_index=True)
        st.caption("Missing values are omitted from the line; they are not interpreted as zero.")
    else:
        st.info("Choose at least one region with reported values for this indicator.")

elif page == "ML Intelligence":
    header("ML Intelligence", "Patterns across regions", "Explore unsupervised groupings of comparable state-level counts. These are descriptive clusters, not risk scores.")
    years=[int(y) for y in quality["years"]]
    a,b,c=st.columns(3)
    year=a.selectbox("Year",years,index=len(years)-1,key="ml_year")
    factors=sorted(regions.loc[regions.year==year,"risk_factor"].unique())
    factor=b.selectbox("Risk factor",factors,key="ml_factor")
    sector=c.selectbox("Reporting sector",sorted(regions.loc[(regions.year==year)&(regions.risk_factor==factor),"sector"].unique()),key="ml_sector")
    raw, complete=regional_feature_matrix(df,year,factor,sector)
    if raw.empty:
        st.warning("No state-level records match this selection.")
    else:
        st.markdown(f"**Comparable indicators:** {raw.shape[1]} · **Regions with any records:** {raw.shape[0]} · **Complete feature rows used:** {complete.shape[0]} · **Rows omitted for missing features:** {raw.shape[0]-complete.shape[0]}")
        if raw.shape[1]<2:
            st.warning("This selection has fewer than two indicators, so meaningful multivariate clustering is unavailable.")
        elif complete.shape[0]<4:
            st.warning("Fewer than four complete regions remain. Choose another year, factor, or sector.")
        else:
            method=st.selectbox("Method",["K-Means","Agglomerative","DBSCAN"])
            if method in ["K-Means","Agglomerative"]:
                k=st.slider("Number of clusters",2,min(6,complete.shape[0]-1),min(3,complete.shape[0]-1))
                eps,min_samples=.9,4
            else:
                u,v=st.columns(2)
                eps=u.slider("DBSCAN eps (standardized distance)",0.2,3.0,0.9,0.1)
                min_samples=v.slider("Minimum points",2,min(10,complete.shape[0]),min(4,complete.shape[0]))
                k=3
            try:
                result,metrics=fit_clusters(complete,method,clusters=k,eps=eps,min_samples=min_samples)
                m=st.columns(6)
                for col,(label,value) in zip(m,metrics.items()):
                    col.metric(label, f"{value:.3f}" if isinstance(value,float) else value if value is not None else "Not defined")
                st.caption("Silhouette: higher is better; Davies–Bouldin: lower is better; Calinski–Harabasz: higher is better. Metrics are omitted when the partition is invalid or includes DBSCAN noise. Compare scores only for the same feature selection.")
                fig=px.scatter(result,x="PC1",y="PC2",color="Cluster",hover_name="State / UT",color_discrete_sequence=["#54d6c4","#4c8ed1","#e9a34b","#bd77d7","#e46b79","#97bd62"])
                fig.update_layout(height=430,margin=dict(l=0,r=0,t=18,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#dcebea",legend_title_text="Cluster")
                st.plotly_chart(fig,use_container_width=True)
                st.dataframe(result[["State / UT","Cluster"]].sort_values(["Cluster","State / UT"]),use_container_width=True,hide_index=True)
                profiled = complete.copy()
                profiled["Cluster"] = result.set_index("State / UT")["Cluster"].reindex(profiled.index)
                cluster_profile = profiled.groupby("Cluster", observed=True)[complete.columns].median().round(1)
                st.subheader("How the groups differ")
                st.write("These are median reported counts for each selected feature within each cluster. A higher count is a larger reported count, not a higher population-adjusted risk.")
                st.dataframe(cluster_profile,use_container_width=True)
                st.caption("PCA compresses the standardized indicators to two axes for display. The projection is a visual summary and does not prove the cluster structure is valid. K-Means uses random_state=42.")
                with st.expander("Features used"):
                    st.dataframe(complete.reset_index(),use_container_width=True,hide_index=True)
            except ValueError as exc:
                st.warning(str(exc))
    st.markdown('<div class="note">Absolute counts are not adjusted for population. Complete cases are used; no missing values are filled with zero. Since indicator values can reflect screening and reporting coverage, cluster labels describe patterns in this dataset only.</div>',unsafe_allow_html=True)

elif page == "Research Insights":
    header("Research Insights", "What the data shows", "Summaries recalculate from the source records and the filters you choose. Counts are not population-adjusted rates.")
    year,factor,sector,parameter=selection_controls("insight")
    view=regions.loc[(regions.year==year)&(regions.risk_factor==factor)&(regions.sector==sector)&(regions.parameter==parameter)].dropna(subset=["value"])
    st.subheader(f"{factor}: {parameter}")
    st.write(describe_pattern(view))
    if len(view)>=5:
        median=view.value.median()
        deviations=(view.value-median).abs()
        mad=deviations.median()
        if mad>0:
            view=view.assign(robust_z=0.6745*(view.value-median)/mad)
            anomalies=view.loc[view.robust_z.abs()>=3.5].sort_values("robust_z",key=abs,ascending=False)
            if anomalies.empty:
                st.info("No observations crossed the descriptive robust-z threshold (absolute robust z ≥ 3.5) for this selection.")
            else:
                st.subheader("Unusual values to review")
                st.dataframe(anomalies[["state","value","robust_z"]].rename(columns={"state":"State / UT","value":"Count","robust_z":"Robust z-score"}),use_container_width=True,hide_index=True)
                st.caption("A statistical flag is not an error finding or a risk classification; it only identifies values far from this selection's median.")
    years=sorted(int(y) for y in regions.year.unique())
    trajectory=regions.loc[(regions.risk_factor==factor)&(regions.parameter==parameter)&(regions.sector==sector)].dropna(subset=["value"])
    agg=trajectory.groupby("year").value.agg(["median","count"]).reset_index()
    if not agg.empty:
        st.subheader("Across-year context")
        fig=px.line(agg,x="year",y="median",markers=True,labels={"year":"Year","median":"Median state/UT count"})
        fig.update_traces(line_color="#55d8c7",marker_size=9)
        fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#dcebea")
        st.plotly_chart(fig,use_container_width=True)
        st.caption("The number of reporting regions can vary by year; see the table to interpret each median.")
        st.dataframe(agg.rename(columns={"year":"Year","median":"Median count","count":"Regions with values"}),use_container_width=True,hide_index=True)

elif page == "AI Explainer":
    header("AI Explainer", "Plain language, grounded in the data", "Select what you are looking at and get a transparent explanation based on the actual rows, without an external AI service or hidden claims.")
    year,factor,sector,parameter=selection_controls("explain")
    view=regions.loc[(regions.year==year)&(regions.risk_factor==factor)&(regions.sector==sector)&(regions.parameter==parameter)]
    topic=st.radio("Explain",["An indicator","A state comparison","A clustering method"],horizontal=True)
    if topic=="An indicator":
        st.subheader("What this chart means")
        st.info(describe_pattern(view))
        missing=int(view.value.isna().sum())
        st.write(f"This selection covers {view.state.nunique()} state/UT labels, with {view.value.notna().sum()} reported values and {missing} blank values. Blank values are left blank; they are not treated as zero.")
    elif topic=="A state comparison":
        picks=st.multiselect("States / UTs",sorted(regions.state.unique()),default=[s for s in ["Maharashtra","Uttar Pradesh"] if s in set(regions.state)],max_selections=6,key="explain_states")
        trend=regions.loc[(regions.risk_factor==factor)&(regions.parameter==parameter)&(regions.sector==sector)&(regions.state.isin(picks))].dropna(subset=["value"])
        if trend.empty:
            st.info("Select regions with reported values for the current indicator.")
        else:
            summary=trend.sort_values("year").groupby("state").agg(first_year=("year","min"),last_year=("year","max"),first_count=("value","first"),last_count=("value","last"),years_reported=("year","nunique")).reset_index()
            summary["count_change"] = summary["last_count"]-summary["first_count"]
            st.write("The table compares each selected region's first and last available reported values for this indicator. Gaps in years are not filled.")
            st.dataframe(summary.rename(columns={"state":"State / UT","first_year":"First year","last_year":"Last year","first_count":"First count","last_count":"Last count","years_reported":"Years reported","count_change":"Count difference"}),use_container_width=True,hide_index=True)
            st.caption("A change in absolute counts is not a change in per-person risk; population, screening, and reporting can change too.")
    else:
        ml_year=st.selectbox("Clustering year",[int(y) for y in quality["years"]],index=len(quality["years"])-1,key="explain_ml_year")
        ml_factor=st.selectbox("Clustering factor",sorted(regions.loc[regions.year==ml_year,"risk_factor"].unique()),key="explain_ml_factor")
        ml_sector=st.selectbox("Clustering sector",sorted(regions.loc[(regions.year==ml_year)&(regions.risk_factor==ml_factor),"sector"].unique()),key="explain_ml_sector")
        raw,complete=regional_feature_matrix(df,ml_year,ml_factor,ml_sector)
        st.write(f"The feature table has {raw.shape[1]} selected indicators. Of {raw.shape[0]} regions, {len(complete)} are complete across all selected indicators; {raw.shape[0]-len(complete)} are excluded because at least one value is missing.")
        st.write("The clustering method groups regions by similarity after standardizing the selected absolute counts. Standardization puts features on comparable scales; it does not convert them to rates. Cluster numbers are arbitrary, PCA is a visual summary, and the grouping is not a risk classification or a causal finding.")

elif page == "TB Knowledge Centre":
    header("TB Knowledge Centre", "Learn about tuberculosis", "A concise educational guide linked to official public-health sources. Content is general awareness, not personal medical advice.")
    left,right=st.columns(2)
    with left:
        st.subheader("What is TB?")
        st.write("Tuberculosis is an infectious disease caused by bacteria. It most often affects the lungs, though it can affect other parts of the body. TB is preventable and treatable; people with symptoms should seek assessment from a qualified health professional.")
        st.subheader("How it spreads")
        st.write("TB bacteria can spread through the air when someone with infectious TB disease coughs or sneezes. Risk depends on exposure and individual circumstances; a regional notification count cannot tell whether a particular person has TB.")
    with right:
        st.subheader("Symptoms that need assessment")
        st.write("A cough that persists, fever, night sweats, weight loss, or coughing blood can have different causes. Seek medical advice for concerning symptoms, especially if they continue or worsen.")
        st.subheader("Factors associated with TB")
        st.write("Close exposure, undernutrition, diabetes, tobacco use, harmful alcohol use, HIV, and other conditions may affect the chance of developing TB disease. This dataset reports selected program indicators about TB patients and screening; it does not estimate an individual's risk or prove that a factor caused TB.")
    st.markdown("### Official learning resources")
    st.markdown("- [WHO: Tuberculosis fact sheet](https://www.who.int/news-room/fact-sheets/detail/tuberculosis)\n- [India National TB Elimination Programme](https://tbcindia.mohfw.gov.in/)\n- [Ni-kshay portal](https://nikshay.in/)")

else:
    header("Find Help & About", "Sources, methods, and limits", "Transparent provenance and practical contact routes for people seeking information or care.")
    st.subheader("Find official help")
    st.markdown("- [India National TB Elimination Programme](https://tbcindia.mohfw.gov.in/)\n- [Ni-kshay portal](https://nikshay.in/)\n- Contact a government health facility or qualified clinician for symptoms or treatment questions.")
    st.subheader("Dataset")
    st.write("Ministry of Health and Family Welfare, annual reports (2019–2023), republished by Dataful as **Year, State, Sector and Risk Factor wise cases of TB**, dataset 20833. The metadata describes annual state-level counts and absolute-number units.")
    st.markdown("[Dataful dataset and citation](https://dataful.in/datasets/20833/20833) · [Original annual reports](https://tbcindia.mohfw.gov.in/annual-reports/)")
    st.write(f"Observed years: {', '.join(map(str,quality['years']))}. State/UT names excluding All India: {quality['regions']}. Rows: {quality['rows']:,}. Missing value cells: {quality['missing_values']}. Blank note cells: {quality['blank_notes']:,}. Duplicate composite key rows: {quality['duplicate_keys']}. Negative values: {quality['negative_values']}.")
    st.write("The metadata does not specify a license in the supplied archive; attribution is provided and terms should be confirmed with the publisher for redistribution. The archive was supplied by the user; retrieval date from the original publisher is not available here.")
    st.subheader("Methodology")
    st.write("The dashboard filters source records without treating blanks as zero. Comparisons hold indicator, sector, and unit definition constant. Clustering excludes the All India aggregate, keeps rows complete across selected indicators, standardizes feature columns, and evaluates only valid partitions. PCA is a display aid.")
    st.subheader("Limitations")
    st.write("All values are absolute counts, with no population denominator. Notifications are not the same as incidence or prevalence. Missingness and reporting coverage can affect comparisons. Some indicator definitions or coverage may vary across years; comparisons should remain cautious. The app is an exploratory academic tool, not a diagnostic, individual risk prediction, or causal analysis.")
    st.subheader("Map source")
    st.markdown("State boundaries are sourced separately from [geoBoundaries open India ADM1](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/), a 2011 boundary representation based on DataMeet India community and Election Commission of India sources. The boundary file has a CC BY 2.5 India attribution requirement. Data values remain from the Dataful dataset; maps only join records to state polygons by name.")
    st.caption(f"Data quality checks currently show {quality['duplicate_keys']} duplicate composite-key rows, {quality['negative_values']} negative counts, and {quality['missing_values']} missing values. State labels are not used as model features.")
