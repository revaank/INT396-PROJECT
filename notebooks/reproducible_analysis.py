"""
Reproducible Regional Tuberculosis Clustering Analysis
======================================================
This script provides an end-to-end, command-line reproducible execution
of the TB Case-Pattern clustering pipeline (Units II, III, IV).

Usage:
    python notebooks/reproducible_analysis.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.data import load_data, get_quality_summary, regional_feature_matrix
from src.analysis import fit_clusters, sweep_k, stability_comparison, feature_contributions, cluster_plain_summary

def main():
    print("=" * 70)
    print("REGIONAL TUBERCULOSIS CASE-PATTERN CLUSTERING ANALYSIS")
    print("Units II, III & IV Execution Pipeline")
    print("=" * 70)

    # 1. Load Data & Validation (Unit II)
    print("\n[Step 1] Loading and Validating Dataset...")
    df = load_data()
    quality = get_quality_summary(df)
    print(f"  • Rows: {quality['rows']:,}")
    print(f"  • Regions: {quality['regions']} (All India national aggregate excluded)")
    print(f"  • Years: {min(quality['years'])} - {max(quality['years'])}")
    print(f"  • Missing value cells: {quality['missing_values']}")
    print(f"  • Duplicate composite keys: {quality['duplicate_keys']}")
    print(f"  • Negative values: {quality['negative_values']}")

    # 2. Regional Feature Matrix Preprocessing (Unit II)
    year = 2023
    factor = "Diabetes"
    sector = "public + private"
    print(f"\n[Step 2] Feature Extraction & Preprocessing (Year: {year}, Factor: {factor}, Sector: {sector})...")
    raw, complete = regional_feature_matrix(df, year, factor, sector)
    print(f"  • Initial regions: {raw.shape[0]}")
    print(f"  • Indicators: {raw.shape[1]}")
    print(f"  • Complete case regions used: {complete.shape[0]}")
    print(f"  • Excluded due to missingness: {raw.shape[0] - complete.shape[0]}")
    print(f"  • Features: {list(complete.columns)}")

    # 3. Multi-k K-Means Sweep: WCSS, Silhouette, Davies-Bouldin (Unit III)
    print("\n[Step 3] Multi-k Partitioning Sweep (WCSS, Silhouette, Davies-Bouldin, CH):")
    sweep_df = sweep_k(complete, max_k=5)
    print(sweep_df.to_string(index=False))

    # 4. Model Selection & PCA Separation (Units III & IV)
    k_selected = 3
    print(f"\n[Step 4] Fitting Selected Configuration (K-Means, k={k_selected}):")
    result, metrics, pca_var = fit_clusters(complete, "K-Means", clusters=k_selected)
    print(f"  • WCSS (Inertia): {metrics['WCSS (Inertia)']:.2f}")
    print(f"  • Silhouette Score: {metrics['Silhouette']:.3f}")
    print(f"  • Davies-Bouldin Index: {metrics['Davies-Bouldin']:.3f}")
    print(f"  • Calinski-Harabasz Index: {metrics['Calinski-Harabasz']:.2f}")
    print(f"  • PCA Variance Explained: PC1 = {pca_var[0]:.1f}%, PC2 = {pca_var[1]:.1f}% (Total: {pca_var[0]+pca_var[1]:.1f}%)")

    # 5. Stability & Distance Comparison: Euclidean vs Manhattan (Units III & IV)
    print("\n[Step 5] Stability Testing: Euclidean K-Means vs Manhattan Agglomerative:")
    stab_df, agreement = stability_comparison(complete, k=k_selected)
    print(f"  • Grouping Agreement across distance metrics: {agreement:.1f}%")
    shifts = stab_df[stab_df["Same group?"] == "❌ Different"]
    if len(shifts) > 0:
        print(f"  • Borderline shifting states ({len(shifts)}): {list(shifts['State / UT'])}")
    else:
        print("  • Complete 100% stability across distance formulations!")

    # 6. Cluster Profiling & Feature Contributions (Unit IV)
    print("\n[Step 6] Cluster Profiles (Median Feature Values):")
    profiled = complete.copy()
    profiled["Cluster"] = result.set_index("State / UT")["Cluster"].reindex(profiled.index).values
    cluster_profile = profiled.groupby("Cluster", observed=True)[complete.columns].median().round(1)
    print(cluster_profile.to_string())

    print("\n[Step 7] Plain-Language Cluster Interpretations:")
    summaries = cluster_plain_summary(cluster_profile, complete.columns.tolist())
    for grp, summary in summaries.items():
        # strip markdown bolding for terminal
        clean_summary = summary.replace("**", "").replace('"', "'")
        print(f"  • {clean_summary}")

    # 7. Save outputs
    output_dir = PROJECT_ROOT / "results"
    output_dir.mkdir(exist_ok=True)
    out_csv = output_dir / f"reproducible_clusters_{year}_{factor}.csv"
    result.to_csv(out_csv, index=False)
    print(f"\n[Step 8] Output saved successfully to: {out_csv}")
    print("\n" + "=" * 70)
    print("REPRODUCIBLE ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
