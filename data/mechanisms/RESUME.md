# IMS mechanism extraction — resume point

## State (updated 2026-07-30)

> ## CH.9 BATCH 2 — eqs 9.13–9.24 (requested: "the next 10 equations")
>
> **CORPUS NOW: 316 records, 316/316 gate-clean** (58 Ch.4 + 228 Ch.8 + **30 Ch.9**). 12/12 agents,
> 0 errors. All 16 new verdicts `faithful=true`. Nothing pre-existing was touched (300-record backup
> diffed: additions only). All 16 render clean through `render_latex.py`.
>
> **Pages (printed = PDF − 11 still holds):** 9.13/9.14/9.15 → PDF 250, 9.16/9.17 → 251, 9.18 → 252,
> 9.19/9.20 → 254, 9.21 → 255, 9.22/9.23/9.24 → 256. **No equation-number gaps in 9.13–9.24**, so
> unlike batch 1 there is nothing to add to `NON_MECHANISM_EQS`. Records exceed the requested ten
> because the branching cascades split: 9.18 → a/b/c, 9.19 → a/b, 9.20 → a/b, and 9.23/9.24 came free
> on the 9.22 page.
>
> **NEW `NON_MECHANISM_PAGES`: PDF 249 (printed 238) and PDF 253 (printed 242)** — both running prose
> only, **read in full** (not a gutter check). Each forward-references equations drawn on later pages,
> which is exactly how a dropped page would look if left unrecorded.
>
> **Reconciliation — every verifier claim re-checked at source before editing; 13 notes patched.**
> This batch the verifiers were RIGHT on every disputed point (batch 1 ran 3-of-7 wrong), but two of
> their claims still needed narrowing, and I only edited what I re-measured myself:
> - **9.13 — third fabricated measurement in three batches.** The note said the two barbs are "~70 px
>   apart" *on the 1760x2560 native scan*. Re-measured: tips at ~(297,441)/(312,449) = **~18 px**; 70 px
>   is the figure on a **4× upscale**. Same failure mode as IMS8-EQ8.97 and 9.12's "7 hits". **Assume
>   any quoted pixel number is on an unstated scale until re-measured.**
> - **9.22 — arrowhead misdescribed.** The note claimed the rH head has "two converging strokes" unlike
>   the 9.23/9.24 fishhooks. On the native scan it is arc body + **one** barb, i.e. the same fishhook;
>   the genuine two-barbed heads are the `i` arrows (9.23's at ~(925,1170) has two barbs diverging from
>   the tip). Encoding was already right; only the prose was wrong.
> - **9.19a/b — "dashed fishhook pair" → ONE dashed arc.** The molecular ion carries **three** arcs:
>   two solid (the O-radical hook, which is SHARED by both branches, plus the 9.19 C1–C2 hook) and one
>   dashed (the 9.20 C1–C6 channel). Both records patched.
> - **9.21 — the note's central negative claim was FALSE and is now a verified positive.** It said no
>   rule can produce the drawn distonic m/z 44 ion. `hTransition_unsaturated_alpha`
>   (`IMS_bookCover.py:50`, `[C.]1[C]2[C]3[C]4{=}[_A+]5[H]6 >> [C]1{=}[C]2 . [C.]3[C]4{=}[_A+]5[H]6`)
>   does exactly that with _A=O. **RDKit-tested, not asserted**: embeds exactly once as
>   (C.1,C2,C3,C4,A5) = (map4,map5,map6,map1,map8), breaks the same map5–map6 bond, forms the same
>   map4=map5 alkene, and its ion half is atom-for-atom the drawn `[1H:10][O+:8]=[CH:1][CH2:6]`. It
>   conserves (guardrail keeps it) and is LIVE: `IMS_bookCover.py:457` → `rearrangements` →
>   `IMS_cover_fragmentation` (:493) → `fragmentation` (`__init__.py:45`). Only the granularity differs.
> - **9.21 — three more note defects, all confirmed in source:** "IMS_8_7_1 is the only indexed rule
>   that matches" (`hTransition_unsaturated`, :40, does the same γ-H transfer); "the only
>   reverse-direction rule is IMS_8_2_bidirectional_up" (IMS_8_7_4, IMS_8_7_5, IMS_8_2_rH_2_0 also run
>   O⁺→C — but each is excluded on skeleton grounds, so the *conclusion* that step 2 has no rule
>   survives); and a **self-contradiction inside one note** — point (3) called IMS_4_9 the only rule
>   matching the molecular ion while point (5) reported IMS_4_37_rH/IMS_4_38_rH matching it too.
> - **9.22 — IMS_4_11 misdescribed:** the note said it "retains BOTH the charge and the odd electron"
>   on the acylium. Its RHS `[C.]1 . [C]2[C]3{#}[_A+]4` puts the unpaired electron on the **departing**
>   fragment. Mismatch verdict unaffected.
> - **Verifier claim NARROWED (not accepted as stated):** it said p244's prose "states no such thing"
>   about m/z 44 being fed by both aldehydes. The page says *"this and the analogously formed
>   2-methylhexanal will also contribute to peaks such as m/z 44 and 58"* — it names both aldehydes and
>   both masses **without partitioning**, so the note over-read it but the verifier's flat denial was
>   also wrong. Now quoted verbatim.
> - **9.14 FLAGGED FOR EXPERT REVIEW (not silently changed):** the only species in the batch where an
>   **explicitly drawn** localization was replaced. The book prints the m/z 119 ion as `(CH3)2C(+)–`
>   on an aromatic circle; the record stores the para-quinoid partner because that is what its arrows
>   produce and it keeps the page's two records in one frame. Defensible, but in a bond-order-sensitive
>   corpus the stored graph is not the printed one. Re-encode as `[CH3][C+]([CH3])c1ccccc1` if a
>   reviewer prefers drawing-fidelity.
> - **9.15 is a near-duplicate of the committed IMS4-EQ4.36** (book prints the scheme twice; identical
>   SMILES/maps/ms_context). The two DISAGREE about m/z 92.0621 — 4.36 (p73) has detected=true/0.6,
>   9.15 (p239) detected=false/inferred — and **both are right for their own page**. Cross-reference
>   note added to 9.15 so nobody "resolves" it by overwriting one.
> - **OPEN, for the FIG4.4 decision:** the Figure 9.7 inset (o-methylphenol, squiggle marks 90/107,
>   zero arrows) was skipped per the eq-9.5 precedent, but `IMS4-FIG4.4a/b` were ENCODED from an
>   identical arrow-free squiggle inset (p62, marks 72/58). The corpus is inconsistent on this class —
>   one more reason the FIG4.4 scope call matters.
>
> **NEXT: eqs 9.25+ start at PDF 257** (dumped through 262; 253–256 were dumped this batch).

