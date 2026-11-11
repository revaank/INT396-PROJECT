import unittest

from src.analysis import fit_clusters
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
        result, metrics = fit_clusters(complete, "K-Means", clusters=3)
        self.assertEqual(len(result), len(complete))
        self.assertEqual(metrics["Regions"], len(complete))
        self.assertEqual(metrics["Clusters"], 3)
        self.assertIsNotNone(metrics["Silhouette"])


if __name__ == "__main__":
    unittest.main()
