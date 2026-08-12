export const meta = {
  name: 'ims-extract-pages',
  description: 'Extract faithful electron-pushing MechanismRecords from IMS book pages, gate-validated + adversarially verified',
  phases: [
    { title: 'Draft', detail: 'vision agent per page; self-validates against the arrow gate until green' },
    { title: 'Verify', detail: 'adversarial vision re-read: does the record match what is DRAWN?' },
  ],
}

const REPO = '/lisc/home/user/reiser/Nextcloud/studium/computationalScience/thesis/mol'

// MIRROR OF src/paths.env -- must be kept in sync by hand.
// Workflow scripts run without filesystem or Node API access, so this file cannot
// parse paths.env the way src/project_paths.py does. The values below are instead
// asserted against paths.env by src/tests/unit_test_project_paths.py, so a drift
// fails the unit suite rather than silently pointing agents at the wrong directory.
const BOOK_PAGES_DIR_REL = 'data/IMS-Book/pages'
const MECHANISMS_DIR_REL = 'data/mechanisms'
const MECHANISM_RECORDS_DIR_REL = 'data/mechanisms/records'

const PAGES_DIR = REPO + '/' + BOOK_PAGES_DIR_REL
const RECORDS_DIR = REPO + '/' + MECHANISM_RECORDS_DIR_REL
// Gitignored scratch root. Records stage here before promotion, and every agent's working
// files (page crops, measurement scripts) live here too -- see workingFiles() below.
const STAGING = REPO + '/' + MECHANISMS_DIR_REL + '/.staging'
const EXAMPLE = REPO + '/' + MECHANISMS_DIR_REL + '/example_mechanism.json'
const RULE_INDEX = REPO + '/' + MECHANISMS_DIR_REL + '/rule_index.json'

// args: { pages: [70, 72, ...] }  -- PDF page indices already dumped to PAGES_DIR.
// args may arrive as an object OR as a JSON-encoded string; handle both, and fail loudly
// rather than silently falling back to a stub page list.
const _a = typeof args === 'string' ? JSON.parse(args) : args
const pageIdxs = _a && _a.pages
if (!Array.isArray(pageIdxs) || pageIdxs.length === 0) {
  throw new Error('extract_pages: args.pages must be a non-empty array of PDF page indices')
}
log(`extracting ${pageIdxs.length} page(s): ${pageIdxs.join(', ')}`)

