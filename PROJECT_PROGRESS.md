# Project progress

## Current status (2026-11-04)

- Built Version 1 of TB Insight with Home, Explore India, Compare States, ML Intelligence, Research Insights, AI Explainer, TB Knowledge Centre, and Find Help & About sections.
- Added the purchased Dataful 20833 CSV and supplied metadata under `data/raw/dataful_20833/`.
- Verified the table contains 4,995 rows, 8 columns, 2019–2023 coverage, 37 state labels including All India, 36 regional labels after All India is excluded, 132 missing values, 4,995 blank note cells, no duplicate composite keys, and no negative values.
- Values are absolute counts. State comparison is like-for-like by indicator and sector. Clustering uses complete cases, excludes All India, standardizes features, evaluates K-Means/Agglomerative/DBSCAN with clustering metrics where defined, and shows PCA only as a visualization.
- Added Windows startup script that sets up a local environment and dependencies, and attempts a one-time download of the attributed geoBoundaries India state polygons.
- Added tests for real-data integrity and a K-Means path. `compileall` and both `unittest` cases passed in the bundled Python runtime.

## Known verification limits

- The dashboard UI could not be launched in this environment because Streamlit and Plotly are not preinstalled and package downloads from PyPI failed due network timeout/certificate restrictions. The startup script installs them on first run where internet access is available.
- Direct access to GitHub was blocked in this environment, so the optional state boundary file was not downloaded or visually checked. The map section gracefully explains/retries when the file is absent and hides unmatched geometries.
- Dataful's supplied metadata does not state a dataset redistribution license or original publisher retrieval date. Confirm terms with the publisher before redistributing the CSV.

## Interpretation limits

Notifications are not incidence or prevalence. Absolute counts are affected by population, screening, and notification coverage. A cluster is a descriptive grouping, not a risk class or causal claim. The tool does not assess an individual's TB status.
