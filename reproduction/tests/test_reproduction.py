"""Regression tests for the PDF benchmark reader; no empirical data required."""
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import tempfile
import unittest

from reproduction.check_reproduction import check_table, tex_number

ROOT = Path(__file__).resolve().parents[2]
TARGETS = json.loads((ROOT / "reproduction/reference/paper_targets.json").read_text())


class BenchmarkReaderTests(unittest.TestCase):
    def test_displayed_numeric_formats(self):
        for cell, expected in [
            (r"-0.0242$^{**}$\\", "-0.0242"),
            (r"($3.07\times 10^{-6}$)\\", "0.00000307"),
            (r"$-2.24\times 10^{-5}$$^{***}$", "-0.0000224"),
            (r"420,772\\", "420772"),
        ]:
            with self.subTest(cell=cell):
                self.assertEqual(tex_number(cell), Decimal(expected))

    def test_non_numeric_cell_is_rejected(self):
        with self.assertRaises(InvalidOperation):
            tex_number(r"$\checkmark$")

    def test_available_references_match_pdf_benchmarks(self):
        count = 0
        for table in TARGETS["regression_tables"]:
            if table["reference_file"]:
                failures, checked = check_table(ROOT / table["reference_file"], table, reference=True)
                self.assertEqual(failures, [])
                count += checked
        self.assertEqual(count, 75)

    def test_nni_values_cannot_validate_nim_even_with_same_counts(self):
        target = next(t for t in TARGETS["regression_tables"] if t["table"] == 4)
        source = (ROOT / "reproduction/reference/tables/didRegNNI.txt").read_text().replace("L(NNI)", "L(NIM)")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "didRegNIM.txt"
            path.write_text(source)
            failures, checked = check_table(path, target)
        self.assertEqual(checked, 15)
        self.assertTrue(any("values" in failure and "L(NIM)" in failure for failure in failures))

    def test_missing_table_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            failures, checked = check_table(Path(directory) / "absent.txt", TARGETS["regression_tables"][0])
        self.assertTrue(failures)
        self.assertEqual(checked, 0)

    def test_duplicate_coefficient_row_is_rejected(self):
        target = next(t for t in TARGETS["regression_tables"] if t["table"] == 5)
        source = (ROOT / target["reference_file"]).read_text()
        line = next(line for line in source.splitlines() if line.strip().startswith(r"g $\times$ L(NNI)"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.txt"
            path.write_text(source + "\n" + line)
            failures, _ = check_table(path, target)
        self.assertTrue(any("exactly one row" in failure for failure in failures))

    def test_coefficient_precision_is_not_silently_relaxed(self):
        target = next(t for t in TARGETS["regression_tables"] if t["table"] == 5)
        source = (ROOT / target["reference_file"]).read_text().replace("-0.0242", "-0.0241")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "different.txt"
            path.write_text(source)
            failures, _ = check_table(path, target)
        self.assertTrue(any("values" in failure for failure in failures))

    def test_standard_error_row_requires_an_empty_label(self):
        target = {"rows": [{"label": "Coefficient", "values": ["0.1"], "standard_errors": ["0.01"]}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "misaligned.txt"
            path.write_text("Coefficient & 0.1\\\\\nOther coefficient & 0.01\\\\\n")
            failures, _ = check_table(path, target)
        self.assertTrue(any("empty label" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
