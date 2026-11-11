# Project progress

## Current status (2026-11-11)

- **Academic Requirements Implemented (Units II, III & IV):**
  - **Unit II:** Complete documented preprocessing pipeline, missing value auditing (preserved as missing, not imputed with zero), national aggregate removal, standardisation via `StandardScaler`.
  - **Unit III:** K-Means clustering with multi-$k$ sweep ($k=2..5$), WCSS (inertia) Elbow evaluation, Silhouette score, Davies-Bouldin index, Calinski-Harabasz index. Added Agglomerative Hierarchical clustering comparing Euclidean vs. Manhattan distances, and an interactive Dendrogram visualization via Plotly.
  - **Unit IV:** 2-component PCA projection with explained variance ratios annotated (~99% variance explained), cluster profile medians, feature contribution analysis, quantitative stability agreement metric comparing distance settings, and explicit defensible configuration selection ($k=3$).
- **AeroTB Command-Center Interface Redesign:**
  - Renamed and rebranded to **AeroTB** (`AeroTB | India Regional Intelligence`).
  - Dark, high-tech command center palette (`#050811`, glowing cyan `#00f2fe` accents) inspired by modern medical intelligence interfaces (1Cell.Ai, Bharat Cancer).
  - Streamlit radio button dots completely removed and converted into glowing interactive pills.
  - Home page reconstructed into a fluid 3-column command center: Left (Dynamic "Did You Know?" cycler + State Leaderboard with quick state selection), Center (Interactive India Choropleth Map with seamless scroll-zoom and layer toggle for `Diabetes in TB`, `Tobacco Users in TB`, `Alcohol Users in TB`, and `AI State Groups`), Right (Live State Telemetry Card showing rank, AI cluster group, recorded notifications, and comorbidity notes).
  - Selected states trigger an interactive glowing target beacon marker directly on the India map.
  - Seamless Unicode diacritic normalization matching 36/36 Indian States and UTs on the GeoJSON boundary.
  - Implemented Apple-style sticky stacked-card 3D scroll transitions for the public health story (`Discovery 01: Airborne Curability`, `Discovery 02: Hidden Multipliers`, `Discovery 03: 36 State Crises`) that smoothly reveal sequentially before opening into the Analysis Suites navigation portal.
  - Synchronized across local active workspace and OneDrive backup.
- **Reproducibility & Quality Assurance:**
  - Added standalone `notebooks/reproducible_analysis.py` CLI pipeline for non-interactive execution and examination reporting.
  - Expanded test suite in `tests/test_analysis.py` covering WCSS, PCA variance, labels, sweep, Manhattan clustering, and feature contributions (6/6 tests passing).
  - Updated `README.md` with complete architecture and setup instructions.

## Interpretation limits

Notifications are not incidence or prevalence. Absolute counts are affected by population, screening, and notification coverage. A cluster is a descriptive grouping, not a risk class or causal claim. The tool does not assess an individual's TB status.
