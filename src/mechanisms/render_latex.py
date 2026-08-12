"""
Render curated ``MechanismRecord`` JSON as chemfig/LaTeX reaction schemes.

Each record becomes a ``\\schemestart ... \\schemestop`` block: the precursor drawn as a
chemfig structure, a labelled reaction arrow, and the products joined by ``\\+``. The
record's ``electron_moves`` are emitted as real curved electron-pushing arrows
(``\\chemmove``) anchored to the atoms they actually touch -- a 2-electron move gets a
full arrowhead, a 1-electron move a half-head (fishhook), matching the book's convention.

The structures are laid out from RDKit 2D coordinates and written as chemfig with
ABSOLUTE bond angles (``-[:37.5]``), so the output is plain vector LaTeX: no image files,
no SVG converter, nothing to rasterise. That matters here -- this machine has no
inkscape, no poppler and no ImageMagick.

Atom-map numbers are the hinge. They are what ``electron_moves`` reference, so every
drawn atom gets a chemfig node name ``@{s<state>a<map>}``; a move on a BOND anchors to the
midpoint of its two atom nodes via TikZ ``calc``. Names are prefixed per drawn instance
because a record reuses the same map numbers in precursor and products.

Runs INSIDE the container (needs RDKit)::

    apptainer exec --bind "$PWD:/app" --env PYTHONPATH=/app mol-spectro.sif \\
        python /app/src/mechanisms/render_latex.py --all --mode document \\
        --out /app/data/outputs/mechanisms_tex/all.tex

Then ``pdflatex`` it on the host. ``--mode fragment`` instead writes one ``\\input``-able
.tex per record, for dropping into the thesis (which already loads chemfig).

Required in the preamble (``--emit-preamble`` prints it)::

    \\usepackage{chemfig}
    \\usetikzlibrary{arrows.meta,calc}

*** COMPILE TWICE. *** chemfig draws ``\\chemmove`` through TikZ ``remember picture`` /
``overlay``, so the absolute node positions come from the .aux file and are only correct on
the SECOND pass. After a single ``pdflatex`` run every electron arrow is displaced -- measured
here at up to 47 pt, i.e. floating in white space nowhere near its bond -- and neither TikZ
nor chemfig raises an error, so the output looks finished and is wrong. Use ``latexmk``, which
reruns automatically, and check with::

    python src/mechanisms/check_arrow_geometry.py <generated>.tex
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

from src.project_paths import shared_path

RDLogger.DisableLog("rdApp.*")

# chemfig bond glyph per RDKit bond order. Aromatic never appears: we Kekulize first,
# which is also what the MOD rule corpus requires of its inputs.
BOND_GLYPH = {
    Chem.BondType.SINGLE: "-",
    Chem.BondType.DOUBLE: "=",
    Chem.BondType.TRIPLE: "~",
}
BOND_TYPE_NUM = {Chem.BondType.SINGLE: 1, Chem.BondType.DOUBLE: 2, Chem.BondType.TRIPLE: 3}

# McLafferty's own arrow labels, so a rendered scheme reads like the book.
STEP_LABEL = {
    "alpha_cleavage": r"$\alpha$",
    "inductive_cleavage": r"\textit{i}",
    "sigma_dissociation": r"$\sigma$",
    "hydrogen_rearrangement": r"\textit{r}H",
    "double_hydrogen_rearrangement": r"2\textit{r}H",
    "retro_diels_alder": r"\textit{rd}",
    "displacement": r"\textit{rd}",
    "elimination": r"\textit{re}",
    "ionization": r"$-e^-$",
    "charge_migration": r"\textit{cm}",
}

PREAMBLE = r"""\usepackage{chemfig}
\usetikzlibrary{arrows.meta,calc}"""


def tex_escape(s: str) -> str:
    """Escape a plain string for LaTeX text mode."""
    out = []
    for ch in s:
        if ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        elif ch == "\\":
            out.append(r"\textbackslash{}")
        else:
            out.append(ch)
    return "".join(out)


# --------------------------------------------------------------------------- structures


def _atom_label(atom: Chem.Atom) -> str:
    """chemfig atom text. Skeletal carbons render as an empty vertex ``{}``."""
    sym = atom.GetSymbol()
    charge = atom.GetFormalCharge()
    radicals = atom.GetNumRadicalElectrons()
    plain_carbon = (
        sym == "C" and charge == 0 and radicals == 0 and atom.GetDegree() > 0
    )
    if plain_carbon:
        return "{}"

    label = sym
    if sym != "C":
        n_h = atom.GetTotalNumHs()
        if n_h == 1:
            label += "H"
        elif n_h > 1:
            label += f"H_{{{n_h}}}"

    decor = ""
    if charge:
        mag = "" if abs(charge) == 1 else str(abs(charge))
        decor += mag + ("+" if charge > 0 else "-")
    decor += r"\bullet" * radicals
    if decor:
        # \chemabove keeps the charge/radical glyph off the bond lines.
        label = r"\chemabove{" + label + r"}{\scriptstyle " + decor + "}"
    return label


def _angle(conf, i: int, j: int) -> float:
    a, b = conf.GetAtomPosition(i), conf.GetAtomPosition(j)
    return round(math.degrees(math.atan2(b.y - a.y, b.x - a.x)), 1)


def mol_from_species(species: dict) -> Chem.Mol:
    mol = Chem.MolFromSmiles(species["mapped_smiles"])
    if mol is None:
        raise ValueError(f"unparseable mapped_smiles for {species['species_id']!r}")
    Chem.Kekulize(mol, clearAromaticFlags=True)
    AllChem.Compute2DCoords(mol)
    return mol


def chemfig_molecule(mol: Chem.Mol, prefix: str, named_maps: set[int]) -> str:
    """Emit a chemfig body for ``mol`` using its 2D conformer for absolute angles.

    ``named_maps`` selects which atoms get a ``@{...}`` node name; naming only the atoms
    an arrow actually touches keeps the emitted code readable.
    """
    conf = mol.GetConformer()
    n = mol.GetNumAtoms()

    # Spanning tree by DFS; every remaining bond becomes an explicit chemfig ring closure.
    # Mark visited on ENTRY, not when queueing: an iterative version that pushes first
    # classifies a ring-closing bond as a tree bond, and the ring then silently renders as
    # an open chain (benzene came out as hexatriene). The bond-count assertion below is
    # the backstop for that whole family of mistakes.
    parent: dict[int, int] = {}
    order: list[int] = []
    tree_bonds: set[frozenset[int]] = set()
    seen = [False] * n
    root = next((a.GetIdx() for a in mol.GetAtoms() if a.GetDegree() == 1), 0)

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10 * n + 1000))

    def walk(idx: int) -> None:
        seen[idx] = True
        order.append(idx)
        for nb in [a.GetIdx() for a in mol.GetAtomWithIdx(idx).GetNeighbors()]:
            if not seen[nb]:
                parent[nb] = idx
                tree_bonds.add(frozenset((idx, nb)))
                walk(nb)

    walk(root)
    if not all(seen):
        raise ValueError("disconnected species: chemfig needs one connected fragment")

    ring_bonds = [
        b for b in mol.GetBonds()
        if frozenset((b.GetBeginAtomIdx(), b.GetEndAtomIdx())) not in tree_bonds
    ]
    pos_in_order = {idx: k for k, idx in enumerate(order)}
    # Ring-closure marks. VERIFIED against chemfig by diffing the PDF content stream:
    # the bond type must sit on the CLOSING '?' -- putting it on the first occurrence
    # silently renders a single bond (6 lineto ops vs 7 for a real double bond).
    closure_at: dict[int, list[str]] = {}
    for k, bond in enumerate(ring_bonds):
        tag = chr(ord("a") + k) if k < 26 else f"z{k}"
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        first, second = (i, j) if pos_in_order[i] < pos_in_order[j] else (j, i)
        btype = BOND_TYPE_NUM.get(bond.GetBondType(), 1)
        closure_at.setdefault(first, []).append(f"?[{tag}]")
        closure_at.setdefault(second, []).append(
            f"?[{tag}]" if btype == 1 else f"?[{tag},{btype}]"
        )

    children: dict[int, list[int]] = {}
    for child, par in parent.items():
        children.setdefault(par, []).append(child)

    def emit(idx: int) -> str:
        atom = mol.GetAtomWithIdx(idx)
        amap = atom.GetAtomMapNum()
        head = f"@{{{prefix}{amap}}}" if amap in named_maps else ""
        out = head + _atom_label(atom) + "".join(closure_at.get(idx, []))

        kids = children.get(idx, [])
        for pos, kid in enumerate(kids):
            bond = mol.GetBondBetweenAtoms(idx, kid)
            glyph = BOND_GLYPH.get(bond.GetBondType(), "-")
            branch = f"{glyph}[:{_angle(conf, idx, kid)}]{emit(kid)}"
            # every child but the last is a parenthesised branch
            out += f"({branch})" if pos < len(kids) - 1 else branch
        return out

    body = emit(root)

    # INVARIANT: every bond of the molecule must reach the page exactly once, as a bond
    # glyph on a tree edge or as a pair of '?' ring-closure marks. A shortfall here is the
    # silent-wrong-picture failure (a ring drawn as a chain), which LaTeX would never flag.
    drawn = len(re.findall(r"[-=~]\[:", body)) + len(re.findall(r"\?\[", body)) // 2
    if drawn != mol.GetNumBonds():
        raise ValueError(
            f"bond accounting: emitted {drawn} of {mol.GetNumBonds()} bonds "
            f"({len(ring_bonds)} ring closure(s)) -- the drawing would be wrong"
        )
    return body


# ----------------------------------------------------------------------------- arrows


def _anchor(loc: dict, prefix: str) -> str | None:
    """TikZ coordinate for an ElectronLocation, or None if it cannot be drawn.

    A bond anchors at the exact midpoint of its two atom nodes, which is ON the drawn bond (in
    a coordinate expression a node name resolves to its centre, so the midpoint is the true
    bond centre).

    An atom anchors at ``.base``. Three candidates were measured against the atom's own axis
    (chemfig centres an atom label on the bond line), using an arrow aimed at a
    ``\\chemabove{O}{+\\bullet}``: the bare node **+6.7 pt** (a path clips to the node BORDER,
    and the decoration makes the box tall), ``.center`` **+4.28 pt**, ``.mid`` +3.14 pt,
    ``.base`` **+1.19 pt**. ``\\chemabove`` inflates the box upward, so centre-like anchors
    drift above the atom and the arrow appears to point at the charge symbol rather than at
    the atom; ``.base`` tracks the glyph. For an empty skeletal vertex all anchors coincide.
    """
    maps = list(loc.get("atom_maps") or ())
    kind = loc.get("type")
    if kind == "bond" and len(maps) == 2:
        return f"($({prefix}{maps[0]})!0.5!({prefix}{maps[1]})$)"
    if maps:
        # atom / lone_pair / radical_orbital all anchor on the atom itself
        return f"({prefix}{maps[0]}.base)"
    return None  # 'external' (e.g. the EI ionization hole) has nothing to point at


def electron_arrows(step: dict, prefix: str, bend: int) -> tuple[list[str], list[str]]:
    """Return (\\chemmove lines, notes about moves that could not be drawn).

    Anchors are exact: a bond move starts at the true midpoint of its two atom nodes, an
    atom/lone-pair move at the atom's node border. Nothing is nudged -- the tail belongs ON
    the bond. (If the arrows do not land there, the document was compiled only once; see the
    module docstring and ``check_arrow_geometry.py``.)
    """
    lines, skipped = [], []
    seen: dict[tuple[str, str], int] = {}
    for k, move in enumerate(step.get("electron_moves", [])):
        src = _anchor(move["source"], prefix)
        dst = _anchor(move["target"], prefix)
        if src is None or dst is None:
            which = "source" if src is None else "target"
            skipped.append(
                f"move {k + 1} ({move['source']['type']} -> {move['target']['type']}): "
                f"{which} has no atom to anchor to"
            )
            continue
        tip = "Stealth" if move.get("electron_count") == 2 else "Stealth[left]"
        # Two moves can share BOTH endpoints -- e.g. the two fishhooks that together make
        # one 2-electron arrow. Drawn with the same bend they coincide exactly and one
        # silently disappears, so fan repeats apart. Endpoints stay untouched.
        n = seen.get((src, dst), 0)
        seen[(src, dst)] = n + 1
        this_bend = bend + (0 if n == 0 else (12 * n if n % 2 else -12 * n))
        lines.append(
            rf"\chemmove[-{{{tip}}}]{{\draw[shorten <=1pt,shorten >=3pt]"
            rf"{src} to[bend left={this_bend}] {dst};}}"
        )
    return lines, skipped


# ------------------------------------------------------------------------------ record


def _species_by_id(rec: dict) -> dict[str, dict]:
    return {s["species_id"]: s for s in rec["species"]}


def _segments(rec: dict) -> list[list[tuple[str, dict | None]]]:
    """Split a record into scheme rows: [[(state, step), ..., (state, None)], ...].

    A linear record becomes ONE chained row (A -> B -> C), which is how the book draws a
    cascade. A BRANCHING record -- one intermediate feeding two competing channels, e.g.
    IMS8-EQ8.101c -- must not be chained: forcing it into one row would print the shared
    intermediate twice in sequence, reading as A -> B -> B -> C. Those get one row per step.
    """
    steps = rec["steps"]
    by_from: dict[str, list[dict]] = {}
    for s in steps:
        by_from.setdefault(s["from_state"], []).append(s)
    targets = {s["to_state"] for s in steps}
    starts = [s["from_state"] for s in steps if s["from_state"] not in targets]

    branching = any(len(v) > 1 for v in by_from.values()) or len(starts) != 1
    if branching:
        return [[(s["from_state"], s), (s["to_state"], None)] for s in steps]

    chain: list[tuple[str, dict | None]] = []
    node, guard = starts[0], 0
    while node in by_from and guard <= len(steps):
        step = by_from[node][0]
        chain.append((node, step))
        node = step["to_state"]
        guard += 1
    chain.append((node, None))
    return [chain]


def _locator(rec: dict) -> str:
    for ev in rec.get("evidence", []):
        loc = ev.get("locator") or {}
        if loc.get("equation") or loc.get("figure"):
            bits = []
            if loc.get("equation"):
                bits.append(f"Eq.~{tex_escape(loc['equation'])}")
            if loc.get("figure"):
                bits.append(f"Fig.~{tex_escape(loc['figure'])}")
            if loc.get("page"):
                bits.append(f"p.~{loc['page']}")
            return ", ".join(bits)
    return ""


def render_record(rec: dict, bend: int = 45, notes: bool = False) -> tuple[str, list[str]]:
    """Return (LaTeX for one record, warnings)."""
    warnings: list[str] = []
    species = _species_by_id(rec)
    states = {s["state_id"]: s for s in rec["states"]}
    # Node names must be unique across a whole DOCUMENT, not merely within a record, so
    # they carry a sanitised mechanism id. TikZ node names take [A-Za-z0-9] only.
    stem = re.sub(r"[^A-Za-z0-9]", "", rec["mechanism_id"])

    head = f"% ==== {rec['mechanism_id']} ".ljust(78, "=")
    # Repeated per record on purpose: fragments get \input'd individually, so the warning has
    # to travel with the code that depends on it.
    out = [head, r"% NOTE: needs TWO LaTeX passes (\chemmove is TikZ overlay-based);"
                 r" one pass silently misplaces every arrow."]

    for seg_no, segment in enumerate(_segments(rec)):
        parts: list[str] = []
        for pos, (state_id, step) in enumerate(segment):
            # Anchors are named per DRAWN INSTANCE, never per state: a branching record
            # draws one state in several rows, and keying by state let the second row
            # silently steal the first row's atom names (caught by self_check on 8.101c).
            prefix = f"{stem}x{seg_no}y{pos}a"
            state = states.get(state_id)
            if state is None:
                warnings.append(f"{rec['mechanism_id']}: unknown state {state_id!r}")
                continue

            needed: set[int] = set()
            if step is not None:
                for move in step["electron_moves"]:
                    needed.update(move["source"].get("atom_maps") or ())
                    needed.update(move["target"].get("atom_maps") or ())

            drawn = []
            for sid in state["species_ids"]:
                sp = species.get(sid)
                if sp is None:
                    warnings.append(f"{rec['mechanism_id']}: unknown species {sid!r}")
                    continue
                try:
                    mol = mol_from_species(sp)
                    body = chemfig_molecule(mol, prefix, needed)
                except Exception as exc:  # noqa: BLE001 - report, never abort the batch
                    warnings.append(f"{rec['mechanism_id']}/{sid}: {exc}")
                    body = r"\textrm{?}"
                drawn.append(f"\\chemfig{{{body}}}")
            parts.append("\n\\+\n".join(drawn))

            if step is not None:
                moves, skipped = electron_arrows(step, prefix, bend)
                parts.extend(moves)
                for note in skipped:
                    parts.append(f"% NOT DRAWN -- {step['step_id']}: {note}")
                    warnings.append(f"{rec['mechanism_id']}/{step['step_id']}: {note}")
                label = STEP_LABEL.get(step["step_class"])
                if label is None:
                    label = r"\textit{" + tex_escape(step["step_class"].replace("_", " ")) + "}"
                parts.append(f"\\arrow{{->[{label}]}}")

        # \setchemfig is the current key-value interface; the older \setatomsep does not
        # exist in the chemfig shipped here (TeX Live 2020 + ~/texmf).
        out += [r"\begin{center}", r"\setchemfig{atom sep=2.2em}", r"\schemestart"]
        out += parts
        out += [r"\schemestop", r"\end{center}"]

    loc = _locator(rec)
    if loc:
        out.append(
            r"\begin{center}\footnotesize " + tex_escape(rec["mechanism_id"])
            + r" --- " + loc + r"\end{center}"
        )
    if notes:
        for ev in rec.get("evidence", []):
            if ev.get("curator_note"):
                out.append(r"{\footnotesize\itshape " + tex_escape(ev["curator_note"]) + "}")
                out.append(r"\par\smallskip")
    return "\n".join(out), warnings


# ------------------------------------------------------------------------------- self-check


def self_check(latex: str) -> list[str]:
    """Structural checks on emitted LaTeX (no rasteriser exists on this machine).

    Catches the failure modes that silently produce a wrong picture rather than a
    LaTeX error: an arrow pointing at an undefined node, or unbalanced groups.
    """
    problems = []
    defined = set(re.findall(r"@\{([A-Za-z0-9]+)\}", latex))
    used: set[str] = set()
    for line in latex.splitlines():
        if line.startswith(r"\chemmove"):
            used.update(re.findall(r"\(([A-Za-z0-9]+)\)", line))
    for name in sorted(used - defined):
        problems.append(f"\\chemmove references undefined node {name!r}")
    if latex.count("{") != latex.count("}"):
        problems.append(f"unbalanced braces: {latex.count('{')} open, {latex.count('}')} close")
    if latex.count(r"\schemestart") != latex.count(r"\schemestop"):
        problems.append("unbalanced schemestart/schemestop")
    for body in re.findall(r"\\chemfig\{(.*)\}", latex):
        if body.count("(") != body.count(")"):
            problems.append("unbalanced parentheses inside a \\chemfig branch")
            break
    return problems


# ------------------------------------------------------------------------------------ cli


def document(bodies: list[str], title: str) -> str:
    return "\n".join([
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[a4paper,margin=2cm]{geometry}",
        r"\usepackage{amsmath}",
        PREAMBLE,
        r"\pagestyle{empty}",
        r"\begin{document}",
        r"\begin{center}\Large " + tex_escape(title) + r"\end{center}",
        *bodies,
        r"\end{document}",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--records-dir", default=str(shared_path("MECHANISM_RECORDS_DIR_REL")))
    ap.add_argument("--id", action="append", default=[], help="mechanism_id (repeatable)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--mode", choices=("fragment", "document"), default="document")
    ap.add_argument("--out", required=False, help="output .tex (document) or dir (fragment)")
    ap.add_argument("--bend", type=int, default=45, help="curvature of electron arrows")
    ap.add_argument("--notes", action="store_true", help="include curator notes")
    ap.add_argument("--emit-preamble", action="store_true")
    args = ap.parse_args()

    if args.emit_preamble:
        print(PREAMBLE)
        return 0

    paths = sorted(glob.glob(os.path.join(args.records_dir, "*.json")))
    if args.id:
        wanted = set(args.id)
        paths = [p for p in paths if os.path.basename(p)[:-5] in wanted]
        missing = wanted - {os.path.basename(p)[:-5] for p in paths}
        for m in sorted(missing):
            print(f"[WARN] no such record: {m}", file=sys.stderr)
    elif not args.all:
        print("give --all or --id ID", file=sys.stderr)
        return 2
    if args.limit:
        paths = paths[: args.limit]

    bodies, all_warnings, failed = [], [], 0
    for path in paths:
        rec = json.load(open(path))
        try:
            body, warns = render_record(rec, bend=args.bend, notes=args.notes)
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {os.path.basename(path)}: {exc}", file=sys.stderr)
            failed += 1
            continue
        problems = self_check(body)
        for p in problems:
            warns.append(f"{rec['mechanism_id']}: SELF-CHECK {p}")
        all_warnings += warns
        bodies.append(body)

        if args.mode == "fragment" and args.out:
            os.makedirs(args.out, exist_ok=True)
            with open(os.path.join(args.out, rec["mechanism_id"] + ".tex"), "w") as fh:
                fh.write(body + "\n")

    if args.mode == "document":
        text = document(bodies, "Curated mechanisms (McLafferty, Interpretation of Mass Spectra 4e)")
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w") as fh:
                fh.write(text + "\n")
        else:
            print(text)

    for w in all_warnings:
        print(f"[WARN] {w}", file=sys.stderr)
    print(
        f"rendered {len(bodies)}/{len(paths)} record(s), {failed} failed, "
        f"{len(all_warnings)} warning(s)",
        file=sys.stderr,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
