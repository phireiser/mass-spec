#!/usr/bin/env python3
"""Regenerate ``thesis/shared/figures/datagen_flamegraph.{png,pdf}``.

Samples the real ``data_generation/main.py`` entry point on a small molecule and renders
the result as an icicle chart, so the thesis figure can be rebuilt from source instead of
being a committed image with no provenance.

Why a hand-rolled sampler: neither the host nor ``mol-spectro.sif`` ships py-spy or austin,
and the container is expensive to rebuild. A background thread walking
``sys._current_frames()`` is what those tools do for pure-Python frames, and it reproduces
the original figure's method *and* its central limitation -- while MØD is inside its own C++
matching loop it holds the GIL and no Python frame is on the stack, so that time is invisible
to any Python-level sampler. ``get_rule_2_molecule_maps`` is therefore under-represented in
the sampled tree; the deterministic cProfile pass below recovers its true share and the
figure's subtitle reports it. This is the same caveat the committed figure carried.

The workload runs via ``runpy`` in this process (main.py is a flat script with no ``__main__``
guard) so the profiled code path is exactly the production one, not a re-implementation.
Dumps go to a scratch directory -- this never touches ``data/processed``.

Usage (inside the container, from the repo root):

    apptainer exec --bind "$PWD/src:/app/src" --bind "$PWD/data/outputs:/app/data/outputs" \
        --bind "$PWD/thesis:/app/thesis" --env PYTHONPATH=/app mol-spectro.sif \
        python /app/src/plot/profile_datagen_flamegraph.py
"""
import argparse
import cProfile
import io
import os
import pstats
import runpy
import sys
import tempfile
import threading
import time
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "src" / "data_generation" / "main.py"
FIG_DIR = ROOT / "thesis" / "shared" / "figures"
FOLDED_PATH = ROOT / "data" / "outputs" / "metrics" / "datagen_flamegraph_folded.txt"

# Frame categories, in priority order of the test applied in `categorize`.
CAT_MINE, CAT_MOD, CAT_IMPORT, CAT_STDLIB = (
    "your Python (dg/)", "MØD (C++ boundary)", "import / startup", "stdlib")
COLORS = {
    CAT_MINE:   "#E08B2E",
    CAT_MOD:    "#1B9C8B",
    CAT_IMPORT: "#7C819D",
    CAT_STDLIB: "#C2C6CF",
}
ORDER = [CAT_MINE, CAT_MOD, CAT_IMPORT, CAT_STDLIB]

# Point size of the box labels; the label-fitting maths in `render` derives from it.
FONT_PT = 10.5


def categorize(filename: str, funcname: str) -> str:
    """Bucket a frame by the file it lives in."""
    f = filename.replace("\\", "/")
    if funcname in ("_find_and_load", "_load_unlocked", "exec_module", "_call_with_frames_removed") \
            or "importlib" in f or "<frozen" in f:
        return CAT_IMPORT
    if "/data_generation/" in f or "/src/plot/" in f:
        return CAT_MINE
    if "/mod/" in f or f.endswith("/mod.py") or "libpymod" in f or "pymod" in f:
        return CAT_MOD
    if "/site-packages/" in f or "/dist-packages/" in f:
        # third-party that is not MØD reads as stdlib-ish support code for this figure
        return CAT_STDLIB
    if "/lib/python" in f or "/lib64/python" in f:
        return CAT_STDLIB
    return CAT_MINE


class StackSampler(threading.Thread):
    """Periodically records the main thread's Python stack as a folded string."""

    def __init__(self, target_tid: int, interval: float):
        super().__init__(daemon=True)
        self.target_tid = target_tid
        self.interval = interval
        self.counts: Counter = Counter()
        self.frame_cat: dict = {}
        self._stop_evt = threading.Event()

    def run(self):
        while not self._stop_evt.is_set():
            # Sampling lives in its own frame so every reference it takes to the *target's*
            # frames dies on return, before we sleep. This is not tidiness -- holding a
            # frame keeps its value stack alive, and the main thread's value stack is where
            # MØD's temporary DGBuilder from `dg.build().execute(strat)` lives. Keep it
            # alive across the sleep and the builder is never destroyed, so the DG is never
            # locked and main.py dies at dump time with
            # "LogicError: Can not dump DG before it is locked."
            self._sample_once()
            time.sleep(self.interval)

    def _sample_once(self):
        frames = sys._current_frames().get(self.target_tid)
        if frames is None:
            return
        stack, entry = [], -1
        f = frames
        while f is not None:
            code = f.f_code
            name = code.co_name
            # The workload's own module frame marks where the harness ends. Everything
            # outer than it is runpy/this script and must not appear in the figure.
            if entry < 0 and code.co_filename == str(MAIN) and name == "<module>":
                entry = len(stack)
            stack.append(name)
            # first writer wins; a name's category is stable in practice
            self.frame_cat.setdefault(name, categorize(code.co_filename, name))
            f = f.f_back
        del f, frames
        if entry < 0:
            return                      # not inside the workload yet -- harness noise
        stack = stack[:entry + 1]       # innermost..entry, still reversed
        stack.reverse()
        if stack:
            self.counts[";".join(stack)] += 1

    def stop(self):
        self._stop_evt.set()
        self.join(timeout=2.0)


