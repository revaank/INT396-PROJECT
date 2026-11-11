"""Clustering and interpretation helpers. All models use scaled counts."""
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------------------------
# Plain-language group labels (A, B, C…) instead of 0, 1, 2
# ---------------------------------------------------------------------------
_GROUP_NAMES = ["Group A", "Group B", "Group C", "Group D", "Group E", "Group F"]


def _friendly_labels(numeric_labels):
    """Convert 0,1,2… to Group A, Group B… and -1 to 'Unassigned'."""
    out = []
    for lab in numeric_labels:
        if lab < 0:
            out.append("Unassigned")
        elif lab < len(_GROUP_NAMES):
            out.append(_GROUP_NAMES[lab])
        else:
            out.append(f"Group {lab + 1}")
    return out


# ---------------------------------------------------------------------------
# Core clustering (returns WCSS, PCA variance, friendly labels)
# ---------------------------------------------------------------------------
def fit_clusters(matrix: pd.DataFrame, method: str, clusters: int = 3,
                 eps: float = 0.9, min_samples: int = 4,
                 distance: str = "euclidean"):
    """
    Cluster the feature matrix and return results with friendly labels.

    Parameters
    ----------
    matrix   : pd.DataFrame – rows=regions, columns=indicators (complete cases)
    method   : str          – "K-Means", "Agglomerative", or "DBSCAN"
    clusters : int          – number of clusters (K-Means / Agglomerative)
    eps, min_samples        – DBSCAN parameters
    distance : str          – "euclidean" or "manhattan" (Agglomerative only)

    Returns
    -------
    result       : pd.DataFrame – State/UT, Cluster (friendly), PC1, PC2
    metrics      : dict          – WCSS, Silhouette, Davies-Bouldin, etc.
    pca_variance : tuple         – (PC1 explained %, PC2 explained %)
    """
    if matrix.shape[0] < 4 or matrix.shape[1] < 2:
        raise ValueError(
            "Clustering needs at least four complete regions and two comparable indicators."
        )
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix.astype(float))

    wcss = None
    if method == "K-Means":
        model = KMeans(n_clusters=clusters, random_state=42, n_init=20)
        labels = model.fit_predict(scaled)
        wcss = float(model.inertia_)
    elif method == "Agglomerative":
        if distance == "manhattan":
            model = AgglomerativeClustering(
                n_clusters=clusters, metric="manhattan", linkage="average"
            )
        else:
            model = AgglomerativeClustering(n_clusters=clusters, linkage="ward")
        labels = model.fit_predict(scaled)
    elif method == "DBSCAN":
        labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(scaled)
    else:
        raise ValueError(f"Unknown clustering method: {method}")

    n_groups = len(set(labels)) - (1 if -1 in labels else 0)
    valid = n_groups >= 2 and n_groups < len(labels)
    metrics = {
        "WCSS (Inertia)": wcss,
        "Silhouette": float(silhouette_score(scaled, labels)) if valid and -1 not in labels else None,
        "Davies-Bouldin": float(davies_bouldin_score(scaled, labels)) if valid and -1 not in labels else None,
        "Calinski-Harabasz": float(calinski_harabasz_score(scaled, labels)) if valid and -1 not in labels else None,
        "Regions": int(len(labels)),
        "Groups found": int(n_groups),
        "Unassigned regions": int(np.sum(labels == -1)),
    }

    pca = PCA(n_components=2, random_state=42)
    coordinates = pca.fit_transform(scaled)
    pca_variance = (
        float(pca.explained_variance_ratio_[0] * 100),
        float(pca.explained_variance_ratio_[1] * 100),
    )

    friendly = _friendly_labels(labels)
    result = pd.DataFrame({
        "State / UT": matrix.index,
        "Cluster": friendly,
        "PC1": coordinates[:, 0],
        "PC2": coordinates[:, 1],
    })
    return result, metrics, pca_variance