> ## CHAPTER 9 STARTED (scope extension, requested 2026-07-30)
>
> Ch.9 was "explicitly out of scope" in the original plan; the user extended it and asked for the
> **first 10 equations**. Ch.9 has NO MØD rules to cross-link (`rule_index` covers Ch.4/Ch.8/cover
> only, 57 equation keys, none starting with "9"), so Ch.9 records carry no rule links by
> construction, not by oversight.
>
> **CORPUS NOW: 298 records, 298/298 gate-clean** (58 Ch.4 + 228 Ch.8 + **12 Ch.9**).
> Ch.9 batch 1 landed `IMS9-EQ` **9.1a, 9.1b, 9.2, 9.3, 9.4a, 9.4b, 9.7, 9.8, 9.9, 9.10** plus
> **9.11, 9.12** (page-granularity bonus: they share PDF 248 with 9.10). All 12 verdicted
> `faithful=true`. Nothing pre-existing was touched (286-record backup diffed byte-for-byte).
>
> **Page calibration (printed = PDF - 11 in this region):** 9.1/9.2 -> PDF 237, 9.3/9.4 -> 241,
> 9.5/9.6 -> 242, 9.7 -> 244, 9.8/9.9 -> 246, 9.10/9.11/9.12 -> 248. `page_map.json` "ch9" lists
> exactly those pages. Pages 238/239/240/243/245/247 are deliberately NOT registered and NOT claimed
> non-mechanism: only the right-margin gutter was inspected, which shows no equation numbers but is
> not enough to rule out schemes. (PDF 245 = printed p234 = Figure 9.3, 5-alpha-pregnane spectrum.)
>
> **eq 9.5 = VERIFIED NON-MECHANISM** (added to `NON_MECHANISM_EQS`): printed p231 draws it as two
> terpenoid polyenes carrying SQUIGGLE cleavage marks with neutral-loss labels (M-83)/(M-57) and a
> generic (C5H8)4H chain -- a fragmentation depicted with ZERO curved arrows. Encoding it would mean
> inventing the electron flow. Read and confirmed directly, not delegated.
>
> **eq 9.6 DONE, but HAND-CURATED — the corpus's only unverified records.** Its page lost the draft
> agent twice (API server error, then the monthly spend limit), so `IMS9-EQ9.6a`/`9.6b` were authored
> directly from the native scan (pypdf `page.images[0]`, 1760x2560, structures cropped at 4x). They
> carry **no independent adversarial verify pass**, unlike all 298 others; `extraction_method` is
> **`manual_from_scan`** (every other record says `vision_multiagent`), so this is machine-detectable —
> `grep -l manual_from_scan records/*.json`. **Re-verify these two when agents are available.**
> - **Split into a/b because the page draws TWO channels.** The printed arrow reads literally
>   "alpha *or* i", and structure 3 carries THREE arcs belonging to different routes: two single-barbed
>   fishhooks (dot on C-gamma -> C-gamma-C-beta bond; one electron of C-beta-C-alpha -> that same
>   forming pi) = the **alpha** channel, plus one **full-headed** arrow (the C-beta-C-alpha pair ->
>   the C-alpha-C2 bond) = the **inductive** channel. Same treatment as eq 9.1 -> 9.1a/9.1b.
> - alpha (9.6a) keeps the charge where it already was: ion = the drawn `.CH2-C+(CH3)R"`, neutral =
>   the alkene. i (9.6b) MIGRATES the charge: ion = the drawn `R-CH=CH-R'` (+.), neutral = isobutene.
>   Opposite partitions, which is exactly why the book prints both.
> - Structure 2's ionized alkene is drawn with the pi as a SINGLE line, `+` on the substituted sp2
>   carbon and the dot on the terminal CH2 — encoded in that localized form (convention B). The `-e-`
>   arrow is folded into the precursor's charge/radical fields, as sibling 9.1a does for eq 9.1.
> - 9.6b's ion is printed `R-CH=CH-R'` with `+.` = McLafferty's one-electron-pi shorthand, which is
>   not valence-complete read literally; encoded as the localized distonic form per the corpus's own
>   **eq 9.3 precedent**, and disclosed.
> - Instantiation R = C2H5, R' = CH3, R" = CH3 -> 2,4-dimethylhept-1-ene, C9H18, M+. 126.1403. R" =
>   CH3 is the minimum the caption's "R" > H" allows. R is deliberately ONE carbon above minimal:
>   with R = CH3 both channels would yield mass-degenerate C4H8+. isomers, which reads like a
>   copy-paste error. Self-audit (RDKit, independent of the authoring script): all three stated masses
>   are EXACT (126.1403 / 56.0621 / 70.0777) and the mass balance closes to 126.1403 in both records.
>   Renders and compiles: 10 arrow tails, 0 adrift, median 0.70 pt.
>
> **CORPUS NOW 300 records, 300/300 gate-clean.** Of the requested first ten Ch.9 equations, 9.1-9.4
> and 9.6-9.10 are encoded and 9.5 is a documented non-mechanism, so the batch is complete.
>
> **Batch-1 corrections, each verified at source before editing** (all 12 records were faithful; every
> defect was note-level):
> - **9.1b** cited page 226 for an "[M-CH4]" discussion. I read p226 in full: it names only m/z 99,
>   57 and CH3+ and never mentions methane loss -- that argument is on the facing p227. Withdrawn. Its
>   weaker valence argument was also replaced: 2,2,3,3-tetramethylbutane has NO CH2 group at all, so
>   the printed skeleton cannot map onto it either way.
> - **9.1b** justified "no rule covers the rH branch" by claiming `§Y` restricts `_A` to a heteroatom,
>   then scoped its scan to rules "whose left side contains only C/H" -- which excludes the very
>   `_A` rules at issue. FALSE, checked in source: `element_sets.py` has `ALL_ATOMS = HETERO_ATOMS +
>   ["H","C"]` and `constrain.py` splices a `constrainLabelAny` over occurring atoms, so `_A` expands
>   to CARBON. The coverage question is now marked OPEN rather than answered.
> - **9.2** imported 9.1's "the '+.' sits on the C-C BOND (2c-1e)" claim. Eq 9.2 actually prints
>   `R-CH2CR'2-R" (+.)` with the charge as a TRAILING SUPERSCRIPT (verified) -- unlocalised, which
>   makes the field-carried encoding *more* faithful here, for a different reason than stated.
> - **9.3 / 9.4a / 9.4b** carried `support_type: computationally_supported` while their own notes
>   report 0 substructure matches for every cited rule -> `curator_inferred` (matching 9.1a/9.2).
> - **9.12** claimed "RDKit-VERIFIED, 7 hits" for the IMS_4_9 pattern. My own run: **4 matches**, with
>   uniquify both True and False. Same fabricated-measurement failure mode as IMS8-EQ8.97.
> - **9.8** cited "288 M+. and 273" as if printed on p235; verified they belong to **Figure 9.3 on
>   printed p234 (PDF 245)**, whose C17-ethyl inset does support the 5-alpha-pregnane instantiation.
> - **9.9** "four bonds away from C13+" -> three along the chain; "cis-fused" -> no stereo is drawn;
>   "nothing in the rule set encodes a ring expansion" narrowed (benzylAllyl_mz91_91 is one, but
>   aromatic-only, so the conclusion holds).
> - **9.12 JUDGEMENT CALL, flagged for review:** `peak_231` keeps `relative_intensity = 1.0` although
>   no percentage is printed -- the prose says the CH3 loss "gives the base peak", which is 100% by
>   definition. This deviates from convention F; `status` stays `proposed` (never `observed`) so the
>   provenance remains machine-readable.

