"""
Verify that rendered electron-pushing arrows actually START AND END ON THE STRUCTURE.

``render_latex.py`` anchors every arrow to chemfig atom nodes, but chemfig draws
``\\chemmove`` through TikZ ``remember picture``/``overlay``: the absolute node positions
live in the .aux file and are only correct on the SECOND LaTeX pass. Compile once and every
arrow is silently displaced -- in one measured case by 96 pt, landing far from its bond with
no error or warning from chemfig. This script is the guard against that, and against any
future regression in anchoring.

It compiles the document (twice, deliberately), then measures the drawn geometry straight
out of the PDF content stream: bonds are the long straight segments, electron arrows are the
Bezier curves. For every arrow endpoint it reports the distance to the nearest bond. A
correctly anchored tail sits ON a bond (~0 pt) or on an atom at a bond end.

No rasteriser is needed, which matters on this machine (no poppler/inkscape/ImageMagick).
Runs on the HOST (needs pypdf only, not RDKit)::

    python src/mechanisms/check_arrow_geometry.py outputs/mechanisms_tex/all.tex
"""

from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import subprocess
import sys

from pypdf import PdfReader

# Bonds at the default atom separation are ~24-30 pt; arrowhead strokes are 1-4 pt. Anything
# shorter than this is head decoration, not a bond, and must not count as a landing site.
MIN_BOND_LEN = 8.0
# Atom labels are set at the body size (~10 pt); \scriptstyle charge/radical marks and
# subscripts land near 7 pt. Only the former count as places an arrow may legitimately touch.
MIN_ATOM_FONT_PT = 8.0
# Rough mean advance width per glyph, in em, for estimating an atom label's extent from the
# character count. Only used to locate a label's centre, so a few tenths of a pt is immaterial.
MEAN_GLYPH_EM = 0.5
# A tail this far out cannot be explained by label-centre estimation -- it is misplaced.
GROSS_PT = 20.0
# Above this share of tails past the tolerance, something systematic is wrong.
MAX_ADRIFT_FRACTION = 0.05
# Slack that is expected even when anchoring is perfect, from two sources: render_latex
# shortens each arrow by 1 pt at the tail, and a glyph's recorded position in the content
# stream is its BASELINE ORIGIN, a few pt below-left of the visual centre of an atom label.
# Correctly anchored tails measure 0.7 pt (median) and at worst ~5.6 pt against this metric;
# a single-pass compile measures up to 47 pt, so the two regimes are not close.
DEFAULT_TOLERANCE = 6.0


_TOKEN = re.compile(
    r"\((?:[^()\\]|\\.)*\)"      # literal string  (Tj/TJ text)
    r"|<[0-9A-Fa-f\s]*>"         # hex string
    r"|-?\d*\.?\d+"              # number
    r"|[A-Za-z']+\*?"            # operator
    r"|/[^\s/\[\]<>()]+"         # name
)


def _ops(stream: str):
    """Yield (operator, numeric_args, text_char_count) in stream order."""
    args: list[float] = []
    chars = 0
    for t in _TOKEN.findall(stream):
        if re.fullmatch(r"-?\d*\.?\d+", t):
            args.append(float(t))
        elif t.startswith("("):
            chars += len(re.sub(r"\\.", "x", t[1:-1]))
        elif t.startswith("<"):
            chars += len(re.sub(r"\s", "", t[1:-1])) // 2
        else:
            yield t, args, chars
            args, chars = [], 0


def page_paths(path: str, page: int) -> tuple[list, list, list]:
    """Return (bond_segments, arrow_curves, label_points) for one page, in PDF user space.

    ``label_points`` are where glyphs are set. They matter because a bond STOPS SHORT of a
    labelled atom (chemfig insets it), so bond endpoints alone under-report where atoms are,
    and an arrow correctly anchored to an ``O`` centre then looks adrift by the label gap.
    """
    data = PdfReader(path).pages[page].get_contents().get_data().decode("latin-1")
    ctm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    stack: list[list[float]] = []
    cur: list[tuple[float, float]] = []
    lines, curves, labels = [], [], []
    tm: list[float] | None = None
    fontsize = 0.0

    def apply(x: float, y: float) -> tuple[float, float]:
        a, b, c, d, e, f = ctm
        return (a * x + c * y + e, b * x + d * y + f)

    for op, a, nchars in _ops(data):
        if op == "q":
            stack.append(list(ctm))
        elif op == "Q" and stack:
            ctm = stack.pop()
        elif op == "cm" and len(a) >= 6:
            m, n = a[-6:], ctm
            ctm = [
                m[0] * n[0] + m[1] * n[2], m[0] * n[1] + m[1] * n[3],
                m[2] * n[0] + m[3] * n[2], m[2] * n[1] + m[3] * n[3],
                m[4] * n[0] + m[5] * n[2] + n[4], m[4] * n[1] + m[5] * n[3] + n[5],
            ]
        elif op == "m" and len(a) >= 2:
            cur = [apply(a[-2], a[-1])]
        elif op == "l" and len(a) >= 2 and cur:
            cur.append(apply(a[-2], a[-1]))
            lines.append((cur[-2], cur[-1]))
        elif op == "c" and len(a) >= 6 and cur:
            p3 = apply(a[4], a[5])
            curves.append((cur[-1], p3))
            cur.append(p3)
        elif op == "BT":
            # A text object starts at the identity matrix; chemfig often positions with Td
            # alone and never emits Tm, so without this the label scan silently finds nothing.
            tm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        elif op == "Tm" and len(a) >= 6:
            tm = list(a[-6:])
        elif op in ("Td", "TD") and len(a) >= 2 and tm:
            tm[4] += a[-2] * tm[0] + a[-1] * tm[2]
            tm[5] += a[-2] * tm[1] + a[-1] * tm[3]
        elif op == "Tf" and a:
            fontsize = a[-1]
        elif op in ("Tj", "TJ") and tm:
            # Keep ATOM labels only. Charge/radical decorations and subscripts are set in
            # \scriptstyle, so they come out ~2-3 pt smaller; counting them as structure lets
            # an arrow that points at a '+' symbol instead of at its atom score as on-target,
            # which made this metric unable to rank .center against .base.
            if fontsize >= MIN_ATOM_FONT_PT:
                # A string's recorded position is the LEFT EDGE of its baseline, but an atom
                # anchored at .base sits at the label's horizontal CENTRE. Without this shift a
                # correctly anchored tail on a wide label such as "OH_2" measures ~11 pt off
                # (verified: 11.32 pt), which is indistinguishable from a real misplacement.
                width = MEAN_GLYPH_EM * fontsize * max(nchars, 1)
                labels.append(apply(tm[4] + width / 2, tm[5]))
    bonds = [
        (p, q) for p, q in lines
        if math.dist(p, q) >= MIN_BOND_LEN
    ]
    return bonds, curves, labels


