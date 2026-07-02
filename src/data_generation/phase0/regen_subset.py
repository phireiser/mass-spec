"""
Regenerate a representative subset of forward DGs with the CURRENT EI ruleset.

Phase 0.1 validation helper. The on-disk dumps under ``data/processed/fwd`` are
stale -- generated before the ``ei_molecular_ion`` rule, so they lack the molecular
ion (M+•) and the EI fragment set. This re-runs *forward* MØD generation for a
small, class-spanning subset into a separate output dir, leaving the stale dumps
untouched, so we can measure a provisional EI ceiling before committing to a full
(SLURM) regeneration.

SMILES are read straight from each molecule's existing dump pickle, so no external
molecule list is needed; generation is delegated to ``data_generation/main.py``
with ``--skip-backward`` (Phase 0.1 only needs the forward DG).
"""
from __future__ import annotations

import argparse
import pickle
import subprocess
import sys
from pathlib import Path

from src.project_paths import shared_path

# Small, fast, and spanning the EI chemistry classes plus every heteroatom the
# formula-aware null supports (N, O, S, Cl, Br). All are MW <= 128.
DEFAULT_SUBSET = [
    "acetone", "acetaldehyde", "2-propanol", "diethyl_ether", "acetic_acid",
    "butane", "1-butene", "benzene", "toluene", "naphthalene", "phenol",
    "aniline", "pyridine", "acetonitrile", "thiophene", "chlorobenzene", "bromoethane",
]


def smiles_from_dump(name: str, fwd_dir: Path) -> str:
    """Read the precursor SMILES stored in a dump's pickle (first tuple element)."""
    with open(Path(fwd_dir) / f"{name}.pkl", "rb") as f:
        return pickle.load(f)[0]


def main() -> None:
    ap = argparse.ArgumentParser(description="Regenerate forward DGs for a subset with the current ruleset")
    ap.add_argument("--stale-fwd", default=str(shared_path("PROCESSED_DIR_REL", "fwd")),
                    help="Existing dump dir to read SMILES from")
    ap.add_argument("--out-dir", default=None, help="Output dir (a fwd/ subdir is created); required unless --emit-manifest")
    ap.add_argument("--spectra-folder", default=str(shared_path("PARQUET_DIR_REL")))
    ap.add_argument("--names", default="", help="Comma-separated subset (default: built-in list)")
    ap.add_argument("--all-with-spectrum", action="store_true",
                    help="Use every molecule that has both a dump and a NIST spectrum (full corpus)")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--emit-manifest", default=None,
                    help="Write 'name<TAB>smiles' lines for the subset to this path (or - for stdout) and exit. "
                         "Used by the SLURM array job to map task index -> molecule.")
    args = ap.parse_args()

    if args.all_with_spectrum:
        from src.data_generation import utils
        stale = Path(args.stale_fwd)
        parquet_dir = Path(args.spectra_folder)
        names = sorted(
            p.stem for p in stale.glob("*.pkl")
            if utils.get_spectra_by_smiles(smiles_from_dump(p.stem, stale), parquet_dir)
        )
    else:
        names = [n.strip() for n in args.names.split(",") if n.strip()] or DEFAULT_SUBSET

    # Manifest mode: emit name<TAB>smiles for the SLURM array, then stop (no generation).
    if args.emit_manifest:
        lines = []
        for name in names:
            try:
                lines.append(f"{name}\t{smiles_from_dump(name, args.stale_fwd)}")
            except Exception as exc:  # noqa: BLE001
                print(f"{name}: no dump SMILES ({exc}); skipping", file=sys.stderr)
        text = "".join(line + "\n" for line in lines)
        if args.emit_manifest == "-":
            sys.stdout.write(text)
        else:
            out = Path(args.emit_manifest)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            print(f"wrote manifest with {len(lines)} molecules to {out}")
        return

    if not args.out_dir:
        ap.error("--out-dir is required unless --emit-manifest is given")

    main_py = Path(__file__).resolve().parents[1] / "main.py"
    failed = []
    for i, name in enumerate(names, 1):
        try:
            smiles = smiles_from_dump(name, args.stale_fwd)
        except Exception as exc:  # noqa: BLE001
            print(f"[{i}/{len(names)}] {name}: no dump SMILES ({exc}); skipping")
            failed.append(name)
            continue
        print(f"[{i}/{len(names)}] regenerating {name}  {smiles}", flush=True)
        result = subprocess.run([
            sys.executable, str(main_py),
            "--smiles", smiles, "--name", name,
            "--output-dir", args.out_dir,
            "--spectra-folder", args.spectra_folder,
            "--number-threads", str(args.threads),
            "--skip-backward",
        ])
        if result.returncode != 0:
            failed.append(name)

    done = len(names) - len(failed)
    print(f"\nregenerated {done}/{len(names)} forward DGs into {args.out_dir}/fwd"
          + (f"; failed: {failed}" if failed else ""))


if __name__ == "__main__":
    main()
