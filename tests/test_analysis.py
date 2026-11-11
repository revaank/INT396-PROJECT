import unittest

from src.analysis import fit_clusters, sweep_k, cluster_plain_summary, feature_contributions
from src.data import DATA_PATH, get_quality_summary, load_data, regional_data, regional_feature_matrix


class DatasetAndModelTests(unittest.TestCase):
    def test_real_dataset_integrity_and_regional_filter(self):
        data = load_data()
        summary = get_quality_summary(data)
        self.assertEqual(summary["rows"], 4995)
        self.assertEqual(summary["regions"], 36)
        self.assertEqual(summary["missing_values"], 132)
        self.assertEqual(summary["duplicate_keys"], 0)
        self.assertFalse(regional_data(data)["state"].str.casefold().isin(["all india", "india"]).any())

    def test_complete_case_feature_matrix_and_kmeans(self):
        data = load_data()
        raw, complete = regional_feature_matrix(data, 2023, "Diabetes", "public + private")
        self.assertGreaterEqual(raw.shape[1], 2)
        self.assertGreaterEqual(len(complete), 4)
        self.assertTrue(complete.notna().all().all())
        result, metrics, pca_var = fit_clusters(complete, "K-Means", clusters=3)
        self.assertEqual(len(result), len(complete))
        self.assertEqual(metrics["Regions"], len(complete))
        self.assertEqual(metrics["Groups found"], 3)
        self.assertIsNotNone(metrics["Silhouette"])
        # New checks: WCSS and PCA variance
        self.assertIsNotNone(metrics["WCSS (Inertia)"])
        self.assertGreater(metrics["WCSS (Inertia)"], 0)
        self.assertEqual(len(pca_var), 2)
        self.assertGreater(pca_var[0], 0)
        # Friendly labels
        self.assertTrue(all(c.startswith("Group") for c in result["Cluster"].unique()))

    def test_sweep_k(self):
        data = load_data()
        _, complete = regional_feature_matrix(data, 2023, "Diabetes", "public")
        sweep_df = sweep_k(complete, max_k=5)
        self.assertGreaterEqual(len(sweep_df), 2)
        self.assertIn("WCSS", sweep_df.columns)
        self.assertIn("Silhouette", sweep_df.columns)
        self.assertIn("Davies-Bouldin", sweep_df.columns)

    def test_manhattan_clustering(self):
        data = load_data()
        _, complete = regional_feature_matrix(data, 2023, "Diabetes", "public")
        result, metrics, pca_var = fit_clusters(
            complete, "Agglomerative", clusters=3, distance="manhattan"
        )
        self.assertEqual(len(result), len(complete))
        self.assertEqual(metrics["Groups found"], 3)

    def test_cluster_plain_summary(self):
        data = load_data()
        _, complete = regional_feature_matrix(data, 2023, "Tobacco", "public")
        result, _, _ = fit_clusters(complete, "K-Means", clusters=3)
        profiled = complete.copy()
        profiled["Cluster"] = result.set_index("State / UT")["Cluster"].reindex(profiled.index).values
        profile = profiled.groupby("Cluster", observed=True)[complete.columns].median()
        summaries = cluster_plain_summary(profile, complete.columns.tolist())
        self.assertGreater(len(summaries), 0)
        for key, val in summaries.items():
            self.assertIn("Group", key)
            self.assertGreater(len(val), 10)

    def test_feature_contributions(self):
        data = load_data()
        _, complete = regional_feature_matrix(data, 2023, "Diabetes", "public")
        result, _, _ = fit_clusters(complete, "K-Means", clusters=3)
        labels = result.set_index("State / UT")["Cluster"].reindex(complete.index).values
        feat = feature_contributions(complete, labels)
        self.assertEqual(feat.shape[1], complete.shape[1])


if __name__ == "__main__":
    unittest.main()
