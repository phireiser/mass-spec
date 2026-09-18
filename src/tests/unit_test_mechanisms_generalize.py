"""
Unit tests for src.data_generation.mechanisms.generalize.

Like ``unit_test_mechanisms_dfs_writer``, these need only RDKit (no ``mod``),
so they run either side of the container boundary. Each case is stated as a
mapped-SMILES step -- the same form the curated corpus records -- so what is
asserted is "given this drawn mechanism, these are the atoms the rule keeps",
which is exactly the question generalization has to get right.
"""
import unittest

from src.data_generation.mechanisms.dfs_writer import parse_mapped_smiles
from src.data_generation.mechanisms.generalize import (
    context_atoms,
    keep_set,
    placeholder_atoms,
    prune_graph,
    reacting_core,
)

# IMS4-EQ4.13: diethyl ether radical cation, alpha cleavage. Bond 1-2 breaks
# and bond 2-3 becomes a double bond, so atoms 1/2/3 react; the ethyl on the
# far side of the oxygen (4, 5) is spectator scaffolding from the book's
# example compound.
ETHER_ALPHA = (
    "[CH3:1][CH2:2][O+:3][CH2:4][CH3:5]",
    "[CH2:2]=[O+:3][CH2:4][CH3:5].[CH3:1]",
)

# A gamma-hydrogen transfer with retro-ene cleavage (McLafferty shape): the
# carbonyl oxygen abstracts H:7 while bond 4-5 breaks. The carbonyl carbon (2)
# is untouched but sits BETWEEN the two reacting ends.
MCLAFFERTY = (
    "[CH3:1][C:2](=[O+:3])[CH2:4][CH2:5][CH2:6][H:7]",
    "[CH3:1][C:2](=[O+:3][H:7])[CH2:4].[CH2:5]=[CH2:6]",
)

# Homolysis at the far end of a chain whose charge sits on a remote oxonium:
# the reacting core (1, 2) carries neither charge nor radical.
REMOTE_CHARGE = (
    "[CH3:1][CH2:2][CH2:3][CH2:4][O+:5]([CH3:6])[CH3:7]",
    "[CH3:1].[CH2:2][CH2:3][CH2:4][O+:5]([CH3:6])[CH3:7]",
)


def _sides(step):
    left, left_h = parse_mapped_smiles(step[0])
    right, right_h = parse_mapped_smiles(step[1])
    return left, left_h, right, right_h


def _core(step, arrows=()):
    left, left_h, right, right_h = _sides(step)
    return reacting_core(left, left_h, right, right_h, arrows)


class TestReactingCore(unittest.TestCase):
    def test_core_is_the_atoms_the_rewrite_touches(self):
        # 1 becomes a radical, bond 1-2 breaks, bond 2-3 gains an order.
        # Nothing about 4/5 changes, so they are not core.
        self.assertEqual(_core(ETHER_ALPHA), {1, 2, 3})

    def test_core_spans_both_ends_of_a_rearrangement(self):
        self.assertEqual(_core(MCLAFFERTY), {3, 4, 5, 6, 7})

    def test_arrows_extend_the_core_beyond_the_graph_diff(self):
        # Atom 6 comes out of the step unchanged, so the diff alone misses it;
        # a curator arrow naming it puts it in the core anyway.
        self.assertEqual(_core(REMOTE_CHARGE), {1, 2})
        self.assertEqual(_core(REMOTE_CHARGE, arrows=(6,)), {1, 2, 6})

    def test_arrow_ids_absent_from_the_reactant_are_ignored(self):
        # Callers pass a step's whole arrow set unfiltered; an id that names no
        # reactant atom (a product-only map) must not leak into the core.
        self.assertEqual(_core(REMOTE_CHARGE, arrows=(6, 999)), {1, 2, 6})


class TestKeepSet(unittest.TestCase):
    def test_radius_zero_keeps_only_the_core(self):
        left, left_h, right, right_h = _sides(ETHER_ALPHA)
        core = reacting_core(left, left_h, right, right_h)
        self.assertEqual(keep_set(core, left, right, 0), {1, 2, 3})

    def test_radius_grows_a_shell_one_bond_at_a_time(self):
        left, left_h, right, right_h = _sides(ETHER_ALPHA)
        core = reacting_core(left, left_h, right, right_h)
        self.assertEqual(keep_set(core, left, right, 1), {1, 2, 3, 4})
        self.assertEqual(keep_set(core, left, right, 2), {1, 2, 3, 4, 5})

    def test_radius_beyond_the_diameter_reproduces_the_original(self):
        left, left_h, right, right_h = _sides(ETHER_ALPHA)
        core = reacting_core(left, left_h, right, right_h)
        self.assertEqual(keep_set(core, left, right, 9), set(left.atoms))

    def test_steiner_connector_is_kept_at_radius_zero(self):
        # Atom 2 is not in the core, but dropping it would leave the core in
        # two disconnected pieces and the rule would stop constraining the ring
        # size that makes this a gamma transfer rather than "any H reaches any O".
        left, left_h, right, right_h = _sides(MCLAFFERTY)
        core = reacting_core(left, left_h, right, right_h)
        self.assertNotIn(2, core)
        self.assertEqual(keep_set(core, left, right, 0), {2, 3, 4, 5, 6, 7})

    def test_remote_charge_is_anchored_with_its_path_to_the_core(self):
        # Without the anchor this rule would mention no charge at all and could
        # embed into a NEUTRAL fragment; with it, the rule still asserts "this
        # substructure belongs to an ion".
        left, left_h, right, right_h = _sides(REMOTE_CHARGE)
        core = reacting_core(left, left_h, right, right_h)
        self.assertEqual(keep_set(core, left, right, 0), {1, 2, 3, 4, 5})
        self.assertEqual(
            keep_set(core, left, right, 0, anchor_ion=False), {1, 2}
        )

    def test_keep_set_never_returns_product_only_atoms(self):
        # keep_set's result indexes the REACTANT graph (prune_graph applies it
        # to both sides), so an id that exists only on the right must not appear.
        left, left_h, right, right_h = _sides(MCLAFFERTY)
        core = reacting_core(left, left_h, right, right_h)
        for radius in (0, 1, 2, 9):
            self.assertLessEqual(
                keep_set(core, left, right, radius), set(left.atoms)
            )


