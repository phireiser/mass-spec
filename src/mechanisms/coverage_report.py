"""
Generate data/mechanisms/coverage_report.md from the committed records + rule_index.

Reports, per chapter: which book equations are covered by a MechanismRecord, which
rule_index equations are still missing, records that flag a mis-encoded / non-matching MØD
rule (audit byproduct), and records lacking an equation id (figure-based). Pure stdlib (host).

    python src/mechanisms/coverage_report.py
"""

from __future__ import annotations

import glob
import json
import re
from pathlib import Path

from src.project_paths import shared_path

RECORDS = shared_path("MECHANISM_RECORDS_DIR_REL")
RULE_INDEX = shared_path("MECHANISMS_DIR_REL", "rule_index.json")
OUT = shared_path("MECHANISMS_DIR_REL", "coverage_report.md")

MISMATCH_RE = re.compile(r"MISMATCH|non-conserv|hypervalent|mis-?encoded|does NOT", re.I)

# Numbered book "equations" that carry NO fragmentation mechanism, verified against the page scan.
# They are gaps in the equation-number sequence by design, not extraction misses.
NON_MECHANISM_EQS = {
    "8.23": "p155: conformational drawings (trans- vs cis-annulated bicyclic ether radical cations) "
            "showing the O n-orbital lobe / bridgehead-H alignment for stereoelectronic control. "
            "No reaction arrow, no products, no electron-pushing arrows.",
    "8.27": "p158: static intramolecular H-bonded MH+ structures (HO···+H···OH proton bridge, "
            "cis/trans 1,4-cyclohexanediol). Dashed lines are hydrogen bonds, not arrows; no products.",
    "8.28": "p158: static proton-bridged MH+ cage structures (H2N···+H···OH and the norbornene "
            "H+-bridged C=C/O-H). No reaction arrows, no products.",
    "8.32": "p161: a TABLE of ionization-energy values for compounds (a)-(g) (amine/sulfide/selenide). "
            "No reaction at all.",
    "9.5": "p231 (PDF 242): a numbered equation that depicts a fragmentation but draws NO mechanism -- "
           "two terpenoid polyenes annotated with SQUIGGLE cleavage marks and the neutral-loss labels "
           "(M-83) and (M-57), showing how double-bond position changes the allylic cleavage. Zero "
           "curved arrows, and the chain is the generic (C5H8)4H. Encoding it would mean inventing the "
           "whole electron flow, which conventions (A)/(D)/(F) forbid -- the same policy that excluded "
           "Table 8.4. Verified by reading the page directly.",
    "8.96": "p206 (PDF 218): four STATIC ion structures labelled (a)-(d) -- a D-labelled protonated "
            "ester, a protonated/ipso-substituted arene, an aryl-ether arenium and a protonated-ester "
            "oxocarbenium -- printed side by side to name the ion types the surrounding text argues "
            "about ('the Equation 8.96(b-d) ions'). No reaction arrow, no products, no curved arrows.",
}

