from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from rdkit import Chem


class StrictModel(BaseModel):
    """Base model that rejects unknown fields and validates assignments."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class SpeciesRole(str, Enum):
    PRECURSOR_ION = "precursor_ion"
    INTERMEDIATE = "intermediate"
    PRODUCT_ION = "product_ion"
    NEUTRAL_LOSS = "neutral_loss"
    NEUTRAL_RADICAL = "neutral_radical"
    REAGENT = "reagent"
    SPECTATOR = "spectator"


class LocationType(str, Enum):
    ATOM = "atom"
    BOND = "bond"
    LONE_PAIR = "lone_pair"
    RADICAL_ORBITAL = "radical_orbital"
    EXTERNAL = "external"


class StepSemantics(str, Enum):
    PHYSICAL_ELEMENTARY_STEP = "physical_elementary_step"
    FORMAL_ARROW_STEP = "formal_arrow_step"
    NET_FRAGMENTATION = "net_fragmentation"
    RESONANCE_INTERCONVERSION = "resonance_interconversion"


class EvidenceTarget(str, Enum):
    MECHANISM = "mechanism"
    STEP = "step"
    SPECIES = "species"
    PEAK_ASSIGNMENT = "peak_assignment"


class SupportType(str, Enum):
    EXPLICITLY_REPORTED = "explicitly_reported"
    AUTHOR_PROPOSED = "author_proposed"
    TEXTBOOK_PROPOSED = "textbook_proposed"
    EXPERIMENTALLY_SUPPORTED = "experimentally_supported"
    COMPUTATIONALLY_SUPPORTED = "computationally_supported"
    CURATOR_INFERRED = "curator_inferred"
    CONTRADICTED = "contradicted"


class AssignmentStatus(str, Enum):
    OBSERVED = "observed"
    PROPOSED = "proposed"
    INFERRED = "inferred"
    REJECTED = "rejected"


class SourceType(str, Enum):
    JOURNAL_ARTICLE = "journal_article"
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    DATABASE = "database"
    THESIS = "thesis"
    SOFTWARE_OUTPUT = "software_output"
    EXPERT_ANNOTATION = "expert_annotation"
    OTHER = "other"


class Polarity(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class Species(StrictModel):
    """
    A chemically relevant species.

    The mapped SMILES defines atom/bond topology and atom-map identities.
    The separate charge and radical_electrons fields are authoritative for
    the electronic state.
    """

    species_id: str = Field(min_length=1)
    mapped_smiles: str = Field(min_length=1)
    role: SpeciesRole
    charge: int
    radical_electrons: int = Field(ge=0)
    spin_multiplicity: int | None = Field(default=None, ge=1)
    detected: bool = False


class ElectronLocation(StrictModel):
    """Source or target of a curved-arrow/fishhook electron move."""

    type: LocationType
    atom_maps: tuple[int, ...] = ()

    @model_validator(mode="after")
    def validate_arity(self) -> "ElectronLocation":
        expected = {
            LocationType.ATOM: 1,
            LocationType.BOND: 2,
            LocationType.LONE_PAIR: 1,
            LocationType.RADICAL_ORBITAL: 1,
            LocationType.EXTERNAL: 0,
        }[self.type]

        if len(self.atom_maps) != expected:
            raise ValueError(
                f"{self.type.value} location requires {expected} atom-map "
                f"number(s), got {len(self.atom_maps)}"
            )

        if any(number <= 0 for number in self.atom_maps):
            raise ValueError("Atom-map numbers must be positive integers")

        if len(set(self.atom_maps)) != len(self.atom_maps):
            raise ValueError(
                "An electron location cannot repeat an atom-map number"
            )

        return self


class ElectronMove(StrictModel):
    source: ElectronLocation
    target: ElectronLocation

    # 1 = fishhook; 2 = full curved arrow.
    electron_count: Literal[1, 2]


class MechanismState(StrictModel):
    """A node in the mechanism DAG."""

    state_id: str = Field(min_length=1)
    species_ids: list[str] = Field(min_length=1)


class ElementaryStep(StrictModel):
    """A directed edge in the mechanism DAG."""

    step_id: str = Field(min_length=1)
    from_state: str
    to_state: str
    step_class: str = Field(min_length=1)
    semantics: StepSemantics = StepSemantics.PHYSICAL_ELEMENTARY_STEP
    electron_moves: list[ElectronMove] = Field(min_length=1)

    # Optional import/export field. If omitted, it is derived from the states.
    reaction_smirks: str | None = None
    reversible: bool = False


class SourceLocator(StrictModel):
    page: int | None = Field(default=None, ge=1)
    equation: str | None = None
    figure: str | None = None
    panel: str | None = None
    section: str | None = None


class SourceReference(StrictModel):
    source_id: str = Field(min_length=1)
    source_type: SourceType
    citation: str = Field(min_length=1)
    doi: str | None = None
    isbn: str | None = None
    url: str | None = None


class EvidenceLink(StrictModel):
    """
    Links a source to a specific claim instead of attaching one coarse
    reference string to the complete mechanism.
    """

    evidence_id: str = Field(min_length=1)
    source_id: str
    target_type: EvidenceTarget
    target_id: str
    support_type: SupportType
    locator: SourceLocator
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    curator_note: str | None = None


class EnergyValue(StrictModel):
    value: float = Field(ge=0)
    unit: Literal["eV", "NCE", "kJ/mol"]


class MSContext(StrictModel):
    ionization_method: str
    polarity: Polarity
    adduct: str | None = None
    activation_method: str | None = None
    collision_energy: EnergyValue | None = None
    electron_energy_ev: float | None = Field(default=None, ge=0)
    precursor_mz: float | None = Field(default=None, gt=0)
    precursor_charge: int | None = None
    instrument_type: str | None = None


class PeakAssignment(StrictModel):
    peak_id: str = Field(min_length=1)
    species_id: str
    step_id: str | None = None
    observed_mz: float = Field(gt=0)
    relative_intensity: float | None = Field(default=None, ge=0.0, le=1.0)
    hydrogen_shift: int = 0
    isotope_offset: int = 0
    status: AssignmentStatus = AssignmentStatus.PROPOSED
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class CurationRecord(StrictModel):
    schema_version: str = "1.0.0"
    record_version: int = Field(default=1, ge=1)
    extraction_method: str
    review_status: Literal[
        "unreviewed",
        "machine_checked",
        "expert_reviewed",
        "verified_against_source",
    ] = "unreviewed"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ValidationReport(StrictModel):
    step_id: str
    atoms_balanced: bool
    charge_balanced: bool
    total_electrons_balanced: bool
    atom_maps_complete_and_unique: bool
    radical_parity_consistent_before: bool
    radical_parity_consistent_after: bool
    reactant_elements: dict[str, int]
    product_elements: dict[str, int]
    reactant_charge: int
    product_charge: int
    reactant_total_electrons: int
    product_total_electrons: int
    warnings: list[str] = Field(default_factory=list)


def _parse_mapped_smiles(smiles: str) -> Chem.Mol:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse mapped SMILES: {smiles}")
    return mol


def _element_counts_and_nuclear_charge(
    mol: Chem.Mol,
) -> tuple[Counter[str], int]:
    """
    Return elemental composition and total nuclear charge.

    Implicit/bracket hydrogens are counted through GetTotalNumHs().
    Separate [H] atoms are counted as ordinary atoms.
    """

    counts: Counter[str] = Counter()
    nuclear_charge = 0

    for atom in mol.GetAtoms():
        symbol = atom.GetSymbol()
        isotope = atom.GetIsotope()
        key = f"{isotope}{symbol}" if isotope else symbol

        counts[key] += 1
        nuclear_charge += atom.GetAtomicNum()

        attached_h = atom.GetTotalNumHs(includeNeighbors=False)
        if symbol != "H" and attached_h:
            counts["H"] += attached_h
            nuclear_charge += attached_h

    return counts, nuclear_charge


def _state_topology(
    species: list[Species],
) -> tuple[set[int], set[tuple[int, int]], list[str]]:
    """Collect atom-map IDs and mapped bonds for one mechanism state."""

    atom_maps: set[int] = set()
    bonds: set[tuple[int, int]] = set()
    warnings: list[str] = []

    for item in species:
        mol = _parse_mapped_smiles(item.mapped_smiles)
        local_maps: dict[int, int] = {}

        for atom in mol.GetAtoms():
            atom_map = atom.GetAtomMapNum()

            if atom_map <= 0:
                warnings.append(
                    f"{item.species_id}: atom {atom.GetIdx()} has no "
                    "atom-map number"
                )
                continue

            if atom_map in atom_maps:
                warnings.append(
                    f"{item.species_id}: atom-map {atom_map} is duplicated "
                    "in the state"
                )

            atom_maps.add(atom_map)
            local_maps[atom.GetIdx()] = atom_map

        for bond in mol.GetBonds():
            begin = local_maps.get(bond.GetBeginAtomIdx())
            end = local_maps.get(bond.GetEndAtomIdx())

            if begin is not None and end is not None:
                bonds.add(tuple(sorted((begin, end))))

    return atom_maps, bonds, warnings


class MechanismRecord(StrictModel):
    """
    Minimal unified PMechDB/RMechDB-style mechanism record with:
    - atom-mapped species,
    - one- and two-electron moves,
    - a mechanism DAG,
    - MS metadata and peak assignments,
    - structured provenance,
    - curation/version data,
    - basic chemistry validation.
    """

    mechanism_id: str = Field(min_length=1)
    species: list[Species] = Field(min_length=1)
    states: list[MechanismState] = Field(min_length=2)
    steps: list[ElementaryStep] = Field(min_length=1)
    sources: list[SourceReference] = Field(min_length=1)
    evidence: list[EvidenceLink] = Field(min_length=1)
    ms_context: MSContext
    peak_assignments: list[PeakAssignment] = Field(default_factory=list)
    curation: CurationRecord

    @model_validator(mode="after")
    def validate_references_and_dag(self) -> "MechanismRecord":
        def unique(values: list[str], label: str) -> set[str]:
            if len(values) != len(set(values)):
                raise ValueError(f"Duplicate {label} IDs are not allowed")
            return set(values)

        species_ids = unique(
            [item.species_id for item in self.species], "species"
        )
        state_ids = unique(
            [item.state_id for item in self.states], "state"
        )
        step_ids = unique(
            [item.step_id for item in self.steps], "step"
        )
        source_ids = unique(
            [item.source_id for item in self.sources], "source"
        )
        unique(
            [item.evidence_id for item in self.evidence], "evidence"
        )
        peak_ids = unique(
            [item.peak_id for item in self.peak_assignments],
            "peak assignment",
        )

        for state in self.states:
            missing = set(state.species_ids) - species_ids
            if missing:
                raise ValueError(
                    f"State {state.state_id} references unknown species: "
                    f"{sorted(missing)}"
                )

            if len(state.species_ids) != len(set(state.species_ids)):
                raise ValueError(
                    f"State {state.state_id} repeats one or more species IDs"
                )

        # Validate state references and detect cycles.
        adjacency: dict[str, list[str]] = {
            state_id: [] for state_id in state_ids
        }

        for step in self.steps:
            if (
                step.from_state not in state_ids
                or step.to_state not in state_ids
            ):
                raise ValueError(
                    f"Step {step.step_id} references an unknown state"
                )

            if step.from_state == step.to_state:
                raise ValueError(
                    f"Step {step.step_id} cannot begin and end at the "
                    "same state"
                )

            adjacency[step.from_state].append(step.to_state)

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise ValueError("Mechanism state graph must be acyclic")

            if node in visited:
                return

            visiting.add(node)
            for child in adjacency[node]:
                visit(child)
            visiting.remove(node)
            visited.add(node)

        for state_id in state_ids:
            visit(state_id)

        valid_targets = {
            EvidenceTarget.MECHANISM: {self.mechanism_id},
            EvidenceTarget.STEP: step_ids,
            EvidenceTarget.SPECIES: species_ids,
            EvidenceTarget.PEAK_ASSIGNMENT: peak_ids,
        }

        for link in self.evidence:
            if link.source_id not in source_ids:
                raise ValueError(
                    f"Evidence {link.evidence_id} references unknown source "
                    f"{link.source_id}"
                )

            if link.target_id not in valid_targets[link.target_type]:
                raise ValueError(
                    f"Evidence {link.evidence_id} references unknown "
                    f"{link.target_type.value} target {link.target_id}"
                )

        for assignment in self.peak_assignments:
            if assignment.species_id not in species_ids:
                raise ValueError(
                    f"Peak {assignment.peak_id} references unknown species"
                )

            if (
                assignment.step_id is not None
                and assignment.step_id not in step_ids
            ):
                raise ValueError(
                    f"Peak {assignment.peak_id} references unknown step"
                )

        return self

    def _species_index(self) -> dict[str, Species]:
        return {item.species_id: item for item in self.species}

    def _state_index(self) -> dict[str, MechanismState]:
        return {item.state_id: item for item in self.states}

    def species_in_state(self, state_id: str) -> list[Species]:
        species_index = self._species_index()
        state = self._state_index()[state_id]
        return [
            species_index[species_id] for species_id in state.species_ids
        ]

    def mapped_reaction_smirks(self, step_id: str) -> str:
        """
        Export one concrete atom-mapped step in P/RMechDB-style notation.

        This is a concrete mapped reaction instance. A generalized reaction
        rule would additionally require SMARTS query constraints.
        """

        try:
            step = next(
                item for item in self.steps if item.step_id == step_id
            )
        except StopIteration as exc:
            raise KeyError(f"Unknown step ID: {step_id}") from exc

        left = ".".join(
            item.mapped_smiles
            for item in self.species_in_state(step.from_state)
        )
        right = ".".join(
            item.mapped_smiles
            for item in self.species_in_state(step.to_state)
        )

        return f"{left}>>{right}"

    def validate_chemistry(self) -> list[ValidationReport]:
        """
        Perform basic machine checks for every elementary step.

        These checks establish atom, charge and total-electron conservation
        and verify that arrow endpoints refer to mapped atoms/bonds. They do
        not prove that the proposed mechanism is physically correct.
        """

        reports: list[ValidationReport] = []

        for step in self.steps:
            before = self.species_in_state(step.from_state)
            after = self.species_in_state(step.to_state)

            before_counts: Counter[str] = Counter()
            after_counts: Counter[str] = Counter()
            before_nuclear_charge = 0
            after_nuclear_charge = 0

            for item in before:
                counts, nuclear_charge = (
                    _element_counts_and_nuclear_charge(
                        _parse_mapped_smiles(item.mapped_smiles)
                    )
                )
                before_counts.update(counts)
                before_nuclear_charge += nuclear_charge

            for item in after:
                counts, nuclear_charge = (
                    _element_counts_and_nuclear_charge(
                        _parse_mapped_smiles(item.mapped_smiles)
                    )
                )
                after_counts.update(counts)
                after_nuclear_charge += nuclear_charge

            before_charge = sum(item.charge for item in before)
            after_charge = sum(item.charge for item in after)

            before_electrons = before_nuclear_charge - before_charge
            after_electrons = after_nuclear_charge - after_charge

            before_radicals = sum(
                item.radical_electrons for item in before
            )
            after_radicals = sum(
                item.radical_electrons for item in after
            )

            before_maps, before_bonds, before_warnings = _state_topology(
                before
            )
            after_maps, after_bonds, after_warnings = _state_topology(
                after
            )

            warnings = before_warnings + after_warnings

            for index, move in enumerate(
                step.electron_moves, start=1
            ):
                source_maps = set(move.source.atom_maps)
                target_maps = set(move.target.atom_maps)

                if move.source.type is not LocationType.EXTERNAL:
                    if not source_maps.issubset(before_maps):
                        warnings.append(
                            f"electron move {index}: source atom maps are "
                            f"not all present in state {step.from_state}"
                        )

                    if (
                        move.source.type is LocationType.BOND
                        and tuple(sorted(move.source.atom_maps))
                        not in before_bonds
                    ):
                        warnings.append(
                            f"electron move {index}: source bond "
                            f"{move.source.atom_maps} does not exist before "
                            "the step"
                        )

                if move.target.type is not LocationType.EXTERNAL:
                    if not target_maps.issubset(after_maps):
                        warnings.append(
                            f"electron move {index}: target atom maps are "
                            f"not all present in state {step.to_state}"
                        )

                    if (
                        move.target.type is LocationType.BOND
                        and tuple(sorted(move.target.atom_maps))
                        not in after_bonds
                    ):
                        warnings.append(
                            f"electron move {index}: target bond "
                            f"{move.target.atom_maps} does not exist after "
                            "the step"
                        )

            maps_ok = not before_warnings and not after_warnings

            if step.reaction_smirks is not None:
                derived = self.mapped_reaction_smirks(step.step_id)
                if step.reaction_smirks != derived:
                    warnings.append(
                        "stored reaction_smirks differs from the reaction "
                        "derived from the referenced states"
                    )

            reports.append(
                ValidationReport(
                    step_id=step.step_id,
                    atoms_balanced=before_counts == after_counts,
                    charge_balanced=before_charge == after_charge,
                    total_electrons_balanced=(
                        before_electrons == after_electrons
                    ),
                    atom_maps_complete_and_unique=maps_ok,
                    radical_parity_consistent_before=(
                        before_radicals % 2 == before_electrons % 2
                    ),
                    radical_parity_consistent_after=(
                        after_radicals % 2 == after_electrons % 2
                    ),
                    reactant_elements=dict(
                        sorted(before_counts.items())
                    ),
                    product_elements=dict(
                        sorted(after_counts.items())
                    ),
                    reactant_charge=before_charge,
                    product_charge=after_charge,
                    reactant_total_electrons=before_electrons,
                    product_total_electrons=after_electrons,
                    warnings=warnings,
                )
            )

        return reports

    def to_json_file(self, path: str | Path) -> None:
        Path(path).write_text(
            self.model_dump_json(indent=2),
            encoding="utf-8",
        )

    @classmethod
    def from_json_file(
        cls,
        path: str | Path,
    ) -> "MechanismRecord":
        return cls.model_validate_json(
            Path(path).read_text(encoding="utf-8")
        )

    @classmethod
    def write_json_schema(cls, path: str | Path) -> None:
        import json

        Path(path).write_text(
            json.dumps(cls.model_json_schema(), indent=2),
            encoding="utf-8",
        )


def build_example() -> MechanismRecord:
    """
    Minimal acetone radical-cation alpha-cleavage example:

        acetone radical cation -> acylium ion + methyl radical
    """

    return MechanismRecord(
        mechanism_id="MSMECH-0001",
        species=[
            Species(
                species_id="acetone_radical_cation",
                mapped_smiles="[CH3:1][C:2](=[O:3])[CH3:4]",
                role=SpeciesRole.PRECURSOR_ION,
                charge=1,
                radical_electrons=1,
                spin_multiplicity=2,
            ),
            Species(
                species_id="acylium_ion",
                mapped_smiles="[CH3:1][C:2]#[O+:3]",
                role=SpeciesRole.PRODUCT_ION,
                charge=1,
                radical_electrons=0,
                spin_multiplicity=1,
                detected=True,
            ),
            Species(
                species_id="methyl_radical",
                mapped_smiles="[CH3:4]",
                role=SpeciesRole.NEUTRAL_RADICAL,
                charge=0,
                radical_electrons=1,
                spin_multiplicity=2,
            ),
        ],
        states=[
            MechanismState(
                state_id="state_precursor",
                species_ids=["acetone_radical_cation"],
            ),
            MechanismState(
                state_id="state_products",
                species_ids=["acylium_ion", "methyl_radical"],
            ),
        ],
        steps=[
            ElementaryStep(
                step_id="step_alpha_cleavage",
                from_state="state_precursor",
                to_state="state_products",
                step_class="alpha_cleavage",
                semantics=StepSemantics.FORMAL_ARROW_STEP,
                electron_moves=[
                    ElectronMove(
                        source=ElectronLocation(
                            type=LocationType.BOND,
                            atom_maps=(2, 4),
                        ),
                        target=ElectronLocation(
                            type=LocationType.ATOM,
                            atom_maps=(4,),
                        ),
                        electron_count=1,
                    ),
                    ElectronMove(
                        source=ElectronLocation(
                            type=LocationType.BOND,
                            atom_maps=(2, 4),
                        ),
                        target=ElectronLocation(
                            type=LocationType.BOND,
                            atom_maps=(2, 3),
                        ),
                        electron_count=1,
                    ),
                ],
            )
        ],
        sources=[
            SourceReference(
                source_id="source_textbook",
                source_type=SourceType.BOOK,
                citation="Replace with the complete textbook citation",
            )
        ],
        evidence=[
            EvidenceLink(
                evidence_id="evidence_step",
                source_id="source_textbook",
                target_type=EvidenceTarget.STEP,
                target_id="step_alpha_cleavage",
                support_type=SupportType.TEXTBOOK_PROPOSED,
                locator=SourceLocator(page=42, equation="4.13"),
                confidence=0.8,
                curator_note=(
                    "Manually transcribed from the reaction scheme."
                ),
            )
        ],
        ms_context=MSContext(
            ionization_method="EI",
            polarity=Polarity.POSITIVE,
            adduct="[M]+•",
            activation_method="electron ionization",
            electron_energy_ev=70.0,
            precursor_mz=58.0419,
            precursor_charge=1,
            instrument_type="unspecified",
        ),
        peak_assignments=[
            PeakAssignment(
                peak_id="peak_43",
                species_id="acylium_ion",
                step_id="step_alpha_cleavage",
                observed_mz=43.0184,
                relative_intensity=1.0,
                status=AssignmentStatus.PROPOSED,
                confidence=0.9,
            )
        ],
        curation=CurationRecord(
            extraction_method="manual_transcription",
            review_status="machine_checked",
        ),
    )


if __name__ == "__main__":
    mechanism = build_example()

    print(
        mechanism.mapped_reaction_smirks(
            "step_alpha_cleavage"
        )
    )

    for report in mechanism.validate_chemistry():
        print(report.model_dump_json(indent=2))

    # Write beside the canonical committed copies rather than into the CWD.
    from src.project_paths import shared_path

    mechanism.to_json_file(str(shared_path("MECHANISMS_DIR_REL", "example_mechanism.json")))
    MechanismRecord.write_json_schema(
        str(shared_path("MECHANISMS_DIR_REL", "mechanism_schema.json"))
    )
