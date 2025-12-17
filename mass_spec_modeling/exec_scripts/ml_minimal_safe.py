import argparse
from pathlib import Path
from typing import List, Tuple

import numpy as np

# Minimal safe runner: loads compound list and reports spectra availability
# Avoids importing torch_geometric, mod, or fragmentation utils


def read_mols_csv(path: Path) -> List[Tuple[str, str]]:
    path = Path(str(path)).expanduser()
    rows: List[Tuple[str, str]] = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8") as f:
        # Expect header: name,smiles
        for i, line in enumerate(f):
            if i == 0 and "," in line:
                continue
            parts = line.strip().split(",")
            if len(parts) >= 2:
                rows.append((parts[0].strip(), parts[1].strip()))
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=20)
    args = p.parse_args()

    MOL_DEF_PATH = Path("~/Nextcloud/studium/computationalScience/thesis/mol/" \
            + "mass_spec_modeling/exec_scripts/ms_data/compounds.csv")
    mols = read_mols_csv(MOL_DEF_PATH)
    if args.limit and args.limit > 0:
        mols = mols[:args.limit]

    print(f"Loaded {len(mols)} molecules (name,smiles) safely.")
    print("First 5:")
    for i, (name, smi) in enumerate(mols[:5]):
        print(f"  - {i+1}: {name} | {smi}")
    print("Safe runner complete. No heavy libs initialized.")


if __name__ == "__main__":
    main()