# Pages inside the dumped Ch.4/Ch.8 ranges that carry NO mechanism, verified against the scan.
# Recorded so a later pass does not re-litigate them -- an in-range page with zero records is
# otherwise indistinguishable from a page the extraction silently dropped (which is exactly the
# bug the byte-size blank heuristic caused for PDF 180).
NON_MECHANISM_PAGES = {
    229: "printed p217: Figure 8.9, a full-page bar spectrum of octadecanoic acid. No scheme.",
    234: "printed p222: tail of the 8.12 General-references prose plus the first page of Table 8.4 "
         "'Examples of other rearrangement reactions' -- a neutral-loss lookup index (columns = "
         "eliminated neutral m/z + formula, and molecule class). Zero arcs, zero product "
         "structures, zero charge/radical marks; the m/z column is the NEUTRAL's mass, not an ion. "
         "Encoding a row would mean inventing both connectivity and electron flow.",
    235: "printed p223: Table 8.4 continued -- same listing, same reason.",
    236: "printed p225: opening page of Chapter 9 (compound classes), which is out of scope. "
         "Prose only; its two inline formulas carry no equation number, arrows or m/z.",
    249: "printed p238: running prose only (end of the terpenoid 'Unknowns' note + the opening of "
         "'Aromatic hydrocarbons'). Zero structures, zero arcs, zero equation numbers; it forward-"
         "references Equations 9.13/9.14, which are drawn on the following page. Read in full.",
    253: "printed p242: running prose only (further decomposition of the C_nH_(2n+1)O+ ions, then "
         "the 'Cyclic aliphatic alcohols' lead-in). Zero structures, zero arcs, zero equation "
         "numbers; it forward-references Equations 9.19/9.20/9.21, drawn on p243/p244. Read in full.",
    257: "printed p246: tail of the 9.23/9.24 prose, then the 'Unknown 9.2' exercise (a peak table "
         "plus its bar spectrum -- an exercise, explicitly out of scope), then the '9.3 Aldehydes "
         "and ketones' section opening, which only lists where spectra appear. No numbered "
         "equation, no scheme, no arcs. Read in full.",
    258: "printed p247: Figures 9.8/9.9/9.10 (bar spectra of 2-ethylhexanal, 6-methyl-2-heptanone "
         "and 6-methyl-5-heptene-2-one) plus prose. The inset structures carry SQUIGGLE cleavage "
         "marks with mass labels and ZERO curved arrows -- the same arrow-free class as Figure 9.7 "
         "and eq 9.5, so nothing to transcribe faithfully. See the FIG4.4a/b scope question: those "
         "two records WERE encoded from an inset of exactly this kind. Read in full.",
    264: "printed p253: Figure 9.11 alone, a rotated full-page bar spectrum of methyl "
         "3,7,11,15-tetramethylhexadecanoate. Its inset structure is again squiggle-marked with "
         "mass labels (74/101/171/241) and draws no arrows. No equation, no scheme. Read in full.",
    268: "printed p257: running prose only (tail of the sec-butyl-acetate discussion, then 'Esters "
         "containing other functional groups'). Zero structures, zero arcs, zero equation numbers; "
         "it back-references Equations 9.32/9.34 and forward-references 4.41/8.81/8.83, all drawn "
         "elsewhere. Read in full.",
    270: "printed p259: opening of section '9.5 Acids, anhydrides, and lactones' -- running prose "
         "only (Aliphatic acids / Aromatic acids / Anhydrides). Names many losses in words "
         "((M - OH)+, (M - H2O)+., (M - CO2)+.) but draws no structure, no arrow and no equation "
         "number. Read in full.",
    271: "printed p260: Figure 9.13 (succinic anhydride bar spectrum, squiggle-marked inset with "
         "the mass labels 28/56 and zero arrows) plus the 'Unknown 9.3' exercise (a peak table and "
         "its bar spectrum). Exercises are explicitly out of scope and the inset is the same "
         "arrow-free class as Figure 9.7/9.10. No numbered equation. Read in full.",
    272: "printed p261: running prose ('Lactones', then the opening of section '9.6 Ethers') plus "
         "Figure 9.14, the isopropyl pentyl ether bar spectrum with a squiggle-marked inset "
         "(71/115/73/43, no arrows). It forward-references Equation 9.37, which is drawn on the "
         "following page. No numbered equation of its own. Read in full.",
}


def eqkey(e: str):
    m = re.match(r"(\d+)\.(\d+)", e or "")
    return (int(m.group(1)), int(re.sub(r"\D", "", m.group(2)) or 0)) if m else (99, 99)


def load_records():
    out = []
    for f in sorted(glob.glob(str(RECORDS / "*.json"))):
        r = json.load(open(f))
        eq = page = fig = mod_note = None
        contra = False
        for e in r["evidence"]:
            loc = e["locator"]
            eq = eq or loc.get("equation")
            page = page or loc.get("page")
            fig = fig or loc.get("figure")
            if e["source_id"] == "mod_rules":
                mod_note = e.get("curator_note") or ""
            if e["support_type"] == "contradicted":
                contra = True
        out.append(
            {
                "id": r["mechanism_id"],
                "eq": eq,
                "page": page,
                "figure": fig,
                "step_class": r["steps"][0]["step_class"],
                "contradicted": contra,
                "mod_note": mod_note or "",
                "mismatch": bool(mod_note and MISMATCH_RE.search(mod_note)),
                "file": Path(f).name,
            }
        )
    return out


