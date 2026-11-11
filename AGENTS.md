# Project instructions: Regional Tuberculosis Case-Pattern Clustering

## Specification and working style

- Treat `Codex_TB_Clustering_Project_Brief.pdf` as the project specification when it is available in the repository or supplied in the task. The current copy was supplied from the user's Downloads folder; the seven-page brief has been reviewed.
- Work in small, reviewable stages. Inspect existing files and real datasets before implementing features. Preserve existing work.
- The developer is a beginner preparing for a university viva. Explain important choices in plain language and keep code readable.
- Never invent data, sample sizes, data-quality findings, metrics, cluster labels, citations, student details, project identifiers, repository URLs, or deployment URLs. Mark unavailable values as pending/placeholders.
- Report only commands and tests that were actually run and their actual outcomes.

## Project scope and safety

- Intended project: exploratory unsupervised clustering of aggregated TB notification patterns across Indian regions, with a Streamlit dashboard.
- This is not a patient-level diagnostic system, does not predict an individual's TB status, and cannot establish causation. Reported notifications are not the same as true incidence or prevalence.
- Use aggregated regional data only. Do not collect or expose personal medical data.
- Distinguish counts, proportions, and rates. Use population-adjusted rates only with reliable matching denominators.
- Do not use region names or arbitrary IDs as numeric clustering features. Do not label a region high-risk solely from raw counts.
- Keep synthetic UI-test data separate and explicitly labelled; never present it as research data.

## Data requirements

- Before analysis, document each source, license/attribution where known, retrieval date, geography, observation unit, years, feature meanings, units, missingness, duplicates, and limitations.
- Validate file format, schema, types, units, geographic level, time coverage, missing values, duplicates, inconsistent labels, invalid values, and comparable definitions before combining sources.
- Never fabricate district observations, fill missing values with zero unless zero is substantively correct, or silently discard large portions of data.
- The currently discovered `TB_provisional_notifications_2026-09-16.csv` is outside the repository in Downloads. It has 647 country-year rows, 24 columns, 142 countries, and years 2020-2026. India is represented as one country-level row per year (six rows, 2020-2025; 2025 is partial). It is global monthly/quarterly notifications data, not Indian state/district data, and is not sufficient for the intended regional clustering. Its source metadata, definitions, license, and meaning of coverage/frequency codes still need verification. Do not silently substitute it as the final project dataset.
- Other discovered Downloads CSVs (`mall_customers.csv`, `tennis.csv`) are unrelated examples and must not be used as TB research data.
- No dataset has yet been placed in the repository. Do not copy or transform an external file into project data until its suitability and provenance have been checked.

## Implementation expectations

- Recommended stack: Python, pandas, NumPy, scikit-learn, Plotly/Matplotlib, and Streamlit. Keep dependencies necessary and portable on Windows; avoid machine-specific absolute paths.
- Choose clustering methods only after inspecting the actual feature matrix and sample size. Evaluate reasonable alternatives and parameters; document random seeds where applicable.
- Use clustering-appropriate evidence such as silhouette, Davies-Bouldin, Calinski-Harabasz when meaningful, cluster sizes, stability, and interpretability. Do not present classification accuracy, precision, recall, or F1 as default clustering metrics.
- Explain that PCA plots are visual summaries and do not prove cluster validity. Create maps only if reliable boundaries and matching identifiers are available.
- Keep reusable data loading, validation, preprocessing, feature engineering, clustering, evaluation, and interpretation code separate from Streamlit UI logic.
- Handle missing or invalid input and empty results clearly. Use relative/configurable paths and do not commit secrets or credentials.

## Suggested sequence

1. Inspect workspace, instructions, environment, and candidate datasets; record known facts, gaps, and a safe first step.
2. Verify a defensible state- or district-level TB dataset, its metadata, definitions, and geographic/time coverage. If unavailable, state the blocker and options; do not fabricate regional data.
3. Build data validation and a documented exploratory baseline using only verified data.
4. Compare clustering approaches and interpret actual results with appropriate limitations.
5. Build the Streamlit dashboard on top of the tested analysis pipeline.
6. Add and run tests, verify installation/startup/reproducibility, and complete README, report, presentation, links, and submission artifacts using actual project details only.

## Repository hygiene

- Adapt the project structure to actual needs; do not create empty files or directories solely to imitate an example.
- Keep raw source data out of version control unless its terms, size, and privacy status permit it. Document where it belongs and provide clear setup instructions.
- Record source attribution and limitations in the application and project documentation.