# ---------------------------------------------------------------------------
# Multi-k sweep: run K-Means for k=2..max_k and collect all metrics
# ---------------------------------------------------------------------------
def sweep_k(matrix: pd.DataFrame, max_k: int = 6):
    """
    Run K-Means for k = 2 through max_k and return a comparison table.

    Returns
    -------
    pd.DataFrame with columns: k, WCSS, Silhouette, Davies-Bouldin, Calinski-Harabasz
    """
    if matrix.shape[0] < 4 or matrix.shape[1] < 2:
        return pd.DataFrame()
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix.astype(float))
    upper = min(max_k, matrix.shape[0] - 1)
    rows = []
    for k in range(2, upper + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(scaled)
        rows.append({
            "k": k,
            "WCSS": float(model.inertia_),
            "Silhouette": float(silhouette_score(scaled, labels)),
            "Davies-Bouldin": float(davies_bouldin_score(scaled, labels)),
            "Calinski-Harabasz": float(calinski_harabasz_score(scaled, labels)),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Dendrogram: hierarchical clustering linkage matrix
# ---------------------------------------------------------------------------
def build_dendrogram(matrix: pd.DataFrame, dist_metric: str = "euclidean",
                     link_method: str = "ward"):
    """
    Compute a scipy linkage matrix for drawing a dendrogram.

    Think of a dendrogram like a family tree of states — the lower two
    branches merge, the more similar those states are to each other.

    Parameters
    ----------
    matrix      : pd.DataFrame – rows=regions, columns=indicators (complete cases)
    dist_metric : str          – "euclidean" or "manhattan"
    link_method : str          – "ward" (euclidean only), "average", "complete"

    Returns
    -------
    Z      : np.ndarray – scipy linkage matrix (passed to scipy dendrogram)
    labels : list[str]  – state names for leaf labels
    """
    if matrix.shape[0] < 3:
        raise ValueError("Need at least 3 regions to draw a dendrogram.")
    # ward linkage only valid with euclidean; fall back to average for manhattan
    if dist_metric == "manhattan" and link_method == "ward":
        link_method = "average"
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix.astype(float))
    Z = linkage(scaled, method=link_method, metric=dist_metric)
    return Z, list(matrix.index)


# ---------------------------------------------------------------------------
# Stability: compare Euclidean K-Means vs Manhattan Agglomerative
# ---------------------------------------------------------------------------
def stability_comparison(matrix: pd.DataFrame, k: int = 3):
    """
    Run K-Means (Euclidean) and Agglomerative (Manhattan) with the same k
    and return how many states land in the same group in both methods.

    Returns
    -------
    comparison_df : pd.DataFrame – state, euclidean_group, manhattan_group, same_group
    agreement_pct : float        – % of states in a matching group
    """
    if matrix.shape[0] < 4 or matrix.shape[1] < 2:
        raise ValueError("Need at least 4 complete regions for stability comparison.")

    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix.astype(float))

    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    km_labels = _friendly_labels(km.fit_predict(scaled))

    agg = AgglomerativeClustering(n_clusters=k, metric="manhattan", linkage="average")
    agg_labels = _friendly_labels(agg.fit_predict(scaled))

    df = pd.DataFrame({
        "State / UT": matrix.index,
        "K-Means (Euclidean)": km_labels,
        "Agglomerative (Manhattan)": agg_labels,
    })

    # Remap manhattan labels to best-matching euclidean labels
    from scipy.optimize import linear_sum_assignment
    unique_km = sorted(set(km_labels))
    unique_agg = sorted(set(agg_labels))
    cost = np.zeros((len(unique_km), len(unique_agg)))
    for i, g1 in enumerate(unique_km):
        for j, g2 in enumerate(unique_agg):
            cost[i, j] = -np.sum(
                (np.array(km_labels) == g1) & (np.array(agg_labels) == g2)
            )
    row_ind, col_ind = linear_sum_assignment(cost)
    mapping = {unique_agg[col_ind[i]]: unique_km[row_ind[i]] for i in range(len(row_ind))}
    mapped_agg = [mapping.get(l, l) for l in agg_labels]

    df["Same group?"] = ["✅ Yes" if a == b else "❌ Different"
                         for a, b in zip(km_labels, mapped_agg)]
    agreement_pct = 100 * sum(a == b for a, b in zip(km_labels, mapped_agg)) / len(km_labels)
    return df, agreement_pct


# ---------------------------------------------------------------------------
# Auto-generate plain-English cluster summaries
# ---------------------------------------------------------------------------
def cluster_plain_summary(cluster_profile: pd.DataFrame, feature_cols: list):
    """
    Given the median-per-cluster profile, create a one-line plain-language
    description per cluster.
    """
    summaries = {}
    for cluster_label in cluster_profile.index:
        best_feature = None
        best_val = -1
        for col in feature_cols:
            col_vals = cluster_profile[col]
            is_max = (col_vals.rank(ascending=False) == 1)
            if is_max.loc[cluster_label]:
                val = cluster_profile.loc[cluster_label, col]
                if val > best_val:
                    best_feature = col
                    best_val = val

        if best_feature:
            short_name = best_feature if len(best_feature) <= 60 else best_feature[:57] + "…"
            summaries[cluster_label] = (
                f"**{cluster_label}** — these states reported the **highest numbers** "
                f"in \"{short_name}\". This does not mean higher risk — it "
                f"reflects reported counts, which depend on population size and screening."
            )
        else:
            total = cluster_profile.loc[cluster_label, feature_cols].sum()
            summaries[cluster_label] = (
                f"**{cluster_label}** — these states had moderate reported counts "
                f"across all indicators (total median: {total:,.0f})."
            )
    return summaries


# ---------------------------------------------------------------------------
# Feature contribution: which indicators separate the groups most
# ---------------------------------------------------------------------------
def feature_contributions(matrix: pd.DataFrame, labels):
    """
    Return mean standardised value per feature per group.
    Shows which indicator each cluster is highest/lowest on.
    """
    scaler = StandardScaler()
    scaled = pd.DataFrame(
        scaler.fit_transform(matrix.astype(float)),
        index=matrix.index,
        columns=matrix.columns,
    )
    scaled["Cluster"] = labels
    return scaled.groupby("Cluster")[matrix.columns.tolist()].mean().round(2)


# ---------------------------------------------------------------------------
# Plain pattern description
# ---------------------------------------------------------------------------
def describe_pattern(data: pd.DataFrame, value_column: str = "value") -> str:
    """Create a modest, data-backed plain-language summary."""
    valid = data.dropna(subset=[value_column])
    if valid.empty:
        return "There are no reported values for this selection."
    top = valid.loc[valid[value_column].idxmax()]
    median = float(valid[value_column].median())
    count = int(valid["state"].nunique())
    return (
        f"Among {count} regions with a reported value, {top['state']} has the largest "
        f"reported count ({top[value_column]:,.0f}). The median reported count is {median:,.0f}. "
        "These are absolute counts, so differences can reflect population size, screening, "
        "or notification coverage; they do not establish relative TB risk."
    )
