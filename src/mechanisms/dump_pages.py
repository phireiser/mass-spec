"""
Dump embedded page-scan images from the McLafferty 4th-ed. PDF to PNGs.

The book PDF (``data/IMS-Book/...4ThEdition.pdf``) is a scanned image PDF with no text
layer, but every page carries exactly one embedded bitonal scan, so we extract that image
directly with pypdf -- no poppler/rasteriser needed. The resulting PNGs are what the vision
extraction pass reads.

Runs on the HOST interpreter (needs pypdf + Pillow, both present); it does not need the
container. Output lands under ``data/IMS-Book/pages/`` which is git-ignored (copyrighted).

Book-page <-> PDF-index is NOT a constant offset (the scan drops blank pages), so this tool
only dumps by PDF index and records byte sizes; the printed-page calibration lives in
``data/mechanisms/page_map.json`` (filled from the vision pass, which can read page numbers).

Examples
--------
    python src/mechanisms/dump_pages.py --range 64 98        # Ch.4 region
    python src/mechanisms/dump_pages.py --indices 70 72 74
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF = (
    REPO_ROOT
    / "data/IMS-Book/McLaferttyInterpretationOfMassSpectral4ThEdition.pdf"
)
DEFAULT_OUT = REPO_ROOT / "data/IMS-Book/pages"
MAX_LONG_EDGE = 1600

# Fraction of dark pixels below which a page is treated as an empty leaf.
# A truly blank scan sits around 1e-4 (speckle/edge noise); a real page of even
# sparse line art is an order of magnitude above it.
BLANK_INK_FRACTION = 0.002
INK_THRESHOLD = 128


def _ink_fraction(im) -> float:
    """Fraction of pixels that are dark (actual marks), for blank detection.

    Byte size is a poor proxy: a rotated, sparsely drawn scheme page compresses
    smaller than a dense text page while carrying the mechanisms we care about.
    """
    hist = im.convert("L").histogram()
    dark = sum(hist[:INK_THRESHOLD])
    total = sum(hist)
    return dark / total if total else 0.0


def _largest_image(page):
    """Return the largest embedded PIL image on a pypdf page, or None."""
    best = None
    best_area = -1
    for img in page.images:
        im = img.image
        area = im.size[0] * im.size[1]
        if area > best_area:
            best, best_area = im, area
    return best


def dump(pdf_path: Path, out_dir: Path, indices: list[int]) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    n = len(reader.pages)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    for i in indices:
        if i < 0 or i >= n:
            print(f"p{i:03d}: OUT OF RANGE (0..{n - 1})")
            continue
        im = _largest_image(reader.pages[i])
        if im is None:
            print(f"p{i:03d}: NO EMBEDDED IMAGE")
            manifest.append({"pdf_index": i, "status": "no_image"})
            continue

        if im.mode == "1":
            im = im.convert("L")
        w, h = im.size
        scale = min(1.0, MAX_LONG_EDGE / max(w, h))
        if scale < 1.0:
            im = im.resize((round(w * scale), round(h * scale)))

        out = out_dir / f"p{i:03d}.png"
        im.save(out)
        size = out.stat().st_size
        ink = _ink_fraction(im)
        blank = ink < BLANK_INK_FRACTION
        manifest.append(
            {
                "pdf_index": i,
                "file": str(out.relative_to(REPO_ROOT)),
                "orig_px": [w, h],
                "bytes": size,
                "ink_fraction": round(ink, 5),
                # A near-empty leaf (chapter-divider verso, dropped blank) is a
                # useful calibration signal. Judge it by ACTUAL INK, not by file
                # size: a sparse rotated line-art page (e.g. the "Table 8.2
                # continued" mechanism page, PDF 180) compresses to <60 kB yet
                # carries fully drawn schemes, and a byte-size rule silently
                # dropped it from the extraction set.
                "likely_blank": blank,
            }
        )
        flag = "  [likely blank]" if blank else ""
        print(
            f"p{i:03d}: {im.mode} {w}x{h} -> {out.name} "
            f"({size} bytes, ink {ink:.4f}){flag}"
        )

    return manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Inclusive PDF-index range to dump.",
    )
    ap.add_argument(
        "--indices",
        nargs="+",
        type=int,
        help="Explicit PDF indices to dump.",
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional path to write a JSON dump manifest.",
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    if args.range:
        indices = list(range(args.range[0], args.range[1] + 1))
    elif args.indices:
        indices = args.indices
    else:
        raise SystemExit("Provide --range START END or --indices N [N ...]")

    manifest = dump(args.pdf, args.out, indices)

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        print(f"\nmanifest -> {args.manifest}")


if __name__ == "__main__":
    main()