const CONVENTIONS = `
=== NON-NEGOTIABLE ENCODING CONVENTIONS ===

(A) FAITHFUL ELECTRON-PUSHING. The arrows must *produce* the product, not merely gesture at it.
    Every electron of every bond that changes must be accounted for:
      - a bond that GAINS one bond order must RECEIVE exactly 2 electrons (2 fishhooks, or 1 double-barbed arrow);
      - a bond that is BROKEN homolytically must have BOTH of its electrons routed somewhere (2 separate fishhooks).
    Canonical radical-site alpha-cleavage therefore needs THREE fishhooks in the ENCODING:
      1. the radical site's odd electron  ->  the forming pi bond      (atom X -> bond X-Y)
      2. one electron of the breaking sigma bond -> the forming pi bond (bond Y-Z -> bond X-Y)
      3. the other electron of that sigma bond -> the departing radical (bond Y-Z -> atom Z)
    A two-fishhook encoding that omits (2) is WRONG and the gate will reject it.
    Use electron_count 1 for a single-barbed fishhook, 2 for a double-barbed (heterolytic) arrow.

(D) DRAWN vs IMPLIED - DO NOT MISREPRESENT THE FIGURE. McLafferty frequently draws only TWO arcs
    and leaves the homolysis hook (3) implicit (the departing R* is simply written as a product).
    You must still ENCODE the complete, balanced electron flow - but you must DESCRIBE it honestly.
    COUNT the arcs actually drawn (zoom in; a barb is a half-arrowhead). Then in the step's
    curator_note state, verbatim in this shape:
      "Book draws N arc(s); move(s) <i,j> are drawn, move <k> is an implicit homolysis hook required
       for electron balance (not drawn on the page)."
    NEVER write "three fishhooks are drawn" when the page shows two. A false claim about the figure
    is a worse defect than an unencoded arrow.

(E) VERIFY CROSS-LINKS - DO NOT ASSERT THEM. Before claiming a MØD rule corresponds to the scheme,
    CHECK that its DFS really describes the same bond changes: which bond is cleaved, which bond
    gains order, and whether the cleaved bond is incident to the atom that forms the new multiple
    bond. Where practical, test that the rule pattern actually matches your instantiated substrate
    (RDKit substructure match). Several existing rules are known to be MIS-ENCODED relative to the
    book. If the rule does NOT match, say so plainly in the curator_note (e.g. "IMS_4_9 cleaves a
    bond not incident to the pi-forming atom and does not match this substrate") and ALSO list it in
    the returned "rule_mismatches". A discovered mismatch is a valuable finding - never paper over it
    with "exact match".

(F) NO INVENTED MEASUREMENTS. Generic schemes (R, Y, CR2) usually print NO m/z and NO intensity.
    In that case: peak status "inferred", detected=false, OMIT relative_intensity, and put the
    computed m/z with a curator_note saying it derives from your chosen instantiation, not the book.
    Only use status "observed"/"proposed" with relative_intensity when the page actually prints a
    percentage. Never present a curator-computed number as a measured one.

(B) LOCALIZE CHARGE AND RADICAL IN THE SMILES. The precursor's mapped_smiles must place the
    charge and the odd electron on the atom where the book draws them, so the arrows have a real
    origin. E.g. a ketone n-ionized at oxygen is [CH3:3][CH2:2][C:1](=[O+:6])[CH2:4][CH3:5]
    (O+ with two bonds carries one radical electron), NOT the neutral closed-shell ketone with
    the charge only in the JSON fields. The species-level charge / radical_electrons fields must
    AGREE with what the SMILES implies. Mirror the MØD DFS, which localizes explicitly ({=}[O+.]).

(C) DELOCALIZED IONS (allyl, benzyl/tropylium, aromatic radical cations). Choose ONE localized
    resonance/Kekule form and be consistent; the arrows must produce exactly that form. Record the
    resonance in a curator_note (and, if the book draws the partner form, mention it). Do not write
    a half-localized structure whose bonds match neither form.

(G) MS CONTEXT & DETECTED FLAG (Chapter 8 mixes EI, CAD, MI and CI - do NOT hardcode 70 eV EI/[M]+.).
    Set ms_context from the experiment ACTUALLY named on the page (see the ms_context field guide). A
    "CAD: 9%" or metastable abundance is NOT a 70 eV EI intensity; a mass-selected fragment precursor is
    NOT the [M]+. molecular ion (adduct=null). Set a product species detected=true ONLY if the page
    prints an m/z or % for that ion; otherwise detected=false with peak status "inferred" and no
    relative_intensity. If the book draws a NON-COVALENT proton-bound complex [A...H...B] as an
    intermediate, it usually cannot be a valid mapped_smiles species -> encode the net reaction and
    DISCLOSE the drawn complex in the step evidence curator_note; never silently drop a drawn intermediate.
    NOTE PLACEMENT: curator notes attach to EvidenceLink.curator_note (an evidence[] entry with
    target_type "step" or "mechanism"); ElementaryStep itself has NO curator_note field (StrictModel
    rejects it), so put step-level commentary on the target_type "step" evidence link.
`

const SELF_CHECK = `
=== SELF-VALIDATE BEFORE YOU FINISH (this is a hard gate) ===
Write your drafts FIRST to your own staging dir: ${STAGING}/p<PDFINDEX>/
Then run the validator on that dir (it runs RDKit inside the project container):

  cd ${REPO} && apptainer exec --bind "$PWD:/app" --env PYTHONPATH=/app mol-spectro.sif \\
    python /app/src/mechanisms/validate_records.py --records-dir /app/data/mechanisms/.staging/p<PDFINDEX>
(the container sees the repo at /app, so the staging path inside it is /app/data/mechanisms/.staging/...)

It checks: schema validity, atom/charge/total-electron conservation, atom-map completeness, AND
the electron-move <-> bond-order bookkeeping from (A). Lines beginning "(soft)" are advisory;
anything else is a hard failure. FIX AND RE-RUN UNTIL IT REPORTS "N/N passed, 0 failed".
Only then copy the record files into ${RECORDS_DIR}/ and remove your staging dir.
Do NOT write unvalidated records into ${RECORDS_DIR}.

*** ID-COLLISION GUARD (check this BEFORE you copy anything) ***
A multi-page table or equation may already be partly encoded from an EARLIER page, and suffix letters
restart per page. For every file you are about to promote, first check whether
${RECORDS_DIR}/<mechanism_id>.json already exists (e.g. ls ${RECORDS_DIR} | grep '<eq-or-table-id>').
If it does and it is a DIFFERENT scheme, DO NOT overwrite it: continue the existing suffix series from
the next free letter, and say so in "issues". Overwriting a committed record silently destroys work.
`

