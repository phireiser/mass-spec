"""
Utilities for the fragmenter project
"""

# Core graph operations
from .basic_mod import (
    get_parents,
    filter_ancestors_out,
    get_out_edges_by_vertex_id,
    get_rule_ids_by_edge_id,
    get_fragment_ids_by_edge_id,
)

# Constraint and rule utilities
from .constrain import (
    apply_constraints,
    get_constraint,
    all_occuring,
    add_constraints,
    convert_to_moel_rule,
    label_constraints_gml,
    label_constraints_dfs,
    split_rule_dfs,
    flatten_list,
    ALL_ATOMS,
    ALK_NES_LABELS,
)

# Persistence
from .file import (
    dump_derivation_graph,
    load_derivation_graph,
)

# Spectrum I/O
from .spect_jdx import get_spectra_from_local_jdx
from .spect_mol import (
    get_parent_rules_for_graph,
    get_spectra_from_mod_derivation_graph,
)
from .spect_pubchem import get_spectra_from_pubchem

# Term transfers (mod integration)
from .term_transfers import (
    term_from_graph,
    term_from_rule,
    graph_from_term,
    rule_from_term,
)

# Printing and visualization
from .printing import (
    print_rules,
    print_graphs,
)

# NetworkX integration
from .net_x import (
    mod_derivation_graph_2_nx,
)

# Comparison utilities
from .compareability import ComparableVertex, ComparableVertexList

# Description utilities
from .describe import (
    spectrum_statistic,
    rule_usage,
    overlap_coefficient,
    dice_coefficient,
)

# Rule extensions / traversal
from .rule_extention import transfer_positions_of_generalization_extention
from .mapping import get_rule_2_molecule_map
from .traversal import (
    vertex_by_id,
    mol_neighbors,
    mol_cleaned_label,
    collect_bfs,
    get_edge_between,
    saturated_path,
)

from .diag import (
    enable_subgroup_diag,
)

__all__ = [
    # Core graph operations
    "get_parents",
    "filter_ancestors_out",
    "get_out_edges_by_vertex_id",
    "get_rule_ids_by_edge_id",
    "get_fragment_ids_by_edge_id",
    # Constraints
    "apply_constraints",
    "get_constraint",
    "all_occuring",
    "add_constraints",
    "convert_to_moel_rule",
    "label_constraints_gml",
    "label_constraints_dfs",
    "split_rule_dfs",
    "flatten_list",
    "ALL_ATOMS",
    "ALK_NES_LABELS",
    "ALKALENES_LABELS",
    # Persistence
    "dump_derivation_graph",
    "load_derivation_graph",
    # Spectrum I/O
    "get_spectra_from_local_jdx",
    "get_parent_rules_for_graph",
    "get_spectra_from_mod_derivation_graph",
    "get_spectra_from_pubchem",
    # Term transfers
    "term_from_graph",
    "term_from_rule",
    "graph_from_term",
    "rule_from_term",
    # Printing
    "print_rules",
    "print_graphs",
    # NetworkX
    "derivation_graph_to_networkx",
    "filter_networkx",
    # Comparison
    "enable_subgroup_diag",
    # Description
    "describe_rule",
    "describe_graph",
    # Rule extensions
    "extend_rule",
]
