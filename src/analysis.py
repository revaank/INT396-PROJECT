"""Clustering and interpretation helpers. All models use scaled counts."""
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler


def fit_clusters(matrix: pd.DataFrame, method: str, clusters: int = 3, eps: float = 0.9, min_samples: int = 4):
    if matrix.shape[0] < 4 or matrix.shape[1] < 2:
        raise ValueError("Clustering needs at least four complete regions and two comparable indicators.")
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix.astype(float))
    if method == "K-Means":
        model = KMeans(n_clusters=clusters, random_state=42, n_init=20)
        labels = model.fit_predict(scaled)
    elif method == "Agglomerative":
        labels = AgglomerativeClustering(n_clusters=clusters, linkage="ward").fit_predict(scaled)
    elif method == "DBSCAN":
        labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(scaled)
    else:
        raise ValueError(f"Unknown clustering method: {method}")

    n_groups = len(set(labels)) - (1 if -1 in labels else 0)
    valid = n_groups >= 2 and n_groups < len(labels)
    metrics = {
        "Silhouette": float(silhouette_score(scaled, labels)) if valid and -1 not in labels else None,
        "Davies-Bouldin": float(davies_bouldin_score(scaled, labels)) if valid and -1 not in labels else None,
        "Calinski-Harabasz": float(calinski_harabasz_score(scaled, labels)) if valid and -1 not in labels else None,
        "Regions": int(len(labels)),
        "Clusters": int(n_groups),
        "Noise regions": int(np.sum(labels == -1)),
    }
    coordinates = PCA(n_components=2, random_state=42).fit_transform(scaled)
    output = pd.DataFrame({"State / UT": matrix.index, "Cluster": labels.astype(str), "PC1": coordinates[:, 0], "PC2": coordinates[:, 1]})
    return output, metrics


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