// Settling fine drawing detail means cropping and zooming the scan, which produces throwaway PNGs and
// one-off measurement scripts. Left unsaid, agents write those into the process CWD -- the repo root --
// where they survive the run and have to be deleted by hand (this happened: ~10 MB of scratch_*.png).
const workingFiles = (dir) => `
=== WORKING FILES: NOTHING MAY BE WRITTEN TO THE REPO ROOT ===
Put EVERY scratch artefact you create -- cropped/zoomed page images, native-resolution scans pulled
with pypdf, throwaway .py measurement scripts, notes to yourself -- under
  ${dir}/
and nowhere else. Create it if it does not exist. Do NOT write them to the repo root, to your current
working directory, or next to the page images: ${REPO} is the user's git repository, and stray scratch
files there outlive the run. The .staging tree is gitignored, so nothing you leave there can pollute a
commit -- but still DELETE YOUR DIRECTORY before you return. Reading the repo is unrestricted; this
rule is only about where new files land.
`

const FIELD_GUIDE = `
Produce ONE MechanismRecord JSON per reaction scheme. Read ${EXAMPLE} for the exact shape.
- mechanism_id "IMS<chapter>-EQ<eq>" (+ a/b suffix if one equation number carries several schemes).
- species[]: species_id, mapped_smiles (RDKit-parseable; EVERY atom carries :N; the SAME map number
  denotes the same atom in precursor and products), role, charge, radical_electrons,
  spin_multiplicity (2 = doublet, 1 = closed shell), detected (true for the observed ion).
  Molecular ion = charge 1 / radical_electrons 1; even-electron product cation = 1 / 0;
  expelled alkyl radical = 0 / 1; neutral closed-shell loss (alkene, CO) = 0 / 0.
- states[]: state_precursor and state_products (add intermediates only if the book draws them).
- steps[]: step_class from the section (alpha_cleavage, inductive_cleavage, sigma_dissociation,
  retro_diels_alder, hydrogen_rearrangement, ...), semantics "formal_arrow_step",
  electron_moves[] transcribed per convention (A).
- ms_context: read the ACTUAL experiment named on the page/text; do NOT assume 70 eV EI of a molecular
  ion (Chapter 8 mixes EI, CAD, MI and CI). The SPECIES UNDERGOING THE DRAWN REACTION sets adduct +
  precursor_mz:
    * neutral molecular ion M+• (whole molecule ionized, odd-electron): adduct "[M]+•",
      precursor_mz = M+• m/z, ionization_method "EI", activation_method "70 eV EI", electron_energy_ev 70.
    * CI protonated molecule (page says "... CI"): adduct "[M+H]+", precursor_mz = [M+H]+ m/z,
      ionization_method "CI", activation_method "chemical ionization", electron_energy_ev null.
    * a MASS-SELECTED FRAGMENT ion (even-electron oxonium/acylium/any daughter ion): adduct null (it is
      NOT [M]+•), precursor_mz = that fragment's m/z; activation_method =
      "collision-activated dissociation (CAD)" when the page prints "CAD", or
      "metastable-ion (MI) decomposition" for MI/metastable studies; electron_energy_ev null.
  polarity "positive". Never store a CAD/MI branching abundance or a CI/MI datum as a 70 eV EI intensity.
- sources[]: (1) source_id "mclafferty_ims_4e", type "book", citation
  "McLafferty & Turecek, Interpretation of Mass Spectra, 4th ed., University Science Books, 1993",
  isbn "0-935702-25-3"; (2) source_id "mod_rules", type "software_output", citation
  "MØD Rule.fromDFS encodings in src/data_generation/rules/ (German-edition provenance)".
- evidence[]: (a) target_type "step" -> the step, source "mclafferty_ims_4e",
  support_type "textbook_proposed", locator {page: <PRINTED BOOK PAGE ON THIS SCAN>, equation "<eq>"};
  (b) target_type "mechanism" -> mechanism_id, source "mod_rules",
  support_type "computationally_supported", curator_note naming the cross-linked MØD rule variables.
  If the book crosses the arrow out / calls the path negligible, use support_type "contradicted"
  and peak status "rejected".
- peak_assignments[]: for the detected ion, observed_mz = computed monoisotopic m/z,
  relative_intensity from the printed % (100% -> 1.0), status "proposed".
- curation: extraction_method "vision_multiagent", review_status "unreviewed".
`

