"""
Mechanism-record curation for McLafferty *Interpretation of Mass Spectra* (4th ed.).

A richer, provenance-tracked representation of the book's EI fragmentation reactions,
parallel to (and cross-linked by book equation ID with) the MØD ``Rule.fromDFS`` rules in
``src/data_generation/rules/``. See ``docs``/the plan for the extraction pipeline.
"""

from .schema import (
    AssignmentStatus,
    CurationRecord,
    ElectronLocation,
    ElectronMove,
    ElementaryStep,
    EnergyValue,
    EvidenceLink,
    EvidenceTarget,
    LocationType,
    MechanismRecord,
    MechanismState,
    MSContext,
    PeakAssignment,
    Polarity,
    Species,
    SpeciesRole,
    SourceLocator,
    SourceReference,
    SourceType,
    StepSemantics,
    ValidationReport,
    build_example,
)

__all__ = [
    "AssignmentStatus",
    "CurationRecord",
    "ElectronLocation",
    "ElectronMove",
    "ElementaryStep",
    "EnergyValue",
    "EvidenceLink",
    "EvidenceTarget",
    "LocationType",
    "MechanismRecord",
    "MechanismState",
    "MSContext",
    "PeakAssignment",
    "Polarity",
    "Species",
    "SpeciesRole",
    "SourceLocator",
    "SourceReference",
    "SourceType",
    "StepSemantics",
    "ValidationReport",
    "build_example",
]