def dist_to_segment(pt, seg) -> float:
    (x0, y0), (x1, y1) = seg
    px, py = pt
    dx, dy = x1 - x0, y1 - y0
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.dist(pt, (x0, y0))
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / denom))
    return math.dist(pt, (x0 + t * dx, y0 + t * dy))


def compile_twice(tex: str) -> str:
    """Run pdflatex twice (required: overlay node positions resolve on pass 2)."""
    tex = os.path.abspath(tex)
    workdir, name = os.path.dirname(tex), os.path.basename(tex)
    if not shutil.which("pdflatex"):
        raise SystemExit("pdflatex not found")
    for run in (1, 2):
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", name],
            cwd=workdir, capture_output=True, text=True,
        )
        if proc.returncode != 0 and run == 2:
            tail = "\n".join(
                l for l in proc.stdout.splitlines() if l.startswith("! ")
            )
            raise SystemExit(f"pdflatex failed on pass {run}:\n{tail}")
    return os.path.join(workdir, name[:-4] + ".pdf")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tex", help="generated .tex (will be compiled twice)")
    ap.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    ap.add_argument("--no-compile", action="store_true", help="measure the existing .pdf")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pdf = (
        args.tex[:-4] + ".pdf" if args.no_compile else compile_twice(args.tex)
    )
    reader = PdfReader(pdf)

    # TAILS carry the strong invariant. Every electron_move in the corpus sources from an
    # EXISTING bond (832) or an atom/lone pair/radical orbital (278) -- never from a bond that
    # does not exist yet -- so a tail has no legitimate reason to float: it must sit on a drawn
    # bond, or on a vertex (an atom, where the standoff of a curved departure is expected).
    # HEADS are reported but not failed: 264 of them target a FORMING bond, whose midpoint is
    # genuinely empty space, which is exactly how the book draws a bond being made.
    tails: list[tuple[float, int]] = []
    heads: list[tuple[float, int]] = []
    for pno in range(len(reader.pages)):
        bonds, curves, labels = page_paths(pdf, pno)
        if not bonds or not curves:
            continue
        # "on the structure" = on a bond line, at a bond vertex, or at an atom LABEL
        atoms = {p for seg in bonds for p in seg} | set(labels)

        def nearest(pt) -> float:
            return min(
                min(dist_to_segment(pt, b) for b in bonds),
                min((math.dist(pt, v) for v in atoms), default=1e9),
            )

        for (start, end) in curves:
            tails.append((nearest(start), pno + 1))
            heads.append((nearest(end), pno + 1))

    tails.sort(reverse=True)
    heads.sort(reverse=True)
    bad = [t for t in tails if t[0] > args.tolerance]
    if not args.quiet:
        print(f"{pdf}: {len(tails)} arrow(s) on {len(reader.pages)} page(s)")
        print(
            f"  TAILS (must be on a bond or atom, tol {args.tolerance} pt): "
            f"{len(tails) - len(bad)} anchored, {len(bad)} ADRIFT"
        )
        for d, pno in tails[:8]:
            print(f"    {'ADRIFT' if d > args.tolerance else 'ok':7s} p{pno:<3d} {d:7.2f} pt")
    if tails:
        print(f"  median tail distance: {tails[len(tails) // 2][0]:.2f} pt")
        print(f"  median head distance: {heads[len(heads) // 2][0]:.2f} pt "
              f"(heads may legitimately aim into a forming bond)")

    # Fail on real misplacement, not on measurement slack. A few tails sit 6-9 pt out because
    # this metric estimates an atom label's centre from a glyph count (subscripts are excluded
    # from the anchor set yet still widen the node). Genuine breakage does not look like that:
    # a single-pass compile put 73% of endpoints adrift by up to 47 pt.
    gross = [t for t in tails if t[0] > GROSS_PT]
    fraction = len(bad) / len(tails) if tails else 0.0
    if gross or fraction > MAX_ADRIFT_FRACTION:
        print(
            f"  FAIL: {len(gross)} tail(s) beyond {GROSS_PT} pt, "
            f"{fraction:.1%} beyond tolerance (limit {MAX_ADRIFT_FRACTION:.0%})"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
