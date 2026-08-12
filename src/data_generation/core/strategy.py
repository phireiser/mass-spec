"""
Strategy definitions for forward and backward derivation graph construction.

Notes
- Forward starts from a single universe graph (the molecule term) and applies ionization once
    and fragmentation up to a bounded repeat.
- Backward starts from a list of fragment graphs and applies inverse rules with the same bounds.
"""
from typing import List, NamedTuple
import mod
from .predicates import (
    sub_group,
    charge_bound,
    amu_bound,
    migration_profit_gate,
    migration_multiplicity_cap,
)


# What to do with the "saturated tail" -- the large, sparsely-reactive molecules where the
# fully delocalized charge model does not pay for itself. See :func:`migration_scope`.
MIGRATION_TAIL_POLICIES = ("cap", "off", "gate", "full")

# Variants per parent-mass skeleton allowed on the tail under ``policy="cap"``. Measured on
# both steroids: cap 2 builds progesterone in 67 min and cholesterol in 88 min, versus a >9 h
# timeout with no dump at all under uncapped migration. Cap 3 costs 1.20x the species, 1.69x
# the wall and 1.81x the isomorphism calls for exactly one extra mass (progesterone m/z 86,
# +0.1% of NIST intensity), so 2 is the operating point.
#
# Re-confirmed at 83 molecules once the ring clause widened the tail (see `migration_scope`):
# cap 3 costs 2.4x cap 2's core-hours and moves only 5 molecules from lossy to clean, so 2
# still stands -- but see there, the cap is NOT lossless on that wider class.
DEFAULT_TAIL_CAP = 2


class MigrationScope(NamedTuple):
    """Outcome of :func:`migration_scope`. Named rather than a bare tuple because the
    decision has grown a third knob and positional unpacking at the call site would make
    ``scope[1] vs scope[2]`` bugs invisible."""

    use_migration: bool
    use_gate: bool
    cap: "int | None"      # variants per parent-mass skeleton; None = uncapped
    reason: str


