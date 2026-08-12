import unittest

from src.project_paths import REPO_ROOT, repo_path, shared_path


class TestProjectPaths(unittest.TestCase):
    def test_shared_paths_resolve_inside_repo(self):
        self.assertEqual(shared_path("DATA_DIR_REL").parent, REPO_ROOT)
        self.assertEqual(shared_path("PROCESSED_DIR_REL"), repo_path("data", "processed"))
        self.assertEqual(shared_path("PARQUET_DIR_REL"), repo_path("data", "outputs", "nist_spectra"))
        self.assertEqual(shared_path("BEST_PARAMS_DIR_REL"), repo_path("data", "outputs", "best_params"))


if __name__ == "__main__":
    unittest.main()