def run_workload(smiles: str, name: str, threads: int, scratch: Path, spectra: Path):
    """Execute main.py exactly as the pipeline does, with its stdout captured."""
    argv = [
        str(MAIN),
        "--smiles", smiles,
        "--name", name,
        "--output-dir", str(scratch),
        "--spectra-folder", str(spectra),
        "--number-threads", str(threads),
    ]
    old_argv, old_stdout = sys.argv, sys.stdout
    sys.argv = argv
    sys.stdout = io.StringIO()
    try:
        runpy.run_path(str(MAIN), run_name="__main__")
    except SystemExit:
        pass
    finally:
        sys.argv, sys.stdout = old_argv, old_stdout


def build_tree(counts: Counter):
    """Fold `a;b;c -> n` counts into a nested tree of {name, value, children}."""
    root = {"name": "all", "value": 0, "children": {}}
    for stack, n in counts.items():
        node = root
        node["value"] += n
        for part in stack.split(";"):
            node = node["children"].setdefault(
                part, {"name": part, "value": 0, "children": {}})
            node["value"] += n
    return root


def layout(node, depth, x0, rows):
    """Assign each node a (depth, x, width) box; children ordered by descending width."""
    if depth >= 0:
        rows.append((depth, x0, node["value"], node["name"]))
    x = x0
    for child in sorted(node["children"].values(), key=lambda c: -c["value"]):
        layout(child, depth + 1, x, rows)
        x += child["value"]


def render(counts: Counter, frame_cat: dict, subtitle: str, title: str, out_stem: Path):
    root = build_tree(counts)
    total = root["value"]
    rows = []
    layout(root, -1, 0, rows)          # depth -1 hides the synthetic root
    max_depth = max(d for d, _, _, _ in rows)

    # Header gets a FIXED inch allocation. Positioning it in figure fractions instead makes
    # the title/subtitle/legend drift into each other whenever the stack depth (and so the
    # figure height) changes.
    fig_w, row_in, header_in, bottom_in = 20.0, 0.42, 1.25, 0.10
    fig_h = header_in + row_in * (max_depth + 1) + bottom_in
    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes([0.005, bottom_in / fig_h,
                       0.992, row_in * (max_depth + 1) / fig_h])

    plot_w_in = fig_w * 0.992
    char_in = FONT_PT * 0.60 / 72.0          # rough advance width of one character
    for depth, x, w, name in rows:
        cat = frame_cat.get(name, CAT_MINE)
        ax.add_patch(Rectangle(
            (x, -depth), w, 0.86, facecolor=COLORS[cat], edgecolor="white", linewidth=0.7))
        # Truncate the label to what the box can actually hold rather than dropping it, so
        # narrow frames still read. Boxes too small for even a few characters stay bare.
        fits = int((w / total * plot_w_in - 0.06) / char_in)
        if fits >= 4:
            label = name if fits >= len(name) else name[:max(3, fits - 1)] + "…"
            ax.text(x + total * 0.0025, -depth + 0.43, label, va="center", ha="left",
                    fontsize=FONT_PT, color="#1a1a1a", clip_on=True)

    ax.set_xlim(0, total)
    ax.set_ylim(-max_depth - 0.14, 0.9)
    ax.axis("off")

    y_title = 1.0 - 0.30 / fig_h
    y_sub = 1.0 - 0.56 / fig_h
    y_leg = 1.0 - 0.98 / fig_h
    fig.text(0.005, y_title, title, ha="left", va="center", fontsize=15, fontweight="bold")
    fig.text(0.005, y_sub, subtitle, ha="left", va="center", fontsize=10, color="#444444")
    handles = [Rectangle((0, 0), 1, 1, facecolor=COLORS[c]) for c in ORDER]
    fig.legend(handles, ORDER, loc="center left", bbox_to_anchor=(0.005, y_leg),
               ncol=4, frameon=False, fontsize=11, handlelength=1.1, columnspacing=1.6)

    out_stem.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out_stem.with_suffix("." + ext), dpi=150)
    plt.close(fig)