def migration_scope(
    heavy_count: int,
    reactive_fraction: float,
    cyclomatic: int = 0,
    min_heavy: int = 18,
    min_cyclomatic: int = 2,
    max_reactive_fraction: float = 0.66,
    policy: str = "cap",
    tail_cap: int = DEFAULT_TAIL_CAP,
    ) -> MigrationScope:
    """Decide whether a molecule gets migration, and how it is bounded.

    Returns a :class:`MigrationScope` -- ``reason`` is a human-readable explanation for the
    run log, so a dump's provenance is self-documenting.

    A molecule is in the **tail** when it is sparsely reactive
    (``reactive_fraction < max_reactive_fraction``) AND structurally expensive -- either large
    (``heavy_count >= min_heavy``) or a fused ring system
    (``cyclomatic >= min_cyclomatic``). The decoration clause and the structure clause are
    both needed; neither alone selects the right molecules:

    * size alone also catches the hetero-dense large molecules (riboflavin 27 heavy, sucrose
      23) where every atom is reactive -- there migration's gains are real (sucrose NIST TPR
      0.068 -> 0.270, chance-corrected p=0.005) or its cost is at least bounded;
    * reactive fraction alone also catches the small *acyclic* alkanes (octane, decane,
      rf 0.000), which build fine with full migration and need no intervention.

    Together they select 12 of the 172 corpus molecules -- all 8 steroids and 4 long-chain
    fatty acids.

    **Why the structure clause is an OR over size and ring count.** Size alone was the
    original design and it was wrong: cost at fixed ``(heavy_count, reactive_fraction)`` spans
    four orders of magnitude with ring count. Measured through
    ``src/plot/bench_datagen_strategy.py`` at the shipping configuration, every row rf 0.000
    and the last three 10 heavy atoms apiece -- i.e. indistinguishable to a size+decoration
    trigger:

    ====================  =====  ===========  =========  =======
    molecule              heavy  cyclomatic   wall       species
    ====================  =====  ===========  =========  =======
    octane                    8            0     2.38 s      521
    decane                   10            0     5.13 s      831
    decalin                  10            2  **79.4 s**    8866
    CC1(C)C2CC3C1C3(C)C2     10            3  **13 h16**       --
    ====================  =====  ===========  =========  =======

    The tricyclic runs ~9000x its acyclic twin. Saturated polycycles are the real cost class:
    a fused cage gives the delocalized charge many near-equivalent cyclic paths with no
    cleavable terminus, and none of that shows up in ``reactive_fraction``.

    Confirmed at scale. In the 1155-molecule decoy build (job 5824027) the five most expensive
    molecules were saturated polycyclic terpenoids at 10-17 heavy atoms and rf 0.000-0.235 --
    every one below ``min_heavy``, so every one uncapped, up to 17 h20 and 8.74 GB each (four
    exceeded 12 h30 and four exceeded 8 GB, i.e. they would have died under the previous
    per-task budget). Adding the ring clause moves 82 of those 1155 decoys into the tail,
    covering **164.7 of the 180.7 core-hours** that build actually cost (91%), and leaves the
    most expensive uncapped molecule at 3.25 h. On the corpus proper it moves exactly one
    molecule -- camphor (11 heavy, cyclomatic 2, rf 0.364, 45 min uncapped) -- and removes the
    cap from none.

    **``min_cyclomatic`` is 2, not 1, because the cap is outright destructive on monocycles:**

    ==============  ==========  ==========================================================
    molecule        cyclomatic  measured cap behaviour
    ==============  ==========  ==========================================================
    piperidine               1  cap 3 loses **26.5%** of NIST intensity, incl. peak #2
    cyclohexanol             1  cap 3 loses **5.9%**
    decalin                  2  cap 3 lossless
    progesterone             4  cap 2 lossless, +24 masses
    cholesterol              4  cap 2 lossless, +24 masses
    ==============  ==========  ==========================================================

    An earlier revision of this docstring generalised those five rows into "the threshold lands
    exactly where the cap stops being lossless". **That claim is false**, and
    ``analysis/validate_migration_cap.py`` refuted it directly: it rebuilt all 83
    ring-clause-captured molecules capped and diffed their nominal-mass sets against the
    uncapped dumps.

    ==========  =========  ==================  ==================  ==============
    cap         lossless   lost no NIST mass   lost a NIST mass    cost (83 mols)
    ==========  =========  ==================  ==================  ==============
    2           11/83      45/83               **38/83**           9.2 core-h
    3           14/83      50/83               **33/83**           22.5 core-h
    uncapped    83/83      83/83               0                   164.7 core-h
    ==========  =========  ==================  ==================  ==============

    On the saturated terpenoids this clause newly captures, the cap **is** lossy, and raising
    it does not repair that -- cap 3 recovers 5 molecules for 2.4x the cost, so the loss is
    structural rather than a threshold artifact and cap 4 would follow the same curve.

    Cap 2 ships on the measured *size* of the loss, not its absence. By the forward model's own
    occurrence weighting the dropped masses are trace: median share 0.00012, p90 0.00176, max
    0.0098, and **zero** of the 83 lose more than 1% of occurrence weight. Nothing separates
    the lossy molecules from the clean ones -- lossy uncapped-wall median 1030 s vs clean
    1767 s, both at cyclomatic 2 -- so there is no sub-criterion left to refine this with; the
    choice is the cap or the 164.7 core-hours. And uncapped is not the lossless alternative it
    appears to be: four of these molecules exceeded 12 h30 and four exceeded 8 GB, so under the
    previous per-task budget they wrote no dump at all, losing every mass rather than a trace.

    The mechanism still holds directionally. A monocycle offers one cyclic path, so each charge
    placement is chemically distinct and dropping any is a real loss; a fused cage offers many
    near-equivalent paths, which is both why it explodes and why capping a redundant subset is
    *mostly* safe. "Mostly" is the correction: on steroids that redundancy is complete, on
    terpenoids it is not.

    **Do not "simplify" this by lowering ``min_heavy`` instead.** Measured: that sweeps in
    decane and octane (cyclomatic 0, rf 0.000, 5.13 s and 2.38 s) which need no intervention,
    and to catch a 10-heavy tricyclic the floor would have to drop low enough to catch
    substantially everything.

    ``max_reactive_fraction`` is 0.66 rather than the 0.6 this guard originally shipped with,
    and the correction was forced by measurement. At 0.6 the cut fell between cortisol (0.577,
    capped) and estrone (13/20 = 0.650, uncapped), and the earlier reasoning here -- that the
    empty span between those two values made the boundary "not delicate" -- had the conclusion
    backwards. The span is real, but the two molecules sitting just above it were the two most
    expensive in the entire corpus. In the full migration-on rebuild (job 5806812, 2026-08-06)
    they were the run's only two failures:

    ==============  =====  ========  ==========================================
    molecule        rf     scope     outcome at max_reactive_fraction = 0.6
    ==============  =====  ========  ==========================================
    cortisol        0.577  cap 2     1 h05, 2.8 GB peak
    estradiol       0.550  cap 2     1 h40, 4.8 GB peak
    **estrone**     0.650  *full*    **7 h04, 7.98 GB against an 8 GB limit**
    **aldosterone** 0.654  *full*    **killed at 12 h30, no dump written**
    ==============  =====  ========  ==========================================

    Six of the eight steroids were capped and finished in about an hour; the two that escaped
    the cap were the only molecule lost and the only near-OOM. Note ``>=`` in the test below:
    0.65 would *not* fix this, because estrone is exactly 0.65. 0.66 is the smallest value
    that captures both, and it is a safe place to stand -- the next tail-eligible molecule up
    is beta-carotene at 0.800, so anything in (0.654, 0.800] selects exactly the same set.

    Both are steroids, the class the cap's losslessness was actually measured on (progesterone
    and cholesterol, table below), so this widens the cap within its evidence base rather than
    extrapolating past it.

    The corpus is otherwise sharply bimodal in ``reactive_fraction`` -- 102 molecules sit at
    exactly 1.000 -- so away from the steroid cluster the boundary genuinely is insensitive.

    Why the tail defaults to ``"cap"``:

    The tail's problem was never that migration is worthless there -- it was that migration
    was *un-buildable* there. Cholesterol and progesterone did not finish in 3 h and did not
    finish again at 9 h, with memory never binding (5.4 of 32 GB), and a molecule that times
    out writes no dump and silently drops out of the corpus, re-introducing exactly the bias
    against hard molecules the pipeline previously fixed. So the tail was switched off.

    :func:`~data_generation.core.predicates.migration_multiplicity_cap` removes that
    constraint. Measured against the no-migration build (what ``policy="off"`` produces, i.e.
    what these molecules got before), a parent-mass-class cap of 2 gives a **strict superset
    with zero masses lost** on both steroids:

    ==============  =====================  =======================================
    molecule        no-migration           cap 2 + migration
    ==============  =====================  =======================================
    progesterone    13434 sp / 10.6 min    50252 sp / **67.1 min** / +24 masses
                    124 masses / 66.5%     148 masses / **71.7% of NIST intensity**
    cholesterol     14361 sp / 16.4 min    53895 sp / **87.8 min** / +24 masses
                    164 masses / 46.9%     188 masses / **51.6% of NIST intensity**
    ==============  =====================  =======================================

    Peak RSS 1.5-2.3 GB, comfortably inside the 16 GB / 23 h30 per-molecule budget in
    ``run/hpc/data_gen.sh``. Those margins are sized off the *uncapped* steroids -- estrone
    peaked at 7.98 GB and aldosterone ran past 12 h30 -- so once the tail is capped the
    headroom is roughly 3x on memory. The cost argument for ``"off"`` is therefore obsolete.

    What is NOT obsolete is the value argument, and it is the reason ``"off"`` is still
    offered: the steroids' TPR gains remain indistinguishable from emitting masses at random,
    because a steroid's NIST reference covers ~75% of the candidate integer masses
    (progesterone observed hit rate 0.810 vs 0.793 by chance, p=0.56). Migration's real,
    chance-corrected wins are elsewhere -- glucose (p=3.7e-05), limonene (p=3.3e-04), sucrose
    (p=0.005), naphthalene (p=0.038) -- and all of those are outside the tail and keep full
    migration regardless. Choose ``"cap"`` to buy the tail's extra masses at ~1.5 h/molecule;
    choose ``"off"`` if you would rather not pay for coverage whose value is unproven.

    ``policy="gate"`` instead wraps the tail in
    :func:`~data_generation.core.predicates.migration_profit_gate` (3 h18 / 5 h07, and lossy
    in a way the cap is not). ``policy="full"`` runs unguarded migration everywhere, which is
    the configuration that times out on the tail; it exists for A/B work, not production.

    **The cap is deliberately confined to the tail.** Its losslessness is class-dependent and
    not monotone in ``reactive_fraction``: at cap 3 decalin (rf 0.000) and the aromatics
    (rf 1.000) lose nothing, but cyclohexanol (rf 0.286) loses 5.9% of its NIST intensity and
    piperidine (rf 0.500) loses 26.5% including its second-largest peak. Those molecules are
    outside the tail and keep full migration. Applying the cap corpus-wide would be a
    regression, which is why no such switch exists here.

    Note the tail test is evaluated on the neutral parent, so it is a property of the input
    molecule and costs one pass over its vertices.
    """
    if policy not in MIGRATION_TAIL_POLICIES:
        raise ValueError(
            f"unknown migration tail policy {policy!r}; "
            f"expected one of {MIGRATION_TAIL_POLICIES}"
        )

    stats = (f"{heavy_count} heavy atoms, cyclomatic {cyclomatic}, "
             f"reactive_fraction {reactive_fraction:.3f}")
    full = MigrationScope(True, False, None, "")
    # `min_heavy <= 0` is the master escape hatch and disables the tail entirely, ring clause
    # included -- it is the documented "full migration for every molecule" switch, and callers
    # rely on that. Disable the ring clause alone with `min_cyclomatic <= 0`.
    if min_heavy <= 0:
        return full._replace(reason=f"full migration ({stats}; tail scoping disabled)")

    # Structure clause: large OR fused. Either alone is enough to make migration expensive --
    # long acyclic chains blow up by length, fused cages by cyclic path count.
    size_hit = heavy_count >= min_heavy
    ring_hit = min_cyclomatic > 0 and cyclomatic >= min_cyclomatic
    if not (size_hit or ring_hit):
        return full._replace(reason=(
            f"full migration ({stats}; neither >= {min_heavy} heavy nor >= "
            f"{min_cyclomatic} cyclomatic, so not structurally expensive)"))
    if reactive_fraction >= max_reactive_fraction:
        return full._replace(reason=(
            f"full migration ({stats}; reactive_fraction >= {max_reactive_fraction}, "
            f"so not the sparsely-reactive tail)"))

    trigger = " and ".join(filter(None, [
        f">= {min_heavy} heavy" if size_hit else "",
        f">= {min_cyclomatic} cyclomatic" if ring_hit else "",
    ]))
    tail = f"{stats}; IN the saturated tail ({trigger}, rf < {max_reactive_fraction})"
    if policy == "cap":
        # The measured evidence is cap-SPECIFIC, so only cite it at the value it was measured
        # at; a custom cap gets the mechanism without the numbers it did not earn.
        evidence = (
            f" At {DEFAULT_TAIL_CAP} this builds a steroid in ~1-1.5 h (uncapped: >9 h "
            f"timeout, no dump). Lossless on steroids; on saturated terpenoids it drops trace "
            f"masses (38 of 83 measured, none above 1% of occurrence weight)."
            if tail_cap == DEFAULT_TAIL_CAP else
            f" NOTE {DEFAULT_TAIL_CAP} is the measured operating point; {tail_cap} is not."
        )
        return MigrationScope(True, False, tail_cap, (
            f"migration + MULTIPLICITY CAP {tail_cap} -- {tail}. Capped to {tail_cap} "
            f"charge/radical variants per parent-mass skeleton.{evidence}"))
    if policy == "off":
        return MigrationScope(False, False, None, (
            f"migration DISABLED -- {tail}. Its TPR gain here is not distinguishable from "
            f"chance (p=0.56); pass --migration-tail-policy cap to build it anyway."))
    if policy == "gate":
        return MigrationScope(True, True, None, f"migration + PROFIT GATE -- {tail}")
    return full._replace(
        reason=f"full migration (forced by --migration-tail-policy full) -- {tail}")