class TestContextAtoms(unittest.TestCase):
    def test_shell_is_what_the_radius_added(self):
        left, left_h, right, right_h = _sides(ETHER_ALPHA)
        core = reacting_core(left, left_h, right, right_h)
        self.assertEqual(context_atoms(core, left, right, 1), {4})
        self.assertEqual(context_atoms(core, left, right, 2), {4, 5})

    def test_radius_zero_has_no_shell(self):
        for step in (ETHER_ALPHA, MCLAFFERTY, REMOTE_CHARGE):
            left, left_h, right, right_h = _sides(step)
            core = reacting_core(left, left_h, right, right_h)
            self.assertEqual(context_atoms(core, left, right, 0), set())

    def test_load_bearing_atoms_are_never_shell(self):
        # The core, the Steiner connectors that keep it connected and the ion
        # anchor's path are all what radius 0 keeps, so placeholdering the shell
        # can never reach them -- that is the property that makes it safe.
        for step in (ETHER_ALPHA, MCLAFFERTY, REMOTE_CHARGE):
            left, left_h, right, right_h = _sides(step)
            core = reacting_core(left, left_h, right, right_h)
            for radius in (1, 2, 9):
                shell = context_atoms(core, left, right, radius)
                self.assertFalse(shell & keep_set(core, left, right, 0))
                self.assertFalse(shell & core)

    def test_mclafferty_connector_is_not_placeholdered(self):
        # Atom 2 is kept at radius 0 as a Steiner connector, so it keeps its
        # element even though it is not itself part of the graph diff.
        left, left_h, right, right_h = _sides(MCLAFFERTY)
        core = reacting_core(left, left_h, right, right_h)
        self.assertNotIn(2, context_atoms(core, left, right, 1))


class TestPlaceholderAtoms(unittest.TestCase):
    def test_element_is_replaced_and_decoration_kept(self):
        left, _, _, _ = _sides(REMOTE_CHARGE)
        self.assertEqual(left.atoms[5].label(), "[O+]")

        placeholder_atoms(left, {1, 5})

        self.assertEqual(left.atoms[1].label(), "[_A]")
        # Charge is part of what the rewrite asserts, so it survives.
        self.assertEqual(left.atoms[5].label(), "[_B+]")
        self.assertEqual(left.atoms[2].label(), "[C]")

    def test_each_position_gets_its_own_variable(self):
        # A shared name would make mod unify the positions, forcing them to the
        # same element -- a constraint the concrete rule never had, and one that
        # measurably LOWERED the corpus ceiling when it was there.
        left, _, _, _ = _sides(REMOTE_CHARGE)

        placeholder_atoms(left, {1, 3, 6})

        names = [left.atoms[i].symbol for i in (1, 3, 6)]
        self.assertEqual(len(set(names)), 3, names)

    def test_both_sides_get_the_same_name_for_the_same_atom(self):
        # The name is the term variable: a binding only carries across the
        # rewrite if the two sides agree on it, and the conservation guard
        # tallies atoms by symbol.
        left, _, right, _ = _sides(ETHER_ALPHA)
        shell = {1, 4}

        placeholder_atoms(left, shell)
        placeholder_atoms(right, shell)

        for atom_id in shell:
            self.assertEqual(left.atoms[atom_id].symbol, right.atoms[atom_id].symbol)

    def test_ids_absent_from_this_side_are_ignored(self):
        # The same shell is applied to both sides, and a fragmenting step's
        # sides need not carry identical id sets after pruning.
        left, _, _, _ = _sides(ETHER_ALPHA)
        placeholder_atoms(left, {4, 999})
        self.assertEqual(left.atoms[4].label(), "[_A]")


class TestPruneGraph(unittest.TestCase):
    def test_prune_drops_spectators_and_their_bonds(self):
        left, left_h, right, right_h = _sides(ETHER_ALPHA)
        core = reacting_core(left, left_h, right, right_h)
        keep = keep_set(core, left, right, 0)

        prune_graph(left, keep)

        self.assertEqual(set(left.atoms), {1, 2, 3})
        # The 3-4 bond went with atom 4; no dangling reference survives.
        for atom_id, neighbours in left.adjacency.items():
            for other, _token in neighbours:
                self.assertIn(other, keep, f"dangling bond {atom_id}-{other}")

    def test_pruning_both_sides_leaves_the_tally_balanced(self):
        # build_rules applies the same keep set to both sides precisely so the
        # conservation guard sees what it saw before pruning.
        left, left_h, right, right_h = _sides(REMOTE_CHARGE)
        core = reacting_core(left, left_h, right, right_h)
        keep = keep_set(core, left, right, 0)

        prune_graph(left, keep)
        prune_graph(right, keep)

        self.assertEqual(set(left.atoms), set(right.atoms))
        self.assertEqual(set(left.atoms), {1, 2, 3, 4, 5})


if __name__ == "__main__":
    unittest.main()
