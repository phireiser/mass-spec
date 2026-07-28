"""
Deterministic electron-move <-> bond-order bookkeeping check ("do the arrows add up?").

``MechanismRecord.validate_chemistry()`` proves a step conserves atoms/charge/electrons and
that arrow endpoints refer to real atoms/bonds -- but it does NOT check that the drawn arrows
actually *produce* the product. A record can be perfectly mass-balanced while its
``electron_moves`` omit an arrow (a classic failure: encoding radical-site alpha-cleavage with
two fishhooks and leaving out the sigma->pi bond-forming arc).

This module closes that gap. Each ElectronMove carries ``electron_count`` electrons from a
source to a target, so:

    delta(bond electrons) = electrons arriving - electrons leaving
    delta(bond order)     = delta(bond electrons) / 2

We recompute the observed per-bond order change and the observed per-atom radical change from
the atom-mapped SMILES of the two states, then require the moves to predict exactly those
changes. An omitted fishhook shows up immediately as a half-order shortfall.

Delocalisation caveat: for bonds RDKit reports as aromatic (order 1.5) integer electron
bookkeeping is ill-defined, so those are reported as warnings rather than hard failures.
"""

from __future__ import annotations

from rdkit import Chem

from schema import ElectronMove, LocationType, MechanismRecord, Species


def _key(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def _state_topology(
    species: list[Species],
) -> tuple[dict[tuple[int, int], float], dict[int, int], set[tuple[int, int]]]:
    """Return {bond -> order}, {atom_map -> radical electrons}, and the aromatic bonds."""
    bonds: dict[tuple[int, int], float] = {}
    radicals: dict[int, int] = {}
    aromatic: set[tuple[int, int]] = set()

    for item in species:
        mol = Chem.MolFromSmiles(item.mapped_smiles)
        if mol is None:
            raise ValueError(
                f"RDKit could not parse mapped SMILES: {item.mapped_smiles}"
            )
        local: dict[int, int] = {}
        for atom in mol.GetAtoms():
            amap = atom.GetAtomMapNum()
            if amap > 0:
                local[atom.GetIdx()] = amap
                radicals[amap] = atom.GetNumRadicalElectrons()
        for bond in mol.GetBonds():
            a = local.get(bond.GetBeginAtomIdx())
            b = local.get(bond.GetEndAtomIdx())
            if a is None or b is None:
                continue
            k = _key(a, b)
            bonds[k] = bond.GetBondTypeAsDouble()
            if bond.GetIsAromatic():
                aromatic.add(k)

    return bonds, radicals, aromatic


def _predicted_deltas(
    moves: list[ElectronMove],
) -> tuple[dict[tuple[int, int], int], dict[int, int], list[str]]:
    """Electrons added(+)/removed(-) per bond and per atom, from the arrows alone."""
    bond_delta: dict[tuple[int, int], int] = {}
    atom_delta: dict[int, int] = {}
    notes: list[str] = []

    def apply(loc, sign: int, n: int) -> None:
        maps = loc.atom_maps
        if loc.type is LocationType.EXTERNAL:
            # sign>0 means electrons ARRIVE at this location; arriving at "external"
            # means they leave the system (e.g. the EI ionization hole).
            notes.append(
                f"{'target' if sign > 0 else 'source'} is EXTERNAL "
                f"({n} e- {'out of' if sign > 0 else 'into'} the system)"
            )
            return
        if loc.type is LocationType.BOND:
            bond_delta[_key(*maps)] = bond_delta.get(_key(*maps), 0) + sign * n
        else:  # atom, lone_pair, radical_orbital -> non-bonding population
            atom_delta[maps[0]] = atom_delta.get(maps[0], 0) + sign * n

    for move in moves:
        apply(move.source, -1, move.electron_count)
        apply(move.target, +1, move.electron_count)

    return bond_delta, atom_delta, notes


def check_step_arrows(record: MechanismRecord, step) -> list[str]:
    """Return a list of problems; empty means the arrows exactly explain the step."""
    before = record.species_in_state(step.from_state)
    after = record.species_in_state(step.to_state)

    bonds_b, rad_b, arom_b = _state_topology(before)
    bonds_a, rad_a, arom_a = _state_topology(after)
    aromatic = arom_b | arom_a

    pred_bond, pred_atom, notes = _predicted_deltas(step.electron_moves)

    problems: list[str] = []
    soft: list[str] = []

    # --- bonds: observed order change must equal predicted electrons / 2 ---
    for k in set(bonds_b) | set(bonds_a) | set(pred_bond):
        observed_order = bonds_a.get(k, 0.0) - bonds_b.get(k, 0.0)
        observed_e = observed_order * 2
        predicted_e = pred_bond.get(k, 0)
        if abs(observed_e - predicted_e) < 1e-6:
            continue
        msg = (
            f"bond {k}: observed change {observed_order:+g} bond order "
            f"({observed_e:+g} e-) but arrows account for {predicted_e:+d} e-"
        )
        if k in aromatic:
            soft.append(f"(aromatic/delocalised) {msg}")
        else:
            problems.append(msg)

    # --- atoms: non-bonding (radical) population change ---
    # Sound for single-electron (fishhook) bookkeeping; a +/-2 change may be a lone
    # pair rather than two radicals, so only flag when the parity disagrees.
    for amap in set(rad_b) | set(rad_a) | set(pred_atom):
        observed = rad_a.get(amap, 0) - rad_b.get(amap, 0)
        predicted = pred_atom.get(amap, 0)
        if observed == predicted:
            continue
        if abs(predicted) % 2 == abs(observed) % 2 and abs(predicted - observed) == 2:
            soft.append(
                f"atom {amap}: radical change {observed:+d} vs arrows {predicted:+d} "
                "(consistent with a lone pair rather than radicals)"
            )
        else:
            problems.append(
                f"atom {amap}: observed radical change {observed:+d} but arrows "
                f"account for {predicted:+d} non-bonding e-"
            )

    return problems + [f"(soft) {s}" for s in soft] + [f"(soft) {n}" for n in notes]


def check_record_arrows(record: MechanismRecord) -> dict[str, list[str]]:
    """Map step_id -> problems for every step of a record."""
    return {
        step.step_id: check_step_arrows(record, step) for step in record.steps
    }
