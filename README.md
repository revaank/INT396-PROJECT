# TB Insight

TB Insight is an interactive Streamlit dashboard for exploring the user's purchased Dataful dataset of Indian state/UT tuberculosis program indicators. It is an educational, exploratory analysis of aggregated notifications, not a diagnostic or personal risk prediction system.

## Start on Windows

1. Double-click `START_TB_INSIGHT.bat`.

The first launch uses Python if present; otherwise it attempts a per-user Python 3.12 install through Windows Package Manager (winget). It creates a local `.venv` and installs the listed packages. Internet access is needed for this first-time setup. It also attempts to download the map boundary file once. The dashboard can still run without the map file, and explains how to retry.

## Dataset and provenance

The supplied `20833- Dataful.zip` contains `metadata.csv` and `year-state-sector-and-risk-factor-wise-cases-of-tb.csv`. The metadata identifies the Ministry of Health and Family Welfare, annual reports as the source, annual state-level granularity, 2019–2023 coverage, and absolute-number units. Dataful citation: Ministry of Health and Family Welfare. Year, State, Sector and Risk Factor wise cases of TB [Data set]. Dataful. https://dataful.in/datasets/20833/20833

The archive does not specify a license, and the original publisher retrieval date is unknown. Confirm redistribution terms with the publisher. The raw CSV and its metadata are retained at `data/raw/dataful_20833/` for reproducibility. All India rows are excluded from state/UT comparisons, maps, and clustering.

An initial inspection found 4,995 rows, 37 distinct state labels including All India (36 state/UTs after its exclusion), 132 blank value cells, blank notes in all 4,995 records, no duplicate composite keys, and no negative counts. Missing values remain missing. Every value uses the unit `value in absolute number`; no population-adjusted rate is calculated.

## Analysis

Clustering is exploratory. Select year, risk factor, and reporting sector; each available parameter becomes one feature. Regions with any missing selected feature are excluded and the dashboard displays that count. Features are standardized. K-Means uses random seed 42; Agglomerative clustering and DBSCAN are also available. Silhouette, Davies–Bouldin, and Calinski–Harabasz scores are shown only when valid. DBSCAN noise prevents those scores from being reported. PCA is only a two-axis display projection.

## Map

State/UT polygons come from geoBoundaries open India ADM1 (boundary representation year 2011; 36 units), based on DataMeet India community and Election Commission of India sources. Attribution is required under CC BY 2.5 India. The map joins by name and may hide unmatched polygons rather than infer a match. Boundary vintage may not capture later administrative changes.

## Limitations

Notifications are not the same as incidence or prevalence. Absolute counts depend on population size, screening, and notification coverage. Some indicators have different denominators and should only be compared when indicator, year, sector, and unit definitions match. This app cannot establish causation or assess any individual's TB status.
