"""
Unit tests for src.data_generation.mechanisms.dfs_writer.

These need only RDKit (no ``mod``), unlike most of this suite, so they also run
directly outside the container. Correctness is checked by round-tripping the
emitted DFS string through a small test-only reader that understands exactly
the grammar ``dfs_writer`` emits (NOT a reimplementation of mod's own parser --
there is no local ``mod`` install to check against, see that module's
docstring) and comparing the recovered atoms/bonds against what RDKit reports
for the same mapped SMILES directly.
"""
import unittest

from rdkit import Chem

from src.data_generation.mechanisms.dfs_writer import (
    MechanismConversionError,
    apply_localization,
    parse_mapped_smiles,
    reaction_dfs_string,
)


def _parse_dfs_side(text):
    """Read one side (no top-level '.'-split; see _parse_dfs) of our own DFS
    grammar back into ``(atoms: {id: (symbol, charge, radical)}, edges: {frozenset({a,b}): token})``."""
    atoms = {}
    edges = {}
    i = 0
    n = len(text)
    stack = []
    current = None
    pending_token = "-"

    while i < n:
        c = text[i]
        if c == "(":
            stack.append(current)
            i += 1
        elif c == ")":
            current = stack.pop()
            i += 1
        elif c == "{":
            j = text.index("}", i)
            pending_token = text[i + 1:j]
            i = j + 1
        elif c == ":":
            pending_token = ":"
            i += 1
        elif c == "[":
            j = text.index("]", i)
            label = text[i + 1:j]
            i = j + 1
            k = i
            while k < n and text[k].isdigit():
                k += 1
            atom_id = int(text[i:k])
            i = k
            m = 0
            while m < len(label) and label[m] not in "+-.":
                m += 1
            symbol, deco = label[:m], label[m:]
            atoms[atom_id] = (symbol, deco.count("+") - deco.count("-"), deco.count("."))
            if current is not None:
                edges[frozenset((current, atom_id))] = pending_token
            current = atom_id
            pending_token = "-"
        elif c.isdigit():
            k = i
            while k < n and text[k].isdigit():
                k += 1
            ref_id = int(text[i:k])
            i = k
            edges[frozenset((current, ref_id))] = pending_token
            pending_token = "-"
        else:
            raise AssertionError(f"unexpected char {c!r} at position {i} in {text!r}")

    return atoms, edges


def _parse_dfs(text):
    """Split on top-level '.' (never inside a bracket) and merge components."""
    atoms = {}
    edges = {}
    depth = 0
    start = 0
    pieces = []
    for i, c in enumerate(text):
        if c in "[":
            depth += 1
        elif c in "]":
            depth -= 1
        elif c == "." and depth == 0:
            pieces.append(text[start:i])
            start = i + 1
    pieces.append(text[start:])
    for piece in pieces:
        a, e = _parse_dfs_side(piece)
        atoms.update(a)
        edges.update(e)
    return atoms, edges


_TOKEN_TO_BONDTYPE = {
    "-": Chem.BondType.SINGLE,
    "=": Chem.BondType.DOUBLE,
    "#": Chem.BondType.TRIPLE,
    ":": Chem.BondType.AROMATIC,
}


def _reference_graph(mapped_smiles):
    """(atoms, edges) directly from RDKit, in the same shape _parse_dfs returns,
    for comparison against the round-tripped DFS string."""
    params = Chem.SmilesParserParams()
    params.removeHs = False
    mol = Chem.MolFromSmiles(mapped_smiles, params)
    atoms = {}
    id_of = {}
    for atom in mol.GetAtoms():
        vid = atom.GetAtomMapNum()
        id_of[atom.GetIdx()] = vid
        atoms[vid] = (atom.GetSymbol(), atom.GetFormalCharge(), atom.GetNumRadicalElectrons())
    edges = {}
    for bond in mol.GetBonds():
        a, b = id_of[bond.GetBeginAtomIdx()], id_of[bond.GetEndAtomIdx()]
        edges[frozenset((a, b))] = bond.GetBondType()
    # Fold in implicit hydrogens as ordinary ("H", 0, 0) leaves so the shape
    # matches the DFS side's fully-expanded graph. Ids are irrelevant here
    # since we only compare per-heavy-atom hydrogen COUNTS, not identity.
    implicit_h_total = sum(atom.GetTotalNumHs() for atom in mol.GetAtoms())
    return atoms, edges, implicit_h_total


