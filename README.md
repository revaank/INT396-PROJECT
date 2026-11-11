# Regional Tuberculosis Case-Pattern Clustering (TB Insight)

An exploratory, unsupervised clustering dashboard and analytics pipeline for aggregated Indian regional tuberculosis surveillance indicators (Ministry of Health and Family Welfare annual reports, 2019–2023).

> **Public Health Problem:** India comprises 36 diverse States and Union Territories with distinct TB risk-factor landscapes (diabetes, tobacco, alcohol, COVID-19 screening co-notifications). National programs frequently deploy uniform interventions. This project identifies clusters of states sharing similar multivariate notification patterns, enabling health administrators to design targeted, evidence-based regional strategies.

---

## Academic Coverage (Units II, III & IV)

| Unit | Focus | Implementation |
|---|---|---|
| **Unit II** | **Data Preparation & Preprocessing** | Missing value auditing (132 values preserved as missing, not imputed with zero); exclusion of national aggregate (`All India`); long-to-wide feature extraction for comparable state indicators; standardisation via `StandardScaler` (zero mean, unit variance). |
| **Unit III** | **Partition Clustering & Hierarchical Comparison** | K-Means clustering across multiple cluster counts ($k \in [2, 5]$); WCSS (inertia) Elbow evaluation; Silhouette score, Davies-Bouldin Index, Calinski-Harabasz Index; Agglomerative Hierarchical clustering comparing Euclidean vs. Manhattan distance metrics; Interactive Dendrogram visualization. |
| **Unit IV** | **PCA Visualisation, Interpretation & Stability** | 2-component PCA projection with explained variance ratios (annotating ~99% total variance captured); cluster profile medians; feature contribution rankings; quantitative stability check across distance metrics; defensible configuration selection ($k=3$). |

---

## Quick Start Instructions

### 1. Launch Interactive Streamlit Dashboard (Windows)
Double-click `START_TB_INSIGHT.bat` or run:
```bash
.venv\Scripts\streamlit run app/main.py
```

### 2. Run Standalone Reproducible Terminal Analysis
To verify all calculations and output the quantitative tables without launching the UI:
```bash
.venv\Scripts\python notebooks/reproducible_analysis.py
```

### 3. Run Automated Unit Tests
```bash
.venv\Scripts\python -m unittest tests.test_analysis -v
```

---

## Repository Structure

```
├── app/
│   └── main.py                 # Interactive Streamlit Web Application (8 sections)
├── data/
│   └── raw/dataful_20833/      # MoHFW TB surveillance dataset & metadata
├── notebooks/
│   └── reproducible_analysis.py # Standalone CLI execution pipeline for viva
├── results/                    # Saved clustering outputs and CSV exports
├── src/
│   ├── data.py                 # Data loading, validation, and pivoting
│   └── analysis.py             # K-Means, Agglomerative, Dendrogram, PCA & Metrics
├── tests/
│   └── test_analysis.py        # Automated test suite (6 passing tests)
├── requirements.txt            # Python dependencies
└── START_TB_INSIGHT.bat        # Windows one-click startup script
```

---

## Dataset Provenance & Integrity

- **Source:** Ministry of Health and Family Welfare (Central Tuberculosis Division), Annual TB Reports (2019–2023).
- **Republished by:** Dataful (Dataset 20833).
- **Geography:** 36 States/UTs (National aggregate `All India` filtered out before modeling).
- **Dimensions:** 4,995 rows, 8 columns, 11 indicators across 4 risk factor categories (`Diabetes`, `Tobacco`, `Alcohol`, `COVID-19`).
- **Integrity Checks:** 0 duplicate composite keys, 0 negative counts, 132 missing values handled by complete-case selection per analysis slice.

---

## Ethical Considerations & Limitations

- **Aggregated Data Only:** No patient-level records or personal identifiable health data.
- **Reported Counts $\neq$ True Incidence:** Values reflect recorded notifications and screening intensity, which are heavily influenced by state population size and health system capacity.
- **Descriptive Clusters:** Cluster labels (`Group A`, `Group B`, etc.) describe statistical similarities in the dataset and must not be used as clinical diagnostic criteria or stigmatizing risk classifications.