## State (updated 2026-07-28)

> # ✅ EXTRACTION COMPLETE — Ch.4 + Ch.8 + inside cover, every page in scope.
>
> **CURRENT TOTALS: 286 records, 286/286 gate-clean** (58 Ch.4 + 228 Ch.8, eqs **8.1–8.124** + Table 8.2
> rows a–q). **No pages remain**: the dumped Ch.8 range PDF 147–236 is fully processed, and every page
> that yielded nothing is documented as a verified non-mechanism page (below).
>
> **Every gap in the Ch.8 equation-number sequence is now explained.** 8.23 / 8.27 / 8.28 / 8.32 were
> already documented; the sweep after the final batch surfaced one more, **8.96** (printed p206, PDF
> 218): four STATIC ion structures (a)–(d) naming the ion types the surrounding prose argues about, no
> reaction arrow and no arcs. It was correctly not encoded in batch 11 but never written down, so it read
> as an unexplained miss. Added to `NON_MECHANISM_EQS`. **New in `coverage_report.py`:
> `NON_MECHANISM_PAGES`** — an in-range page with zero records is otherwise indistinguishable from a page
> the pipeline silently dropped, which is exactly the PDF-180 bug.
>
> **Batch 14 (PDF 230–234 + 236, +13 records, eqs 8.113–8.124; 12/12 agents, 0 errors) — reconciled
> 2026-07-28.** All 13 verdicts `faithful=true`. Nothing pre-existing was touched (full 273-record
> backup diffed byte-for-byte). PDF 234 (printed p222: §8.12 references tail + Table 8.4, a neutral-loss
> lookup index with zero arcs/structures) and PDF 236 (printed p225: Chapter 9 opening, out of scope)
> correctly yielded 0 records.
> - **Three false rule descriptions, all confirmed against the rule source and corrected.** Each note's
>   negative CONCLUSION survived; only the justification was wrong. (a) **8.115a** called
>   `IMS_4_44`/`IMS_4_45` "the retro-ene/RDA-type rules" — they are a chloroalkane displacement pair
>   (`[Cl+.]`/`[Cl..]`) and an ester-oxonium pair; the set's real retro-DA rules are
>   `IMS_4_31_alpha1/alpha2`, `IMS_4_32_alpha/ind` and `dielsAdler_*`. Replaced with a stronger argument:
>   **zero occurrences of `Si` in any DFS in `src/data_generation/rules/`**, so a TMS ether cannot be
>   written in the rule corpus at all. (b) **8.119** claimed `IMS_8_12` has "the same left-hand side" as
>   `IMS_8_11`; its oxocarbenium carbon bears one H **plus a methyl**, not two H. (c) **8.121** called
>   `IMS_8_2_ind_2_7` the "same acylium motif" — its `[C]14[O+]15` bond is **unspecified (single)**, not
>   `{#}`, and it further needs a pre-existing `[C+]11` in a saturated chain.
> - **8.123 dashed-bond count corrected 6 → 5**, re-measured myself on the native scan at 6×–10×: two
>   H···O (left-ring H → `+•` phosphoryl O; bottom H → lower-right ester O) and three C···C. The **third**
>   H, on the top-right ring near native (345,845), has **no dashed line** — its transfer is marked by a
>   curved arrow alone. Chemistry unchanged (3 C–H broken, 3 O–H made → H₃PO₄); the missing dash is a
>   drawing economy. Same class of defect as the 8.102 dashed-bond miscount in batch 12.
> - **Undisclosed `70 eV EI` assumptions closed** on 8.118 / 8.121 / 8.122 / 8.123 — none of those pages
>   prints ionisation conditions. Value kept (it is the corpus house default) and now disclosed, matching
>   how 8.114 / 8.115a/b already handled it.
> - **8.115a**: the substrate is drawn **NEUTRAL** — no bracket, no `+•`; only the products carry it, so
>   the precursor's ionisation site is a curator localisation carried back from the product. Also added
>   the book's own prose claim, verified verbatim on the scan: *"the long-range rearrangement of Equation
>   8.115 proceeds through an ion-molecule complex and gives rise to a base peak of the spectrum
>   (Longevialle 1987)"* — the complex is asserted only in prose with no structure drawn, so it stays
>   unencoded, but the attribution is now recorded.
> - **8.118 — another book self-contradiction, verified at 9×.** The prose introducing the block calls
>   Equations 8.117–8.120 examples of **"EE⁺ ions"**, yet 8.118's own bracket closes with **`+•`** (an
>   odd-electron molecular ion). The record follows the drawing; disclosed in the note.
> - Verifier claim **checked and narrowed**: 8.113's provenance said printed p216 is "the recto one leaf
>   earlier". p216 is a **verso**, two printed pages back (printed p217 in between is the full-page
>   Figure 8.9) — but it *is* one leaf earlier, so the verifier's "two leaves" was also off. Reworded to
>   state the geometry exactly.
>
> **Batch 13 (PDF 180, +2 records = `IMS8-EQT8.2p`/`IMS8-EQT8.2q`; 2/2 agents) — reconciled 2026-07-28.**
> This is the page the byte-size blank heuristic had skipped (see COVERAGE BUG below); it is now
> extracted, so that gap is closed.
> - **The ID-collision guard worked.** Suffix letters restart per page, and rows a–o were already
>   committed from PDF 178/179, so a fresh agent could have overwritten them. The new guard block in
>   `extract_pages.mjs` `SELF_CHECK` (check `records/<mechanism_id>.json` before promoting; continue the
>   suffix series from the next free letter) made the agent land on **p/q**. Verified after the run:
>   all 15 of `IMS8-EQT8.2a..o` are byte-identical to the pre-run backup.
> - **8.2q — the page is INTERNALLY INCONSISTENT, and that is now disclosed rather than resolved
>   silently.** Re-measured independently on the native scan (`page.images[0]`, 1400x2016, rotated
>   upright): the reactant's alkyl vertex (1054,809) has three bonds — 32 px and 34 px lines ending at
>   the two `H` labels, and a 47 px C–C down to (1055,856), which bonds to the ester O+ — so the printed
>   reactant is a **two-carbon** ester with **both** migrating H's on the terminal carbon (C–C bonds here
>   are 44–48 px, bonds to labels 32–35 px). The printed neutral, however, is unambiguously the
>   **three-carbon allyl radical** (vertical C=C plus a separate bond to a radical dot), which with the
>   m/z 61 ion needs a 102 precursor and two H's from *different* carbons. The record keeps n-propyl
>   acetate — it matches the drawn products, the mass balance, and the book's own full treatment in
>   **eq 4.46** (`IMS4-EQ4.46`, p82) — and the note now states the discrepancy, the measurements, and
>   which half was followed. Corroboration that the omission is the BOOK's: the German inside-cover rule
>   `h2Transiton_1`, whose comment cites Gl. 4.46, transcribes exactly the printed two-carbon,
>   both-H-on-one-carbon geometry.
> - **NEW MØD BUG CONFIRMED — `IMS_4_14` is a chain TRANSPOSITION.** Read from source: left
>   `[C]1([C]2[C]3)([C]4[C]5){=}[O+.]` bonds C1–C4; right `[C.]2[C]3.[C]4[C]5[C]1{#}[O+]` bonds C5–C1.
>   Besides the intended α cleavage it therefore breaks C1–C4 and forms C1–C5, so on cyclohexanone M+•
>   it yields the **branched** acylium CH₃–CH(C≡O⁺)–CH₂CH₂CH₂• instead of the linear ring-opened
>   distonic acylium the page draws. Conservation is untouched, so the guardrail cannot see it. Fix would
>   be `[C]5[C]4[C]1{#}[O+]`. The 8.2p note's "VERIFIED cross-link … describes exactly this bond change"
>   was downgraded accordingly (confidence 0.5 → 0.4), and its "1 RDKit match" softened (the pattern is
>   symmetric in its two ring branches → 2 symmetry-equivalent embeddings; `uniquify` artefact).
> - Verifier claim **checked and kept**: 8.2p is faithful (6 arcs). Verifier claim **checked and
>   narrowed**: `IMS_4_46_rH_1` does not "MATCH the first half" — its left graph needs charge *and*
>   radical on the carbonyl O, while the page draws them separated (convention B), so it cannot embed;
>   note rewritten as same-reaction-but-does-not-embed.
>
> **Batch 12 (PDF 221–228, +16 records, eqs 8.101–8.112; 16/16 agents, 0 errors) — reconciled 2026-07-28.**
> All verdicts faithful. Pages 221/224/226 correctly yielded 0 records. Fixes applied to **8.102**, both
> confirmed at native scan resolution: (a) the bracketed three-membered ring has only TWO dashed bonds
> (C4···C2 and C3···C2); the C4–C3 bond is SOLID — the note had implied all three were dashed; (b) the
> book draws the dihydroxycarbene fragment as a plain `C` with two OH bonds, NO charge and NO dot, with
> the `+•` printed OUTSIDE the bracket — so the record's `[C+]` is a disclosed curator localization, not
> the drawing; (c) `70 eV EI` is a chapter default for this equation, not printed (the nearby "70 eV"
> belongs to the 3-methylbutanal sentence carried over from p210).
>
> KNOWN CORPUS PROPERTY (not a defect): **`species_id` is record-scoped, not a global key.** 98 ids are
> reused across records with different `mapped_smiles`, almost always the same species under different
> per-record atom numbering (maps are record-local). Do not chain species across records by id.
>
> OPEN, disclosed by verify and not encoded: the bottom-RIGHT leg of the eq-8.101 brace is a drawn
> transformation with no record. Its start ion and both products are label-identical to IMS8-EQ8.101b's,
> so encoding it would mirror IMS8-EQ8.101d; the drafter disclosed the omission.
>
> **COVERAGE BUG FOUND + FIXED 2026-07-28 — a real mechanism page was silently skipped.**
> `dump_pages.py` flagged empty leaves by FILE SIZE (`bytes < 60_000`). That is a bad proxy: a rotated,
> sparsely drawn scheme page compresses smaller than a dense text page. Three pages were excluded from
> `page_map.json` on that basis, and one of them is **real mechanism content**:
> - **PDF 180 (book p168) = "Table 8.2 (continued) — Three bonds cleaved"**, with TWO fully drawn
>   fishhook schemes (an OE+• ααα cyclohexanone cascade → enone acylium + •C3H7, and an OE+• αii
>   double-rH giving allyl radical + protonated acid). 58,649 bytes — just under the threshold.
>   **EXTRACTED 2026-07-28 as `IMS8-EQT8.2p`/`IMS8-EQT8.2q` (batch 13 above) — gap closed.** It continues
>   the Table 8.2 set already captured as `IMS8-EQT8.2a..o` from PDF 178/179.
> - PDF 229 (book p217) = Figure 8.9, a rotated full-page bar spectrum of octadecanoic acid — verified
>   NON-mechanism, nothing to extract.
> - PDF 235 (book p223) = Table 8.4 (continued), a listing of eliminated neutrals — verified
>   NON-mechanism, nothing to extract.
>
> Fix: `dump_pages.py` now measures ACTUAL INK (`_ink_fraction`, dark-pixel fraction, blank below
> `BLANK_INK_FRACTION = 0.002`) instead of byte size, and records `ink_fraction` in the manifest.
> Re-measured: p180 = 0.0212, p229 = 0.0120, p235 = 0.0170 ink — all an order of magnitude above the
> blank floor, all now correctly kept. `page_map.json` ch8 is now the contiguous run 147–236.
>
> **Batch 11 (PDF 218–220, +4 records, eqs 8.97–8.100; 6/6 agents) — reconciled 2026-07-28:**
> - **NEW FAILURE MODE — a FABRICATED MEASUREMENT in a curator note.** IMS8-EQ8.97's note claimed it had
>   measured arrowhead glyphs on the native scan ("head bulge is 6 px against a 3 px stroke", matching
>   "8.94 hooks (6 px against 3 px)", unlike "Equation 8.35, 9 px against a 3 px stroke") and used those
>   numbers to argue both arcs were fishhooks. **The numbers are not reproducible.** An independent scipy
>   distance-transform sweep over the whole eq-8.97 band of the native scan gives max stroke **5.0 px**
>   with the ordinary baseline at **~4.7 px** — no 6-vs-3 discrimination on any arc head, and the claimed
>   3 px baseline is wrong too. Note rewritten with an explicit retraction. **Lesson: treat precise
>   pixel/measurement claims inside notes as checkable assertions, and re-run them.**
> - The correct reading of 8.97 is **two 2-electron arrows**, settled by chemistry not pixels: the
>   precursor is a CLOSED-SHELL EE+ ion (radical_electrons 0), so there is no unpaired electron for a
>   fishhook to come from. Corroborated by the book's own practice — Eqs 8.94/8.95 on the facing page
>   draw the SAME four-membered array with FOUR arcs when four hooks are meant; 8.97 draws two. The
>   "page is under-drawn / needs FOUR hooks" claim is withdrawn. **The electron_moves were already
>   correct** (2 x 1e == one 2-electron arrow); only the narrative was wrong.
> - **NEW MØD BUG CONFIRMED — `IMS_4_20` is DEAD FOR EVERY SUBSTRATE.** Its GML context has node 2 = H
>   with TWO edges (`_A+ - H` and `H - H`): the DFS `[_A+]2[H]3([H]4)` was written with one parenthesised
>   branch so it CHAINS the hydrogens instead of branching them. It demands a hydrogen of degree 2, which
>   no molecule graph can supply. Fix: `[_A+]2([H]3)([H]4)`. (The _A-unification concern is real but only
>   a second, downstream blocker; and §R1Y2 is a build-time rightPredicate that a bare `b.apply` test
>   never evaluates.) 8.98's note corrected accordingly.
>
> **Batch 10 (PDF 211–217, +21 records, eqs 8.84–8.95; 14/14 agents, 0 errors) — reconciled 2026-07-28:**
> - **8.88a/8.88b were genuinely UNFAITHFUL and are now RE-ENCODED.** They collapsed a drawn 2-fishhook
>   H-rearrangement into ONE net heavy-atom electron move that transcribed neither drawn arc, justified by
>   the claim that "the migrating hydrogen cannot carry an atom map (RDKit folds mapped explicit [H:n]
>   into implicit valence)". That is FALSE as stated — it holds for bare `[H:n]`, but the corpus's
>   standard workaround is the ISOTOPE-TAGGED `[1H:n]`, used in **80 records**, and `IMS8-EQ8.19` encodes
>   this exact reaction type with the full three-hook flow. Both now carry `[1H:10]` and the complete
>   balanced 3-move flow, matching 8.19. Gate-clean.
> - **8.89 note corrections (verified at native scan resolution):** the page draws **2 disjoint fishhooks**,
>   not 1 (so move <2> is DRAWN, not implicit); the breaking C2–H bond is a **solid** line, not
>   "part-dashed" (only the central C···CH(CH3)2 bond is genuinely dashed); and `sigma_lowIE`
>   (`[_A+.]1[I]2 >> [_A.]1 . [I+]2`) **requires an explicit IODINE** so it cannot match an alkane C–C
>   bond — now cited as family resemblance only, not a match.
> - New MØD audit findings recorded in rule_mismatches: `IMS_8_14_1` atom-imbalance, and
>   `IMS_8_11`/`IMS_8_13`/`IMS_8_14_2` all repeat the missing-C=C-in-the-ethylene-neutral defect.
> **`pending_review/` is EMPTY — nothing quarantined.** 8.59 was re-extracted and restored 2026-07-28:
> the book labels its arrow "i, α" (inductive AND alpha), and at native scan resolution the LEFT arc
> (C1–C3, the α CH2 beside the gem-dimethyl carbon) carries a FULL two-barbed head = the 2-electron
> inductive move. The quarantined version called all 4 arcs fishhooks and put the 2-electron move on
> C1–C7, swapping the charge/radical termini. Fixed; see `pending_review/README.md`.
> The per-batch history below is kept in chronological order — earlier counts in it are historical,
> not current.

