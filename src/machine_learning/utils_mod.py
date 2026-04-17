"""
This module contains utilities for reading molecule definitions from CSV files
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple


def read_mols_csv(csv_path: Path) -> List[Tuple[str, str]]:
    """Read molecule definitions as ``[(name, smiles), ...]``.

    The CSV must contain at least two columns; the first is interpreted as the
    molecule name and the second as the SMILES string. A header row is skipped
    automatically when the second column contains the word ``smiles``.
    """
    path = Path(csv_path)
    rows: List[Tuple[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            name = row[0].strip()
            smiles = row[1].strip()
            if not name or not smiles:
                continue
            if not rows and smiles.lower() == "smiles":
                continue
            rows.append((name, smiles))
    return rows


__all__ = ["read_mols_csv"]