def native_share(smiles, name, threads, scratch, spectra) -> float:
    """Deterministic pass: what fraction of cumulative time is get_rule_2_molecule_maps."""
    prof = cProfile.Profile()
    prof.enable()
    run_workload(smiles, name, threads, scratch, spectra)
    prof.disable()
    st = pstats.Stats(prof)
    total = max(st.total_tt, 1e-9)
    for (_, _, fn), (_, _, _, ct, _) in st.stats.items():
        if fn == "get_rule_2_molecule_maps":
            return 100.0 * ct / total
    return float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    # Subject choice is governed by sample count. The achievable sample RATE is ~100/s and is
    # not tunable: MØD holds the GIL inside its C++ matching loop, so the sampler only runs
    # when it is briefly released, and shrinking --interval below ~1 ms changes nothing.
    # Sample count therefore tracks build duration alone. 2-propanol was the original
    # subject, but with imports pre-warmed its build is now ~0.2 s (~25 samples) -- the
    # pipeline got far faster on small molecules than DATA_GEN_PERFORMANCE.md records.
    # folic_acid builds in ~2 min, giving a count comparable to the original's 9,588.
    ap.add_argument("--smiles", default="NC1=NC(O)=C2N=C(CNC3=CC=C(C(=O)NC(CCC(=O)O)C(=O)O)C=C3)C=NC2=N1")
    ap.add_argument("--name", default="folic_acid")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--interval", type=float, default=0.0005,
                    help="sampling period in seconds (default 0.5 ms)")
    ap.add_argument("--no-warmup", action="store_true",
                    help="skip the import-priming pass (the figure then includes startup)")
    ap.add_argument("--spectra-folder", default=str(ROOT / "data" / "nist_spectra"))
    ap.add_argument("--out", default=str(FIG_DIR / "datagen_flamegraph"))
    ap.add_argument("--skip-cprofile", action="store_true",
                    help="skip the second deterministic pass (halves the runtime)")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="flamegraph-") as tmp:
        scratch = Path(tmp)
        (scratch / "fwd").mkdir()
        (scratch / "bwd").mkdir()
        spectra = Path(args.spectra_folder)

        # Warm-up pass. main.py is re-executed by runpy each time, but `import mod` and
        # friends are cached in sys.modules after the first run, so this strips interpreter
        # startup out of the measured pass. Without it a fast molecule profiles as mostly
        # importlib: 2-propanol's actual build is now ~1 s, far below the import cost.
        if not args.no_warmup:
            run_workload(args.smiles, args.name, args.threads, scratch, spectra)
            for sub in ("fwd", "bwd"):
                for p in (scratch / sub).glob("*"):
                    p.unlink()

        sampler = StackSampler(threading.get_ident(), args.interval)
        t0 = time.time()
        sampler.start()
        run_workload(args.smiles, args.name, args.threads, scratch, spectra)
        sampler.stop()
        wall = time.time() - t0
        print(f"sampled {sum(sampler.counts.values()):,} stacks over {wall:.1f} s "
              f"({len(sampler.counts):,} distinct)", file=sys.stderr)

        share = float("nan")
        if not args.skip_cprofile:
            for sub in ("fwd", "bwd"):          # fresh scratch so it rebuilds, not skips
                for p in (scratch / sub).glob("*"):
                    p.unlink()
            share = native_share(args.smiles, args.name, args.threads, scratch, spectra)
            print(f"cProfile: get_rule_2_molecule_maps = {share:.0f}% cumulative",
                  file=sys.stderr)

    FOLDED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FOLDED_PATH, "w") as fh:
        for stack, n in sampler.counts.most_common():
            fh.write(f"{stack} {n}\n")

    total = sum(sampler.counts.values())
    # The headline number is how much of the profile is native MØD with no Python frame
    # below it -- samples that land exactly on the execute/__call__ spine. That is time the
    # C++ matching loop holds the GIL, and no Python-level sampler can see inside it.
    opaque = sum(n for stack, n in sampler.counts.items()
                 if stack.endswith("execute;__call__") or stack.endswith("execute"))
    share_txt = (f"{100.0 * opaque / total:.0f}% of samples are inside MØD's C++ matching "
                 f"loop with no Python frame below")
    if share == share:
        share_txt += f" · get_rule_2_molecule_maps {share:.1f}% cumulative (cProfile)"
    render(
        sampler.counts, sampler.frame_cat,
        title=(f"MØD data generation — sampled call tree "
               f"({args.name}, forward-only, {args.threads} thread)"),
        subtitle=(f"width ∝ wall time · {total:,} stack samples over {wall:.1f} s "
                  f"of build (imports pre-warmed) · {share_txt}"),
        out_stem=Path(args.out),
    )
    print(f"wrote {args.out}.png / .pdf and {FOLDED_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