**Chapter 4: COMPLETE (100%).** 58 records in `data/mechanisms/records/`, **all pass** the
deterministic gate (schema + atom/charge/electron conservation + electron-move↔bond-order arrows).
- **43 of 43** rule_index equations covered; plus 4.16 (disfavored, no MØD rule) and Figure 4.4.
- eq 4.3 (propane radical cation) is encoded as 4.3a/4.3b using the saturated-alkane convention:
  neutral-skeleton SMILES + charge/radical in fields + an `external` electron location for the EI
  ionization hole (same as 4.5/4.8). The gate passes with a soft "external" note.
- Coverage detail + rule-mismatch findings: `data/mechanisms/coverage_report.md`
  (regenerate with `python src/mechanisms/coverage_report.py`).

**Chapter 8: IN PROGRESS — 61 records (eqs 8.1–8.25, all through book p~152), all gate-clean.**
Total corpus now **119 records, 119/119 gate-clean** (58 Ch.4 + 61 Ch.8). Coverage: Ch.8 rule_index =
**14/14 eqs covered** (8.7/8.8/8.9 filled in batch 3); plus beyond-rule-index 8.15–8.22, 8.24, 8.25.
- Batch 3 (pages 156,157,158,161,164,166,168) completed FULLY (14/14 agents, spend window held) and
  ALL verify verdicts were faithful — the context-aware ms_context fix worked. +22 records.