def make_fwd_strategy(
    derivation_graph: mod.DG,
    universe: mod.Graph,
    ionization: List[mod.Rule],
    fragmentation: List[mod.Rule],
    migration: List[mod.Rule] = None,
    gate_migration: bool = False,
    migration_cap: "int | None" = None,
    trim_terminal_migration: bool = True,
    max_mass: float = 100,
    min_mass: float = 10,
    frag_repeat: int = 5,
    ) -> mod.DGStrat:

    """
    compile a strategy to perform the ionization and fragmentation

    Fully delocalized charge model: when ``migration`` is given, the charge/radical
    migration rules are interleaved with fragmentation *in the same repeat* rather than
    run as a separate phase. mod's strategy subset flows forward -- a dedicated
    ``repeat[k](migration)`` phase would hand fragmentation only the migration products and
    drop the fragmentable M+* isomers, zeroing the output. Interleaving instead lets both
    the M+* isomers (from ionization) and every charge-position isomer migration reaches
    chain through fragmentation, exactly as fragments-of-fragments already chain across the
    repeat's rounds. ``amu_bound`` still filters on the fragment side; a migration product
    keeps its parent's mass, so migrating the intact M+* (mass == ``max_mass``) is filtered
    out there, but that is redundant while per-site ionization seeds every charge position,
    and intermediate fragments (mass < ``max_mass``) migrate freely to reposition the
    charge for a subsequent cleavage. Migration carries no ``§`` extension, so ``sub_group``
    admits it unconditionally.

    ``gate_migration`` wraps the interleaved repeat in :func:`migration_profit_gate`, which
    keeps a charge/radical hop only when the decoration lands on a reactive site (see the
    predicate's docstring). It is the molecule-scoped scope guard for the large saturated
    tail: those molecules blow up (and time out) because the charge wanders the saturated
    sigma framework, and the gate prunes exactly those unproductive hops so the DG stays
    buildable.

    ``trim_terminal_migration`` (default on) drops migration from the FINAL repeat round,
    where its products are unobservable by construction -- see the comment at the call site.
    It is free: identical mass set on 12/12 molecules, ~40% fewer species on the expensive
    ones. Every cost figure quoted for ``migration_cap`` is measured on top of it.

    ``migration_cap`` bounds how many charge/radical placement variants of one parent-mass
    skeleton the graph may retain (see
    :func:`~data_generation.core.predicates.migration_multiplicity_cap`). It is what makes
    the saturated tail buildable at all -- a steroid finishes in ~1-1.5 h at cap 2 versus a
    >9 h timeout uncapped -- and it is applied outermost so it cannot be overruled. It is
    LOSSY outside the tail and must not be enabled corpus-wide; ``migration_scope`` owns that
    decision.

    ``gate_migration`` defaults to off and the caller enables it selectively (see
    ``main.py``), because the gate is **lossy wherever the framework is only partly
    decorated**: its
    radius-1 reactive shell also blocks transit hops, so a decoration cannot walk across
    three or more saturated bonds to reach a heteroatom (cyclohexanol loses m/z 41 at 22%
    relative intensity). It is ~free only on fully decorated frameworks (toluene 363->357,
    glucose 4322->4286), where it also prunes nothing. Because the gate never touches
    fragmentation, enabling it cannot remove a peak that migration was not itself
    responsible for -- but it can, and does, remove peaks migration would have produced.
    """

    assert frag_repeat > 0, "fragmentation repeat must be positive."
    assert max_mass > min_mass, "fragmentation max mass must be larger than min mass."

    frag_rules = list(fragmentation) + list(migration) if migration else fragmentation

    if migration and trim_terminal_migration and frag_repeat > 1:
        # TERMINAL-ROUND TRIM. A hop moves one ``+`` or one ``.`` across an existing bond, so
        # its product has the reactant's exact atom multiset and net charge and therefore an
        # IDENTICAL mass; and nothing follows the last round, so a final-round hop product is
        # never an educt. Those species are unobservable by construction: they add no peak and
        # fragment into nothing. Dropping migration from the final round alone cut decalin
        # 14388->8866 species and limonene 7579->4534 with the integer mass set IDENTICAL on
        # 12/12 molecules at frag_repeat 3, 4, 5 and 6.
        #
        # Two controls confirm this is redundancy removal rather than truncation: a plain
        # repeat[k-1] loses 2-13 masses on 6/8 molecules (cyclohexanol drops m/z 57, its 100%
        # base peak), and the mirror prune -- dropping FRAGMENTATION in the last round and
        # keeping migration -- loses exactly the same masses. The final round's entire
        # observable contribution is fragmentation.
        #
        # Guarded on ``frag_repeat > 1`` because at k=1 the trim would degenerate to
        # "migration off", which is lossy rather than free.
        frag_stage = (
                sub_group(mod.repeat[frag_repeat - 1](frag_rules), derivation_graph)
            >>  sub_group(mod.repeat[1](list(fragmentation)), derivation_graph)
        )
    else:
        frag_stage = sub_group(mod.repeat[frag_repeat](frag_rules), derivation_graph)

    if migration and gate_migration:
        # Per-round gate: a hop rejected here is not added, so it cannot seed the next
        # round's migration/fragmentation -- the pruning compounds across the repeat.
        frag_stage = migration_profit_gate(frag_stage)

    bounded = charge_bound(
        amu_bound(
            frag_stage,
            minimum = min_mass,  # TODO: consider configuring from dataset stats
            maximum = max_mass,
        )
    )

    if migration and migration_cap:
        # OUTERMOST, outside charge_bound/amu_bound: nested right predicates run
        # innermost-first and short-circuit, so placing the cap here means everything it sees
        # has already passed the mass/charge filters and its accept can never be overruled --
        # the budget therefore never charges for a derivation that is later discarded.
        # Scoped to the parent-mass class (``universe`` is the neutral molecule term), which
        # is where MØD's quadratic bucket cost actually lives.
        bounded = migration_multiplicity_cap(
            bounded, cap=migration_cap, parent_vertex_count=universe.numVertices
        )

    strategy = (
            mod.addSubset(universe)
		>> 	sub_group(mod.repeat[1](ionization), derivation_graph)
        >>  bounded
    )
    return strategy


def make_bwd_strategy(
    derivation_graph: mod.DG,
    universe: List[mod.Graph],
    fragmentation: List[mod.Rule],
    max_mass: float = 100,
    min_mass: float = 10,
    frag_repeat: int = 5,
    ) -> mod.DGStrat:

    """
    compile a strategy to perform the ionization and fragmentation
    """
    assert frag_repeat > 0, "fragmentation repeat must be positive."
    assert max_mass > min_mass, "fragmentation max mass must be larger than min mass."

    strategy = (
            mod.addSubset(universe)
        >>  charge_bound(
                amu_bound(
                    sub_group(mod.repeat[frag_repeat](fragmentation), derivation_graph),
                    minimum = min_mass,  # TODO: consider configuring from dataset stats
                    maximum = max_mass,
                )
            )
    )
    return strategy
