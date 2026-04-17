import tempfile
import unittest
from pathlib import Path

from src.machine_learning.utils_mod import read_mols_csv


class TestReadMolsCsv(unittest.TestCase):
    def test_read_mols_csv_skips_header_and_invalid_rows(self):
        content = "name,smiles\nwater,O\n\ninvalid_only_one_column\nethanol,CCO\n ,CC\n"

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "mols.csv"
            csv_path.write_text(content, encoding="utf-8")

            rows = read_mols_csv(csv_path)

        self.assertEqual(rows, [("water", "O"), ("ethanol", "CCO")])

    def test_read_mols_csv_accepts_headerless_files(self):
        content = "benzene,c1ccccc1\ntoluene,CC1=CC=CC=C1\n"

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "mols.csv"
            csv_path.write_text(content, encoding="utf-8")

            rows = read_mols_csv(csv_path)

        self.assertEqual(rows, [("benzene", "c1ccccc1"), ("toluene", "CC1=CC=CC=C1")])


if __name__ == "__main__":
    unittest.main()