- eq **8.9** note corrected: substrate is ALPHA,BETA-unsaturated (conjugated enone, not γ,δ), and the
  drawn rH is **5** fishhooks (O•→H + the C–H bond hook + 3 framework π-shifts), not 4.
- AUDIT (verified in-container): **IMS_8_7_5 has a malformed bond token `[=}` (should be `{=}`)** at
  `[C]2[=}[C+.]3`. It does NOT crash — `mod.Rule.fromDFS` parses it and the module imports — but MOD
  SILENTLY absorbs the bad token into a product node label (`node[id 2 label "=}[C+."]`), so the intended
  C2=C3 double bond + C⁺• are LOST: the rule loads but its RHS is corrupt. Fix in source: `[=}`→`{=}`.
  (This REFUTES the drafter/verify guess that it was a parse-failure/dead rule.) Also IMS_8_7_4 and
  IMS_8_9_2_CH3/_OCH3 flagged as collapsed-net / radical-placement mismatches (recorded in rule_mismatches).
- eq **8.6** re-extracted FAITHFULLY as a single stepwise retro-DA (vinylcyclohexene+• → symmetric
  ring-opened distonic intermediate → butadiene+• m/z 54 + neutral butadiene); the note discloses that
  the book's products (a)/(b) are s-cis/s-trans forms that coincide for the symmetric parent. The old
  unfaithful 8.6a/b in `pending_review/` are DELETED (superseded).
