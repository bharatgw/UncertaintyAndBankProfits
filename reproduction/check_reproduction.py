"""Check source integrity, analysis inputs, or selected PDF result benchmarks."""
import argparse
import ast
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys


def tex_number(cell):
    """Read one numeric fixest table cell, including scientific notation and stars."""
    value = re.sub(r"\$?\^\{\*+\}\$?", "", cell)
    value = value.replace(r"\\", "").replace("$", "").strip().strip("()")
    value = re.sub(r"\\times\s*10\^\{(-?\d+)\}", r"e\1", value)
    return Decimal(value.replace(",", "").replace(" ", ""))


def check_table(path, target, reference=False):
    """Compare explicitly labelled table rows with PDF benchmarks at printed precision."""
    problems, checked = [], 0
    if not path.is_file():
        return [f"Missing table: {path}"], checked
    lines = [line for line in path.read_text().splitlines() if "&" in line]
    for row in target["rows"]:
        label = row.get("reference_label", row["label"]) if reference else row["label"]
        matches = [i for i, line in enumerate(lines) if line.split("&")[0].strip() == label]
        if len(matches) != 1:
            problems.append(f"{path.name}: expected exactly one row labelled {label!r}")
            continue
        index = matches[0]
        for offset, key in [(0, "values"), (1, "standard_errors")]:
            if key not in row:
                continue
            try:
                if offset and lines[index + offset].split("&")[0].strip():
                    raise ValueError("standard-error row must have an empty label")
                actual = [tex_number(cell) for cell in lines[index + offset].split("&")[1:]]
                expected = [Decimal(value.replace(",", "")) for value in row[key]]
                checked += len(expected)
                if actual != expected:
                    problems.append(f"{path.name}: {label} {key}: expected {expected}, got {actual}")
            except (InvalidOperation, IndexError, ValueError) as error:
                problems.append(f"{path.name}: cannot read {label} {key}: {error}")
    return problems, checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--source-only", action="store_true", help="Check sources and reference benchmarks without requiring analysis inputs.")
    mode.add_argument("--results", action="store_true", help="Also compare generated tables with the selected PDF benchmarks.")
    args = parser.parse_args()
    support = Path(__file__).resolve().parent
    root = support.parent
    manifest = json.loads((support / "source_provenance.json").read_text())
    problems, code_cells = [], 0
    for record in manifest:
        path = root / record["path"]
        if not path.is_file():
            problems.append("Missing provenance file: " + record["path"])
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            problems.append("SHA-256 differs from source_provenance.json: " + record["path"])
        try:
            if path.suffix == ".ipynb":
                notebook = json.loads(path.read_text())
                for index, cell in enumerate(notebook["cells"]):
                    if cell["cell_type"] == "code":
                        ast.parse("".join(cell["source"]), filename=f"{path.name}:cell{index}")
                        code_cells += 1
            elif path.suffix == ".py":
                ast.parse(path.read_text(), filename=path.name)
                code_cells += 1
        except (SyntaxError, ValueError, KeyError) as error:
            problems.append(f'Invalid source {record["path"]}: {error}')
    targets = json.loads((support / "reference/paper_targets.json").read_text())
    reference_cells = 0
    for table in targets["regression_tables"]:
        if table["reference_file"]:
            failures, count = check_table(root / table["reference_file"], table, reference=True)
            problems.extend(failures)
            reference_cells += count
    if not (args.source_only or args.results):
        for name in ["Data/finalData/findf_RelSeriesContiguousSA.csv", "Data/bankTreasuryHoldings.csv"]:
            if not (root / name).is_file():
                problems.append("Missing analysis input: " + name)
    if args.results:
        output = root / "outputs/paper/tables"
        table_1 = targets["table_1"]
        path = output / table_1["file"]
        table_1_checked = path.is_file()
        if not table_1_checked:
            problems.append(f"Missing table: {path}")
        else:
            with path.open(newline="") as stream:
                actual = list(csv.reader(stream))
            with (root / table_1["reference_file"]).open(newline="") as stream:
                expected = list(csv.reader(stream))
            if actual != expected:
                problems.append("Table 1 differs from the PDF reference (displayed values, labels, or order).")
        result_cells = 0
        for table in targets["regression_tables"]:
            failures, count = check_table(output / table["file"], table)
            problems.extend(failures)
            result_cells += count
        print(f"Checked {result_cells}/140 regression benchmarks; Table 1 CSV checked: {table_1_checked}.")
        print(targets["scope"])
        print("Other coefficients, significance stars, figure regeneration, and data provenance need separate verification.")
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"Checked {len(manifest)} provenance records, {code_cells} Python files/cells, and {reference_cells} reference-table benchmarks.")
    print("No model was executed. Checks do not establish end-to-end numerical reproduction.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