def main() -> None:
    recs = load_records()
    idx = json.load(open(RULE_INDEX))
    chapters = sorted({eqkey(r["eq"])[0] for r in recs if r["eq"]})

    lines = ["# IMS mechanism-record coverage report", ""]
    lines.append(f"Total records: **{len(recs)}**  |  "
                 f"flagging a MØD rule mismatch: **{sum(r['mismatch'] for r in recs)}**  |  "
                 f"marked contradicted/disfavored: **{sum(r['contradicted'] for r in recs)}**")
    lines.append("")
    lines.append("Gate status is authoritative from `validate_records.py`, not this script; "
                 "run it separately to confirm 0 failures.")
    lines.append("")

    for ch in chapters:
        ch_recs = [r for r in recs if r["eq"] and eqkey(r["eq"])[0] == ch]
        covered = {r["eq"] for r in ch_recs}
        rule_eqs = sorted(
            {e for e in idx["by_equation"] if e.startswith(f"{ch}.")}, key=eqkey
        )
        missing = [e for e in rule_eqs if e not in covered]
        beyond = sorted({r["eq"] for r in ch_recs if r["eq"] not in rule_eqs}, key=eqkey)

        lines += [f"## Chapter {ch}", ""]
        lines.append(f"- rule_index equations: {len(rule_eqs)}; "
                     f"covered by a record: {len(rule_eqs) - len(missing)}")
        lines.append(f"- **still missing** (in rule_index, no record): "
                     f"{', '.join(missing) or 'none'}")
        lines.append(f"- covered beyond rule_index (no MØD rule exists): "
                     f"{', '.join(beyond) or 'none'}")
        lines += ["", "| eq | record | pg | step_class | flags |", "|---|---|---|---|---|"]
        for r in sorted(ch_recs, key=lambda x: (eqkey(x["eq"]), x["id"])):
            flags = " ".join(
                t for t, on in [("contradicted", r["contradicted"]),
                                ("rule-mismatch", r["mismatch"])] if on
            )
            lines.append(f"| {r['eq']} | {r['id']} | {r['page']} | "
                         f"{r['step_class']} | {flags} |")
        lines.append("")

    # figure-based / no-equation records
    figs = [r for r in recs if not r["eq"]]
    if figs:
        lines += ["## Records without an equation id (figure-based)", ""]
        for r in figs:
            lines.append(f"- {r['id']} (figure {r['figure']}, p{r['page']}, "
                         f"{r['file']}) — verify these transcribe a *drawn* scheme, "
                         f"not spectrum cleavage-marks")
        lines.append("")

    lines += ["## Verified non-mechanism equations (intentional sequence gaps)", "",
              "Numbered equations that carry no fragmentation mechanism at all — checked against the "
              "page scan. They are NOT extraction misses, so an equation-number gap here is expected.",
              ""]
    for eq, why in sorted(NON_MECHANISM_EQS.items(), key=lambda kv: eqkey(kv[0])):
        covered = " **(but a record exists — re-check!)**" if any(
            r["eq"] == eq for r in recs
        ) else ""
        lines.append(f"- **{eq}** — {why}{covered}")
    lines.append("")

    lines += ["### Verified non-mechanism PAGES (in range, nothing to extract)", ""]
    for pdf_idx, why in sorted(NON_MECHANISM_PAGES.items()):
        lines.append(f"- **PDF {pdf_idx}** — {why}")
    lines.append("")

    lines += ["## MØD rule-mismatch findings (audit byproduct)", "",
              "Records whose cross-link note flags the cited MØD rule as mis-encoded or "
              "non-matching vs the book. These are extraction-flagged; the alpha-cleavage "
              "geometry bugs (4.9/4.11/4.12) were additionally spot-verified against source "
              "(see memory `project_ims_chap4_rule_geometry_bugs`). A rule-corpus audit is "
              "the recommended follow-up.", ""]
    for r in sorted([r for r in recs if r["mismatch"]], key=lambda x: eqkey(x["eq"])):
        note = re.sub(r"\s+", " ", r["mod_note"]).strip()
        lines.append(f"- **{r['eq']}** ({r['id']}): {note[:260]}")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(recs)} records, "
          f"{sum(r['mismatch'] for r in recs)} mismatch-flagged)")


if __name__ == "__main__":
    main()