- **MS-CONTEXT LESSON (important):** Ch.8 "Detailed Mechanisms" mixes EI / CAD / MI(metastable) / CI.
  The workflow used to hardcode EI/70eV/[M]+•; that mislabeled CAD abundances (8.10/8.11 "CAD 9%/58%")
  and MI decompositions (8.14) as EI, and put [M]+• on even-electron fragment/oxonium precursors. FIXED
  the promoted records (activation_method CAD/MI, adduct null, electron_energy_ev null, detected=false
  where nothing printed) AND fixed the root cause in `extract_pages.mjs` (context-aware ms_context guide
  + new convention (G)). Non-covalent proton-bound complexes the book draws (8.14/8.15) are documented
  in the step evidence note, not encoded as mapped species (partial bonds aren't RDKit-representable).
  Curator notes attach to `EvidenceLink.curator_note` (target_type step/mechanism) — ElementaryStep has
  NO curator_note field.

**Resume point:** pages through PDF 210 DONE (**229 records**, 229/229 gate-clean).
STILL to extract: PDF **211–236** (skip dropped blanks 229, 235). Batch 9 (PDF 204–210) added eqs
8.74–8.83 (+22 records), 14/14 agents, 0 errors.

**Batch-9 reconcile (2026-07-26):** verify marked 8.81a/8.81b BAD on measurement status — **REFUTED,
no data change.** p197 prints only the symbolic label "(M − 76)+•" (no numeric m/z, no %), but the prose
reports the ions as observed peaks ("yielding (M − CH3OH)+• and (M − 76)+• peaks ... very useful for
identifying substitution at C-6"), and BOTH records already say verbatim that no number is printed, that
`detected=true` "rests on that sentence only", and that the m/z is curator-computed, with
`relative_intensity` omitted. Same precedent as 8.60. **That is the THIRD measurement complaint from a
verifier that did not hold** (8.60, 8.81a, 8.81b) — when a verifier calls a measurement unsupported,
check the running prose, not just the scheme. Two small real fixes applied: (a) 8.81b's precursor is the
SAME m/z-174 ion that 8.81a marks detected=true, so it is now detected=true in both (they previously
disagreed); (b) 8.78's rule-rejection note called `[_A+]4` a "heteroatom" when `_A` is an element
wildcard — reworded (the rejection itself is sound: the rule needs the donor's neighbour to bear the
charged atom DIRECTLY, but in 8.78 that neighbour is the ester carbon with the charge one bond further
out on its oxygen).

**TWO OPEN ITEMS FROM BATCH 8 (stopped early — monthly token cap at ~80%):**
1. ~~p203 records unverified~~ **RESOLVED 2026-07-26 — verified by hand (no agents), all 6 FAITHFUL.**
   `IMS8-EQ8.70a/b, 8.71a/b, 8.72, 8.73` (book p191, §8.10 Hydrogen rearrangements). Independent read of
   the page confirms: 8.70/8.71 draw 2 fishhooks for the H-transfer step and 0 for the retention/migration
   branch (labelled straight arrows only); 8.72 draws 0 curved arcs (explicit H letters + wavy cleavage
   mark + "r 2H"); 8.73 draws 2 arrows that are NOT fishhooks (plain straight atom-transfer arrows) —
   every note states exactly this. Charge-retention vs charge-migration correctly assigned in both 8.70
   and 8.71. p191 prints no m/z and no %, and all six correctly use status "inferred"/detected=false/no
   relative_intensity. Both structural deviations are explicitly disclosed: 8.70b/8.71b encode ONE
   localized resonance form because an intact-C=C or saturated-ring radical cation has no valid localized
   mapped SMILES. NOTE: a suspicion that 8.71's butan-1-ol instantiation was wrong (substrate looking
   cyclic) was REFUTED — the drawn curve is the TS array, the ring FORMS in the product, and the record
   cites the p193 text ("five- or six-membered-ring formation ... is favored") as support.
2. ~~Note-level defects~~ **RESOLVED 2026-07-26 — each claim re-checked against source before acting;
   2 of 4 were verifier errors.** Corpus stayed 207/207 gate-clean.
   - **8.66 — BOTH claims CONFIRMED, fixed.** (a) The note said `hTransition_saturated_1/_2` "move the H
     onto the heteroatom, not onto a carbon radical terminus". Verified against IMS_bookCover.py: true of
     `_1` (`[H]1[C]2[C]3[C]4[C]5[_A+.]6`), but **false of `_2`** (`[H]1[C]2[C]3([_A+]4)[C]5[C.]6 >>
     [C.]2[C]3([_A+]4)[C]5[C]6([H]1)`), which moves H onto a radical CARBON — its own source comment says
     so. Note rewritten to reject `_2` on the real grounds: it is a 1,4-shift with the onium BETWEEN donor
     and acceptor, while 8.66 is a 1,5-shift with the oxocarbenium outside that chain. (b) "1,4-H transfer
     from C2 to C6" → the encoded moves are `bond[3,8]->bond[7,8]` on chain C3-C4-C5-C6-C7, i.e. a
     **1,5-shift from C3 to C7**. Both corrected.
   - **8.60 — verifier REFUTED, no change.** It claimed `detected=true`/`relative_intensity=1.0` were
     unsupported because the scheme prints no m/z or %. True of the scheme, but the prose on p185 says the
     CH2=C(OH)CH3+• ion "is the most abundant" (with 10% C4H6+•) — and the record ALREADY states verbatim
     "NO m/z and NO percentage is printed for the drawn ion" and that the 1.0 "encodes that verbal
     statement ... and is NOT a printed number". The record was already fully honest. Its arc-count claim
     (5 ring arcs, top-arc mapping) is left UNCONFIRMED — not resolvable at scan resolution, and this same
     verifier was wrong about the measurement on this very record.
   - **8.65a / 8.65c — RESOLVED 2026-07-26 at full scan resolution; the verifier was RIGHT, both fixed.**
     Re-extracted PDF p199 from the PDF's embedded scan at native 1375x2016 (vs the 1600-capped dump),
     cropped the shared bottom structure and upscaled 2x. Tracing it from the acylium carbon: the skeleton
     runs C1 -> C2(radical dot) -> C3 -> C4 -> C5 -> C6 -> C7(bears R'), and the three explicit hydrogens
     bond to **C7 = UPPER H, C6 = MIDDLE H, C5 = LOWER H**. So the assignments were exactly mirror-imaged:
     8.65a's "5th carbon = uppermost H" should be **lowest**, and 8.65c's "7th carbon = lowest H" should be
     **uppermost** (which also reconciles it with its own phrase "the carbon that also carries R'"). Both
     notes corrected and the `[RECHECK]` caveats removed.
     TECHNIQUE WORTH REUSING for any future fine-detail dispute: `pypdf` `page.images[0]` gives the native
     scan (bigger than `dump_pages.py`'s 1600px cap); crop the region of interest with PIL and upscale.

   (original verify report, for reference:)
   - **8.65a / 8.65c** — mirror-image positional errors: the note misidentifies which of the three
     explicit hydrogens in the shared bracket the 5th/7th carbon corresponds to.
   - **8.66** — `ev_mech_mod` note contains a FALSE claim about `hTransition_saturated_1/_2` ("they
     move the H onto the heteroatom, not onto a carbon radical terminus" — true of _1, not of _2); and
     `ev_step_rh_to_enol_ion` calls it a "1,4-H transfer" when donor/acceptor are four bonds apart
     (a 1,5-shift w.r.t. the radical).
   - **8.60** — arc-to-move mapping wrong for the top arc; only FIVE ring arcs are actually drawn; and
     it sets `detected=true` / `relative_intensity=1.0` although the page prints no m/z or % for the
     drawn ion (should be `inferred` / detected=false — same class as the Table 8.2 fix).
   - **8.59** — judged NOT faithful (charge/radical sites swapped, arrow type misread) → moved to
     `pending_review/`, see that README.

Batch 7 added 8.42, 8.51–8.58 (pages 192/196 correctly yielded 0 records). Batch 6 added
8.43–8.50 (pages 186/189 correctly yielded 0 records — running prose with only inline generic R–Y
expressions). p184 draft died on a transient "Connection closed mid-response" API error, NOT the spend
cap — re-queued in batch 7.

**Equation-number gaps are EXPECTED and verified** (see the coverage report's "Verified non-mechanism
equations" section, driven by `NON_MECHANISM_EQS` in `coverage_report.py`): 8.23 (stereoelectronic
conformer drawings), 8.27/8.28 (static H-bonded MH+ structures), 8.32 (IE value table). None of these
draw a reaction, so none is encodable — they are not extraction misses.

Batch 5 added 8.36–8.41 + Table 8.2
(15 generic fragmentation-type rows, records `IMS8-EQT8.2a..o`, from p178/179). Batch-5 fixes: Table 8.2
rows a–j `detected`→false (schematic type-table, nothing printed); 8.36 note (book under-draws product
as a mono-ene → record supplies the mass-conserving 1,3-diene, now disclosed); EQT8.2d IMS_4_18 cross-link
corrected to MISMATCH (its `[_A]1[_A+.]2` unifies both atoms to one element → cannot cleave the C–O ether
bond; same latent bug as canonical IMS4-EQ4.18).

**NEW GATE CHECK — MS-context coherence (convention G), added 2026-07-26.** `validate_records.py` now
runs `check_ms_context()`: an `adduct` of `[M]+•` claims the precursor IS the radical molecular ion, so
it is only legitimate when the precursor species is odd-electron (charge +1 / radical_electrons 1).
Soft/advisory by default, HARD under `--strict` (exits 1). Negative-tested. This class is invisible to
the conservation + arrow gates, and a corpus sweep with it found **11 real violations** (even-electron
fragment precursors tagged `[M]+•`), all fixed: IMS4-EQ4.20/4.21 (protonated ethanol / methoxymethyl
cation), IMS4-EQ4.6a–e, IMS8-EQ8.1c, and IMS8-EQ8.2f/g/h — the last three ALSO had `precursor_mz` set
to the parent molecular ion (100.0883) instead of the ion that actually reacts, corrected to
43.0173 / 57.0693 / 85.0642 to match sibling IMS8-EQ8.1c.

REFUTED verifier flag (do NOT "fix" this): batch 7 reported eqs 8.51/8.52 vs 8.53/8.54 as inconsistent
because the same page carries different ms_context. They are CORRECT — 8.51/8.52 react an even-electron
cyclic onium (q1/rad0 → adduct null), while 8.53/8.54 react an odd-electron molecular ion (q1/rad1 →
`[M]+•` + 70 eV EI). The difference is exactly what convention G prescribes. Likewise, a note reading
"70 eV is the book's standing EI condition, not a datum on this page" is an honest disclosure, not a
self-contradiction.

OPEN CONSISTENCY ITEM (not blocking): ~14 non-table records set a product `detected=true` without a
per-scheme printed m/z/% (tropylium base peak, butadiene⁺• RDA product, butene⁺• "predominates", etc.).
These are defensible as text/context-observed, so left as-is; a corpus-wide "detected = printed-number
only vs book-reports-observed" policy call could tidy them but is a separate decision. The spend cap is INTERMITTENT — a window clears
~14 agents (= 7 pages) reliably; batch 2 (14 pages/28 agents) hit the cap mid-run, batches 3 & 4
(7 pages/14 agents) completed fully. So run in **7-page batches**:
`Workflow(scriptPath="src/mechanisms/extract_pages.mjs", args={"pages":[176,177,178,179,181,182,183]})`
then 184–190, etc. After each: promote is automatic (draft agents copy gate-clean files into records/);
reconcile the verify verdicts (fix any flagged notes/ms_context by hand — no agents needed), then
`validate_records.py` (expect N/N passed) + `coverage_report.py`. If a window exhausts mid-batch,
salvage whatever landed and resume with the next page list.

## Open items on the Ch.4 set (review, not blocking)

- **`IMS4-FIG4.4a/b` (p62, Figure 4.4)** — gate-clean but a prior verifier called p62 a spectrum
  with cleavage-*marks*, not electron-pushing arrows. Re-check these two transcribe a *drawn* scheme;
  delete if they invent arrows.
- **37 records flag a mis-encoded / non-matching MØD rule** (audit byproduct) — see coverage report +
  memory `project_ims_chap4_rule_geometry_bugs`. A rule-corpus audit is the recommended follow-up
  (separate chemistry task).
- Generic-scheme records carry curator-*computed* m/z (disclosed in notes, status "inferred").

## How to run Ch.8 (or any pages)

Workflow (committed): `src/mechanisms/extract_pages.mjs`. Tooling: `schema.py`, `arrow_check.py`,
`validate_records.py`, `dump_pages.py`, `rule_index.py`, `coverage_report.py` (all `src/mechanisms/`).

1. `Workflow(scriptPath="src/mechanisms/extract_pages.mjs", args={"pages": <subset of page_map ch8>})`.
   Batch ~14 pages/launch (matches the intermittent spend-cap window — each launch clears ~28 agents).
   Within one session, add `resumeFromRunId:"<runId>"` to replay completed agents free after a cap.
2. After each run — promote gate-clean staging, then re-gate:
   - for each `data/mechanisms/.staging/p*/`: `validate_records.py --records-dir` it; if `N/N passed,
     0 failed`, move its files into `records/`; else leave (needs redraft). Then `rm -rf .staging`.
   - `apptainer exec --bind "$PWD:/app" --env PYTHONPATH=/app mol-spectro.sif python /app/src/mechanisms/validate_records.py --records-dir /app/data/mechanisms/records`
3. `python src/mechanisms/coverage_report.py` to refresh coverage.

## Acceptance / done criteria

- Every `records/*.json` passes `validate_records.py` (0 failed).
- Ch.8 equations extracted; coverage report shows the gaps + rule mismatches.
- Human sign-off promotes `review_status` from `unreviewed` → `expert_reviewed`.