phase('Draft')
const results = await pipeline(
  pageIdxs,
  (idx) => agent(
    `Extract electron-pushing mechanism records from ONE page of McLafferty & Turecek, *Interpretation of Mass Spectra*, 4th ed.

PAGE IMAGE (read it with the Read tool): ${PAGES_DIR}/p${String(idx).padStart(3, '0')}.png

Steps:
1. Read the page image. Note the PRINTED book page number in the header - you will cite it.
2. Identify EVERY numbered equation / reaction scheme on the page that depicts an ion fragmentation
   or ionization mechanism. Skip pure prose, spectra plots, and "Unknown" exercises. If one equation
   number labels several distinct schemes, encode each as its own record (suffix a/b/...).
3. For each, look up its equation id in ${RULE_INDEX} (JSON: "by_equation" maps "4.13" -> MØD rule
   variable names; "entries" holds each variable's DFS string). Use the DFS as the authoritative
   connectivity/charge/spin change, and cross-link the variable names. Some equations have no MØD
   rule - that is fine, note it.
   MØD DFS legend: [Sym]N = atom with map N; bonds single by default, {=}/{#}/{-} set order;
   +/-/. after the symbol mark formal charge and unpaired electrons; "." separates fragments;
   ">>" splits reactant>>product.
4. Draft one MechanismRecord per scheme.
5. Self-validate and iterate until the gate is green, then promote the files.

${CONVENTIONS}
${FIELD_GUIDE}
${SELF_CHECK}
${workingFiles(`${STAGING}/p${idx}/work`)}

Return ONLY a JSON object (no prose, no code fence) as your final message:
{"pdf_index": ${idx}, "book_page": <printed page number you read>, "records": [{"equation_id": "...", "mechanism_id": "...", "file": "<absolute path in records dir>", "kind": "concrete|generic-instantiated|disfavored", "step_class": "...", "arcs_drawn": <how many arcs the page actually draws>, "moves_encoded": <length of electron_moves>, "printed_intensity": "<the % printed, or null>", "detected_ion_mz": <number>, "mod_rules": ["..."], "note": "..."}], "rule_mismatches": [{"equation_id": "...", "rule": "IMS_x_y", "why": "..."}], "gate": "<final validator line, e.g. 5/5 passed, 0 failed>", "issues": ["schemes you could not encode and why"]}`,
    { label: `draft:p${idx}`, phase: 'Draft', agentType: 'general-purpose' }
  ),
  (draftText, idx) => agent(
    `Adversarially verify drafted mechanism records against the source page. Be skeptical; default to reporting a problem.

Source page image: ${PAGES_DIR}/p${String(idx).padStart(3, '0')}.png
The drafting agent reported: ${draftText}

A deterministic gate has ALREADY proven these records are schema-valid, mass/charge/electron
conserving, and that their arrows balance the bond-order changes. Do NOT re-derive that.
Your job is FAITHFULNESS TO WHAT IS DRAWN. For each record file: Read the page image AND the JSON.
1. Are the precursor and product the molecules actually drawn (right substrate, right bond broken,
   charge retained on the fragment the book shows)?
2. Is the charge/radical site the one drawn (convention B: localized in the SMILES)?
3. ARROWS, two separate questions:
   (a) COUNT the arcs actually drawn (zoom in; a barb is a half-arrowhead).
   (b) The record must ENCODE the complete balanced flow (often 3 moves) even where the book draws
       only 2 - that is correct and required. What must be TRUE is the curator_note's description:
       it must state how many arcs are drawn and mark any extra move as an implicit homolysis hook.
   Report a problem if the note claims arrows are drawn that are NOT on the page (or vice versa),
   or if a move's origin/destination contradicts an arc that IS drawn.
4. MEASUREMENTS: does the page actually PRINT an m/z / % for this scheme? If not, the record must
   use status "inferred", detected=false, no relative_intensity. Flag any curator-computed number
   presented as measured.
5. PROVENANCE: correct PRINTED book page and equation number. And CHECK the MØD cross-link claim -
   does the cited rule's DFS really describe this bond change (same bond cleaved, same bond gaining
   order, cleaved bond incident to the pi-forming atom)? Several rules are mis-encoded; a note
   claiming "exact match" for a rule that cannot match the substrate is a defect. Report it.
6. Did the drafter MISS any mechanism scheme on the page, or invent one that is not there?
${workingFiles(`${STAGING}/p${idx}-verify`)}
Return ONLY a JSON object (no prose, no fence):
{"pdf_index": ${idx}, "verdicts": [{"file": "...", "equation_id": "...", "faithful": true|false, "arcs_drawn": <count you observed>, "note_honest": true|false, "problems": ["..."]}], "rule_mismatches": [{"equation_id": "...", "rule": "IMS_x_y", "why": "..."}], "missing_equations": ["..."], "spurious_records": ["..."]}`,
    { label: `verify:p${idx}`, phase: 'Verify', agentType: 'general-purpose' }
  )
)

function tryParse(s) { try { return JSON.parse(s) } catch (e) { return { parse_error: String(e), raw: s } } }
const verifications = results.filter(Boolean).map(tryParse)
log(`extraction complete: ${verifications.length} page(s)`)
return { verifications }