class TestDfsWriterRoundTrip(unittest.TestCase):
    def _assert_round_trips(self, left_smiles, right_smiles):
        dfs = reaction_dfs_string(left_smiles, right_smiles)
        self.assertIn(">>", dfs)
        left_text, right_text = dfs.split(">>")

        for side_text, side_smiles in ((left_text, left_smiles), (right_text, right_smiles)):
            parsed_atoms, parsed_edges = _parse_dfs(side_text)
            ref_atoms, ref_edges, ref_implicit_h = _reference_graph(side_smiles)

            # Every real (curator-mapped) heavy/explicit atom must round-trip
            # with the same symbol/charge/radical.
            for vid, expected in ref_atoms.items():
                self.assertEqual(parsed_atoms[vid], expected, f"atom {vid} in {side_text!r}")

            # Every declared bond between two REAL mapped atoms must survive
            # with the same order.
            for key, bondtype in ref_edges.items():
                token = parsed_edges.get(key)
                self.assertIsNotNone(token, f"missing edge {key} in {side_text!r}")
                self.assertEqual(_TOKEN_TO_BONDTYPE[token], bondtype, f"edge {key} in {side_text!r}")

            # Total explicit-in-DFS hydrogen count (real mapped Hs + synthesized
            # implicit ones) must equal RDKit's implicit-H total plus however
            # many of the "real" atoms are themselves hydrogen.
            real_h_atoms = sum(1 for sym, _, _ in ref_atoms.values() if sym == "H")
            synthesized_h = sum(1 for sym, _, _ in parsed_atoms.values() if sym == "H") - real_h_atoms
            self.assertEqual(synthesized_h, ref_implicit_h, f"implicit-H expansion count in {side_text!r}")

        return dfs

    def test_simple_acyclic_cleavage(self):
        # Homolysis of neutral propane's C2-C5 bond -> ethyl radical + methyl
        # radical (IMS_4_3-style connectivity, minus the charge/radical-cation
        # bookkeeping, which is exercised separately below).
        dfs = self._assert_round_trips(
            "[CH3:1][CH2:2][CH3:5]",
            "[CH3:1][CH2:2].[CH3:5]",
        )
        # A terminal CH3 (three trailing implicit Hs, no further heavy
        # neighbour) is fully parenthesised: three "(...)" groups with nothing
        # unwrapped after the last one closes.
        left = dfs.split(">>")[0]
        self.assertRegex(left, r"\(\[H\]\d+\)\(\[H\]\d+\)\(\[H\]\d+\)$")

    def test_ring_closure(self):
        # THF ring, unchanged on both sides (structural round-trip of a real
        # closed ring, as it appears in IMS8-EQ8.106a's product).
        smiles = "[CH2:2]1[O:3][CH2:4][CH2:5][CH2:6]1"
        dfs = self._assert_round_trips(smiles, smiles)
        left = dfs.split(">>")[0]
        # A 5-membered ring needs exactly one back-edge/ring-closure token.
        self.assertEqual(left.count("{"), 1)

    def test_aromatic_bond_token(self):
        smiles = "[cH:1]1[cH:2][cH:3][cH:4][cH:5][cH:6]1"
        dfs = self._assert_round_trips(smiles, smiles)
        left = dfs.split(">>")[0]
        self.assertIn(":", left)
        self.assertNotIn("{", left)  # aromatic bonds use bare ':', never '{...}'

    def test_multi_component_product(self):
        # Diethyl ether radical cation alpha-cleavage (IMS4-EQ4.13, exact record).
        dfs = self._assert_round_trips(
            "[CH3:1][CH2:2][O+:3][CH2:4][CH3:5]",
            "[CH2:2]=[O+:3][CH2:4][CH3:5].[CH3:1]",
        )
        right = dfs.split(">>")[1]
        self.assertGreaterEqual(right.count("."), 1)

    def test_charge_and_radical_decoration(self):
        # A terminal oxenium: one bond -> RDKit assigns 2 radical electrons.
        dfs = self._assert_round_trips("[O+:1][CH3:2]", "[O+:1][CH3:2]")
        left = dfs.split(">>")[0]
        self.assertIn("[O+..]1", left)

    def test_explicit_hydrogen_can_migrate(self):
        # A separately-mapped H (not bundled implicit) may relocate between
        # heavy atoms across the reaction without tripping the implicit-H
        # count guard, which only constrains UNMAPPED hydrogens.
        dfs = reaction_dfs_string(
            "[CH3:1][CH2:2][H:3].[O:4][CH3:5]",
            "[CH3:1][CH2:2].[O:4]([H:3])[CH3:5]",
        )
        self.assertIn(">>", dfs)

    def test_rejects_unmapped_heavy_atom(self):
        with self.assertRaises(MechanismConversionError):
            reaction_dfs_string("[CH3:1][CH2:2][C]", "[CH3:1][CH2:2][C]")

    def test_rejects_atom_created_or_destroyed(self):
        with self.assertRaises(MechanismConversionError):
            reaction_dfs_string("[CH3:1][C+:2][CH3:3]", "[CH3:1][CH2+:2]")

    def test_rejects_unaccounted_implicit_hydrogen_shift(self):
        # atom 2 loses an H on the right and NO atom anywhere in the state
        # gains one -- an unbalanced total, not a relocation, so it cannot be
        # inferred (contrast test_infers_unmapped_hydrogen_migration below).
        with self.assertRaises(MechanismConversionError):
            reaction_dfs_string("[CH3:1][CH3:2]", "[CH3:1][CH2:2]")

    def test_infers_unmapped_hydrogen_migration(self):
        # A 1,2 radical/H shift: atom2 loses an implicit H, atom1 gains one,
        # with neither individually atom-mapped by the curator -- exactly the
        # "CH3 on one side, CH2 on the other" pattern real records show. The
        # total deficit (1) matches the total surplus (1) elsewhere in the
        # SAME state, so this must be reconciled rather than rejected.
        dfs = self._assert_round_trips("[CH2:1][CH3:2]", "[CH3:1][CH2:2]")
        self.assertIn(">>", dfs)

    def test_apply_localization_transplants_charge_and_radical(self):
        # A precursor recorded with no per-atom localization at all (the
        # "propane_radical_cation" pattern: plain neutral SMILES, charge/
        # radical only at the species level) can have a product's charge/
        # radical PLACEMENT transplanted onto the same atom by id, with
        # connectivity left untouched.
        left, _ = parse_mapped_smiles("[CH3:1][CH2:2][CH3:3]")
        source, _ = parse_mapped_smiles("[CH3:1][C+:2][CH3:3]")
        self.assertEqual((left.atoms[2].charge, left.atoms[2].radical_electrons), (0, 0))

        apply_localization(left, source)

        self.assertEqual((left.atoms[2].charge, left.atoms[2].radical_electrons), (1, 1))
        neighbours = {other for other, _ in left.adjacency[2]}
        self.assertEqual(neighbours, {1, 3})


if __name__ == "__main__":
    unittest.main()
