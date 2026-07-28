# Pending re-extraction

**Currently EMPTY — nothing is quarantined.** All extracted records live in `records/` and pass the gate.

## Resolved

- **IMS8-EQ8.59** (book p185, 3,3,5-trimethylcyclohexanone M+• → CO + 1,1,3-trimethylcyclopentane+•,
  m/z 112, 25%) — quarantined 2026-07-26 for unfaithfulness, **RE-EXTRACTED and restored 2026-07-28.**
  Settled at native scan resolution (`pypdf` `page.images[0]`, 1375x2016, cropped and upscaled 9x on the
  arrowheads). The book labels the reaction arrow **"i, α"** — it declares the step to be both inductive
  and α — and the drawing matches: a MIXED arrow set. Four arcs are drawn, and the **LEFT** arc (tail on
  the C1–C3 bond, C3 = the α CH₂ next to the gem-dimethyl carbon) carries a **full two-barbed arrowhead**
  = the 2-electron inductive move. The quarantined version had called all four arcs single-barbed
  fishhooks AND placed the 2-electron move on the C1–C7 bond, which swapped the charge and radical
  termini relative to the drawing. Both fixed; the bogus "HONEST READING / over-specified arc set"
  paragraph (an artefact of the miscount) was deleted. Product remains the disclosed ring-OPEN distonic
  form, since a saturated carbocycle radical cation has no valid localized mapped SMILES.

- **IMS8-EQ8.6** — RESOLVED 2026-07-26, re-extracted as a single stepwise retro-Diels-Alder
  (4-vinylcyclohexene+• → symmetric ring-opened distonic radical cation → 1,3-butadiene+• m/z 54 +
  neutral butadiene), disclosing that the book's (a)/(b) are s-cis / s-trans forms that coincide for
  the symmetric parent. The old two-channel 8.6a/8.6b were deleted.
