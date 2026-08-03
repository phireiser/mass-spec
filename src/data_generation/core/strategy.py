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
    min_heavy: int = 18,
    max_reactive_fraction: float = 0.6,
    policy: str = "cap",
    tail_cap: int = DEFAULT_TAIL_CAP,
    ) -> MigrationScope:
    """Decide whether a molecule gets migration, and how it is bounded.

    Returns a :class:`MigrationScope` -- ``reason`` is a human-readable explanation for the
    run log, so a dump's provenance is self-documenting.

    A molecule is in the **tail** when it is both large (``heavy_count >= min_heavy``) and
    sparsely reactive (``reactive_fraction < max_reactive_fraction``). Both clauses are
    needed; neither alone selects the right molecules:

    * size alone also catches the hetero-dense large molecules (riboflavin 27 heavy, sucrose
      23) where every atom is reactive -- there migration's gains are real (sucrose NIST TPR
      0.068 -> 0.270, chance-corrected p=0.005) or its cost is at least bounded;
    * reactive fraction alone also catches the small alkanes (octane/decalin, rf 0.000),
      which build fine with full migration and need no intervention.

    Together they select 10 of the 172 corpus molecules -- 6 steroids and 4 long-chain fatty
    acids -- and the corpus is sharply bimodal in ``reactive_fraction`` (102 molecules sit at
    exactly 1.000), so the boundary is not delicate: nothing in the corpus falls between
    0.577 and 0.650.

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

    Peak RSS 1.5-2.3 GB against a 32 GB budget, and both fit inside the 7-day per-molecule
    budget with three orders of magnitude to spare. The cost argument for ``"off"`` is
    therefore obsolete.

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

    stats = f"{heavy_count} heavy atoms, reactive_fraction {reactive_fraction:.3f}"
    full = MigrationScope(True, False, None, "")
    if min_heavy <= 0:
        return full._replace(reason=f"full migration ({stats}; tail scoping disabled)")

    if heavy_count < min_heavy:
        return full._replace(
            reason=f"full migration ({stats}; below the {min_heavy}-heavy tail floor)")
    if reactive_fraction >= max_reactive_fraction:
        return full._replace(reason=(
            f"full migration ({stats}; reactive_fraction >= {max_reactive_fraction}, "
            f"so not the sparsely-reactive tail)"))

    tail = f"{stats}; IN the saturated tail (>= {min_heavy} heavy and < {max_reactive_fraction})"
    if policy == "cap":
        # The measured evidence is cap-SPECIFIC, so only cite it at the value it was measured
        # at; a custom cap gets the mechanism without the numbers it did not earn.
        evidence = (
            f" At {DEFAULT_TAIL_CAP} this builds a steroid in ~1-1.5 h (uncapped: >9 h "
            f"timeout, no dump) and is a strict superset of the no-migration result, zero "
            f"masses lost."
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
