"""
GENERATED FILE -- do not hand-edit.

Compiled from the curated mechanism corpus in data/mechanisms/records by:

    python -m src.data_generation.mechanisms.write_generated_rules

Each rule is the FULL, CONCRETE reactant/product graph from one curated
book example (not a generalized template like src/data_generation/rules --
see src/data_generation/mechanisms/__init__.py for what that means in
practice). A rule tagged 'auto-localized precursor' or 'N hydrogen
migration(s) inferred' below had its reactant reconstructed from the
product/curated data rather than read verbatim off the record's own
reactant SMILES -- see build_rules.py's iter_conversions for exactly how
and why that reconstruction is safe. Regenerate after editing
data/mechanisms/records/*.json or src/data_generation/mechanisms/
dfs_writer.py; do not edit by hand, changes will be silently overwritten
by the next regeneration.
"""
import mod

# IMS4-EQ4.10:step_alpha_cleavage
IMS4_EQ4_10_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[O+]3([C]2([H]1000003)([H]1000004)([H]1000005))[C]4([H]1000006)([H]1000007)[C.]5([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[O+.]3[C]2([H]1000003)([H]1000004)([H]1000005).[C]4([H]1000006)([H]1000007){=}[C]5([H]1000008)([H]1000009)',
    name='IMS4-EQ4.10:step_alpha_cleavage',
)

# IMS4-EQ4.11:step_alpha_cleavage
IMS4_EQ4_11_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[C]4([H]1000003)([H]1000004)([H]1000005)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2({#}[O+]3)[C]4([H]1000003)([H]1000004)([H]1000005)',
    name='IMS4-EQ4.11:step_alpha_cleavage',
)

# IMS4-EQ4.12:step_alpha_cleavage
IMS4_EQ4_12_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C+]4([H]1000006)([H]1000007)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[C]3([H]1000005)[C+]4([H]1000006)([H]1000007)',
    name='IMS4-EQ4.12:step_alpha_cleavage',
)

# IMS4-EQ4.13:step_alpha_cleavage
IMS4_EQ4_13_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+.]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[O+]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS4-EQ4.13:step_alpha_cleavage',
)

# IMS4-EQ4.14:step_alpha_cleavage
IMS4_EQ4_14_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3({=}[O+.]4)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C]3({#}[O+]4)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)',
    name='IMS4-EQ4.14:step_alpha_cleavage',
)

# IMS4-EQ4.15a:step_allylic_alpha_cleavage
IMS4_EQ4_15a_step_allylic_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C+]4([H]1000006)([H]1000007)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[C]3([H]1000005)[C+]4([H]1000006)([H]1000007)',
    name='IMS4-EQ4.15a:step_allylic_alpha_cleavage',
)

# IMS4-EQ4.15b:step_benzylic_alpha_cleavage
IMS4_EQ4_15b_step_benzylic_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([C]4([H]1000005){=}[C]5([H]1000006)[C+]6([H]1000007)[C]7([H]1000008){=}[C]8({-}3)([H]1000009))>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[C]3([C]4([H]1000005){=}[C]5([H]1000006)[C+]6([H]1000007)[C]7([H]1000008){=}[C]8({-}3)([H]1000009))',
    name='IMS4-EQ4.15b:step_benzylic_alpha_cleavage',
)

# IMS4-EQ4.17a:step_alpha_cleavage_loss_propyl
IMS4_EQ4_17a_step_alpha_cleavage_loss_propyl = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006))([C]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)([H]1000011))([C]7([H]1000012)([H]1000013)([H]1000014))[O+.]8[H]1000015>>[C]1([C]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)([H]1000011))([C]7([H]1000012)([H]1000013)([H]1000014)){=}[O+]8[H]1000015.[C.]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006)',
    name='IMS4-EQ4.17a:step_alpha_cleavage_loss_propyl',
)

# IMS4-EQ4.17b:step_alpha_cleavage_loss_ethyl
IMS4_EQ4_17b_step_alpha_cleavage_loss_ethyl = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006))([C]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)([H]1000011))([C]7([H]1000012)([H]1000013)([H]1000014))[O+.]8[H]1000015>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006))([C]7([H]1000012)([H]1000013)([H]1000014)){=}[O+]8[H]1000015.[C.]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)([H]1000011)',
    name='IMS4-EQ4.17b:step_alpha_cleavage_loss_ethyl',
)

# IMS4-EQ4.17c:step_alpha_cleavage_loss_methyl
IMS4_EQ4_17c_step_alpha_cleavage_loss_methyl = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006))([C]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)([H]1000011))([C]7([H]1000012)([H]1000013)([H]1000014))[O+.]8[H]1000015>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006))([C]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)([H]1000011)){=}[O+]8[H]1000015.[C.]7([H]1000012)([H]1000013)([H]1000014)',
    name='IMS4-EQ4.17c:step_alpha_cleavage_loss_methyl',
)

# IMS4-EQ4.18:step_inductive_cleavage
IMS4_EQ4_18_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([O+.]2[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006))([H]1000000)([H]1000001)[C]6([H]1000007)([H]1000008)([H]1000009)>>[C+]1([H]1000000)([H]1000001)[C]6([H]1000007)([H]1000008)([H]1000009).[O.]2[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)([H]1000006)',
    name='IMS4-EQ4.18:step_inductive_cleavage',
)

# IMS4-EQ4.19:step_inductive_cleavage
IMS4_EQ4_19_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[C]4([H]1000003)([H]1000004)([H]1000005)>>[C+]1([H]1000000)([H]1000001)([H]1000002).[C.]2({=}[O]3)[C]4([H]1000003)([H]1000004)([H]1000005)',
    name='IMS4-EQ4.19:step_inductive_cleavage',
)

# IMS4-EQ4.20:step_inductive_cleavage
IMS4_EQ4_20_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([O+]2([H]1000002)([H]1000003))([H]1000000)([H]1000001)[C]4([H]1000004)([H]1000005)([H]1000006)>>[C+]1([H]1000000)([H]1000001)[C]4([H]1000004)([H]1000005)([H]1000006).[O]2([H]1000002)([H]1000003)',
    name='IMS4-EQ4.20:step_inductive_cleavage',
)

# IMS4-EQ4.21:step_inductive_cleavage
IMS4_EQ4_21_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[O+]2{=}[C]3([H]1000003)([H]1000004)>>[C+]1([H]1000000)([H]1000001)([H]1000002).[O]2{=}[C]3([H]1000003)([H]1000004)',
    name='IMS4-EQ4.21:step_inductive_cleavage',
)

# IMS4-EQ4.22:step_inductive_cleavage
IMS4_EQ4_22_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+.]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O.]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS4-EQ4.22:step_inductive_cleavage',
)

# IMS4-EQ4.23:step_inductive_cleavage
IMS4_EQ4_23_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[Cl+.]5>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C+]4([H]1000007)([H]1000008).[Cl.]5',
    name='IMS4-EQ4.23:step_inductive_cleavage',
)

# IMS4-EQ4.24:step_inductive_cleavage
IMS4_EQ4_24_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]3([C]2([H]1000003)([H]1000004)([H]1000005))([H]1000006)[C]4([H]1000007)([H]1000008)[Cl+.]5>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]3([C]2([H]1000003)([H]1000004)([H]1000005))([H]1000006)[C+]4([H]1000007)([H]1000008).[Cl.]5',
    name='IMS4-EQ4.24:step_inductive_cleavage',
)

# IMS4-EQ4.25:step_inductive_cleavage
IMS4_EQ4_25_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]1000003)([H]1000004)([H]1000005))[O.]4>>[C+]1([H]1000000)([H]1000001)([H]1000002).[C.]2([C]3([H]1000003)([H]1000004)([H]1000005)){=}[O]4',
    name='IMS4-EQ4.25:step_inductive_cleavage',
)

# IMS4-EQ4.26:step_alpha_cleavage
IMS4_EQ4_26_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+.]3[C]4([H]1000005)([H]1000006)([H]1000007)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[O+]3[C]4([H]1000005)([H]1000006)([H]1000007)',
    name='IMS4-EQ4.26:step_alpha_cleavage',
)

# IMS4-EQ4.26:step_inductive_cleavage
IMS4_EQ4_26_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[O+]3[C]4([H]1000005)([H]1000006)([H]1000007)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[O]3.[C+]4([H]1000005)([H]1000006)([H]1000007)',
    name='IMS4-EQ4.26:step_inductive_cleavage',
)

# IMS4-EQ4.27:step_alpha_cleavage
IMS4_EQ4_27_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[C]4([H]1000003)([H]1000004)([H]1000005)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2({#}[O+]3)[C]4([H]1000003)([H]1000004)([H]1000005)',
    name='IMS4-EQ4.27:step_alpha_cleavage',
)

# IMS4-EQ4.27:step_inductive_cleavage
IMS4_EQ4_27_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2({#}[O+]3)[C]4([H]1000003)([H]1000004)([H]1000005)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C-]2{#}[O+]3.[C+]4([H]1000003)([H]1000004)([H]1000005)',
    name='IMS4-EQ4.27:step_inductive_cleavage',
)

# IMS4-EQ4.28:step_inductive_cleavage
IMS4_EQ4_28_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[O+]2([H]1000003)([H]1000004)>>[C+]1([H]1000000)([H]1000001)([H]1000002).[O]2([H]1000003)([H]1000004)',
    name='IMS4-EQ4.28:step_inductive_cleavage',
)

# IMS4-EQ4.29:step_inductive_cleavage
IMS4_EQ4_29_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[C]7([O]8[H]1000006)([H]1000005)[C]9([C]10([H]1000008)([H]1000009)([H]1000010))([H]1000007)[N+]11([H]1000011)([H]1000012)[C]12([H]1000013)([H]1000014)([H]1000015)>>[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[C]7([O]8[H]1000006)([H]1000005)[C+]9([H]1000007)[C]10([H]1000008)([H]1000009)([H]1000010).[N]11([H]1000011)([H]1000012)[C]12([H]1000013)([H]1000014)([H]1000015)',
    name='IMS4-EQ4.29:step_inductive_cleavage',
)

# IMS4-EQ4.30:step_alpha_cleavage
IMS4_EQ4_30_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C+]6([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[C.]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C+]6([H]1000010)([H]1000011)',
    name='IMS4-EQ4.30:step_alpha_cleavage',
)

# IMS4-EQ4.31:step_alpha1_ring_opening
IMS4_EQ4_31_step_alpha1_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C+]5([H]1000005)[C.]6([H]1000006)[C]7({-}2)([H]1000007)([H]1000008))([H]1000000))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013))>>[C]1([C.]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C+]5([H]1000005)[C]6([H]1000006){=}[C]7([H]1000007)([H]1000008))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013))',
    name='IMS4-EQ4.31:step_alpha1_ring_opening',
)

# IMS4-EQ4.31:step_alpha2_charge_retention
IMS4_EQ4_31_step_alpha2_charge_retention = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C+]5([H]1000005)[C]6([H]1000006){=}[C]7([H]1000007)([H]1000008))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013))>>[C]1([C]2([H]1000000){=}[C]3([H]1000001)([H]1000002))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013)).[C.]4([H]1000003)([H]1000004)[C+]5([H]1000005)[C]6([H]1000006){=}[C]7([H]1000007)([H]1000008)',
    name='IMS4-EQ4.31:step_alpha2_charge_retention',
)

# IMS4-EQ4.32:step_alpha1_ring_opening
IMS4_EQ4_32_step_alpha1_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C+]5([H]1000005)[C.]6([H]1000006)[C]7({-}2)([H]1000007)([H]1000008))([H]1000000))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013))>>[C]1([C.]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C+]5([H]1000005)[C]6([H]1000006){=}[C]7([H]1000007)([H]1000008))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013))',
    name='IMS4-EQ4.32:step_alpha1_ring_opening',
)

# IMS4-EQ4.32:step_inductive_charge_migration
IMS4_EQ4_32_step_inductive_charge_migration = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C+]5([H]1000005)[C]6([H]1000006){=}[C]7([H]1000007)([H]1000008))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013))>>[C]1([C.]2([H]1000000)[C+]3([H]1000001)([H]1000002))(:[C]8([H]1000009):[C]9([H]1000010):[C]10([H]1000011):[C]11([H]1000012):[C]12(:1)([H]1000013)).[C]4([H]1000003)([H]1000004){=}[C]5([H]1000005)[C]6([H]1000006){=}[C]7([H]1000007)([H]1000008)',
    name='IMS4-EQ4.32:step_inductive_charge_migration',
)

# IMS4-EQ4.33:step_gamma_h_rearrangement  [1 hydrogen migration(s) inferred]
IMS4_EQ4_33_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000011)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1({=}[O+]2[H]1000011)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS4-EQ4.33:step_gamma_h_rearrangement',
)

# IMS4-EQ4.33:step_beta_cleavage_alpha
IMS4_EQ4_33_step_beta_cleavage_alpha = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C.]4([H]1000004)([H]1000005).[C]5([H]1000006)([H]1000007){=}[C]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS4-EQ4.33:step_beta_cleavage_alpha',
)

# IMS4-EQ4.34:step_inductive_cleavage
IMS4_EQ4_34_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C+]1([O]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([O]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003)){=}[C]4([H]1000004)([H]1000005).[C+]5([H]1000006)([H]1000007)[C.]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS4-EQ4.34:step_inductive_cleavage',
)

# IMS4-EQ4.35:step_gamma_h_rearrangement
IMS4_EQ4_35_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[N+.]2[N]8([C]9([H]1000009)([H]1000010)([H]1000011))[C]10([H]1000012)([H]1000013)([H]1000014))([H]1000000)[C]4([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[C]6([H]3)([H]1000005)[C]7([H]1000006)([H]1000007)([H]1000008)>>[C]1({=}[N+]2([H]3)[N]8([C]9([H]1000009)([H]1000010)([H]1000011))[C]10([H]1000012)([H]1000013)([H]1000014))([H]1000000)[C]4([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[C.]6([H]1000005)[C]7([H]1000006)([H]1000007)([H]1000008)',
    name='IMS4-EQ4.35:step_gamma_h_rearrangement',
)

# IMS4-EQ4.35:step_beta_cleavage_alpha
IMS4_EQ4_35_step_beta_cleavage_alpha = mod.Rule.fromDFS(
    s='[C]1({=}[N+]2([H]3)[N]8([C]9([H]1000009)([H]1000010)([H]1000011))[C]10([H]1000012)([H]1000013)([H]1000014))([H]1000000)[C]4([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[C.]6([H]1000005)[C]7([H]1000006)([H]1000007)([H]1000008)>>[C]1({=}[N+]2([H]3)[N]8([C]9([H]1000009)([H]1000010)([H]1000011))[C]10([H]1000012)([H]1000013)([H]1000014))([H]1000000)[C.]4([H]1000001)([H]1000002).[C]5([H]1000003)([H]1000004){=}[C]6([H]1000005)[C]7([H]1000006)([H]1000007)([H]1000008)',
    name='IMS4-EQ4.35:step_beta_cleavage_alpha',
)

# IMS4-EQ4.36:step_gamma_h_rearrangement
IMS4_EQ4_36_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]4)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C+]7([C.]8([H]1000010)[C]9([H]1000011){=}[C]10([H]1000012)[C]11([H]1000013){=}[C]12({-}7)([H]1000014))>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C+]7([C]8([H]4)([H]1000010)[C]9([H]1000011){=}[C]10([H]1000012)[C]11([H]1000013){=}[C]12({-}7)([H]1000014))',
    name='IMS4-EQ4.36:step_gamma_h_rearrangement',
)

# IMS4-EQ4.36:step_beta_cleavage_alpha
IMS4_EQ4_36_step_beta_cleavage_alpha = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C+]7([C]8([H]4)([H]1000010)[C]9([H]1000011){=}[C]10([H]1000012)[C]11([H]1000013){=}[C]12({-}7)([H]1000014))>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005){=}[C]5([H]1000006)([H]1000007).[H]4[C]8([C+]7([C.]6([H]1000008)([H]1000009))[C]12([H]1000014){=}[C]11([H]1000013)[C]10([H]1000012){=}[C]9({-}8)([H]1000011))([H]1000010)',
    name='IMS4-EQ4.36:step_beta_cleavage_alpha',
)

# IMS4-EQ4.37:step_rH_hydrogen_rearrangement
IMS4_EQ4_37_step_rH_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]8)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]6([H]1000010)([H]1000011)[O+.]7[H]1000012>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]6([H]1000010)([H]1000011)[O+]7([H]8)([H]1000012)',
    name='IMS4-EQ4.37:step_rH_hydrogen_rearrangement',
)

# IMS4-EQ4.37:step_rd_displacement_charge_retention
IMS4_EQ4_37_step_rd_displacement_charge_retention = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]6([H]1000010)([H]1000011)[O+]7([H]8)([H]1000012)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]6({-}3)([H]1000010)([H]1000011))([H]1000005).[O+.]7([H]8)([H]1000012)',
    name='IMS4-EQ4.37:step_rd_displacement_charge_retention',
)

# IMS4-EQ4.38a:step_rH_hydrogen_rearrangement
IMS4_EQ4_38a_step_rH_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]8)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]6([H]1000010)([H]1000011)[O+.]7[H]1000012>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]6([H]1000010)([H]1000011)[O+]7([H]8)([H]1000012)',
    name='IMS4-EQ4.38a:step_rH_hydrogen_rearrangement',
)

# IMS4-EQ4.38a:step_i_inductive_water_loss_charge_migration
IMS4_EQ4_38a_step_i_inductive_water_loss_charge_migration = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]6([H]1000010)([H]1000011)[O+]7([H]8)([H]1000012)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C+]6([H]1000010)([H]1000011).[O]7([H]8)([H]1000012)',
    name='IMS4-EQ4.38a:step_i_inductive_water_loss_charge_migration',
)

# IMS4-EQ4.38b:step_i_inductive_ethylene_loss
IMS4_EQ4_38b_step_i_inductive_ethylene_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C+]6([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C+]4([H]1000006)([H]1000007).[C]5([H]1000008)([H]1000009){=}[C]6([H]1000010)([H]1000011)',
    name='IMS4-EQ4.38b:step_i_inductive_ethylene_loss',
)

# IMS4-EQ4.39:step_rH
IMS4_EQ4_39_step_rH = mod.Rule.fromDFS(
    s='[C]1([H]5)([H]1000000)([H]1000001)[C]2({=}[O]3)[N+.]4([H]1000002)[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)[C]8([H]1000007)([H]1000008)[C]9([H]1000009)([H]1000010)([H]1000011)>>[C.]1([H]1000000)([H]1000001)[C]2({=}[O]3)[N+]4([H]5)([H]1000002)[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)[C]8([H]1000007)([H]1000008)[C]9([H]1000009)([H]1000010)([H]1000011)',
    name='IMS4-EQ4.39:step_rH',
)

# IMS4-EQ4.39:step_alpha
IMS4_EQ4_39_step_alpha = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C]2({=}[O]3)[N+]4([H]5)([H]1000002)[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)[C]8([H]1000007)([H]1000008)[C]9([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001){=}[C]2{=}[O]3.[N+.]4([H]5)([H]1000002)[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)[C]8([H]1000007)([H]1000008)[C]9([H]1000009)([H]1000010)([H]1000011)',
    name='IMS4-EQ4.39:step_alpha',
)

# IMS4-EQ4.3a:step_sigma_cleavage  [auto-localized precursor]
IMS4_EQ4_3a_step_sigma_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004)[C.]3([H]1000005)([H]1000006)([H]1000007)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[C.]3([H]1000005)([H]1000006)([H]1000007)',
    name='IMS4-EQ4.3a:step_sigma_cleavage',
)

# IMS4-EQ4.3b:step_sigma_cleavage  [auto-localized precursor]
IMS4_EQ4_3b_step_sigma_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004)[C+]3([H]1000005)([H]1000006)([H]1000007)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C+]3([H]1000005)([H]1000006)([H]1000007)',
    name='IMS4-EQ4.3b:step_sigma_cleavage',
)

# IMS4-EQ4.40:step_rH
IMS4_EQ4_40_step_rH = mod.Rule.fromDFS(
    s='[Cl+.]1[C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]7)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)>>[Cl+]1([H]7)[C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)',
    name='IMS4-EQ4.40:step_rH',
)

# IMS4-EQ4.40:step_ind
IMS4_EQ4_40_step_ind = mod.Rule.fromDFS(
    s='[Cl+]1([H]7)[C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)>>[Cl]1[H]7.[C+]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)',
    name='IMS4-EQ4.40:step_ind',
)

# IMS4-EQ4.41:step_rH
IMS4_EQ4_41_step_rH = mod.Rule.fromDFS(
    s='[H]1[O]2[C]3(:[C]4([H]1000000):[C]5([H]1000001):[C]6([H]1000002):[C]7([H]1000003):[C]8(:3)[C]9({=}[O]10)[O+.]11[C]12([H]1000004)([H]1000005)([H]1000006))>>[H]1[O+]11([C]9([C]8(:[C]3([O.]2):[C]4([H]1000000):[C]5([H]1000001):[C]6([H]1000002):[C]7(:8)([H]1000003))){=}[O]10)[C]12([H]1000004)([H]1000005)([H]1000006)',
    name='IMS4-EQ4.41:step_rH',
)

# IMS4-EQ4.41:step_elimination
IMS4_EQ4_41_step_elimination = mod.Rule.fromDFS(
    s='[H]1[O+]11([C]9([C]8(:[C]3([O.]2):[C]4([H]1000000):[C]5([H]1000001):[C]6([H]1000002):[C]7(:8)([H]1000003))){=}[O]10)[C]12([H]1000004)([H]1000005)([H]1000006)>>[H]1[O]11[C]12([H]1000004)([H]1000005)([H]1000006).[O.]2[C]3(:[C]4([H]1000000):[C]5([H]1000001):[C]6([H]1000002):[C]7([H]1000003):[C]8(:3)[C]9{#}[O+]10)',
    name='IMS4-EQ4.41:step_elimination',
)

# IMS4-EQ4.42:step_displacement
IMS4_EQ4_42_step_displacement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5([H]1000009)([H]1000010)[Cl+.]6>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5([H]1000009)([H]1000010)[Cl+]6{-}2)([H]1000003)([H]1000004)',
    name='IMS4-EQ4.42:step_displacement',
)

# IMS4-EQ4.43:step_alpha_cleavage
IMS4_EQ4_43_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[N+.]8([H]1000005)[C]10([H]1000006)([H]1000007)[C]13([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[N+]8([H]1000005){=}[C]10([H]1000006)([H]1000007).[C.]13([H]1000008)([H]1000009)([H]1000010)',
    name='IMS4-EQ4.43:step_alpha_cleavage',
)

# IMS4-EQ4.43:step_h_rearrangement  [1 hydrogen migration(s) inferred]
IMS4_EQ4_43_step_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000010)[C]5([H]1000002)([H]1000003)[N+]8([H]1000004){=}[C]10([H]1000005)([H]1000006).[C.]13([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001){=}[C]5([H]1000002)([H]1000003).[N+]8([H]1000004)([H]1000010){=}[C]10([H]1000005)([H]1000006).[C.]13([H]1000007)([H]1000008)([H]1000009)',
    name='IMS4-EQ4.43:step_h_rearrangement',
)

# IMS4-EQ4.44:step_inductive_cleavage
IMS4_EQ4_44_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[Cl+.]1[C]2([C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]8([H]1000004)([H]1000005)[C]11([H]1000006)([H]1000007)[Cl]14>>[Cl.]1.[C+]2([C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]8([H]1000004)([H]1000005)[C]11([H]1000006)([H]1000007)[Cl]14',
    name='IMS4-EQ4.44:step_inductive_cleavage',
)

# IMS4-EQ4.44:step_h_rearrangement  [1 hydrogen migration(s) inferred]
IMS4_EQ4_44_step_h_rearrangement = mod.Rule.fromDFS(
    s='[Cl.]1.[C+]2([C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]8([H]1000004)([H]1000007)[C]11([H]1000005)([H]1000006)[Cl]14>>[Cl.]1.[C+]2([C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]8([H]1000004){=}[C]11([H]1000005)([H]1000006).[Cl]14[H]1000007',
    name='IMS4-EQ4.44:step_h_rearrangement',
)

# IMS4-EQ4.45:step_rH
IMS4_EQ4_45_step_rH = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]8)([H]1000003)[C]3([H]1000004)([H]1000005)[O]4[C]5({=}[O+.]6)[C]7([H]1000006)([H]1000007)([H]1000008)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C]3([H]1000004)([H]1000005)[O]4[C]5({=}[O+]6[H]8)[C]7([H]1000006)([H]1000007)([H]1000008)',
    name='IMS4-EQ4.45:step_rH',
)

# IMS4-EQ4.45:step_alpha_cleavage
IMS4_EQ4_45_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C]3([H]1000004)([H]1000005)[O]4[C]5({=}[O+]6[H]8)[C]7([H]1000006)([H]1000007)([H]1000008)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[C]3([H]1000004)([H]1000005).[O.]4[C]5({=}[O+]6[H]8)[C]7([H]1000006)([H]1000007)([H]1000008)',
    name='IMS4-EQ4.45:step_alpha_cleavage',
)

# IMS4-EQ4.46:step_rH_first
IMS4_EQ4_46_step_rH_first = mod.Rule.fromDFS(
    s='[C]1([H]9)([H]1000000)([H]1000001)[C]2([H]8)([H]1000002)[C]3([H]1000003)([H]1000004)[O]4[C]5({=}[O+.]6)[C]7([H]1000005)([H]1000006)([H]1000007)>>[C]1([H]9)([H]1000000)([H]1000001)[C.]2([H]1000002)[C]3([H]1000003)([H]1000004)[O]4[C]5({=}[O+]6[H]8)[C]7([H]1000005)([H]1000006)([H]1000007)',
    name='IMS4-EQ4.46:step_rH_first',
)

# IMS4-EQ4.46:step_rH_second
IMS4_EQ4_46_step_rH_second = mod.Rule.fromDFS(
    s='[C]1([H]9)([H]1000000)([H]1000001)[C.]2([H]1000002)[C]3([H]1000003)([H]1000004)[O]4[C]5({=}[O+]6[H]8)[C]7([H]1000005)([H]1000006)([H]1000007)>>[C.]1([H]1000000)([H]1000001)[C]2([H]1000002){=}[C]3([H]1000003)([H]1000004).[O]4([H]9)[C]5({=}[O+]6[H]8)[C]7([H]1000005)([H]1000006)([H]1000007)',
    name='IMS4-EQ4.46:step_rH_second',
)

# IMS4-EQ4.4a:step_retro_2plus2
IMS4_EQ4_4a_step_retro_2plus2 = mod.Rule.fromDFS(
    s='[C]1([C]2([O+.]3[H]1000003)([H]1000002)[C]5([H]1000006)([H]1000007)[C]4({-}1)([H]1000004)([H]1000005))([H]1000000)([H]1000001)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[O+.]3[H]1000003.[C]4([H]1000004)([H]1000005){=}[C]5([H]1000006)([H]1000007)',
    name='IMS4-EQ4.4a:step_retro_2plus2',
)

# IMS4-EQ4.4c:step_water_elimination
IMS4_EQ4_4c_step_water_elimination = mod.Rule.fromDFS(
    s='[C]1([H]4)([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[O+.]3[H]5>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[O+.]3([H]4)([H]5)',
    name='IMS4-EQ4.4c:step_water_elimination',
)

# IMS4-EQ4.5:step_three_bond_cleavage  [auto-localized precursor]
IMS4_EQ4_5_step_three_bond_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C+]4([H]5)([H]6)([H]1000007)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C]3([H]1000005)([H]1000006){=}[C+]4[H]1000007.[H]5[H]6',
    name='IMS4-EQ4.5:step_three_bond_cleavage',
)

# IMS4-EQ4.6a:step_inductive_cleavage
IMS4_EQ4_6a_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+]3{=}[C]4([H]1000005)([H]1000006)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O]3{=}[C]4([H]1000005)([H]1000006)',
    name='IMS4-EQ4.6a:step_inductive_cleavage',
)

# IMS4-EQ4.6b:step_hydrogen_rearrangement
IMS4_EQ4_6b_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]5)([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[O+]3{=}[C]4([H]1000004)([H]1000005)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[O+]3([H]5){=}[C]4([H]1000004)([H]1000005)',
    name='IMS4-EQ4.6b:step_hydrogen_rearrangement',
)

# IMS4-EQ4.6d:step_retro_2plus2
IMS4_EQ4_6d_step_retro_2plus2 = mod.Rule.fromDFS(
    s='[C]1([C+]2([H]1000002)[C]4([H]1000005)([H]1000006)[C]3({-}1)([H]1000003)([H]1000004))([H]1000000)([H]1000001)>>[C]1([H]1000000)([H]1000001){=}[C+]2[H]1000002.[C]3([H]1000003)([H]1000004){=}[C]4([H]1000005)([H]1000006)',
    name='IMS4-EQ4.6d:step_retro_2plus2',
)

# IMS4-EQ4.7:step_sigma_dissociation  [auto-localized precursor]
IMS4_EQ4_7_step_sigma_dissociation = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004)([H]1000005)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C+]2([H]1000003)([H]1000004)([H]1000005)',
    name='IMS4-EQ4.7:step_sigma_dissociation',
)

# IMS4-EQ4.8:step_sigma_dissociation  [auto-localized precursor]
IMS4_EQ4_8_step_sigma_dissociation = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]6([H]1000003)([H]1000004)([H]1000005))([C]10([H]1000006)([H]1000007)([H]1000008))[C.]14([H]1000009)([H]1000010)[C]20([H]1000011)([H]1000012)([H]1000013)>>[C+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]6([H]1000003)([H]1000004)([H]1000005))[C]10([H]1000006)([H]1000007)([H]1000008).[C.]14([H]1000009)([H]1000010)[C]20([H]1000011)([H]1000012)([H]1000013)',
    name='IMS4-EQ4.8:step_sigma_dissociation',
)

# IMS4-EQ4.9:step_alpha_cleavage
IMS4_EQ4_9_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[N+.]3([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000008)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[N+]3([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000008)',
    name='IMS4-EQ4.9:step_alpha_cleavage',
)

# IMS4-FIG4.4a:step_alpha_cleavage_ch3
IMS4_FIG4_4a_step_alpha_cleavage_ch3 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[N+.]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[N+]3([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010)',
    name='IMS4-FIG4.4a:step_alpha_cleavage_ch3',
)

# IMS4-FIG4.4b:step_alpha_cleavage_h
IMS4_FIG4_4b_step_alpha_cleavage_h = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]6)([H]1000003)[N+.]3([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[N+]3([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009).[H.]6',
    name='IMS4-FIG4.4b:step_alpha_cleavage_h',
)

# IMS8-EQ8.10:step_inductive_cleavage
IMS8_EQ8_10_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+]3{=}[C]4([H]1000005)([H]1000006)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O]3{=}[C]4([H]1000005)([H]1000006)',
    name='IMS8-EQ8.10:step_inductive_cleavage',
)

# IMS8-EQ8.100:step_alpha_cleavage
IMS8_EQ8_100_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[O+.]1([H]2)[C]3([C]4([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)([H]1000008)>>[O+]1([H]2){=}[C]3([H]1000000)[C]4([H]1000001)([H]1000002)([H]1000003).[C.]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.100:step_alpha_cleavage',
)

# IMS8-EQ8.100:step_rH_methane_loss
IMS8_EQ8_100_step_rH_methane_loss = mod.Rule.fromDFS(
    s='[O+]1([H]2){=}[C]3([H]1000000)[C]4([H]1000001)([H]1000002)([H]1000003).[C.]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)([H]1000008)>>[O+]1{#}[C]3[H]1000000.[H]2[C]4([H]1000001)([H]1000002)([H]1000003).[C.]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.100:step_rH_methane_loss',
)

# IMS8-EQ8.101a:step_gamma_H_transfer
IMS8_EQ8_101a_step_gamma_H_transfer = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]7)([H]1000004)([H]1000005))([O]5[H]1000006){=}[O+.]6>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)([H]1000005))([O]5[H]1000006){=}[O+]6[H]7',
    name='IMS8-EQ8.101a:step_gamma_H_transfer',
)

# IMS8-EQ8.101a:step_mclafferty_cleavage
IMS8_EQ8_101a_step_mclafferty_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)([H]1000005))([O]5[H]1000006){=}[O+]6[H]7>>[C]1({=}[C]2([H]1000000)([H]1000001))([O]5[H]1000006)[O+.]6[H]7.[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005)',
    name='IMS8-EQ8.101a:step_mclafferty_cleavage',
)

# IMS8-EQ8.101b:step_beta_H_transfer
IMS8_EQ8_101b_step_beta_H_transfer = mod.Rule.fromDFS(
    s='[C]1([C]2([H]8)([H]1000000)[C]3([H]7)([H]1000001)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+.]6>>[C]1([C]2([H]8)([H]1000000)[C.]3([H]1000001)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+]6[H]7',
    name='IMS8-EQ8.101b:step_beta_H_transfer',
)

# IMS8-EQ8.101b:step_rH_1_2_to_enediol
IMS8_EQ8_101b_step_rH_1_2_to_enediol = mod.Rule.fromDFS(
    s='[C]1([C]2([H]8)([H]1000000)[C.]3([H]1000001)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+]6[H]7>>[C]1({=}[C]2([H]1000000)[C]3([H]8)([H]1000001)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005)[O+.]6[H]7',
    name='IMS8-EQ8.101b:step_rH_1_2_to_enediol',
)

# IMS8-EQ8.101b:step_alpha_methyl_loss
IMS8_EQ8_101b_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1({=}[C]2([H]1000000)[C]3([H]8)([H]1000001)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005)[O+.]6[H]7>>[C]1([C]2([H]1000000){=}[C]3([H]8)([H]1000001))([O]5[H]1000005){=}[O+]6[H]7.[C.]4([H]1000002)([H]1000003)([H]1000004)',
    name='IMS8-EQ8.101b:step_alpha_methyl_loss',
)

# IMS8-EQ8.101c:step_rC_1_2_carboxyl_migration
IMS8_EQ8_101c_step_rC_1_2_carboxyl_migration = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C.]3([H]8)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+]6[H]7>>[C]1([C]3([C.]2([H]1000000)([H]1000001))([H]8)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+]6[H]7',
    name='IMS8-EQ8.101c:step_rC_1_2_carboxyl_migration',
)

# IMS8-EQ8.101c:step_rH_1_2_to_isobutyric_enediol
IMS8_EQ8_101c_step_rH_1_2_to_isobutyric_enediol = mod.Rule.fromDFS(
    s='[C]1([C]3([C.]2([H]1000000)([H]1000001))([H]8)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+]6[H]7>>[C]1({=}[C]3([C]2([H]8)([H]1000000)([H]1000001))[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005)[O+.]6[H]7',
    name='IMS8-EQ8.101c:step_rH_1_2_to_isobutyric_enediol',
)

# IMS8-EQ8.101c:step_rH_1_4_to_isobutyric_acid_ion
IMS8_EQ8_101c_step_rH_1_4_to_isobutyric_acid_ion = mod.Rule.fromDFS(
    s='[C]1([C]3([C.]2([H]1000000)([H]1000001))([H]8)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+]6[H]7>>[C]1([C]3([C]2([H]7)([H]1000000)([H]1000001))([H]8)[C]4([H]1000002)([H]1000003)([H]1000004))([O]5[H]1000005){=}[O+.]6',
    name='IMS8-EQ8.101c:step_rH_1_4_to_isobutyric_acid_ion',
)

# IMS8-EQ8.101d:step_rH_1_4_from_C4
IMS8_EQ8_101d_step_rH_1_4_from_C4 = mod.Rule.fromDFS(
    s='[C]1([C]3([C]2([H]1000000)([H]1000001)([H]1000002))([H]8)[C]4([H]9)([H]10)([H]1000003))([O]5[H]1000004){=}[O+.]6>>[C]1([C]3([C]2([H]1000000)([H]1000001)([H]1000002))([H]8)[C.]4([H]10)([H]1000003))([O]5[H]1000004){=}[O+]6[H]9',
    name='IMS8-EQ8.101d:step_rH_1_4_from_C4',
)

# IMS8-EQ8.101d:step_rC_1_2_reverse_migration
IMS8_EQ8_101d_step_rC_1_2_reverse_migration = mod.Rule.fromDFS(
    s='[C]1([C]3([C]2([H]1000000)([H]1000001)([H]1000002))([H]8)[C.]4([H]10)([H]1000003))([O]5[H]1000004){=}[O+]6[H]9>>[C]1([C]4([H]10)([H]1000003)[C.]3([H]8)[C]2([H]1000000)([H]1000001)([H]1000002))([O]5[H]1000004){=}[O+]6[H]9',
    name='IMS8-EQ8.101d:step_rC_1_2_reverse_migration',
)

# IMS8-EQ8.101d:step_rH_1_2_to_alpha_radical
IMS8_EQ8_101d_step_rH_1_2_to_alpha_radical = mod.Rule.fromDFS(
    s='[C]1([C]4([H]10)([H]1000003)[C.]3([H]8)[C]2([H]1000000)([H]1000001)([H]1000002))([O]5[H]1000004){=}[O+]6[H]9>>[C]1([C.]4([H]1000003)[C]3([H]8)([H]10)[C]2([H]1000000)([H]1000001)([H]1000002))([O]5[H]1000004){=}[O+]6[H]9',
    name='IMS8-EQ8.101d:step_rH_1_2_to_alpha_radical',
)

# IMS8-EQ8.101d:step_alpha_methyl_loss
IMS8_EQ8_101d_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([C.]4([H]1000003)[C]3([H]8)([H]10)[C]2([H]1000000)([H]1000001)([H]1000002))([O]5[H]1000004){=}[O+]6[H]9>>[C]1([C]4([H]1000003){=}[C]3([H]8)([H]10))([O]5[H]1000004){=}[O+]6[H]9.[C.]2([H]1000000)([H]1000001)([H]1000002)',
    name='IMS8-EQ8.101d:step_alpha_methyl_loss',
)

# IMS8-EQ8.102:step_gamma_h_rearrangement
IMS8_EQ8_102_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([C]4([H]8)([H]1000003)([H]1000004))([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))({=}[O+.]6)[O]7[H]1000008>>[C+]1([C]2([H]1000000)([H]1000001)[C]3([C.]4([H]1000003)([H]1000004))([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))([O]6[H]8)[O]7[H]1000008',
    name='IMS8-EQ8.102:step_gamma_h_rearrangement',
)

# IMS8-EQ8.102:step_ring_closure_carboxyl_detachment
IMS8_EQ8_102_step_ring_closure_carboxyl_detachment = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000000)([H]1000001)[C]3([C.]4([H]1000003)([H]1000004))([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))([O]6[H]8)[O]7[H]1000008>>[C+.]1([O]6[H]8)[O]7[H]1000008.[C]2([C]3([C]4({-}2)([H]1000003)([H]1000004))([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)',
    name='IMS8-EQ8.102:step_ring_closure_carboxyl_detachment',
)

# IMS8-EQ8.102:step_carboxyl_reattachment
IMS8_EQ8_102_step_carboxyl_reattachment = mod.Rule.fromDFS(
    s='[C+.]1([O]6[H]8)[O]7[H]1000008.[C]2([C]3([C]4({-}2)([H]1000003)([H]1000004))([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)>>[C+]1([C]3([C]4([H]1000003)([H]1000004)[C.]2([H]1000000)([H]1000001))([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))([O]6[H]8)[O]7[H]1000008',
    name='IMS8-EQ8.102:step_carboxyl_reattachment',
)

# IMS8-EQ8.102:step_alpha_cleavage_ethylene_loss
IMS8_EQ8_102_step_alpha_cleavage_ethylene_loss = mod.Rule.fromDFS(
    s='[C+]1([C]3([C]4([H]1000003)([H]1000004)[C.]2([H]1000000)([H]1000001))([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))([O]6[H]8)[O]7[H]1000008>>[C]1({=}[C]3([H]1000002)[C]5([H]1000005)([H]1000006)([H]1000007))([O+.]6[H]8)[O]7[H]1000008.[C]2([H]1000000)([H]1000001){=}[C]4([H]1000003)([H]1000004)',
    name='IMS8-EQ8.102:step_alpha_cleavage_ethylene_loss',
)

# IMS8-EQ8.103:step_rd_displacement
IMS8_EQ8_103_step_rd_displacement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5([H]1000009)([H]1000010)[C]6([H]1000011)([H]1000012)[Cl+.]7>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C]3([C]4([H]1000007)([H]1000008)[C]5([H]1000009)([H]1000010)[C]6([H]1000011)([H]1000012)[Cl+]7{-}3)([H]1000005)([H]1000006)',
    name='IMS8-EQ8.103:step_rd_displacement',
)

# IMS8-EQ8.104:step_rd_displacement_distonic
IMS8_EQ8_104_step_rd_displacement_distonic = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[N+]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5([H]1000009)([H]1000010)[C.]6([H]1000011)([H]1000012)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[N+]2([C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5([H]1000009)([H]1000010)[C]6({-}2)([H]1000011)([H]1000012))([H]1000003)([H]1000004)',
    name='IMS8-EQ8.104:step_rd_displacement_distonic',
)

# IMS8-EQ8.105:step_charge_site_displacement
IMS8_EQ8_105_step_charge_site_displacement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O]3)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C+]8([H]1000011)([H]1000012)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2{#}[O+]3.[C]4([C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8({-}4)([H]1000011)([H]1000012))([H]1000003)([H]1000004)',
    name='IMS8-EQ8.105:step_charge_site_displacement',
)

# IMS8-EQ8.106a:step_re_elimination_charge_on_AD
IMS8_EQ8_106a_step_re_elimination_charge_on_AD = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)[O+.]7[C]8([H]1000011)([H]1000012)([H]1000013)>>[C]1([H]1000000)([H]1000001)([H]1000002)[O+.]7[C]8([H]1000011)([H]1000012)([H]1000013).[C]2([O]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)[C]6({-}2)([H]1000009)([H]1000010))([H]1000003)([H]1000004)',
    name='IMS8-EQ8.106a:step_re_elimination_charge_on_AD',
)

# IMS8-EQ8.106b:step_re_elimination_charge_on_ring
IMS8_EQ8_106b_step_re_elimination_charge_on_ring = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)[C]6([H]1000009)([H]1000010)[O+.]7[C]8([H]1000011)([H]1000012)([H]1000013)>>[C]1([H]1000000)([H]1000001)([H]1000002)[O]7[C]8([H]1000011)([H]1000012)([H]1000013).[C]2([O+.]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)[C]6({-}2)([H]1000009)([H]1000010))([H]1000003)([H]1000004)',
    name='IMS8-EQ8.106b:step_re_elimination_charge_on_ring',
)

# IMS8-EQ8.107:step_rd_phenonium
IMS8_EQ8_107_step_rd_phenonium = mod.Rule.fromDFS(
    s='[C.]1([C]2([H]1000000){=}[C]3([H]1000001)[C+]4([H]1000002)[C]5([H]1000003){=}[C]6({-}1)([H]1000004))[C]7([H]1000005)([H]1000006)[C]8([H]1000007)([H]1000008)[Br]9>>[C]1([C]2([H]1000000){=}[C]3([H]1000001)[C+]4([H]1000002)[C]5([H]1000003){=}[C]6({-}1)([H]1000004))([C]7([H]1000005)([H]1000006)[C]8({-}1)([H]1000007)([H]1000008)).[Br.]9',
    name='IMS8-EQ8.107:step_rd_phenonium',
)

# IMS8-EQ8.108:step_rd_cyclization_to_nitrogen
IMS8_EQ8_108_step_rd_cyclization_to_nitrogen = mod.Rule.fromDFS(
    s='[N+.]1([C]2({=}[O]3)[C]4([H]1000000){=}[C]5([H]1000001)[C]6([H]1000002)([H]1000003)([H]1000004))([C]10([H]1000005)([H]1000006)[C]11([H]1000007)([H]1000008)[C]12([H]1000009)([H]1000010)[C]13([H]1000011)([H]1000012)[C]14({-}1)([H]1000013)([H]1000014))>>[N+]1([C]2({=}[O]3)[C]4([H]1000000){=}[C]5({-}1)([H]1000001))([C]10([H]1000005)([H]1000006)[C]11([H]1000007)([H]1000008)[C]12([H]1000009)([H]1000010)[C]13([H]1000011)([H]1000012)[C]14({-}1)([H]1000013)([H]1000014)).[C.]6([H]1000002)([H]1000003)([H]1000004)',
    name='IMS8-EQ8.108:step_rd_cyclization_to_nitrogen',
)

# IMS8-EQ8.109:step_rd_ring_closure_loss_of_X
IMS8_EQ8_109_step_rd_ring_closure_loss_of_X = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[Br]15)[C]7({=}[C]8([H]1000004)([H]1000005))[C]10({=}[N+.]9[C]14([H]1000009){=}[C]13([H]1000008)[C]12([H]1000007){=}[C]11({-}10)([H]1000006))>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[N+]9(:[C]10([C]7({-}1){=}[C]8([H]1000004)([H]1000005)):[C]11([H]1000006):[C]12([H]1000007):[C]13([H]1000008):[C]14(:9)([H]1000009))).[Br.]15',
    name='IMS8-EQ8.109:step_rd_ring_closure_loss_of_X',
)

# IMS8-EQ8.11:step_hydrogen_rearrangement
IMS8_EQ8_11_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]5)([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[O+]3{=}[C]4([H]1000004)([H]1000005)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[O+]3([H]5){=}[C]4([H]1000004)([H]1000005)',
    name='IMS8-EQ8.11:step_hydrogen_rearrangement',
)

# IMS8-EQ8.110:step_rH_beta_hydrogen
IMS8_EQ8_110_step_rH_beta_hydrogen = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([O]3[C]4([H]1000000)([H]1000001)[C]5([H]1000002)([H]1000003)([H]1000004))[C]6([H]1000005)([H]1000006)[C]7([H]14)([H]1000007)[C]8(:[C]9([H]1000008):[C]10([H]1000009):[C]11([H]1000010):[C]12([H]1000011):[C]13(:8)([H]1000012))>>[C]1({=}[O+]2[H]14)([O]3[C]4([H]1000000)([H]1000001)[C]5([H]1000002)([H]1000003)([H]1000004))[C]6([H]1000005)([H]1000006)[C.]7([H]1000007)[C]8(:[C]9([H]1000008):[C]10([H]1000009):[C]11([H]1000010):[C]12([H]1000011):[C]13(:8)([H]1000012))',
    name='IMS8-EQ8.110:step_rH_beta_hydrogen',
)

# IMS8-EQ8.110:step_rd_ethyl_radical_loss
IMS8_EQ8_110_step_rd_ethyl_radical_loss = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]14)([O]3[C]4([H]1000000)([H]1000001)[C]5([H]1000002)([H]1000003)([H]1000004))[C]6([H]1000005)([H]1000006)[C.]7([H]1000007)[C]8(:[C]9([H]1000008):[C]10([H]1000009):[C]11([H]1000010):[C]12([H]1000011):[C]13(:8)([H]1000012))>>[C]1([O+]2([H]14)[C]7([C]6({-}1)([H]1000005)([H]1000006))([H]1000007)[C]8(:[C]9([H]1000008):[C]10([H]1000009):[C]11([H]1000010):[C]12([H]1000011):[C]13(:8)([H]1000012)))({=}[O]3).[C.]4([H]1000000)([H]1000001)[C]5([H]1000002)([H]1000003)([H]1000004)',
    name='IMS8-EQ8.110:step_rd_ethyl_radical_loss',
)

# IMS8-EQ8.110:step_retro_2plus2_ketene_loss
IMS8_EQ8_110_step_retro_2plus2_ketene_loss = mod.Rule.fromDFS(
    s='[C]1([O+]2([H]14)[C]7([C]6({-}1)([H]1000005)([H]1000006))([H]1000007)[C]8(:[C]9([H]1000008):[C]10([H]1000009):[C]11([H]1000010):[C]12([H]1000011):[C]13(:8)([H]1000012)))({=}[O]3).[C.]4([H]1000000)([H]1000001)[C]5([H]1000002)([H]1000003)([H]1000004)>>[C]1({=}[O]3){=}[C]6([H]1000005)([H]1000006).[O+]2([H]14){=}[C]7([H]1000007)[C]8(:[C]9([H]1000008):[C]10([H]1000009):[C]11([H]1000010):[C]12([H]1000011):[C]13(:8)([H]1000012)).[C.]4([H]1000000)([H]1000001)[C]5([H]1000002)([H]1000003)([H]1000004)',
    name='IMS8-EQ8.110:step_retro_2plus2_ketene_loss',
)

# IMS8-EQ8.111:step_rH_six_membered
IMS8_EQ8_111_step_rH_six_membered = mod.Rule.fromDFS(
    s='[C.]1([C+]2([H]1000001)[C]3({=}[O]4)[O]5[C]6([H]7)([H]1000002)([H]1000003))([H]1000000)[C]8({=}[O]9)[O]10[C]11([H]1000004)([H]1000005)([H]1000006)>>[C]1([C+]2([H]1000001)[C]3({=}[O]4)[O]5[C.]6([H]1000002)([H]1000003))([H]7)([H]1000000)[C]8({=}[O]9)[O]10[C]11([H]1000004)([H]1000005)([H]1000006)',
    name='IMS8-EQ8.111:step_rH_six_membered',
)

# IMS8-EQ8.111:step_rd_lactone_closure
IMS8_EQ8_111_step_rd_lactone_closure = mod.Rule.fromDFS(
    s='[C]1([C+]2([H]1000001)[C]3({=}[O]4)[O]5[C.]6([H]1000002)([H]1000003))([H]7)([H]1000000)[C]8({=}[O]9)[O]10[C]11([H]1000004)([H]1000005)([H]1000006)>>[C]1([C+]2([H]1000001)[C]3({=}[O]4)[O]5[C]6({-}1)([H]1000002)([H]1000003))([H]7)([H]1000000).[C.]8({=}[O]9)[O]10[C]11([H]1000004)([H]1000005)([H]1000006)',
    name='IMS8-EQ8.111:step_rd_lactone_closure',
)

# IMS8-EQ8.112:step_alpha_cleavage
IMS8_EQ8_112_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[N+.]1([C]2([C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))([H]1000000)[C]7([H]1000009)([H]1000010)([H]1000011))[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[N]11([H]1000018)[C]12({=}[O]13)[C]14([H]1000019)([H]1000020)([H]1000021)>>[N+]1({=}[C]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[N]11([H]1000018)[C]12({=}[O]13)[C]14([H]1000019)([H]1000020)([H]1000021).[C.]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.112:step_alpha_cleavage',
)

# IMS8-EQ8.112:step_rd_amide_oxygen_displacement
IMS8_EQ8_112_step_rd_amide_oxygen_displacement = mod.Rule.fromDFS(
    s='[N+]1({=}[C]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[N]11([H]1000018)[C]12({=}[O]13)[C]14([H]1000019)([H]1000020)([H]1000021).[C.]7([H]1000009)([H]1000010)([H]1000011)>>[N]1({=}[C]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008)).[C.]7([H]1000009)([H]1000010)([H]1000011).[C]8([C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[N]11([H]1000018)[C]12({=}[O+]13{-}8)[C]14([H]1000019)([H]1000020)([H]1000021))([H]1000012)([H]1000013)',
    name='IMS8-EQ8.112:step_rd_amide_oxygen_displacement',
)

# IMS8-EQ8.113:step_rd_phenyl_migration
IMS8_EQ8_113_step_rd_phenyl_migration = mod.Rule.fromDFS(
    s='[C]1(:[C]2([H]1000001):[C]3([H]1000002):[C]4([H]1000003):[C]5([H]1000004):[C]6(:1)[C]7([H]1000005){=}[N]8[O+]9([H]1000006)([H]1000007))([H]1000000)>>[C]1(:[C]2([H]1000001):[C]3([H]1000002):[C]4([H]1000003):[C]5([H]1000004):[C]6(:1)[N]8{=}[C+]7[H]1000005)([H]1000000).[O]9([H]1000006)([H]1000007)',
    name='IMS8-EQ8.113:step_rd_phenyl_migration',
)

# IMS8-EQ8.114:step_alpha_cleavage
IMS8_EQ8_114_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([O+.]2[C]3([H]1000001)([H]1000002)([H]1000003))([C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([O]8[C]9([H]1000011)([H]1000012)([H]1000013))([H]1000010)[C]10({-}1)([H]1000014)([H]1000015))([H]1000000)>>[C]1({=}[O+]2[C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]10([H]1000014)([H]1000015)[C]7([C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005))([H]1000010)[O]8[C]9([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.114:step_alpha_cleavage',
)

# IMS8-EQ8.114:step_re_methoxyl_migration
IMS8_EQ8_114_step_re_methoxyl_migration = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]10([H]1000014)([H]1000015)[C]7([C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005))([H]1000010)[O]8[C]9([H]1000011)([H]1000012)([H]1000013)>>[C]1({=}[O+]2[C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[O]8[C]9([H]1000011)([H]1000012)([H]1000013).[C.]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010){=}[C]10([H]1000014)([H]1000015)',
    name='IMS8-EQ8.114:step_re_methoxyl_migration',
)

# IMS8-EQ8.115a:step_ring_b_cleavage_double_h_transfer  [2 hydrogen migration(s) inferred]
IMS8_EQ8_115a_step_ring_b_cleavage_double_h_transfer = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([C]4([H]1000004){=}[C]5([C]6([H]1000005)([H]1000006)[C]7([H]1000007)([H]1000008)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000022)([H]1000023)([H]1000024))([H]1000009)[C]11([H]1000010)([H]1000045)[C]12([H]1000011)([H]1000012)[C]13([C]14({-}8)([H]1000013)[C]15([H]1000014)([H]1000015)[C]16([H]1000016)([H]1000017)[C]17({-}13)([H]1000018)[C]20([C]21([H]1000026)([H]1000027)([H]1000028))([H]1000025)[C]22([H]1000029)([H]1000030)[C]23([H]1000031)([H]1000032)[C]24([H]1000033)([H]1000034)[O]26[Si]27([C]28([H]1000035)([H]1000036)([H]1000037))([C]29([H]1000038)([H]1000039)([H]1000040))[C]30([H]1000041)([H]1000042)([H]1000043))[C]18([H]1000019)([H]1000020)([H]1000021))([H]1000044))){=}[O+.]25)([H]1000000)([H]1000001)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([C]4([H]1000004)([H]1000044)[C]5({=}[C]6([H]1000005)([H]1000006))[C]10({-}1)([H]1000045)[C]19([H]1000022)([H]1000023)([H]1000024)){=}[O+.]25)([H]1000000)([H]1000001).[C]7([H]1000007)([H]1000008){=}[C]8([C]9([H]1000009){=}[C]11([H]1000010)[C]12([H]1000011)([H]1000012)[C]13([C]14({-}8)([H]1000013)[C]15([H]1000014)([H]1000015)[C]16([H]1000016)([H]1000017)[C]17({-}13)([H]1000018)[C]20([C]21([H]1000026)([H]1000027)([H]1000028))([H]1000025)[C]22([H]1000029)([H]1000030)[C]23([H]1000031)([H]1000032)[C]24([H]1000033)([H]1000034)[O]26[Si]27([C]28([H]1000035)([H]1000036)([H]1000037))([C]29([H]1000038)([H]1000039)([H]1000040))[C]30([H]1000041)([H]1000042)([H]1000043))[C]18([H]1000019)([H]1000020)([H]1000021))',
    name='IMS8-EQ8.115a:step_ring_b_cleavage_double_h_transfer',
)

# IMS8-EQ8.115b:step_remote_tms_migration_and_ring_b_cleavage  [2 hydrogen migration(s) inferred]
IMS8_EQ8_115b_step_remote_tms_migration_and_ring_b_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([C]4([H]1000004){=}[C]5([C]6([H]1000005)([H]1000006)[C]7([H]1000007)([H]1000008)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000022)([H]1000023)([H]1000024))([H]1000009)[C]11([H]1000010)([H]1000045)[C]12([H]1000011)([H]1000012)[C]13([C]14({-}8)([H]1000013)[C]15([H]1000014)([H]1000015)[C]16([H]1000016)([H]1000017)[C]17({-}13)([H]1000018)[C]20([C]21([H]1000026)([H]1000027)([H]1000028))([H]1000025)[C]22([H]1000029)([H]1000030)[C]23([H]1000031)([H]1000032)[C]24([H]1000033)([H]1000034)[O]26[Si]27([C]28([H]1000035)([H]1000036)([H]1000037))([C]29([H]1000038)([H]1000039)([H]1000040))[C]30([H]1000041)([H]1000042)([H]1000043))[C]18([H]1000019)([H]1000020)([H]1000021))([H]1000044))){=}[O+.]25)([H]1000000)([H]1000001)>>[C]1([C]2([H]1000002)([H]1000003)[C]3({=}[C]4([H]1000004)[C]5({=}[C]6([H]1000005)([H]1000006))[C]10({-}1)([H]1000044)[C]19([H]1000022)([H]1000023)([H]1000024))[O+.]25[Si]27([C]28([H]1000035)([H]1000036)([H]1000037))([C]29([H]1000038)([H]1000039)([H]1000040))[C]30([H]1000041)([H]1000042)([H]1000043))([H]1000000)([H]1000001).[C]7([H]1000007)([H]1000008){=}[C]8([C]9([H]1000009){=}[C]11([H]1000010)[C]12([H]1000011)([H]1000012)[C]13([C]14({-}8)([H]1000013)[C]15([H]1000014)([H]1000015)[C]16([H]1000016)([H]1000017)[C]17({-}13)([H]1000018)[C]20([C]21([H]1000026)([H]1000027)([H]1000028))([H]1000025)[C]22([H]1000029)([H]1000030)[C]23([H]1000031)([H]1000032)[C]24([H]1000033)([H]1000034)[O]26[H]1000045)[C]18([H]1000019)([H]1000020)([H]1000021))',
    name='IMS8-EQ8.115b:step_remote_tms_migration_and_ring_b_cleavage',
)

# IMS8-EQ8.116:step_ring_closure
IMS8_EQ8_116_step_ring_closure = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004){=}[O+]4[H]1000005>>[C]1([C]2([H]1000002)([H]1000003)[C]3({-}1)([H]1000004)[O+.]4[H]1000005)([H]1000000)([H]1000001)',
    name='IMS8-EQ8.116:step_ring_closure',
)

# IMS8-EQ8.116:step_ring_opening
IMS8_EQ8_116_step_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3({-}1)([H]1000004)[O+.]4[H]1000005)([H]1000000)([H]1000001)>>[C]1([C.]2([H]1000002)([H]1000003))([H]1000000)([H]1000001)[C]3([H]1000004){=}[O+]4[H]1000005',
    name='IMS8-EQ8.116:step_ring_opening',
)

# IMS8-EQ8.117:step_re_silyl_migration_with_elimination
IMS8_EQ8_117_step_re_silyl_migration_with_elimination = mod.Rule.fromDFS(
    s='[Si]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))([C]4([H]1000006)([H]1000007)([H]1000008))[O]5[C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[O+]8{=}[Si]9([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018)>>[Si]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))([C]4([H]1000006)([H]1000007)([H]1000008))[O+]8{=}[Si]9([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018).[O]5([C]6([H]1000009)([H]1000010)[C]7({-}5)([H]1000011)([H]1000012))',
    name='IMS8-EQ8.117:step_re_silyl_migration_with_elimination',
)

# IMS8-EQ8.118:step_re_double_silyl_migration
IMS8_EQ8_118_step_re_double_silyl_migration = mod.Rule.fromDFS(
    s='[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[S]7({=}[O+.]8)({=}[O]9)[C]10([Si]11([C]12([H]1000005)([H]1000006)([H]1000007))([C]13([H]1000008)([H]1000009)([H]1000010))[C]14([H]1000011)([H]1000012)([H]1000013))([C]15([H]1000014)([H]1000015)[C]16([H]1000016)([H]1000017)[C]17(:[C]18([H]1000018):[C]19([H]1000019):[C]20([H]1000020):[C]21([H]1000021):[C]22(:17)([H]1000022)))[C]23([H]1000023)([H]1000024)[C]24([H]1000025)([H]1000026)[C]25([H]1000027)([H]1000028)[C]26([H]1000029)([H]1000030)[C]27([H]1000031)([H]1000032)[C]28([H]1000033)([H]1000034)[S]29[C]30([H]1000035)([H]1000036)[C]31([H]1000037)([H]1000038)[Si]32([C]33([H]1000039)([H]1000040)([H]1000041))([C]34([H]1000042)([H]1000043)([H]1000044))[C]35([H]1000045)([H]1000046)([H]1000047)>>[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[S+]7([O]8[Si]11([C]12([H]1000005)([H]1000006)([H]1000007))([C]13([H]1000008)([H]1000009)([H]1000010))[C]14([H]1000011)([H]1000012)([H]1000013))[O]9[Si]32([C]33([H]1000039)([H]1000040)([H]1000041))([C]34([H]1000042)([H]1000043)([H]1000044))[C]35([H]1000045)([H]1000046)([H]1000047).[C.]10([C]15([H]1000014)([H]1000015)[C]16([H]1000016)([H]1000017)[C]17(:[C]18([H]1000018):[C]19([H]1000019):[C]20([H]1000020):[C]21([H]1000021):[C]22(:17)([H]1000022)))([C]23([H]1000023)([H]1000024)[C]24([H]1000025)([H]1000026)[C]25([H]1000027)([H]1000028)[C]26([H]1000029)([H]1000030)[C]27([H]1000031)([H]1000032)[C]28([H]1000033)([H]1000034)[S]29[C]30([H]1000035)([H]1000036)[C]31({-}10)([H]1000037)([H]1000038))',
    name='IMS8-EQ8.118:step_re_double_silyl_migration',
)

# IMS8-EQ8.119:step_re_methoxyl_migration_with_elimination
IMS8_EQ8_119_step_re_methoxyl_migration_with_elimination = mod.Rule.fromDFS(
    s='[O]1([C]2([H]1000000)([H]1000001)([H]1000002))[C]3([H]1000003)([H]1000004)[C]4([O]5[C]6([H]1000006)([H]1000007)([H]1000008))([H]1000005)[C]7([H]1000009){=}[O+]8[C]9([H]1000010)([H]1000011)([H]1000012)>>[O]1([C]2([H]1000000)([H]1000001)([H]1000002))[C]7([H]1000009){=}[O+]8[C]9([H]1000010)([H]1000011)([H]1000012).[C]3([H]1000003)([H]1000004){=}[C]4([H]1000005)[O]5[C]6([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.119:step_re_methoxyl_migration_with_elimination',
)

# IMS8-EQ8.12:step_inductive_cleavage
IMS8_EQ8_12_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+]3{=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O]3{=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.12:step_inductive_cleavage',
)

# IMS8-EQ8.120:step_re_double_acetyl_migration  [1 hydrogen migration(s) inferred]
IMS8_EQ8_120_step_re_double_acetyl_migration = mod.Rule.fromDFS(
    s='[C+]1([C]2([C]3([C]4([C]5([C]6([H]1000004)([H]1000005)[O]20[C]21({=}[O]22)[C]23([H]1000015)([H]1000016)([H]1000017))([H]1000003)[O]7{-}1)([H]1000002)[O]16[C]17({=}[O]18)[C]19([H]1000012)([H]1000013)([H]1000014))([H]1000018)[O]12[C]13({=}[O]14)[C]15([H]1000009)([H]1000010)([H]1000011))([H]1000001)[O]8[C]9({=}[O]10)[C]11([H]1000006)([H]1000007)([H]1000008))([H]1000000)>>[C]1({=}[C]2([H]1000001)[C]3([C]4([C]5([C]6([H]1000004)([H]1000005)[O]20[C]21({=}[O]22)[C]23([H]1000015)([H]1000016)([H]1000017))([H]1000003)[O]7{-}1)([H]1000002)[O]16[H]1000018){=}[O]12)([H]1000000).[O+]8([C]9({=}[O]10)[C]11([H]1000006)([H]1000007)([H]1000008))([C]13({=}[O]14)[C]15([H]1000009)([H]1000010)([H]1000011))[C]17({=}[O]18)[C]19([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.120:step_re_double_acetyl_migration',
)

# IMS8-EQ8.121:step_co_loss_1
IMS8_EQ8_121_step_co_loss_1 = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3(:[C]8([C]6([C]5(:[C]4({-}1):[C]13([H]1000004):[C]14([H]1000005):[C]15([H]1000006):[C]16(:5)([H]1000007))){=}[O]7):[C]12([H]1000003):[C]11([H]1000002):[C]10([H]1000001):[C]9(:3)([H]1000000)))>>[C-]1{#}[O+]2.[C]3([C]4(:[C]5([C]6({=}[O+.]7)[C]8(:3):[C]12([H]1000003):[C]11([H]1000002):[C]10([H]1000001):[C]9(:3)([H]1000000)):[C]16([H]1000007):[C]15([H]1000006):[C]14([H]1000005):[C]13(:4)([H]1000004)))',
    name='IMS8-EQ8.121:step_co_loss_1',
)

# IMS8-EQ8.121:step_co_loss_2
IMS8_EQ8_121_step_co_loss_2 = mod.Rule.fromDFS(
    s='[C-]1{#}[O+]2.[C]3([C]4(:[C]5([C]6({=}[O+.]7)[C]8(:3):[C]12([H]1000003):[C]11([H]1000002):[C]10([H]1000001):[C]9(:3)([H]1000000)):[C]16([H]1000007):[C]15([H]1000006):[C]14([H]1000005):[C]13(:4)([H]1000004)))>>[C-]1{#}[O+]2.[C]3([C]4(:[C]5([C]8({-}3){=}[C]12([H]1000003)[C+]11([H]1000002)[C.]10([H]1000001)[C]9({=}3)([H]1000000)):[C]16([H]1000007):[C]15([H]1000006):[C]14([H]1000005):[C]13(:4)([H]1000004))).[C-]6{#}[O+]7',
    name='IMS8-EQ8.121:step_co_loss_2',
)

# IMS8-EQ8.122:step_ortho_cyclization
IMS8_EQ8_122_step_ortho_cyclization = mod.Rule.fromDFS(
    s='[N+.]1({=}[C]2([C]3([H]1000000){=}[C]4([H]1000001)[C]5([H]1000002){=}[C]6({-}1)([H]1000003))[N]7([C]8([H]1000004)([H]1000005)([H]1000006))[C]9({=}[O]10)[C]11(:[C]12([H]17):[C]13([H]1000007):[C]14([H]1000008):[C]15([H]1000009):[C]16(:11)([H]1000010)))>>[N+]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[N]7([C]8([H]1000004)([H]1000005)([H]1000006))[C]9({=}[O]10)[C.]11([C]12({-}1)([H]17)[C]13([H]1000007){=}[C]14([H]1000008)[C]15([H]1000009){=}[C]16({-}11)([H]1000010)))',
    name='IMS8-EQ8.122:step_ortho_cyclization',
)

# IMS8-EQ8.122:step_co_elimination
IMS8_EQ8_122_step_co_elimination = mod.Rule.fromDFS(
    s='[N+]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[N]7([C]8([H]1000004)([H]1000005)([H]1000006))[C]9({=}[O]10)[C.]11([C]12({-}1)([H]17)[C]13([H]1000007){=}[C]14([H]1000008)[C]15([H]1000009){=}[C]16({-}11)([H]1000010)))>>[N+]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[N]7([C]8([H]1000004)([H]1000005)([H]1000006))[C.]11([C]12({-}1)([H]17)[C]13([H]1000007){=}[C]14([H]1000008)[C]15([H]1000009){=}[C]16({-}11)([H]1000010))).[C-]9{#}[O+]10',
    name='IMS8-EQ8.122:step_co_elimination',
)

# IMS8-EQ8.122:step_hydrogen_atom_loss
IMS8_EQ8_122_step_hydrogen_atom_loss = mod.Rule.fromDFS(
    s='[N+]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[N]7([C]8([H]1000004)([H]1000005)([H]1000006))[C.]11([C]12({-}1)([H]17)[C]13([H]1000007){=}[C]14([H]1000008)[C]15([H]1000009){=}[C]16({-}11)([H]1000010))).[C-]9{#}[O+]10>>[N+]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003)):[N]7([C]8([H]1000004)([H]1000005)([H]1000006)):[C]11(:[C]12(:1):[C]13([H]1000007):[C]14([H]1000008):[C]15([H]1000009):[C]16(:11)([H]1000010))).[C-]9{#}[O+]10.[H.]17',
    name='IMS8-EQ8.122:step_hydrogen_atom_loss',
)

# IMS8-EQ8.123:step_h3po4_elimination
IMS8_EQ8_123_step_h3po4_elimination = mod.Rule.fromDFS(
    s='[P]1({=}[O+.]2)([O]3[C]20(:[C]21([H]41):[C]22([H]1000004):[C]23([H]1000005):[C]24([H]1000006):[C]25(:20)([H]1000007)))([O]4[C]10(:[C]11([H]40):[C]12([H]1000000):[C]13([H]1000001):[C]14([H]1000002):[C]15(:10)([H]1000003)))[O]5[C]30(:[C]31([H]42):[C]32([H]1000008):[C]33([H]1000009):[C]34([H]1000010):[C]35(:30)([H]1000011))>>[P]1([O]2[H]40)([O]3[H]41)({=}[O]4)[O]5[H]42.[C.]10([C+]11([C]12([H]1000000){=}[C]13([H]1000001)[C]14([H]1000002){=}[C]15({-}10)([H]1000003))[C]20(:[C]21(:[C]22([H]1000004):[C]23([H]1000005):[C]24([H]1000006):[C]25(:20)([H]1000007))[C]30(:[C]31({-}10):[C]32([H]1000008):[C]33([H]1000009):[C]34([H]1000010):[C]35(:30)([H]1000011))))',
    name='IMS8-EQ8.123:step_h3po4_elimination',
)

# IMS8-EQ8.124:step_phenyl_migration
IMS8_EQ8_124_step_phenyl_migration = mod.Rule.fromDFS(
    s='[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[N+]7([O]8[H]10){=}[O]9>>[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[O+]8([H]10)[N]7{=}[O]9',
    name='IMS8-EQ8.124:step_phenyl_migration',
)

# IMS8-EQ8.13:step_hydrogen_rearrangement
IMS8_EQ8_13_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]6)([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[O+]3{=}[C]4([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[O+]3([H]6){=}[C]4([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007)',
    name='IMS8-EQ8.13:step_hydrogen_rearrangement',
)

# IMS8-EQ8.14a:step_hydrogen_rearrangement
IMS8_EQ8_14a_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]4)([H]1000000)([H]1000001)[C]5([H]1000002)([H]1000003)[O+]8{=}[C]9([H]1000004)([H]1000005)>>[C]1([H]1000000)([H]1000001){=}[C]5([H]1000002)([H]1000003).[H]4[O+]8{=}[C]9([H]1000004)([H]1000005)',
    name='IMS8-EQ8.14a:step_hydrogen_rearrangement',
)

# IMS8-EQ8.14b:step_inductive_cleavage
IMS8_EQ8_14b_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[O+]8{=}[C]9([H]1000005)([H]1000006)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]5([H]1000003)([H]1000004).[O]8{=}[C]9([H]1000005)([H]1000006)',
    name='IMS8-EQ8.14b:step_inductive_cleavage',
)

# IMS8-EQ8.15a:step_hydrogen_rearrangement
IMS8_EQ8_15a_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[O+]7([H]1000005)[C]9([H]1000006)([H]1000007)[C]10([H]20)([H]1000008)[C]11([H]1000009){=}[C]12([H]1000010)([H]1000011)>>[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[O+]7([H]20)([H]1000005).[C]9([H]1000006)([H]1000007){=}[C]10([H]1000008)[C]11([H]1000009){=}[C]12([H]1000010)([H]1000011)',
    name='IMS8-EQ8.15a:step_hydrogen_rearrangement',
)

# IMS8-EQ8.15b:step_hydrogen_rearrangement
IMS8_EQ8_15b_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[O+]7([H]1000005)[C]9([H]1000006)([H]1000007)[C]10([H]20)([H]1000008)[C]11([H]1000009){=}[C]12([H]1000010)([H]1000011)>>[C]1(:[C]2([H]1000000):[C]3([H]1000001):[C]4([H]1000002):[C]5([H]1000003):[C]6(:1)([H]1000004))[O]7[H]1000005.[C+]9([H]1000006)([H]1000007)[C]10([H]1000008){=}[C]11([H]1000009)[C]12([H]20)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.15b:step_hydrogen_rearrangement',
)

# IMS8-EQ8.16a:step_rH_hydroxyl_H_rearrangement
IMS8_EQ8_16a_step_rH_hydroxyl_H_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([O]6[H]8)([H]1000005)[C]7([H]1000006)([H]1000007)([H]1000008)>>[C]1([O+.]2[H]8)([C]3([H]1000000)([H]1000001)([H]1000002)){=}[C]4([H]1000003)([H]1000004).[C]5({=}[O]6)([H]1000005)[C]7([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.16a:step_rH_hydroxyl_H_rearrangement',
)

# IMS8-EQ8.16b:step_rH_gamma_CH_rearrangement
IMS8_EQ8_16b_step_rH_gamma_CH_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([O]6[H]1000006)([H]1000005)[C]7([H]8)([H]1000007)([H]1000008)>>[C]1([O+.]2[H]8)([C]3([H]1000000)([H]1000001)([H]1000002)){=}[C]4([H]1000003)([H]1000004).[C]5([O]6[H]1000006)([H]1000005){=}[C]7([H]1000007)([H]1000008)',
    name='IMS8-EQ8.16b:step_rH_gamma_CH_rearrangement',
)

# IMS8-EQ8.17:step_rH_hydroxyl_H_to_ester_carbonyl
IMS8_EQ8_17_step_rH_hydroxyl_H_to_ester_carbonyl = mod.Rule.fromDFS(
    s='[C]1([O]2[H]13)([C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9({=}[O+.]10)[O]11[C]12([H]1000014)([H]1000015)([H]1000016)>>[C]1([O.]2)([C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9({=}[O+]10[H]13)[O]11[C]12([H]1000014)([H]1000015)([H]1000016)',
    name='IMS8-EQ8.17:step_rH_hydroxyl_H_to_ester_carbonyl',
)

# IMS8-EQ8.17:step_alpha_cleavage_to_aldehyde
IMS8_EQ8_17_step_alpha_cleavage_to_aldehyde = mod.Rule.fromDFS(
    s='[C]1([O.]2)([C]3([H]1000001)([H]1000002)([H]1000003))([H]1000000)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9({=}[O+]10[H]13)[O]11[C]12([H]1000014)([H]1000015)([H]1000016)>>[C]1({=}[O]2)([H]1000000)[C]3([H]1000001)([H]1000002)([H]1000003).[C.]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9({=}[O+]10[H]13)[O]11[C]12([H]1000014)([H]1000015)([H]1000016)',
    name='IMS8-EQ8.17:step_alpha_cleavage_to_aldehyde',
)

# IMS8-EQ8.18a:step_heterolytic_cleavage
IMS8_EQ8_18a_step_heterolytic_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[O+]2([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C]1([H]1000000)([H]1000001)([H]1000002)[O]2[H]1000003.[C+]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.18a:step_heterolytic_cleavage',
)

# IMS8-EQ8.19:step_gamma_H_transfer
IMS8_EQ8_19_step_gamma_H_transfer = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]8)([H]1000007)([H]1000008)){=}[O+.]6>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)([H]1000008)){=}[O+]6[H]8',
    name='IMS8-EQ8.19:step_gamma_H_transfer',
)

# IMS8-EQ8.1a:step_h_shift_1_3  [1 hydrogen migration(s) inferred]
IMS8_EQ8_1a_step_h_shift_1_3 = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C+]2([H]1000002)[C]3([H]1000003)([H]1000009)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C]1([H]1000000)([H]1000001)([H]1000009)[C+]2([H]1000002)[C.]3([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.1a:step_h_shift_1_3',
)

# IMS8-EQ8.1b:step_alpha_cleavage
IMS8_EQ8_1b_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C+]4([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[C]3([H]1000005)[C+]4([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.1b:step_alpha_cleavage',
)

# IMS8-EQ8.1c:step_methane_loss  [1 hydrogen migration(s) inferred]
IMS8_EQ8_1c_step_methane_loss = mod.Rule.fromDFS(
    s='[C]2([H]1000000)([H]1000006){=}[C]3([H]1000001)[C+]4([H]1000002)[C]5([H]1000003)([H]1000004)([H]1000005)>>[C+]2(:[C]3([H]1000001):[C]4(:2)([H]1000002))([H]1000000).[C]5([H]1000003)([H]1000004)([H]1000005)([H]1000006)',
    name='IMS8-EQ8.1c:step_methane_loss',
)

# IMS8-EQ8.1d:step_alpha_cleavage
IMS8_EQ8_1d_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C+]1([H]1000000)([H]1000001)[C.]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C+]1([H]1000000)([H]1000001)[C]2([H]1000002){=}[C]3([H]1000003)([H]1000004).[C.]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.1d:step_alpha_cleavage',
)

# IMS8-EQ8.1f:step_h_shift_1_5  [1 hydrogen migration(s) inferred]
IMS8_EQ8_1f_step_h_shift_1_5 = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C+]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000009)[C+]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)([H]1000008)',
    name='IMS8-EQ8.1f:step_h_shift_1_5',
)

# IMS8-EQ8.1g:step_alpha_cleavage
IMS8_EQ8_1g_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C+]4([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[C.]3([H]1000004)([H]1000005)[C+]4([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.1g:step_alpha_cleavage',
)

# IMS8-EQ8.20a:step_rH_six_membered_formaldehyde_loss
IMS8_EQ8_20a_step_rH_six_membered_formaldehyde_loss = mod.Rule.fromDFS(
    s='[C]1([O]2[H]8)([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4({=}[C]5([H]1000004)[C]6([H]1000005){=}[C]7([H]1000006)[C.]9([H]1000007)[C+]10({-}4)([H]1000008))>>[C]1([H]1000000)([H]1000001){=}[O]2.[C]3([H]1000002)([H]1000003){=}[C]4([C]5([H]8)([H]1000004)[C]6([H]1000005){=}[C]7([H]1000006)[C.]9([H]1000007)[C+]10({-}4)([H]1000008))',
    name='IMS8-EQ8.20a:step_rH_six_membered_formaldehyde_loss',
)

# IMS8-EQ8.20b:step_rH_four_membered_formaldehyde_loss
IMS8_EQ8_20b_step_rH_four_membered_formaldehyde_loss = mod.Rule.fromDFS(
    s='[C]1([O]2[H]8)([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4({=}[C]5([H]1000004)[C]6([H]1000005){=}[C]7([H]1000006)[C.]9([H]1000007)[C+]10({-}4)([H]1000008))>>[C]1([H]1000000)([H]1000001){=}[O]2.[C]3([H]8)([H]1000002)([H]1000003)[C]4({=}[C]5([H]1000004)[C]6([H]1000005){=}[C]7([H]1000006)[C.]9([H]1000007)[C+]10({-}4)([H]1000008))',
    name='IMS8-EQ8.20b:step_rH_four_membered_formaldehyde_loss',
)

# IMS8-EQ8.21a:step_gamma_H_beta_cleavage
IMS8_EQ8_21a_step_gamma_H_beta_cleavage = mod.Rule.fromDFS(
    s='[C]1({=}[O]2)([C]3([H]1000000)([H]1000001)([H]1000002))[N]4([C]5([H]1000003)([H]1000004)([H]1000005))[C]6([C]7([H]12)([H]1000007)[C]8([H]1000008)([H]1000009)[C]9([C]10([C]11({-}6)([H]1000011)([H]1000012))([H]1000010)[C]14([H]1000016)([H]1000017)[C]15([H]1000018)([H]1000019)[C]16([C]17({-}9)([H]1000021)[C]18([H]1000022)([H]1000023)[C]19([H]1000024)([H]1000025)[C]20([C]21({-}16)([H]1000026)[C]23([H]1000030)([H]1000031)[C]24([H]1000032)([H]1000033)[C]25({-}20)([H]1000034)[C]26([H]1000035)([H]1000036)[N+.]27([H]1000037)([H]1000038))([C]22([H]1000027)([H]1000028)([H]1000029)))([H]1000020))([C]13([H]1000013)([H]1000014)([H]1000015)))([H]1000006)>>[C]1([O]2[H]12)([C]3([H]1000000)([H]1000001)([H]1000002)){=}[N]4[C]5([H]1000003)([H]1000004)([H]1000005).[C]6({=}[C]7([H]1000007)[C]8([H]1000008)([H]1000009)[C]9([C]10([C]11({-}6)([H]1000011)([H]1000012))([H]1000010)[C]14([H]1000016)([H]1000017)[C]15([H]1000018)([H]1000019)[C]16([C]17({-}9)([H]1000021)[C]18([H]1000022)([H]1000023)[C]19([H]1000024)([H]1000025)[C]20([C]21({-}16)([H]1000026)[C]23([H]1000030)([H]1000031)[C]24([H]1000032)([H]1000033)[C]25({-}20)([H]1000034)[C]26([H]1000035)([H]1000036)[N+.]27([H]1000037)([H]1000038))([C]22([H]1000027)([H]1000028)([H]1000029)))([H]1000020))([C]13([H]1000013)([H]1000014)([H]1000015)))([H]1000006)',
    name='IMS8-EQ8.21a:step_gamma_H_beta_cleavage',
)

# IMS8-EQ8.21b:step_alpha_cleavage
IMS8_EQ8_21b_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([O]2[H]12)([C]3([H]1000000)([H]1000001)([H]1000002)){=}[N]4[C]5([H]1000003)([H]1000004)([H]1000005).[C]6({=}[C]7([H]1000007)[C]8([H]1000008)([H]1000009)[C]9([C]10([C]11({-}6)([H]1000011)([H]1000012))([H]1000010)[C]14([H]1000016)([H]1000017)[C]15([H]1000018)([H]1000019)[C]16([C]17({-}9)([H]1000021)[C]18([H]1000022)([H]1000023)[C]19([H]1000024)([H]1000025)[C]20([C]21({-}16)([H]1000026)[C]23([H]1000030)([H]1000031)[C]24([H]1000032)([H]1000033)[C]25({-}20)([H]1000034)[C]26([H]1000035)([H]1000036)[N+.]27([H]1000037)([H]1000038))([C]22([H]1000027)([H]1000028)([H]1000029)))([H]1000020))([C]13([H]1000013)([H]1000014)([H]1000015)))([H]1000006)>>[C]1([O]2[H]12)([C]3([H]1000000)([H]1000001)([H]1000002)){=}[N]4[C]5([H]1000003)([H]1000004)([H]1000005).[C]6({=}[C]7([H]1000007)[C]8([H]1000008)([H]1000009)[C]9([C]10([C]11({-}6)([H]1000011)([H]1000012))([H]1000010)[C]14([H]1000016)([H]1000017)[C]15([H]1000018)([H]1000019)[C]16([C]17({-}9)([H]1000021)[C]18([H]1000022)([H]1000023)[C]19([H]1000024)([H]1000025)[C]20([C]21({-}16)([H]1000026)[C]23([H]1000030)([H]1000031)[C]24([H]1000032)([H]1000033)[C.]25({-}20)([H]1000034))([C]22([H]1000027)([H]1000028)([H]1000029)))([H]1000020))([C]13([H]1000013)([H]1000014)([H]1000015)))([H]1000006).[C]26([H]1000035)([H]1000036){=}[N+]27([H]1000037)([H]1000038)',
    name='IMS8-EQ8.21b:step_alpha_cleavage',
)

# IMS8-EQ8.22:step_rH
IMS8_EQ8_22_step_rH = mod.Rule.fromDFS(
    s='[C+]1([O]2[H]12)([H]1000000)[C]3(:[C]4([H]1000001):[C]5([H]1000002):[C]6(:[C]7([H]1000003):[C]8(:3)([H]1000004))[C]9([H]1000005)([H]1000006)[O]10[C]11([H]1000007)([H]1000008)([H]1000009))>>[C]1({=}[O]2)([H]1000000)[C]3([C+]4([H]1000001)[C]5([H]1000002){=}[C]6([C]7([H]1000003){=}[C]8({-}3)([H]1000004))[C]9([H]1000005)([H]1000006)[O]10[C]11([H]1000007)([H]1000008)([H]1000009))([H]12)',
    name='IMS8-EQ8.22:step_rH',
)

# IMS8-EQ8.22:step_ring_walk
IMS8_EQ8_22_step_ring_walk = mod.Rule.fromDFS(
    s='[C]1({=}[O]2)([H]1000000)[C]3([C+]4([H]1000001)[C]5([H]1000002){=}[C]6([C]7([H]1000003){=}[C]8({-}3)([H]1000004))[C]9([H]1000005)([H]1000006)[O]10[C]11([H]1000007)([H]1000008)([H]1000009))([H]12)>>[C]1({=}[O]2)([H]1000000)[O+]10([C]9([H]1000005)([H]1000006)[C]6(:[C]5([H]1000002):[C]4([H]1000001):[C]3([H]12):[C]8([H]1000004):[C]7(:6)([H]1000003)))[C]11([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.22:step_ring_walk',
)

# IMS8-EQ8.22:step_i
IMS8_EQ8_22_step_i = mod.Rule.fromDFS(
    s='[C]1({=}[O]2)([H]1000000)[O+]10([C]9([H]1000005)([H]1000006)[C]6(:[C]5([H]1000002):[C]4([H]1000001):[C]3([H]12):[C]8([H]1000004):[C]7(:6)([H]1000003)))[C]11([H]1000007)([H]1000008)([H]1000009)>>[C]1({=}[O]2)([H]1000000)[O]10[C]11([H]1000007)([H]1000008)([H]1000009).[C]3(:[C]4([H]1000001):[C]5([H]1000002):[C]6(:[C]7([H]1000003):[C]8(:3)([H]1000004))[C+]9([H]1000005)([H]1000006))([H]12)',
    name='IMS8-EQ8.22:step_i',
)

# IMS8-EQ8.24a:step_cl_loss
IMS8_EQ8_24a_step_cl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000001)([H]1000002)[C]4([C]5([H]1000004)([H]1000005)[C]6({-}1)([H]1000006)[Cl]9)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008)){=}[O+.]8)([H]1000000)>>[C]1({=}[C]6([H]1000006)[C]5([H]1000004)([H]1000005)[C]4([C]3([H]1000001)([H]1000002)[C]2{#}[O+]8)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008))([H]1000000).[Cl.]9',
    name='IMS8-EQ8.24a:step_cl_loss',
)

# IMS8-EQ8.24b:step_cl_loss
IMS8_EQ8_24b_step_cl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000001)([H]1000002)[C]4([C]5([H]1000004)([H]1000005)[C]6({-}1)([H]1000006)[Cl]9)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008)){=}[O+.]8)([H]1000000)>>[C]1({=}[C]6([H]1000006)[C]5([H]1000004)([H]1000005)[C]4([C]3([H]1000001)([H]1000002)[C]2{#}[O+]8)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008))([H]1000000).[Cl.]9',
    name='IMS8-EQ8.24b:step_cl_loss',
)

# IMS8-EQ8.24c:step_cl_loss
IMS8_EQ8_24c_step_cl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000001)([H]1000002)[C]4([C]5([H]1000004)([H]1000005)[C]6({-}1)([H]1000006)[Cl]9)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008)){=}[O+.]8)([H]1000000)>>[C]1({=}[C]6([H]1000006)[C]5([H]1000004)([H]1000005)[C]4([C]3([H]1000001)([H]1000002)[C]2{#}[O+]8)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008))([H]1000000).[Cl.]9',
    name='IMS8-EQ8.24c:step_cl_loss',
)

# IMS8-EQ8.24d:step_cl_loss
IMS8_EQ8_24d_step_cl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000001)([H]1000002)[C]4([C]5([H]1000004)([H]1000005)[C]6({-}1)([H]1000006)[Cl]9)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008)){=}[O+.]8)([H]1000000)>>[C]1({=}[C]6([H]1000006)[C]5([H]1000004)([H]1000005)[C]4([C]3([H]1000001)([H]1000002)[C]2{#}[O+]8)([H]1000003)[C]7({-}1)([H]1000007)([H]1000008))([H]1000000).[Cl.]9',
    name='IMS8-EQ8.24d:step_cl_loss',
)

# IMS8-EQ8.25a:step_retro_da
IMS8_EQ8_25a_step_retro_da = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}2)([H]1000008)[C]7([C]8([H]12)([H]1000010)[C]9({-}1){=}[O+.]11)([H]1000009)[C]10({-}1)([H]1000011)([H]1000012))([H]1000001))([H]1000000)>>[C]1({=}[C]9([C]8([H]1000010){=}[C]7([H]1000009)[C]10({-}1)([H]1000011)([H]1000012))[O+.]11[H]12)([H]1000000).[C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({=}2)([H]1000008))([H]1000001)',
    name='IMS8-EQ8.25a:step_retro_da',
)

# IMS8-EQ8.25b:step_retro_da
IMS8_EQ8_25b_step_retro_da = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}2)([H]1000008)[C]7([C]8([H]12)([H]1000010)[C]9({-}1){=}[O+.]11)([H]1000009)[C]10({-}1)([H]1000011)([H]1000012))([H]1000001))([H]1000000)>>[C]1({=}[C]9([C]8([H]1000010){=}[C]7([H]1000009)[C]10({-}1)([H]1000011)([H]1000012))[O+.]11[H]12)([H]1000000).[C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({=}2)([H]1000008))([H]1000001)',
    name='IMS8-EQ8.25b:step_retro_da',
)

# IMS8-EQ8.26a:step_hydrogen_rearrangement
IMS8_EQ8_26a_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))([H]12)[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000)[O+.]7[H]1000009>>[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000)[O+]7([H]12)([H]1000009)',
    name='IMS8-EQ8.26a:step_hydrogen_rearrangement',
)

# IMS8-EQ8.26a:step_inductive_cleavage
IMS8_EQ8_26a_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000)[O+]7([H]12)([H]1000009)>>[C+]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000).[O]7([H]12)([H]1000009)',
    name='IMS8-EQ8.26a:step_inductive_cleavage',
)

# IMS8-EQ8.26b:step_hydrogen_rearrangement
IMS8_EQ8_26b_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))([H]12)[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000)[O+.]7[H]1000009>>[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000)[O+]7([H]12)([H]1000009)',
    name='IMS8-EQ8.26b:step_hydrogen_rearrangement',
)

# IMS8-EQ8.26b:step_inductive_cleavage
IMS8_EQ8_26b_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000)[O+]7([H]12)([H]1000009)>>[C+]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]8([C]9([H]1000010)([H]1000011)([H]1000012))([C]10([H]1000013)([H]1000014)([H]1000015))[C]11([H]1000016)([H]1000017)([H]1000018))([H]1000000).[O]7([H]12)([H]1000009)',
    name='IMS8-EQ8.26b:step_inductive_cleavage',
)

# IMS8-EQ8.29a:step_anchimeric_displacement
IMS8_EQ8_29a_step_anchimeric_displacement = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000003)[O]11[C]12({=}[O+]13[H]1000013)[C]14([H]1000014)([H]1000015)([H]1000016))([H]1000000)[O]7[C]8({=}[O]9)[C]10([H]1000010)([H]1000011)([H]1000012)>>[C]1([C]2([H]1000001)([H]1000002)[C]3([C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000003)[O]9[C+]8([O]7{-}1)[C]10([H]1000010)([H]1000011)([H]1000012))([H]1000000).[O]11{=}[C]12([O]13[H]1000013)[C]14([H]1000014)([H]1000015)([H]1000016)',
    name='IMS8-EQ8.29a:step_anchimeric_displacement',
)

# IMS8-EQ8.29b:step_inductive_cleavage
IMS8_EQ8_29b_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000003)[O]11[C]12({=}[O+]13[H]1000013)[C]14([H]1000014)([H]1000015)([H]1000016))([H]1000000)[O]7[C]8({=}[O]9)[C]10([H]1000010)([H]1000011)([H]1000012)>>[C]1([C]2([H]1000001)([H]1000002)[C+]3([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000000)[O]7[C]8({=}[O]9)[C]10([H]1000010)([H]1000011)([H]1000012).[O]11{=}[C]12([O]13[H]1000013)[C]14([H]1000014)([H]1000015)([H]1000016)',
    name='IMS8-EQ8.29b:step_inductive_cleavage',
)

# IMS8-EQ8.2a:step_alpha_1_1
IMS8_EQ8_2a_step_alpha_1_1 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5({=}[O+.]6)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C.]4([H]1000007)([H]1000008).[C]5({#}[O+]6)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.2a:step_alpha_1_1',
)

# IMS8-EQ8.2b:step_inductive_2_1
IMS8_EQ8_2b_step_inductive_2_1 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5({=}[O+.]6)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C+]4([H]1000007)([H]1000008).[C.]5({=}[O]6)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.2b:step_inductive_2_1',
)

# IMS8-EQ8.2c:step_alpha_0_7
IMS8_EQ8_2c_step_alpha_0_7 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5({=}[O+.]6)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5{#}[O+]6.[C.]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.2c:step_alpha_0_7',
)

# IMS8-EQ8.2d:step_gamma_H_rearrangement
IMS8_EQ8_2d_step_gamma_H_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]8)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({=}[O+.]6)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({=}[O+]6[H]8)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.2d:step_gamma_H_rearrangement',
)

# IMS8-EQ8.2d:step_alpha_0_6
IMS8_EQ8_2d_step_alpha_0_6 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({=}[O+]6[H]8)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[C]3([H]1000004)([H]1000005).[C]4([H]1000006)([H]1000007){=}[C]5([O+.]6[H]8)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.2d:step_alpha_0_6',
)

# IMS8-EQ8.2e:step_gamma_H_rearrangement
IMS8_EQ8_2e_step_gamma_H_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]8)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({=}[O+.]6)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({=}[O+]6[H]8)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.2e:step_gamma_H_rearrangement',
)

# IMS8-EQ8.2e:step_inductive_1_6
IMS8_EQ8_2e_step_inductive_1_6 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({=}[O+]6[H]8)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C+]3([H]1000004)([H]1000005).[C]4([H]1000006)([H]1000007){=}[C]5([O]6[H]8)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.2e:step_inductive_1_6',
)

# IMS8-EQ8.2f:step_inductive_4_5
IMS8_EQ8_2f_step_inductive_4_5 = mod.Rule.fromDFS(
    s='[C]5({#}[O+]6)[C]7([H]1000000)([H]1000001)([H]1000002)>>[C-]5{#}[O+]6.[C+]7([H]1000000)([H]1000001)([H]1000002)',
    name='IMS8-EQ8.2f:step_inductive_4_5',
)

# IMS8-EQ8.2g:step_inductive_3_1
IMS8_EQ8_2g_step_inductive_3_1 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C+]4([H]1000007)([H]1000008)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[C]3([H]1000005)([H]1000006){=}[C]4([H]1000007)([H]1000008)',
    name='IMS8-EQ8.2g:step_inductive_3_1',
)

# IMS8-EQ8.2h:step_inductive_2_7
IMS8_EQ8_2h_step_inductive_2_7 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5{#}[O+]6>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C+]4([H]1000007)([H]1000008).[C-]5{#}[O+]6',
    name='IMS8-EQ8.2h:step_inductive_2_7',
)

# IMS8-EQ8.2i:step_rH_2_0
IMS8_EQ8_2i_step_rH_2_0 = mod.Rule.fromDFS(
    s='[C]4([H]1000000)([H]1000001){=}[C]5([O+.]6[H]8)[C]7([H]1000002)([H]1000003)([H]1000004)>>[C.]4([H]8)([H]1000000)([H]1000001).[C]5({#}[O+]6)[C]7([H]1000002)([H]1000003)([H]1000004)',
    name='IMS8-EQ8.2i:step_rH_2_0',
)

# IMS8-EQ8.2j:step_alpha_3_8
IMS8_EQ8_2j_step_alpha_3_8 = mod.Rule.fromDFS(
    s='[C]1([H]9)([H]1000000)([H]1000001)[C.]2([H]1000002)[C+]3([H]1000003)([H]1000004)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C+]3([H]1000003)([H]1000004).[H.]9',
    name='IMS8-EQ8.2j:step_alpha_3_8',
)

# IMS8-EQ8.30a:step_ring_opening
IMS8_EQ8_30a_step_ring_opening = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([C]3([C]4([O]5[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)([H]1000007))([H]1000002)[C]8([H]1000008)([H]1000009)[C]9({-}3)([H]1000010)[C]10([H]1000011)([H]1000012)[C]11({-}1)([H]1000013)([H]1000014))([H]1000001))>>[C]1([O]2[H]1000000)({=}[C]3([H]1000001)[C]9([C]8([H]1000008)([H]1000009)[C]4([H]1000002){=}[O+]5[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)([H]1000007))([H]1000010)[C]10([H]1000011)([H]1000012)[C]11({-}1)([H]1000013)([H]1000014))',
    name='IMS8-EQ8.30a:step_ring_opening',
)

# IMS8-EQ8.30a:step_retro_ene_elimination
IMS8_EQ8_30a_step_retro_ene_elimination = mod.Rule.fromDFS(
    s='[C]1([O]2[H]1000000)({=}[C]3([H]1000001)[C]9([C]8([H]1000008)([H]1000009)[C]4([H]1000002){=}[O+]5[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)([H]1000007))([H]1000010)[C]10([H]1000011)([H]1000012)[C]11({-}1)([H]1000013)([H]1000014))>>[C]1({=}[O+]2[H]1000000)([C]3([H]1000001){=}[C]9([H]1000010)[C]10([H]1000011)([H]1000012)[C]11({-}1)([H]1000013)([H]1000014)).[C]4([O]5[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)([H]1000007))([H]1000002){=}[C]8([H]1000008)([H]1000009)',
    name='IMS8-EQ8.30a:step_retro_ene_elimination',
)

# IMS8-EQ8.30d:step_inductive_ethanol_loss
IMS8_EQ8_30d_step_inductive_ethanol_loss = mod.Rule.fromDFS(
    s='[C]1({=}[O]2)([C]3([C]8([H]1000008)([H]1000009)[C]4([O+]5([H]1000002)[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)([H]1000007))([H]1000001)[C]9({-}3)([H]1000010)[C]10([H]1000011)([H]1000012)[C]11({-}1)([H]1000013)([H]1000014))([H]1000000))>>[C]1({=}[O]2)([C]3([C]8([H]1000008)([H]1000009)[C+]4([H]1000001)[C]9({-}3)([H]1000010)[C]10([H]1000011)([H]1000012)[C]11({-}1)([H]1000013)([H]1000014))([H]1000000)).[O]5([H]1000002)[C]6([H]1000003)([H]1000004)[C]7([H]1000005)([H]1000006)([H]1000007)',
    name='IMS8-EQ8.30d:step_inductive_ethanol_loss',
)

# IMS8-EQ8.31a:step_methanol_elimination
IMS8_EQ8_31a_step_methanol_elimination = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([C]4([C]5([H]1000004)([H]1000005)[O]13[C]14([H]1000016)([H]1000017)([H]1000018))([H]1000003)[O]6{-}1)([H]1000002)[O]11[C]12([H]1000013)([H]1000014)([H]1000015))([H]1000001)[O]9[C]10([H]1000010)([H]1000011)([H]1000012))([H]1000000)[O+]7([H]1000006)[C]8([H]1000007)([H]1000008)([H]1000009)>>[C]1([C]2([C]3([C]4([C]5([H]1000004)([H]1000005)[O]13[C]14([H]1000016)([H]1000017)([H]1000018))([H]1000003)[O+]6{=}1)([H]1000002)[O]11[C]12([H]1000013)([H]1000014)([H]1000015))([H]1000001)[O]9[C]10([H]1000010)([H]1000011)([H]1000012))([H]1000000).[O]7([H]1000006)[C]8([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.31a:step_methanol_elimination',
)

# IMS8-EQ8.31b:step_methanol_elimination
IMS8_EQ8_31b_step_methanol_elimination = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([C]4([C]5([H]1000004)([H]1000005)[O]13[C]14([H]1000016)([H]1000017)([H]1000018))([H]1000003)[O]6{-}1)([H]1000002)[O]11[C]12([H]1000013)([H]1000014)([H]1000015))([H]1000001)[O]9[C]10([H]1000010)([H]1000011)([H]1000012))([H]1000000)[O+]7([H]1000006)[C]8([H]1000007)([H]1000008)([H]1000009)>>[C]1([C]2([C]3([C]4([C]5([H]1000004)([H]1000005)[O]13[C]14([H]1000016)([H]1000017)([H]1000018))([H]1000003)[O+]6{=}1)([H]1000002)[O]11[C]12([H]1000013)([H]1000014)([H]1000015))([H]1000001)[O]9[C]10([H]1000010)([H]1000011)([H]1000012))([H]1000000).[O]7([H]1000006)[C]8([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.31b:step_methanol_elimination',
)

# IMS8-EQ8.33:step_inductive_cleavage
IMS8_EQ8_33_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C+]6([H]1000010)([H]1000011)>>[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C+]4([H]1000006)([H]1000007).[C]5([H]1000008)([H]1000009){=}[C]6([H]1000010)([H]1000011)',
    name='IMS8-EQ8.33:step_inductive_cleavage',
)

# IMS8-EQ8.34:step_alpha_cleavage
IMS8_EQ8_34_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[N+.]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000001)[C]7([H]1000010)([H]1000011)([H]1000012))([H]1000000)>>[N+]1({=}[C]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000000).[C.]7([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQ8.34:step_alpha_cleavage',
)

# IMS8-EQ8.34:step_retro_diels_alder
IMS8_EQ8_34_step_retro_diels_alder = mod.Rule.fromDFS(
    s='[N+]1({=}[C]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000000).[C.]7([H]1000010)([H]1000011)([H]1000012)>>[N+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000){=}[C]6([H]1000008)([H]1000009).[C]4([H]1000004)([H]1000005){=}[C]5([H]1000006)([H]1000007).[C.]7([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQ8.34:step_retro_diels_alder',
)

# IMS8-EQ8.35:step_gamma_d_rearrangement
IMS8_EQ8_35_step_gamma_d_rearrangement = mod.Rule.fromDFS(
    s='[C+]1([C]2({=}[C]3([H]1000000)([H]1000001))[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6([H]15)([H]16)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)[C]11([H]1000012)([H]1000013)([H]1000014))([O]9[H]1000010)[O]10[H]1000011>>[C]1({=}[C]2([C]3([H]15)([H]1000000)([H]1000001))[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C+]6([H]16)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)[C]11([H]1000012)([H]1000013)([H]1000014))([O]9[H]1000010)[O]10[H]1000011',
    name='IMS8-EQ8.35:step_gamma_d_rearrangement',
)

# IMS8-EQ8.35:step_beta_cleavage
IMS8_EQ8_35_step_beta_cleavage = mod.Rule.fromDFS(
    s='[C]1({=}[C]2([C]3([H]15)([H]1000000)([H]1000001))[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C+]6([H]16)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)[C]11([H]1000012)([H]1000013)([H]1000014))([O]9[H]1000010)[O]10[H]1000011>>[C]1({=}[C]2([C]3([H]15)([H]1000000)([H]1000001))[C+]4([H]1000002)([H]1000003))([O]9[H]1000010)[O]10[H]1000011.[C]5([H]1000004)([H]1000005){=}[C]6([H]16)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)[C]11([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.35:step_beta_cleavage',
)

# IMS8-EQ8.36:step_charge_remote_fragmentation
IMS8_EQ8_36_step_charge_remote_fragmentation = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]20)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]21)([H]1000008)[C]6([H]1000009){=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)[C+]9([O]10[Li]11)[O]12[Li]13>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[C]3([H]1000004)([H]1000005).[C]4([H]1000006)([H]1000007){=}[C]5([H]1000008)[C]6([H]1000009){=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)[C+]9([O]10[Li]11)[O]12[Li]13.[H]20[H]21',
    name='IMS8-EQ8.36:step_charge_remote_fragmentation',
)

# IMS8-EQ8.37a:step_sigma_cleavage  [auto-localized precursor]
IMS8_EQ8_37a_step_sigma_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004)[C+]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C+]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.37a:step_sigma_cleavage',
)

# IMS8-EQ8.37b:step_alpha_cleavage
IMS8_EQ8_37b_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+.]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[O+]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.37b:step_alpha_cleavage',
)

# IMS8-EQ8.37c:step_sigma_cleavage  [auto-localized precursor]
IMS8_EQ8_37c_step_sigma_cleavage = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)([H]1000009)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C+]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.37c:step_sigma_cleavage',
)

# IMS8-EQ8.38a:step_sigma_cleavage  [auto-localized precursor]
IMS8_EQ8_38a_step_sigma_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004)[C+]3([C]4([H]1000006)([H]1000007)([H]1000008))([H]1000005)[C]5([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C+]3([C]4([H]1000006)([H]1000007)([H]1000008))([H]1000005)[C]5([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.38a:step_sigma_cleavage',
)

# IMS8-EQ8.38b:step_sigma_cleavage  [auto-localized precursor]
IMS8_EQ8_38b_step_sigma_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004)[C.]3([C]4([H]1000006)([H]1000007)([H]1000008))([H]1000005)[C]5([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[C.]3([C]4([H]1000006)([H]1000007)([H]1000008))([H]1000005)[C]5([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.38b:step_sigma_cleavage',
)

# IMS8-EQ8.39:step_hydride_shift
IMS8_EQ8_39_step_hydride_shift = mod.Rule.fromDFS(
    s='[C+]1([H]1000000)([H]1000001)[C]2([H]8)([H]1000002)[C]3([H]1000003)([H]1000004)([H]1000005).[C.]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]13([H]1000010)([H]1000011)([H]1000012)>>[C]1([H]8)([H]1000000)([H]1000001)[C+]2([H]1000002)[C]3([H]1000003)([H]1000004)([H]1000005).[C.]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[C]13([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQ8.39:step_hydride_shift',
)

# IMS8-EQ8.3a:step_inductive_cleavage
IMS8_EQ8_3a_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[O+.]5[C]6([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C+]4([H]1000007)([H]1000008).[O.]5[C]6([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.3a:step_inductive_cleavage',
)

# IMS8-EQ8.3c:step_inductive_cleavage
IMS8_EQ8_3c_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[O+.]5[C]6([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C+]3([H]1000005)([H]1000006).[C.]4([H]1000007)([H]1000008)[O]5[C]6([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.3c:step_inductive_cleavage',
)

# IMS8-EQ8.3d:step_alpha_cleavage
IMS8_EQ8_3d_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[O+.]5[C]6([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)([H]1000006).[C]4([H]1000007)([H]1000008){=}[O+]5[C]6([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.3d:step_alpha_cleavage',
)

# IMS8-EQ8.40a:step_alpha_cleavage_ch
IMS8_EQ8_40a_step_alpha_cleavage_ch = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]6)([H]1000003)[F+.]3>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[F+]3.[H.]6',
    name='IMS8-EQ8.40a:step_alpha_cleavage_ch',
)

# IMS8-EQ8.40b:step_alpha_cleavage_cc
IMS8_EQ8_40b_step_alpha_cleavage_cc = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[F+.]3>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[F+]3',
    name='IMS8-EQ8.40b:step_alpha_cleavage_cc',
)

# IMS8-EQ8.41:step_alpha_cleavage
IMS8_EQ8_41_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+.]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[O+]3[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.41:step_alpha_cleavage',
)

# IMS8-EQ8.42a:step_alpha_cleavage
IMS8_EQ8_42a_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[N+.]3([H]1000005)([H]1000006)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[N+]3([H]1000005)([H]1000006)',
    name='IMS8-EQ8.42a:step_alpha_cleavage',
)

# IMS8-EQ8.42b:step_sigma_cleavage
IMS8_EQ8_42b_step_sigma_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[N+.]3([H]1000005)([H]1000006)>>[C+]1([H]1000000)([H]1000001)([H]1000002).[C.]2([H]1000003)([H]1000004)[N]3([H]1000005)([H]1000006)',
    name='IMS8-EQ8.42b:step_sigma_cleavage',
)

# IMS8-EQ8.43a:step_inductive_cleavage
IMS8_EQ8_43a_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+.]3[C]4([H]1000005)([H]1000006)([H]1000007)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O.]3[C]4([H]1000005)([H]1000006)([H]1000007)',
    name='IMS8-EQ8.43a:step_inductive_cleavage',
)

# IMS8-EQ8.43b:step_inductive_cleavage
IMS8_EQ8_43b_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005){=}[O+.]4>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[C.]3([H]1000005){=}[O]4',
    name='IMS8-EQ8.43b:step_inductive_cleavage',
)

# IMS8-EQ8.44a:step_inductive_cleavage
IMS8_EQ8_44a_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O]3[C+]4([H]1000005)([H]1000006)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O]3{=}[C]4([H]1000005)([H]1000006)',
    name='IMS8-EQ8.44a:step_inductive_cleavage',
)

# IMS8-EQ8.44b:step_inductive_cleavage
IMS8_EQ8_44b_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+]3{=}[C]4([H]1000005)([H]1000006)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O]3{=}[C]4([H]1000005)([H]1000006)',
    name='IMS8-EQ8.44b:step_inductive_cleavage',
)

# IMS8-EQ8.45a:step_inductive_cleavage
IMS8_EQ8_45a_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[O+.]3[H]1000002)([C]4([H]1000003)([H]1000004)([H]1000005))([C]5([H]1000006)([H]1000007)([H]1000008))[C]6([H]1000009)([H]1000010)([H]1000011)>>[C]1([C+]2([H]1000000)([H]1000001))([C]4([H]1000003)([H]1000004)([H]1000005))([C]5([H]1000006)([H]1000007)([H]1000008))[C]6([H]1000009)([H]1000010)([H]1000011).[O.]3[H]1000002',
    name='IMS8-EQ8.45a:step_inductive_cleavage',
)

# IMS8-EQ8.45b:step_alpha_cleavage
IMS8_EQ8_45b_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[O+.]3[H]1000002)([C]4([H]1000003)([H]1000004)([H]1000005))([C]5([H]1000006)([H]1000007)([H]1000008))[C]6([H]1000009)([H]1000010)([H]1000011)>>[C.]1([C]4([H]1000003)([H]1000004)([H]1000005))([C]5([H]1000006)([H]1000007)([H]1000008))[C]6([H]1000009)([H]1000010)([H]1000011).[C]2([H]1000000)([H]1000001){=}[O+]3[H]1000002',
    name='IMS8-EQ8.45b:step_alpha_cleavage',
)

# IMS8-EQ8.45c:step_sigma_dissociation
IMS8_EQ8_45c_step_sigma_dissociation = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[O+.]3[H]1000002)([C]4([H]1000003)([H]1000004)([H]1000005))([C]5([H]1000006)([H]1000007)([H]1000008))[C]6([H]1000009)([H]1000010)([H]1000011)>>[C+]1([C]4([H]1000003)([H]1000004)([H]1000005))([C]5([H]1000006)([H]1000007)([H]1000008))[C]6([H]1000009)([H]1000010)([H]1000011).[C.]2([H]1000000)([H]1000001)[O]3[H]1000002',
    name='IMS8-EQ8.45c:step_sigma_dissociation',
)

# IMS8-EQ8.46a:step_alpha_cleavage
IMS8_EQ8_46a_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[O+.]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]13([H]1000023)([H]1000024)([H]1000025))[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)([H]1000022)>>[O+]1({=}[C]2([H]1000000)([H]1000001))[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)([H]1000022).[C.]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]13([H]1000023)([H]1000024)([H]1000025)',
    name='IMS8-EQ8.46a:step_alpha_cleavage',
)

# IMS8-EQ8.46b:step_inductive_cleavage
IMS8_EQ8_46b_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[O+.]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]13([H]1000023)([H]1000024)([H]1000025))[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)([H]1000022)>>[O.]1[C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]13([H]1000023)([H]1000024)([H]1000025).[C+]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)([H]1000022)',
    name='IMS8-EQ8.46b:step_inductive_cleavage',
)

# IMS8-EQ8.46c:step_inductive_cleavage
IMS8_EQ8_46c_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)([H]1000001))[C]7([H]1000002)([H]1000003)[C]8([H]1000004)([H]1000005)[C]9([H]1000006)([H]1000007)[C]10([H]1000008)([H]1000009)[C]11([H]1000010)([H]1000011)[C]12([H]1000012)([H]1000013)([H]1000014)>>[O]1{=}[C]2([H]1000000)([H]1000001).[C+]7([H]1000002)([H]1000003)[C]8([H]1000004)([H]1000005)[C]9([H]1000006)([H]1000007)[C]10([H]1000008)([H]1000009)[C]11([H]1000010)([H]1000011)[C]12([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.46c:step_inductive_cleavage',
)

# IMS8-EQ8.47:step_neighboring_group_displacement
IMS8_EQ8_47_step_neighboring_group_displacement = mod.Rule.fromDFS(
    s='[N]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[N+]6([H]1000010)([H]1000011)([H]1000012)>>[N+]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({-}1)([H]1000008)([H]1000009))([H]1000000)([H]1000001).[N]6([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQ8.47:step_neighboring_group_displacement',
)

# IMS8-EQ8.48:step_alpha_heteroalkene
IMS8_EQ8_48_step_alpha_heteroalkene = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)([H]1000001))[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O+.]1{=}[C]2([H]1000000)([H]1000001).[C]3([C]4([H]1000004)([H]1000005)[C]5({-}3)([H]1000006)([H]1000007))([H]1000002)([H]1000003)',
    name='IMS8-EQ8.48:step_alpha_heteroalkene',
)

# IMS8-EQ8.49:step_alpha_ring_opening
IMS8_EQ8_49_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5({-}1)([H]1000006)([H]1000007))>>[O+]1({=}[C]2([H]1000000)([H]1000001))[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)',
    name='IMS8-EQ8.49:step_alpha_ring_opening',
)

# IMS8-EQ8.49:step_inductive_cleavage
IMS8_EQ8_49_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)([H]1000001))[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O]1{=}[C]2([H]1000000)([H]1000001).[C.]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C+]5([H]1000006)([H]1000007)',
    name='IMS8-EQ8.49:step_inductive_cleavage',
)

# IMS8-EQ8.4a:step_inductive_cleavage
IMS8_EQ8_4a_step_inductive_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5({=}[O+.]6)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C+]4([H]1000007)([H]1000008).[C.]5({=}[O]6)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.4a:step_inductive_cleavage',
)

# IMS8-EQ8.4b:step_alpha_cleavage
IMS8_EQ8_4b_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]4([H]1000007)([H]1000008)[C]5({=}[O+.]6)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C.]4([H]1000007)([H]1000008).[C]5({#}[O+]6)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.4b:step_alpha_cleavage',
)

# IMS8-EQ8.50:step_alpha_ethylene_loss
IMS8_EQ8_50_step_alpha_ethylene_loss = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)([H]1000001))[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O+]1({=}[C]2([H]1000000)([H]1000001))[C.]5([H]1000006)([H]1000007).[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005)',
    name='IMS8-EQ8.50:step_alpha_ethylene_loss',
)

# IMS8-EQ8.51:step_double_inductive_ring_cleavage
IMS8_EQ8_51_step_double_inductive_ring_cleavage = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7({-}1)([H]1000009)([H]1000010))>>[O+]1{#}[C]2[C]3([H]1000000)([H]1000001)([H]1000002).[C]4([C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7({-}4)([H]1000009)([H]1000010))([H]1000003)([H]1000004)',
    name='IMS8-EQ8.51:step_double_inductive_ring_cleavage',
)

# IMS8-EQ8.52:step_double_inductive_retro_cleavage
IMS8_EQ8_52_step_double_inductive_retro_cleavage = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7({-}1)([H]1000009)([H]1000010))>>[O+]1([C]2([C]3([H]1000000)([H]1000001)([H]1000002)){=}[C]4([H]1000003)([H]1000004)){=}[C]7([H]1000009)([H]1000010).[C]5([H]1000005)([H]1000006){=}[C]6([H]1000007)([H]1000008)',
    name='IMS8-EQ8.52:step_double_inductive_retro_cleavage',
)

# IMS8-EQ8.53a:step_alpha_ring_opening
IMS8_EQ8_53a_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1([H]1000000)[C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7({-}2)([H]1000010)([H]1000011))([H]1000001)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)',
    name='IMS8-EQ8.53a:step_alpha_ring_opening',
)

# IMS8-EQ8.53a:step_alpha_homolytic_ring_closure
IMS8_EQ8_53a_step_alpha_homolytic_ring_closure = mod.Rule.fromDFS(
    s='[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C.]7([H]1000010)([H]1000011).[C]3([C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}3)([H]1000008)([H]1000009))([H]1000002)([H]1000003)',
    name='IMS8-EQ8.53a:step_alpha_homolytic_ring_closure',
)

# IMS8-EQ8.53b:step_alpha_ring_opening
IMS8_EQ8_53b_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1([H]1000000)[C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7({-}2)([H]1000010)([H]1000011))([H]1000001)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)',
    name='IMS8-EQ8.53b:step_alpha_ring_opening',
)

# IMS8-EQ8.53b:step_alpha_loss_c2h4
IMS8_EQ8_53b_step_alpha_loss_c2h4 = mod.Rule.fromDFS(
    s='[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C.]5([H]1000006)([H]1000007).[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005)',
    name='IMS8-EQ8.53b:step_alpha_loss_c2h4',
)

# IMS8-EQ8.53b:step_alpha_loss_cnh2n
IMS8_EQ8_53b_step_alpha_loss_cnh2n = mod.Rule.fromDFS(
    s='[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C.]5([H]1000006)([H]1000007).[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C.]7([H]1000010)([H]1000011).[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005).[C]5([H]1000006)([H]1000007){=}[C]6([H]1000008)([H]1000009)',
    name='IMS8-EQ8.53b:step_alpha_loss_cnh2n',
)

# IMS8-EQ8.54:step_alpha_ring_opening
IMS8_EQ8_54_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1([H]1000000)[C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7({-}2)([H]1000010)([H]1000011))([H]1000001)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)',
    name='IMS8-EQ8.54:step_alpha_ring_opening',
)

# IMS8-EQ8.54:step_rh_to_alpha_position  [1 hydrogen migration(s) inferred]
IMS8_EQ8_54_step_rh_to_alpha_position = mod.Rule.fromDFS(
    s='[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000010)([H]1000011)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C.]7([H]1000010)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C]3([H]1000002)([H]1000003)([H]1000011)',
    name='IMS8-EQ8.54:step_rh_to_alpha_position',
)

# IMS8-EQ8.54:step_alpha_alkyl_loss
IMS8_EQ8_54_step_alpha_alkyl_loss = mod.Rule.fromDFS(
    s='[O+]1([H]1000000){=}[C]2([H]1000001)[C.]7([H]1000011)[C]6([H]1000009)([H]1000010)[C]5([H]1000007)([H]1000008)[C]4([H]1000005)([H]1000006)[C]3([H]1000002)([H]1000003)([H]1000004)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C]7([H]1000011){=}[C]6([H]1000009)([H]1000010).[C]3([H]1000002)([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)([H]1000008)',
    name='IMS8-EQ8.54:step_alpha_alkyl_loss',
)

# IMS8-EQ8.55a:step_ring_opening_alpha
IMS8_EQ8_55a_step_ring_opening_alpha = mod.Rule.fromDFS(
    s='[C+]1([C.]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000000)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005)',
    name='IMS8-EQ8.55a:step_ring_opening_alpha',
)

# IMS8-EQ8.55b:step_alpha_ethylene_loss
IMS8_EQ8_55b_step_alpha_ethylene_loss = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C.]6([H]1000008)([H]1000009).[C]4([H]1000004)([H]1000005){=}[C]5([H]1000006)([H]1000007)',
    name='IMS8-EQ8.55b:step_alpha_ethylene_loss',
)

# IMS8-EQ8.55c:step_random_h_rearrangement
IMS8_EQ8_55c_step_random_h_rearrangement = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]8)([H]1000007)[C]5([H]7)([H]1000006)[C.]4([H]1000004)([H]1000005)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C.]6([H]1000007)[C]5([H]8)([H]1000006)[C]4([H]7)([H]1000004)([H]1000005)',
    name='IMS8-EQ8.55c:step_random_h_rearrangement',
)

# IMS8-EQ8.55d:step_alpha_methyl_loss
IMS8_EQ8_55d_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C.]6([H]1000009)[C]5([H]1000007)([H]1000008)[C]4([H]1000004)([H]1000005)([H]1000006)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000009){=}[C]5([H]1000007)([H]1000008).[C.]4([H]1000004)([H]1000005)([H]1000006)',
    name='IMS8-EQ8.55d:step_alpha_methyl_loss',
)

# IMS8-EQ8.56a:step_alpha_ring_opening
IMS8_EQ8_56a_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))>>[O+]1({=}[C]2([H]1000000)([H]1000001))[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)',
    name='IMS8-EQ8.56a:step_alpha_ring_opening',
)

# IMS8-EQ8.56b:step_inductive_ch2o_loss
IMS8_EQ8_56b_step_inductive_ch2o_loss = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)([H]1000001))[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O]1{=}[C]2([H]1000000)([H]1000001).[C.]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C+]6([H]1000008)([H]1000009)',
    name='IMS8-EQ8.56b:step_inductive_ch2o_loss',
)

# IMS8-EQ8.56c:step_alpha_central_cc_cleavage
IMS8_EQ8_56c_step_alpha_central_cc_cleavage = mod.Rule.fromDFS(
    s='[C.]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C+]6([H]1000006)([H]1000007)>>[C]3([H]1000000)([H]1000001){=}[C]4([H]1000002)([H]1000003).[C.]5([H]1000004)([H]1000005)[C+]6([H]1000006)([H]1000007)',
    name='IMS8-EQ8.56c:step_alpha_central_cc_cleavage',
)

# IMS8-EQ8.56d:step_alpha_ethylene_loss
IMS8_EQ8_56d_step_alpha_ethylene_loss = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)([H]1000001))[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000002)([H]1000003)>>[O+]1({=}[C]2([H]1000000)([H]1000001))[C]6([H]1000008)([H]1000009)[C.]5([H]1000006)([H]1000007).[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005)',
    name='IMS8-EQ8.56d:step_alpha_ethylene_loss',
)

# IMS8-EQ8.56e:step_alpha_second_ethylene_loss
IMS8_EQ8_56e_step_alpha_second_ethylene_loss = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)([H]1000001))[C]6([H]1000004)([H]1000005)[C.]5([H]1000002)([H]1000003)>>[O+.]1{=}[C]2([H]1000000)([H]1000001).[C]5([H]1000002)([H]1000003){=}[C]6([H]1000004)([H]1000005)',
    name='IMS8-EQ8.56e:step_alpha_second_ethylene_loss',
)

# IMS8-EQ8.57:step_alpha_ring_opening
IMS8_EQ8_57_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[N+.]1([C]2([H]1000001)([H]1000002)[C]3([C]4([H]1000004)([H]1000005)[C]5({-}1)([H]1000006)([H]1000007))([H]1000003)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000)>>[N+]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000003)[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.57:step_alpha_ring_opening',
)

# IMS8-EQ8.57:step_alpha_alkene_loss
IMS8_EQ8_57_step_alpha_alkene_loss = mod.Rule.fromDFS(
    s='[N+]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C.]3([H]1000003)[C]6([H]1000008)([H]1000009)([H]1000010)>>[N+]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[C.]5([H]1000006)([H]1000007).[C]3({=}[C]4([H]1000004)([H]1000005))([H]1000003)[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.57:step_alpha_alkene_loss',
)

# IMS8-EQ8.58a:step_alpha_cleavage_ring_opening
IMS8_EQ8_58a_step_alpha_cleavage_ring_opening = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5({-}1)([H]1000004)([H]1000005))>>[C]1({#}[O+]2)[C]5([H]1000004)([H]1000005)[C]4([H]1000002)([H]1000003)[C.]3([H]1000000)([H]1000001)',
    name='IMS8-EQ8.58a:step_alpha_cleavage_ring_opening',
)

# IMS8-EQ8.58a:step_alpha_cleavage_alkene_loss
IMS8_EQ8_58a_step_alpha_cleavage_alkene_loss = mod.Rule.fromDFS(
    s='[C]1({#}[O+]2)[C]5([H]1000004)([H]1000005)[C]4([H]1000002)([H]1000003)[C.]3([H]1000000)([H]1000001)>>[C]1({#}[O+]2)[C.]5([H]1000004)([H]1000005).[C]3([H]1000000)([H]1000001){=}[C]4([H]1000002)([H]1000003)',
    name='IMS8-EQ8.58a:step_alpha_cleavage_alkene_loss',
)

# IMS8-EQ8.58a:step_resonance_to_ketene
IMS8_EQ8_58a_step_resonance_to_ketene = mod.Rule.fromDFS(
    s='[C]1({#}[O+]2)[C.]5([H]1000004)([H]1000005).[C]3([H]1000000)([H]1000001){=}[C]4([H]1000002)([H]1000003)>>[C]1({=}[O+.]2){=}[C]5([H]1000004)([H]1000005).[C]3([H]1000000)([H]1000001){=}[C]4([H]1000002)([H]1000003)',
    name='IMS8-EQ8.58a:step_resonance_to_ketene',
)

# IMS8-EQ8.58b:step_alpha_cleavage_ring_opening
IMS8_EQ8_58b_step_alpha_cleavage_ring_opening = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([C]4([H]1000000)([H]1000001)[C]5({-}1)([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013))([C]6([H]1000002)([H]1000003)([H]1000004))[C]7([H]1000005)([H]1000006)([H]1000007))>>[C]1({#}[O+]2)[C]5([C]4([H]1000000)([H]1000001)[C.]3([C]6([H]1000002)([H]1000003)([H]1000004))[C]7([H]1000005)([H]1000006)([H]1000007))([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.58b:step_alpha_cleavage_ring_opening',
)

# IMS8-EQ8.58b:step_alpha_cleavage_alkene_loss
IMS8_EQ8_58b_step_alpha_cleavage_alkene_loss = mod.Rule.fromDFS(
    s='[C]1({#}[O+]2)[C]5([C]4([H]1000000)([H]1000001)[C.]3([C]6([H]1000002)([H]1000003)([H]1000004))[C]7([H]1000005)([H]1000006)([H]1000007))([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013)>>[C]1({#}[O+]2)[C.]5([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013).[C]3({=}[C]4([H]1000000)([H]1000001))([C]6([H]1000002)([H]1000003)([H]1000004))[C]7([H]1000005)([H]1000006)([H]1000007)',
    name='IMS8-EQ8.58b:step_alpha_cleavage_alkene_loss',
)

# IMS8-EQ8.58b:step_resonance_to_ketene
IMS8_EQ8_58b_step_resonance_to_ketene = mod.Rule.fromDFS(
    s='[C]1({#}[O+]2)[C.]5([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013).[C]3({=}[C]4([H]1000000)([H]1000001))([C]6([H]1000002)([H]1000003)([H]1000004))[C]7([H]1000005)([H]1000006)([H]1000007)>>[C]1({=}[O+.]2){=}[C]5([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013).[C]3({=}[C]4([H]1000000)([H]1000001))([C]6([H]1000002)([H]1000003)([H]1000004))[C]7([H]1000005)([H]1000006)([H]1000007)',
    name='IMS8-EQ8.58b:step_resonance_to_ketene',
)

# IMS8-EQ8.59:step_co_loss_alpha_inductive
IMS8_EQ8_59_step_co_loss_alpha_inductive = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)[C]4([C]5([H]1000002)([H]1000003)[C]6([C]7({-}1)([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015))([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012))>>[C-]1{#}[O+]2.[C+]3([H]1000000)([H]1000001)[C]4([C]5([H]1000002)([H]1000003)[C]6([C.]7([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015))([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQ8.59:step_co_loss_alpha_inductive',
)

# IMS8-EQ8.5a:step_mclafferty_alpha_i
IMS8_EQ8_5a_step_mclafferty_alpha_i = mod.Rule.fromDFS(
    s='[O+.]1{=}[C]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]9)([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)>>[O]1([H]9)[C]2([H]1000000){=}[C]3([H]1000001)([H]1000002).[C+]4([H]1000003)([H]1000004)[C.]5([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.5a:step_mclafferty_alpha_i',
)

# IMS8-EQ8.5b:step_mclafferty_alpha_alpha
IMS8_EQ8_5b_step_mclafferty_alpha_alpha = mod.Rule.fromDFS(
    s='[O+.]1{=}[C]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]9)([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)>>[O+]1([H]9){=}[C]2([H]1000000)[C.]3([H]1000001)([H]1000002).[C]4([H]1000003)([H]1000004){=}[C]5([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.5b:step_mclafferty_alpha_alpha',
)

# IMS8-EQ8.5c:step_mclafferty_alpha_i
IMS8_EQ8_5c_step_mclafferty_alpha_i = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)[C.]3([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]9)([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)>>[O]1{=}[C]2([H]1000000)[C]3([H]9)([H]1000001)([H]1000002).[C+]4([H]1000003)([H]1000004)[C.]5([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.5c:step_mclafferty_alpha_i',
)

# IMS8-EQ8.5d:step_mclafferty_alpha_alpha
IMS8_EQ8_5d_step_mclafferty_alpha_alpha = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([H]1000000)[C.]3([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]9)([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)>>[O+.]1{=}[C]2([H]1000000)[C]3([H]9)([H]1000001)([H]1000002).[C]4([H]1000003)([H]1000004){=}[C]5([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.5d:step_mclafferty_alpha_alpha',
)

# IMS8-EQ8.6:step_alpha1_ring_opening
IMS8_EQ8_6_step_alpha1_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C+]5([H]1000006)[C.]6([H]1000007)[C]7({-}2)([H]1000008)([H]1000009))([H]1000001))([H]1000000){=}[C]8([H]1000010)([H]1000011)>>[C]1([C.]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C+]5([H]1000006)[C]6([H]1000007){=}[C]7([H]1000008)([H]1000009))([H]1000000){=}[C]8([H]1000010)([H]1000011)',
    name='IMS8-EQ8.6:step_alpha1_ring_opening',
)

# IMS8-EQ8.6:step_alpha2_charge_retention
IMS8_EQ8_6_step_alpha2_charge_retention = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C+]5([H]1000006)[C]6([H]1000007){=}[C]7([H]1000008)([H]1000009))([H]1000000){=}[C]8([H]1000010)([H]1000011)>>[C]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000){=}[C]8([H]1000010)([H]1000011).[C.]4([H]1000004)([H]1000005)[C+]5([H]1000006)[C]6([H]1000007){=}[C]7([H]1000008)([H]1000009)',
    name='IMS8-EQ8.6:step_alpha2_charge_retention',
)

# IMS8-EQ8.60:step_alpha2_ring_cleavage
IMS8_EQ8_60_step_alpha2_ring_cleavage = mod.Rule.fromDFS(
    s='[C]1([O+.]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))([C]4([H]1000004)([H]1000005)[C]5([H]1000006){=}[C]6([H]1000007)[C]7([H]1000008)([H]1000009)[C]8({-}1)([H]1000010)([H]1000011))>>[C]1([O+.]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003)){=}[C]8([H]1000010)([H]1000011).[C]4([H]1000004)([H]1000005){=}[C]5([H]1000006)[C]6([H]1000007){=}[C]7([H]1000008)([H]1000009)',
    name='IMS8-EQ8.60:step_alpha2_ring_cleavage',
)

# IMS8-EQ8.61:step_alpha_cleavage
IMS8_EQ8_61_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[N+.]1([C]2([C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))([H]1000000)[C]8([H]1000012)([H]1000013)([H]1000014))[C]7([H]1000009)([H]1000010)([H]1000011)>>[N+]1({=}[C]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]7([H]1000009)([H]1000010)([H]1000011).[C.]8([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.61:step_alpha_cleavage',
)

# IMS8-EQ8.61:step_retro_diels_alder
IMS8_EQ8_61_step_retro_diels_alder = mod.Rule.fromDFS(
    s='[N+]1({=}[C]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))[C]7([H]1000009)([H]1000010)([H]1000011).[C.]8([H]1000012)([H]1000013)([H]1000014)>>[N+]1([C]2([H]1000000){=}[C]3([H]1000001)([H]1000002))({=}[C]6([H]1000007)([H]1000008))[C]7([H]1000009)([H]1000010)([H]1000011).[C]4([H]1000003)([H]1000004){=}[C]5([H]1000005)([H]1000006).[C.]8([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.61:step_retro_diels_alder',
)

# IMS8-EQ8.62:step_alpha_cleavage
IMS8_EQ8_62_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[O+.]1([C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}1)([H]1000006)([H]1000007))([C]7([H]1000008)([H]1000009)([H]1000010))[C]8([H]1000011)([H]1000012)([H]1000013))>>[O+]1({=}[C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}1)([H]1000006)([H]1000007))[C]7([H]1000008)([H]1000009)([H]1000010)).[C.]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.62:step_alpha_cleavage',
)

# IMS8-EQ8.62:step_ring_co_cleavage
IMS8_EQ8_62_step_ring_co_cleavage = mod.Rule.fromDFS(
    s='[O+]1({=}[C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}1)([H]1000006)([H]1000007))[C]7([H]1000008)([H]1000009)([H]1000010)).[C.]8([H]1000011)([H]1000012)([H]1000013)>>[O+]1{#}[C]2[C]7([H]1000008)([H]1000009)([H]1000010).[C]3([C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}3)([H]1000006)([H]1000007))([H]1000000)([H]1000001).[C.]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.62:step_ring_co_cleavage',
)

# IMS8-EQ8.63:step_alpha_ring_opening
IMS8_EQ8_63_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[N+.]1([C]2([C]3([H]9)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}2)([H]1000007)([H]1000008))([H]1000001))([H]1000000)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013)>>[N+]1({=}[C]2([H]1000001)[C]3([H]9)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)([H]1000008))([H]1000000)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.63:step_alpha_ring_opening',
)

# IMS8-EQ8.63:step_h_rearrangement
IMS8_EQ8_63_step_h_rearrangement = mod.Rule.fromDFS(
    s='[N+]1({=}[C]2([H]1000001)[C]3([H]9)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)([H]1000008))([H]1000000)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013)>>[N+]1({=}[C]2([H]1000001)[C.]3([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]9)([H]1000007)([H]1000008))([H]1000000)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.63:step_h_rearrangement',
)

# IMS8-EQ8.63:step_alpha_ethyl_loss
IMS8_EQ8_63_step_alpha_ethyl_loss = mod.Rule.fromDFS(
    s='[N+]1({=}[C]2([H]1000001)[C.]3([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]9)([H]1000007)([H]1000008))([H]1000000)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013)>>[N+]1({=}[C]2([H]1000001)[C]3([H]1000002){=}[C]4([H]1000003)([H]1000004))([H]1000000)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013).[C.]5([H]1000005)([H]1000006)[C]6([H]9)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.63:step_alpha_ethyl_loss',
)

# IMS8-EQ8.64:step_alpha_ring_opening
IMS8_EQ8_64_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1{=}[C]2([C]3([H]11)([H]1000000)[C]4([C]5([H]1000001)([H]1000002)[C]6([C]7({-}2)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011))>>[O+]1{#}[C]2[C]3([H]11)([H]1000000)[C]4([C]5([H]1000001)([H]1000002)[C]6([C.]7([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.64:step_alpha_ring_opening',
)

# IMS8-EQ8.64:step_h_rearrangement
IMS8_EQ8_64_step_h_rearrangement = mod.Rule.fromDFS(
    s='[O+]1{#}[C]2[C]3([H]11)([H]1000000)[C]4([C]5([H]1000001)([H]1000002)[C]6([C.]7([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)>>[O+]1{#}[C]2[C.]3([H]1000000)[C]4([C]5([H]1000001)([H]1000002)[C]6([C]7([H]11)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.64:step_h_rearrangement',
)

# IMS8-EQ8.64:step_alpha_butyl_loss
IMS8_EQ8_64_step_alpha_butyl_loss = mod.Rule.fromDFS(
    s='[O+]1{#}[C]2[C.]3([H]1000000)[C]4([C]5([H]1000001)([H]1000002)[C]6([C]7([H]11)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)>>[O+]1{#}[C]2[C]3([H]1000000){=}[C]4([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011).[C.]5([H]1000001)([H]1000002)[C]6([C]7([H]11)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.64:step_alpha_butyl_loss',
)

# IMS8-EQ8.65a:step_alpha_cleavage_ring_opening
IMS8_EQ8_65a_step_alpha_cleavage_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1{=}[C]2([C]3([C]4([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[C]6({-}2)([H]9)([H]1000005))([H]1000000)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)([H]1000010))>>[O+]1{#}[C]2[C]6([H]9)([H]1000005)[C]5([H]1000003)([H]1000004)[C]4([H]1000001)([H]1000002)[C.]3([H]1000000)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.65a:step_alpha_cleavage_ring_opening',
)

# IMS8-EQ8.65a:step_hydrogen_rearrangement
IMS8_EQ8_65a_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[O+]1{#}[C]2[C]6([H]9)([H]1000005)[C]5([H]1000003)([H]1000004)[C]4([H]1000001)([H]1000002)[C.]3([H]1000000)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)([H]1000010)>>[O+]1{#}[C]2[C.]6([H]1000005)[C]5([H]1000003)([H]1000004)[C]4([H]1000001)([H]1000002)[C]3([H]9)([H]1000000)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.65a:step_hydrogen_rearrangement',
)

# IMS8-EQ8.65b:step_alpha_cleavage_ring_opening
IMS8_EQ8_65b_step_alpha_cleavage_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1{=}[C]2([C]3([C]4([H]1000001)([H]1000002)[C]5([H]1000003)([H]1000004)[C]6([H]1000005)([H]1000006)[C]7({-}2)([H]9)([H]1000007))([H]1000000)[C]8([H]1000008)([H]1000009)([H]1000010))>>[O+]1{#}[C]2[C]7([H]9)([H]1000007)[C]6([H]1000005)([H]1000006)[C]5([H]1000003)([H]1000004)[C]4([H]1000001)([H]1000002)[C.]3([H]1000000)[C]8([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.65b:step_alpha_cleavage_ring_opening',
)

# IMS8-EQ8.65b:step_hydrogen_rearrangement
IMS8_EQ8_65b_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[O+]1{#}[C]2[C]7([H]9)([H]1000007)[C]6([H]1000005)([H]1000006)[C]5([H]1000003)([H]1000004)[C]4([H]1000001)([H]1000002)[C.]3([H]1000000)[C]8([H]1000008)([H]1000009)([H]1000010)>>[O+]1{#}[C]2[C.]7([H]1000007)[C]6([H]1000005)([H]1000006)[C]5([H]1000003)([H]1000004)[C]4([H]1000001)([H]1000002)[C]3([H]9)([H]1000000)[C]8([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.65b:step_hydrogen_rearrangement',
)

# IMS8-EQ8.65c:step_alpha_cleavage_ring_opening
IMS8_EQ8_65c_step_alpha_cleavage_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1{=}[C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)[C]8({-}2)([H]9)([H]1000010))>>[O+]1{#}[C]2[C]8([H]9)([H]1000010)[C]7([H]1000008)([H]1000009)[C]6([H]1000006)([H]1000007)[C]5([H]1000004)([H]1000005)[C]4([H]1000002)([H]1000003)[C.]3([H]1000000)([H]1000001)',
    name='IMS8-EQ8.65c:step_alpha_cleavage_ring_opening',
)

# IMS8-EQ8.65c:step_hydrogen_rearrangement
IMS8_EQ8_65c_step_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[O+]1{#}[C]2[C]8([H]9)([H]1000010)[C]7([H]1000008)([H]1000009)[C]6([H]1000006)([H]1000007)[C]5([H]1000004)([H]1000005)[C]4([H]1000002)([H]1000003)[C.]3([H]1000000)([H]1000001)>>[O+]1{#}[C]2[C.]8([H]1000010)[C]7([H]1000008)([H]1000009)[C]6([H]1000006)([H]1000007)[C]5([H]1000004)([H]1000005)[C]4([H]1000002)([H]1000003)[C]3([H]9)([H]1000000)([H]1000001)',
    name='IMS8-EQ8.65c:step_hydrogen_rearrangement',
)

# IMS8-EQ8.66:step_alpha_ring_opening
IMS8_EQ8_66_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[O+.]1([H]1000000)[C]2([C]3([H]8)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7({-}2)([H]1000009)([H]1000010))([H]1000001)>>[O+]1([H]1000000){=}[C]2([H]1000001)[C]3([H]8)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C.]7([H]1000009)([H]1000010)',
    name='IMS8-EQ8.66:step_alpha_ring_opening',
)

# IMS8-EQ8.66:step_rh_to_enol_ion
IMS8_EQ8_66_step_rh_to_enol_ion = mod.Rule.fromDFS(
    s='[O+]1([H]1000000){=}[C]2([H]1000001)[C]3([H]8)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C.]7([H]1000009)([H]1000010)>>[O+.]1([H]1000000)[C]2([H]1000001){=}[C]3([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]8)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.66:step_rh_to_enol_ion',
)

# IMS8-EQ8.67:step_alpha_ring_opening
IMS8_EQ8_67_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[N+.]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)[C]6({-}1)([H]7)([H]1000009))([H]1000000)>>[N+]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[C]6([H]7)([H]1000009)[C]5([H]1000007)([H]1000008)[C]4([H]1000005)([H]1000006)[C.]3([H]1000003)([H]1000004)',
    name='IMS8-EQ8.67:step_alpha_ring_opening',
)

# IMS8-EQ8.67:step_rh_with_beta_cleavage
IMS8_EQ8_67_step_rh_with_beta_cleavage = mod.Rule.fromDFS(
    s='[N+]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[C]6([H]7)([H]1000009)[C]5([H]1000007)([H]1000008)[C]4([H]1000005)([H]1000006)[C.]3([H]1000003)([H]1000004)>>[N+]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[C]6([H]1000009){=}[C]5([H]1000007)([H]1000008).[C]3([H]7)([H]1000003)([H]1000004)[C.]4([H]1000005)([H]1000006)',
    name='IMS8-EQ8.67:step_rh_with_beta_cleavage',
)

# IMS8-EQ8.68a:step_double_ring_cleavage_to_mz83
IMS8_EQ8_68a_step_double_ring_cleavage_to_mz83 = mod.Rule.fromDFS(
    s='[N+.]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([C]6({-}1)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([O]10[H]1000014)([H]1000013)[C]11({-}5)([H]1000015)([H]1000016))([H]1000007))>>[N+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)[C]6({=}1)([H]1000008)).[C]7([C]8([H]1000011)([H]1000012)[C]9([O]10[H]1000014)([H]1000013)[C]11({-}7)([H]1000015)([H]1000016))([H]1000009)([H]1000010)',
    name='IMS8-EQ8.68a:step_double_ring_cleavage_to_mz83',
)

# IMS8-EQ8.68b:step_alpha_cleavage_ring_opening
IMS8_EQ8_68b_step_alpha_cleavage_ring_opening = mod.Rule.fromDFS(
    s='[N+.]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([C]6({-}1)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([O]10[H]1000014)([H]1000013)[C]11({-}5)([H]1000015)([H]1000016))([H]1000007))>>[N+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([C]6({=}1)([H]1000008))([H]1000007)[C]11([H]1000015)([H]1000016)[C]9([C]8([H]1000011)([H]1000012)[C.]7([H]1000009)([H]1000010))([H]1000013)[O]10[H]1000014)',
    name='IMS8-EQ8.68b:step_alpha_cleavage_ring_opening',
)

# IMS8-EQ8.68b:step_h_transfer_and_beta_cleavage  [1 hydrogen migration(s) inferred]
IMS8_EQ8_68b_step_h_transfer_and_beta_cleavage = mod.Rule.fromDFS(
    s='[N+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([C]6({=}1)([H]1000007))([H]1000016)[C]11([H]1000014)([H]1000015)[C]9([C]8([H]1000010)([H]1000011)[C.]7([H]1000008)([H]1000009))([H]1000012)[O]10[H]1000013)>>[N+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([C]6({=}1)([H]1000007)){=}[C]11([H]1000014)([H]1000015)).[C]7([H]1000008)([H]1000009)([H]1000016)[C]8([H]1000010)([H]1000011)[C.]9([H]1000012)[O]10[H]1000013',
    name='IMS8-EQ8.68b:step_h_transfer_and_beta_cleavage',
)

# IMS8-EQ8.69:step_double_ring_cleavage_to_mz125
IMS8_EQ8_69_step_double_ring_cleavage_to_mz125 = mod.Rule.fromDFS(
    s='[N+.]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([C]6({-}1)([H]1000007)[C]7([C]8([C]9([O]10[H]1000011)([H]1000010)[C]11({=}5)([H]1000012))([H]1000009)[O]12[C]13({=}[O]14)[C]20(:[C]15({-}7):[C]16([H]1000013):[C]17(:[C]18(:[C]19(:20)([H]1000014))[O]23[C]21([H]1000015)([H]1000016)[O]22{-}17)))([H]1000008)))>>[N+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([C]6({=}1)([H]1000007)){=}[C]11([H]1000012)[C.]9([H]1000010)[O]10[H]1000011).[C]7(:[C]8([H]1000009):[O]12:[C]13({=}[O]14):[C]20(:[C]15(:7):[C]16([H]1000013):[C]17(:[C]18(:[C]19(:20)([H]1000014))[O]23[C]21([H]1000015)([H]1000016)[O]22{-}17)))([H]1000008)',
    name='IMS8-EQ8.69:step_double_ring_cleavage_to_mz125',
)

# IMS8-EQ8.70a:step_gamma_h_rearrangement  [1 hydrogen migration(s) inferred]
IMS8_EQ8_70a_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000011)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1({=}[O+]2[H]1000011)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.70a:step_gamma_h_rearrangement',
)

# IMS8-EQ8.70a:step_beta_cleavage_charge_retention
IMS8_EQ8_70a_step_beta_cleavage_charge_retention = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([O+.]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003)){=}[C]4([H]1000004)([H]1000005).[C]5([H]1000006)([H]1000007){=}[C]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.70a:step_beta_cleavage_charge_retention',
)

# IMS8-EQ8.70b:step_gamma_h_rearrangement  [1 hydrogen migration(s) inferred]
IMS8_EQ8_70b_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000011)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1({=}[O+]2[H]1000011)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.70b:step_gamma_h_rearrangement',
)

# IMS8-EQ8.70b:step_beta_cleavage_charge_migration
IMS8_EQ8_70b_step_beta_cleavage_charge_migration = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)>>[C]1([O]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003)){=}[C]4([H]1000004)([H]1000005).[C+]5([H]1000006)([H]1000007)[C.]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.70b:step_beta_cleavage_charge_migration',
)

# IMS8-EQ8.71a:step_h_rearrangement_to_saturated_y  [1 hydrogen migration(s) inferred]
IMS8_EQ8_71a_step_h_rearrangement_to_saturated_y = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000009))([H]1000000)([H]1000001)[O+.]5[H]1000008>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C.]4([H]1000006)([H]1000007))([H]1000000)([H]1000001)[O+]5([H]1000008)([H]1000009)',
    name='IMS8-EQ8.71a:step_h_rearrangement_to_saturated_y',
)

# IMS8-EQ8.71a:step_ring_closure_charge_retention
IMS8_EQ8_71a_step_ring_closure_charge_retention = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C.]4([H]1000006)([H]1000007))([H]1000000)([H]1000001)[O+]5([H]1000008)([H]1000009)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4({-}1)([H]1000006)([H]1000007))([H]1000000)([H]1000001).[O+.]5([H]1000008)([H]1000009)',
    name='IMS8-EQ8.71a:step_ring_closure_charge_retention',
)

# IMS8-EQ8.71b:step_h_rearrangement_to_saturated_y  [1 hydrogen migration(s) inferred]
IMS8_EQ8_71b_step_h_rearrangement_to_saturated_y = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000009))([H]1000000)([H]1000001)[O+.]5[H]1000008>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C.]4([H]1000006)([H]1000007))([H]1000000)([H]1000001)[O+]5([H]1000008)([H]1000009)',
    name='IMS8-EQ8.71b:step_h_rearrangement_to_saturated_y',
)

# IMS8-EQ8.71b:step_cy_cleavage_charge_migration
IMS8_EQ8_71b_step_cy_cleavage_charge_migration = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C.]4([H]1000006)([H]1000007))([H]1000000)([H]1000001)[O+]5([H]1000008)([H]1000009)>>[C+]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C.]4([H]1000006)([H]1000007).[O]5([H]1000008)([H]1000009)',
    name='IMS8-EQ8.71b:step_cy_cleavage_charge_migration',
)

# IMS8-EQ8.72:step_double_hydrogen_rearrangement  [2 hydrogen migration(s) inferred]
IMS8_EQ8_72_step_double_hydrogen_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[O]4[C]5([H]1000003)([H]1000004)[C]6([H]1000005)([H]1000010)[C]7([H]1000006)([H]1000011)[C]8([H]1000007)([H]1000008)([H]1000009)>>[C]1({=}[O+]2[H]1000010)([C]3([H]1000000)([H]1000001)([H]1000002))[O]4[H]1000011.[C]5([H]1000003)([H]1000004){=}[C]6([H]1000005)[C.]7([H]1000006)[C]8([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.72:step_double_hydrogen_rearrangement',
)

# IMS8-EQ8.73:step_h_h_rearrangement  [1 hydrogen migration(s) inferred]
IMS8_EQ8_73_step_h_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000013)[C]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)[C]8([H]1000010)([H]1000011)([H]1000012)>>[C]1({=}[O+]2[H]1000013)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003){=}[C]5([H]1000004)([H]1000005).[C.]6([H]1000006)([H]1000007)[C]7([H]1000008)([H]1000009)[C]8([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQ8.73:step_h_h_rearrangement',
)

# IMS8-EQ8.74a:step_gamma_h_rearrangement  [1 hydrogen migration(s) inferred]
IMS8_EQ8_74a_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000011)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1({=}[O+]2[H]1000011)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.74a:step_gamma_h_rearrangement',
)

# IMS8-EQ8.74b:step_ring_alpha_cleavage
IMS8_EQ8_74b_step_ring_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([O+.]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))([C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011))>>[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.74b:step_ring_alpha_cleavage',
)

# IMS8-EQ8.75a:step_rH_hydroxyl_charge_retention  [1 hydrogen migration(s) inferred]
IMS8_EQ8_75a_step_rH_hydroxyl_charge_retention = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([O]6[H]1000011)([C]7([H]1000005)([H]1000006)([H]1000007))[C]8([H]1000008)([H]1000009)([H]1000010)>>[C]1([O+.]2[H]1000011)([C]3([H]1000000)([H]1000001)([H]1000002)){=}[C]4([H]1000003)([H]1000004).[C]5({=}[O]6)([C]7([H]1000005)([H]1000006)([H]1000007))[C]8([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.75a:step_rH_hydroxyl_charge_retention',
)

# IMS8-EQ8.75b:step_rH_methyl_charge_migration  [1 hydrogen migration(s) inferred]
IMS8_EQ8_75b_step_rH_methyl_charge_migration = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([H]1000003)([H]1000004)[C]5([O]6[H]1000005)([C]7([H]1000006)([H]1000007)([H]1000011))[C]8([H]1000008)([H]1000009)([H]1000010)>>[C]1([O]2[H]1000011)([C]3([H]1000000)([H]1000001)([H]1000002)){=}[C]4([H]1000003)([H]1000004).[C]5([O+.]6[H]1000005)({=}[C]7([H]1000006)([H]1000007))[C]8([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.75b:step_rH_methyl_charge_migration',
)

# IMS8-EQ8.76a:step_mclafferty
IMS8_EQ8_76a_step_mclafferty = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]10)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({=}[O+.]6)[C]7([H]1000008)([H]1000009)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[C]3([H]1000004)([H]1000005).[C.]4([H]1000006)([H]1000007)[C]5({=}[O+]6[H]10)[C]7([H]1000008)([H]1000009)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.76a:step_mclafferty',
)

# IMS8-EQ8.76b:step_consecutive_rearrangement
IMS8_EQ8_76b_step_consecutive_rearrangement = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C]2({=}[O+]3[H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]7)([H]1000007)([H]1000008)>>[C]1([H]7)([H]1000000)([H]1000001)[C]2({=}[O+]3[H]1000002)[C.]4([H]1000003)([H]1000004).[C]5([H]1000005)([H]1000006){=}[C]6([H]1000007)([H]1000008)',
    name='IMS8-EQ8.76b:step_consecutive_rearrangement',
)

# IMS8-EQ8.77:step_radical_site_displacement  [1 hydrogen migration(s) inferred]
IMS8_EQ8_77_step_radical_site_displacement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000007)[S+.]3[C]4([H]1000004)([H]1000005)([H]1000006)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[S+]3[H]1000007.[C.]4([H]1000004)([H]1000005)([H]1000006)',
    name='IMS8-EQ8.77:step_radical_site_displacement',
)

# IMS8-EQ8.78:step_rH_1_delta_to_carbonyl_oxygen  [1 hydrogen migration(s) inferred]
IMS8_EQ8_78_step_rH_1_delta_to_carbonyl_oxygen = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([O]3[C]4([H]1000000)([H]1000001)([H]1000002))[C]5([H]1000003)([H]1000004)[C]6([H]1000005)([H]1000006)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000015)[C]9([H]1000010)([H]1000011)[C]10([H]1000012)([H]1000013)([H]1000014)>>[C]1({=}[O+]2[H]1000015)([O]3[C]4([H]1000000)([H]1000001)([H]1000002))[C]5([H]1000003)([H]1000004)[C]6([H]1000005)([H]1000006)[C]7([H]1000007)([H]1000008)[C.]8([H]1000009)[C]9([H]1000010)([H]1000011)[C]10([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.78:step_rH_1_delta_to_carbonyl_oxygen',
)

# IMS8-EQ8.78:step_rH_2_alpha_to_delta_carbon  [1 hydrogen migration(s) inferred]
IMS8_EQ8_78_step_rH_2_alpha_to_delta_carbon = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([O]3[C]4([H]1000001)([H]1000002)([H]1000003))[C]5([H]1000004)([H]1000015)[C]6([H]1000005)([H]1000006)[C]7([H]1000007)([H]1000008)[C.]8([H]1000009)[C]9([H]1000010)([H]1000011)[C]10([H]1000012)([H]1000013)([H]1000014)>>[C]1({=}[O+]2[H]1000000)([O]3[C]4([H]1000001)([H]1000002)([H]1000003))[C.]5([H]1000004)[C]6([H]1000005)([H]1000006)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000015)[C]9([H]1000010)([H]1000011)[C]10([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.78:step_rH_2_alpha_to_delta_carbon',
)

# IMS8-EQ8.78:step_alpha_cleavage
IMS8_EQ8_78_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([O]3[C]4([H]1000001)([H]1000002)([H]1000003))[C.]5([H]1000004)[C]6([H]1000005)([H]1000006)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)[C]9([H]1000011)([H]1000012)[C]10([H]1000013)([H]1000014)([H]1000015)>>[C]1({=}[O+]2[H]1000000)([O]3[C]4([H]1000001)([H]1000002)([H]1000003))[C]5([H]1000004){=}[C]6([H]1000005)([H]1000006).[C.]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)[C]9([H]1000011)([H]1000012)[C]10([H]1000013)([H]1000014)([H]1000015)',
    name='IMS8-EQ8.78:step_alpha_cleavage',
)

# IMS8-EQ8.79:step_rH_gamma  [1 hydrogen migration(s) inferred]
IMS8_EQ8_79_step_rH_gamma = mod.Rule.fromDFS(
    s='[C]1({=}[O+.]2)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([C]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000015)[C]7([H]1000007)([H]1000008)([H]1000009))([H]1000003)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014)>>[C]1({=}[O+]2[H]1000015)([C]3([H]1000000)([H]1000001)([H]1000002))[C]4([C]5([H]1000004)([H]1000005)[C.]6([H]1000006)[C]7([H]1000007)([H]1000008)([H]1000009))([H]1000003)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.79:step_rH_gamma',
)

# IMS8-EQ8.79:step_alpha_beta_cleavage
IMS8_EQ8_79_step_alpha_beta_cleavage = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C]4([C]5([H]1000005)([H]1000006)[C.]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010))([H]1000004)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)([H]1000015)>>[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C.]4([H]1000004)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)([H]1000015).[C]5([H]1000005)([H]1000006){=}[C]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.79:step_alpha_beta_cleavage',
)

# IMS8-EQ8.79:step_third_bond_cleavage
IMS8_EQ8_79_step_third_bond_cleavage = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C.]4([H]1000004)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)([H]1000015).[C]5([H]1000005)([H]1000006){=}[C]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010)>>[C]1({=}[O+]2[H]1000000)([C]3([H]1000001)([H]1000002)([H]1000003))[C]4([H]1000004){=}[C]8([H]1000011)([H]1000012).[C]5([H]1000005)([H]1000006){=}[C]6([H]1000007)[C]7([H]1000008)([H]1000009)([H]1000010).[C.]9([H]1000013)([H]1000014)([H]1000015)',
    name='IMS8-EQ8.79:step_third_bond_cleavage',
)

# IMS8-EQ8.7a:step_gamma_h_transfer
IMS8_EQ8_7a_step_gamma_h_transfer = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]8)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+.]7>>[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+]7[H]8',
    name='IMS8-EQ8.7a:step_gamma_h_transfer',
)

# IMS8-EQ8.7b:step_beta_cleavage_high_energy
IMS8_EQ8_7b_step_beta_cleavage_high_energy = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+]7[H]8>>[C]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[O+.]7[H]8.[C]3([H]1000003)([H]1000004){=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.7b:step_beta_cleavage_high_energy',
)

# IMS8-EQ8.7c:step_beta_cleavage_low_energy
IMS8_EQ8_7c_step_beta_cleavage_low_energy = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+]7[H]8>>[C]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[O+.]7[H]8.[C]3([H]1000003)([H]1000004){=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.7c:step_beta_cleavage_low_energy',
)

# IMS8-EQ8.7d:step_intracomplex_proton_transfer
IMS8_EQ8_7d_step_intracomplex_proton_transfer = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([H]1000008)([H]1000009){=}[C]6([H]1000010)[O+.]7[H]8>>[C]1([H]8)([H]1000000)([H]1000001)[C+]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([H]1000008)([H]1000009){=}[C]6([H]1000010)[O.]7',
    name='IMS8-EQ8.7d:step_intracomplex_proton_transfer',
)

# IMS8-EQ8.7e:step_intracomplex_h_transfer
IMS8_EQ8_7e_step_intracomplex_h_transfer = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]9)([H]1000003)[C+]3([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([H]1000008)([H]1000009){=}[C]6([H]1000010)[O.]7>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)[C+]3([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([H]9)([H]1000008)([H]1000009)[C]6([H]1000010){=}[O]7',
    name='IMS8-EQ8.7e:step_intracomplex_h_transfer',
)

# IMS8-EQ8.80:step_triple_h_rearrangement  [3 hydrogen migration(s) inferred]
IMS8_EQ8_80_step_triple_h_rearrangement = mod.Rule.fromDFS(
    s='[P]1({=}[O+.]2)([O]3[C]4([H]1000000)([H]1000001)([H]1000002))([O]5[C]6([C]7([H]1000003)([H]1000004)([H]1000007))([H]1000006)[C]8([H]1000005)([H]1000008)[O]9{-}1)>>[P]1({=}[O+]2[H]1000006)([O]3[C]4([H]1000000)([H]1000001)([H]1000002))([O]5[H]1000007)[O]9[H]1000008.[C]6({=}[C]7([H]1000003)([H]1000004)){=}[C.]8[H]1000005',
    name='IMS8-EQ8.80:step_triple_h_rearrangement',
)

# IMS8-EQ8.81a:step_rH_epsilon_H_to_alkoxy_O
IMS8_EQ8_81a_step_rH_epsilon_H_to_alkoxy_O = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]11)([H]1000006)[C]6([H]10)([H]1000007)[C]20(:[C]21([H]1000011):[C]22([H]1000012):[C]23([H]1000013):[C]24([H]1000014):[C]25(:20)([H]1000015)))({=}[O]7)[O+.]8[C]9([H]1000008)([H]1000009)([H]1000010)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]11)([H]1000006)[C.]6([H]1000007)[C]20(:[C]21([H]1000011):[C]22([H]1000012):[C]23([H]1000013):[C]24([H]1000014):[C]25(:20)([H]1000015)))({=}[O]7)[O+]8([H]10)[C]9([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.81a:step_rH_epsilon_H_to_alkoxy_O',
)

# IMS8-EQ8.81a:step_rd_methanol_displacement
IMS8_EQ8_81a_step_rd_methanol_displacement = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]11)([H]1000006)[C.]6([H]1000007)[C]20(:[C]21([H]1000011):[C]22([H]1000012):[C]23([H]1000013):[C]24([H]1000014):[C]25(:20)([H]1000015)))({=}[O]7)[O+]8([H]10)[C]9([H]1000008)([H]1000009)([H]1000010)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006){=}[C]6([H]1000007)[C]20(:[C]21([H]1000011):[C]22([H]1000012):[C]23([H]1000013):[C]24([H]1000014):[C]25(:20)([H]1000015)))([H]11){=}[O+.]7.[O]8([H]10)[C]9([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.81a:step_rd_methanol_displacement',
)

# IMS8-EQ8.81b:step_rH_i_enol_loss
IMS8_EQ8_81b_step_rH_i_enol_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]12)([H]1000004)[C]5([H]1000005){=}[C]6([H]1000006)[C]20(:[C]21([H]1000007):[C]22([H]1000008):[C]23([H]1000009):[C]24([H]1000010):[C]25(:20)([H]1000011)))([H]11){=}[O+.]7>>[C]1({=}[C]2([H]1000000)([H]1000001))([H]11)[O]7[H]12.[C+]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005){=}[C]6([H]1000006)[C]20(:[C]21([H]1000007):[C]22([H]1000008):[C]23([H]1000009):[C]24([H]1000010):[C]25(:20)([H]1000011))',
    name='IMS8-EQ8.81b:step_rH_i_enol_loss',
)

# IMS8-EQ8.82a:step_rH_hydroxyl_to_ester_oxygen  [1 hydrogen migration(s) inferred]
IMS8_EQ8_82a_step_rH_hydroxyl_to_ester_oxygen = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[O]9[H]1000017)({=}[O]10)[O+.]11[C]12([H]1000014)([H]1000015)([H]1000016)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[O.]9)({=}[O]10)[O+]11([H]1000017)[C]12([H]1000014)([H]1000015)([H]1000016)',
    name='IMS8-EQ8.82a:step_rH_hydroxyl_to_ester_oxygen',
)

# IMS8-EQ8.82b:step_alpha_loss_of_R
IMS8_EQ8_82b_step_alpha_loss_of_R = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[O]9[H]1000014)({=}[O]10)[O+.]11[C]12([H]1000015)([H]1000016)([H]1000017)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010){=}[O+]9[H]1000014)({=}[O]10)[O]11[C]12([H]1000015)([H]1000016)([H]1000017).[C.]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.82b:step_alpha_loss_of_R',
)

# IMS8-EQ8.82c:step_rH_proton_transfer  [1 hydrogen migration(s) inferred]
IMS8_EQ8_82c_step_rH_proton_transfer = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010){=}[O+]9[H]1000014)({=}[O]10)[O]11[C]12([H]1000011)([H]1000012)([H]1000013)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010){=}[O]9)({=}[O]10)[O+]11([H]1000014)[C]12([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.82c:step_rH_proton_transfer',
)

# IMS8-EQ8.82d:step_alpha_loss_of_R_from_alkoxy
IMS8_EQ8_82d_step_alpha_loss_of_R_from_alkoxy = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[O.]9)({=}[O]10)[O+]11([H]1000014)[C]12([H]1000015)([H]1000016)([H]1000017)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010){=}[O]9)({=}[O]10)[O+]11([H]1000014)[C]12([H]1000015)([H]1000016)([H]1000017).[C.]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS8-EQ8.82d:step_alpha_loss_of_R_from_alkoxy',
)

# IMS8-EQ8.82e:step_alpha_loss_of_RCHO
IMS8_EQ8_82e_step_alpha_loss_of_RCHO = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[O.]9)({=}[O]10)[O+]11([H]1000014)[C]12([H]1000015)([H]1000016)([H]1000017)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)([H]1000009))({=}[O]10)[O+]11([H]1000014)[C]12([H]1000015)([H]1000016)([H]1000017).[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010){=}[O]9',
    name='IMS8-EQ8.82e:step_alpha_loss_of_RCHO',
)

# IMS8-EQ8.82f:step_rH_alpha_backbite  [1 hydrogen migration(s) inferred]
IMS8_EQ8_82f_step_rH_alpha_backbite = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000013)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)([H]1000008))({=}[O]10)[O+]11([H]1000009)[C]12([H]1000010)([H]1000011)([H]1000012)>>[C]1([C]2([H]1000000){=}[C]3([H]1000001)([H]1000002))({=}[O]10)[O+]11([H]1000009)[C]12([H]1000010)([H]1000011)([H]1000012).[C.]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000013)',
    name='IMS8-EQ8.82f:step_rH_alpha_backbite',
)

# IMS8-EQ8.82g:step_inductive_loss_of_methanol
IMS8_EQ8_82g_step_inductive_loss_of_methanol = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010){=}[O]9)({=}[O]10)[O+]11([H]1000011)[C]12([H]1000012)([H]1000013)([H]1000014)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010){=}[O]9){#}[O+]10.[O]11([H]1000011)[C]12([H]1000012)([H]1000013)([H]1000014)',
    name='IMS8-EQ8.82g:step_inductive_loss_of_methanol',
)

# IMS8-EQ8.82h:step_inductive_loss_of_methanol_55
IMS8_EQ8_82h_step_inductive_loss_of_methanol_55 = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000){=}[C]3([H]1000001)([H]1000002))({=}[O]10)[O+]11([H]1000003)[C]12([H]1000004)([H]1000005)([H]1000006)>>[C]1([C]2([H]1000000){=}[C]3([H]1000001)([H]1000002)){#}[O+]10.[O]11([H]1000003)[C]12([H]1000004)([H]1000005)([H]1000006)',
    name='IMS8-EQ8.82h:step_inductive_loss_of_methanol_55',
)

# IMS8-EQ8.83a:step_rH_to_beta_carbon  [1 hydrogen migration(s) inferred]
IMS8_EQ8_83a_step_rH_to_beta_carbon = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003){=}[C]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000015)[C]11(:[C]12([H]1000010):[C]13([H]1000011):[C]14([H]1000012):[C]15([H]1000013):[C]16(:11)([H]1000014))){=}[O+.]8>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C]4([H]1000004)([H]1000015)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C+]7([H]1000009)[C]11(:[C]12([H]1000010):[C]13([H]1000011):[C]14([H]1000012):[C]15([H]1000013):[C]16(:11)([H]1000014)))[O.]8',
    name='IMS8-EQ8.83a:step_rH_to_beta_carbon',
)

# IMS8-EQ8.83b:step_rH_inductive_styrene_loss  [1 hydrogen migration(s) inferred]
IMS8_EQ8_83b_step_rH_inductive_styrene_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C]4([H]1000004)([H]1000015)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C+]7([H]1000009)[C]11(:[C]12([H]1000010):[C]13([H]1000011):[C]14([H]1000012):[C]15([H]1000013):[C]16(:11)([H]1000014)))[O.]8>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C.]4([H]1000004)[C+]5([H]1000005)([H]1000006))[O]8[H]1000015.[C]6([H]1000007)([H]1000008){=}[C]7([H]1000009)[C]11(:[C]12([H]1000010):[C]13([H]1000011):[C]14([H]1000012):[C]15([H]1000013):[C]16(:11)([H]1000014))',
    name='IMS8-EQ8.83b:step_rH_inductive_styrene_loss',
)

# IMS8-EQ8.84a:step_1_2_alkyl_shift
IMS8_EQ8_84a_step_1_2_alkyl_shift = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))([H]8)[C]6([H]1000008)([H]1000009)([H]1000010))[O]7[H]1000011>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C+]3([H]8)[C]6([H]1000008)([H]1000009)([H]1000010))([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[O]7[H]1000011',
    name='IMS8-EQ8.84a:step_1_2_alkyl_shift',
)

# IMS8-EQ8.84b:step_1_2_alkyl_shift
IMS8_EQ8_84b_step_1_2_alkyl_shift = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C+]3([H]8)[C]6([H]1000008)([H]1000009)([H]1000010))([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[O]7[H]1000011>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]3([C+]2([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[O]7[H]1000011)([H]8)[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.84b:step_1_2_alkyl_shift',
)

# IMS8-EQ8.84c:step_1_2_H_shift
IMS8_EQ8_84c_step_1_2_H_shift = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))([H]8)[C]6([H]1000008)([H]1000009)([H]1000010))[O]7[H]1000011>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C+]3([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[C]6([H]1000008)([H]1000009)([H]1000010))([H]8)[O]7[H]1000011',
    name='IMS8-EQ8.84c:step_1_2_H_shift',
)

# IMS8-EQ8.84d:step_1_2_H_shift
IMS8_EQ8_84d_step_1_2_H_shift = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]3([C+]2([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[O]7[H]1000011)([H]8)[C]6([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]3([C]2([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))([H]8)[O]7[H]1000011)[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.84d:step_1_2_H_shift',
)

# IMS8-EQ8.84e:step_1_2_alkyl_shift
IMS8_EQ8_84e_step_1_2_alkyl_shift = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C+]3([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[C]6([H]1000008)([H]1000009)([H]1000010))([H]8)[O]7[H]1000011>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]3([C+]2([H]8)[O]7[H]1000011)([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.84e:step_1_2_alkyl_shift',
)

# IMS8-EQ8.84f:step_1_2_alkyl_shift
IMS8_EQ8_84f_step_1_2_alkyl_shift = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]3([C+]2([H]8)[O]7[H]1000011)([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))[C]6([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]3([C]2([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)([H]1000007))([H]8)[O]7[H]1000011)[C]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.84f:step_1_2_alkyl_shift',
)

# IMS8-EQ8.85a:step_inductive_CO_cleavage
IMS8_EQ8_85a_step_inductive_CO_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]7)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))([H]1000000)[O+]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C+]1([C]2([H]7)([H]1000001)([H]1000002))([H]1000000)[C]3([H]1000003)([H]1000004)([H]1000005).[O]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.85a:step_inductive_CO_cleavage',
)

# IMS8-EQ8.85b:step_proton_transfer_elimination
IMS8_EQ8_85b_step_proton_transfer_elimination = mod.Rule.fromDFS(
    s='[C]1([C]2([H]7)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))([H]1000000)[O+]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C]1({=}[C]2([H]1000001)([H]1000002))([H]1000000)[C]3([H]1000003)([H]1000004)([H]1000005).[O+]4([H]6)([H]7)[C]5([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.85b:step_proton_transfer_elimination',
)

# IMS8-EQ8.85c:step_complex_formation
IMS8_EQ8_85c_step_complex_formation = mod.Rule.fromDFS(
    s='[C]1([C]2([H]7)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))([H]1000000)[O+]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C+]1([C]2([H]7)([H]1000001)([H]1000002))([H]1000000)[C]3([H]1000003)([H]1000004)([H]1000005).[O]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.85c:step_complex_formation',
)

# IMS8-EQ8.85c:step_1_2_hydride_shift
IMS8_EQ8_85c_step_1_2_hydride_shift = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]7)([H]1000001)([H]1000002))([H]1000000)[C]3([H]1000003)([H]1000004)([H]1000005).[O]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C]1([C+]2([H]1000001)([H]1000002))([H]7)([H]1000000)[C]3([H]1000003)([H]1000004)([H]1000005).[O]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.85c:step_1_2_hydride_shift',
)

# IMS8-EQ8.85c:step_complex_collapse
IMS8_EQ8_85c_step_complex_collapse = mod.Rule.fromDFS(
    s='[C]1([C+]2([H]1000001)([H]1000002))([H]7)([H]1000000)[C]3([H]1000003)([H]1000004)([H]1000005).[O]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008)>>[C]1([C]2([H]1000001)([H]1000002)[O+]4([H]6)[C]5([H]1000006)([H]1000007)([H]1000008))([H]7)([H]1000000)[C]3([H]1000003)([H]1000004)([H]1000005)',
    name='IMS8-EQ8.85c:step_complex_collapse',
)

# IMS8-EQ8.86a:step_rH_proton_transfer_to_remote_ether
IMS8_EQ8_86a_step_rH_proton_transfer_to_remote_ether = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C+]3([C]4([H]11)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[O]9[C]10([H]1000013)([H]1000014)([H]1000015))[O]7[C]8([H]1000010)([H]1000011)([H]1000012)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3({=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[O+]9([H]11)[C]10([H]1000013)([H]1000014)([H]1000015))[O]7[C]8([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQ8.86a:step_rH_proton_transfer_to_remote_ether',
)

# IMS8-EQ8.86a:step_rd_displacement_of_methanol
IMS8_EQ8_86a_step_rd_displacement_of_methanol = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3({=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[O+]9([H]11)[C]10([H]1000013)([H]1000014)([H]1000015))[O]7[C]8([H]1000010)([H]1000011)([H]1000012)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3({=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[O+]7({-}3)[C]8([H]1000010)([H]1000011)([H]1000012)).[O]9([H]11)[C]10([H]1000013)([H]1000014)([H]1000015)',
    name='IMS8-EQ8.86a:step_rd_displacement_of_methanol',
)

# IMS8-EQ8.86b:step_rH_hydride_shift_to_carbenium
IMS8_EQ8_86b_step_rH_hydride_shift_to_carbenium = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C+]3([C]4([H]1000005)([H]1000006)[C]5([H]12)([H]1000007)[C]6([H]11)([H]1000008)[O]9[C]10([H]1000012)([H]1000013)([H]1000014))[O]7[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([C]4([H]1000005)([H]1000006)[C]5([H]12)([H]1000007)[C+]6([H]1000008)[O]9[C]10([H]1000012)([H]1000013)([H]1000014))([H]11)[O]7[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.86b:step_rH_hydride_shift_to_carbenium',
)

# IMS8-EQ8.86b:step_rH_proton_transfer_to_remote_ether
IMS8_EQ8_86b_step_rH_proton_transfer_to_remote_ether = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([C]4([H]1000005)([H]1000006)[C]5([H]12)([H]1000007)[C+]6([H]1000008)[O]9[C]10([H]1000012)([H]1000013)([H]1000014))([H]11)[O]7[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([C]4([H]1000005)([H]1000006)[C]5([H]1000007){=}[C]6([H]1000008)[O]9[C]10([H]1000012)([H]1000013)([H]1000014))([H]11)[O+]7([H]12)[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.86b:step_rH_proton_transfer_to_remote_ether',
)

# IMS8-EQ8.86b:step_rd_displacement_of_methanol
IMS8_EQ8_86b_step_rd_displacement_of_methanol = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([C]4([H]1000005)([H]1000006)[C]5([H]1000007){=}[C]6([H]1000008)[O]9[C]10([H]1000012)([H]1000013)([H]1000014))([H]11)[O+]7([H]12)[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([C]4([H]1000005)([H]1000006)[C]5([H]1000007){=}[C]6([H]1000008)[O+]9({-}3)[C]10([H]1000012)([H]1000013)([H]1000014))([H]11).[O]7([H]12)[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.86b:step_rd_displacement_of_methanol',
)

# IMS8-EQ8.87:step_delta_rH_to_carbonyl_oxygen
IMS8_EQ8_87_step_delta_rH_to_carbonyl_oxygen = mod.Rule.fromDFS(
    s='[O+.]1{=}[C]2([C]3([C]9([H]1000007)([H]1000008)[C]8([C]7([H]1000004)([H]1000005)[C]6([C]5([C]4({-}2)([H]1000001)[C]11({-}8)([H]1000011)([H]1000012))([H]1000002)[C]12([C]13([H]20)([H]1000013)([H]1000014))([C]14([H]1000015)([H]1000016)([H]1000017))[C]15([H]1000018)([H]1000019)([H]1000020))([H]1000003)[C]10({-}3)([H]1000009)([H]1000010))([H]1000006))([H]1000000))>>[O+]1([H]20){=}[C]2([C]3([C]9([H]1000007)([H]1000008)[C]8([C]7([H]1000004)([H]1000005)[C]6([C]5([C]4({-}2)([H]1000001)[C]11({-}8)([H]1000011)([H]1000012))([H]1000002)[C]12([C.]13([H]1000013)([H]1000014))([C]14([H]1000015)([H]1000016)([H]1000017))[C]15([H]1000018)([H]1000019)([H]1000020))([H]1000003)[C]10({-}3)([H]1000009)([H]1000010))([H]1000006))([H]1000000))',
    name='IMS8-EQ8.87:step_delta_rH_to_carbonyl_oxygen',
)

# IMS8-EQ8.87:step_alpha_cleavage_isobutene_loss
IMS8_EQ8_87_step_alpha_cleavage_isobutene_loss = mod.Rule.fromDFS(
    s='[O+]1([H]20){=}[C]2([C]3([C]9([H]1000007)([H]1000008)[C]8([C]7([H]1000004)([H]1000005)[C]6([C]5([C]4({-}2)([H]1000001)[C]11({-}8)([H]1000011)([H]1000012))([H]1000002)[C]12([C.]13([H]1000013)([H]1000014))([C]14([H]1000015)([H]1000016)([H]1000017))[C]15([H]1000018)([H]1000019)([H]1000020))([H]1000003)[C]10({-}3)([H]1000009)([H]1000010))([H]1000006))([H]1000000))>>[O+]1([H]20){=}[C]2([C]3([C]9([H]1000007)([H]1000008)[C]8([C]7([H]1000004)([H]1000005)[C]6([C.]5([H]1000002)[C]4({-}2)([H]1000001)[C]11({-}8)([H]1000011)([H]1000012))([H]1000003)[C]10({-}3)([H]1000009)([H]1000010))([H]1000006))([H]1000000)).[C]12({=}[C]13([H]1000013)([H]1000014))([C]14([H]1000015)([H]1000016)([H]1000017))[C]15([H]1000018)([H]1000019)([H]1000020)',
    name='IMS8-EQ8.87:step_alpha_cleavage_isobutene_loss',
)

# IMS8-EQ8.88a:step_rH_to_Y
IMS8_EQ8_88a_step_rH_to_Y = mod.Rule.fromDFS(
    s='[O+.]1([H]1000000)[C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[N]9([H]1000014)([H]1000015)>>[O+]1([H]10)([H]1000000)[C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[N]9([H]1000014)([H]1000015)',
    name='IMS8-EQ8.88a:step_rH_to_Y',
)

# IMS8-EQ8.88b:step_rH_to_X
IMS8_EQ8_88b_step_rH_to_X = mod.Rule.fromDFS(
    s='[O]1([H]1000000)[C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[N+.]9([H]1000014)([H]1000015)>>[O]1([H]1000000)[C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[N+]9([H]10)([H]1000014)([H]1000015)',
    name='IMS8-EQ8.88b:step_rH_to_X',
)

# IMS8-EQ8.89:step_sigma_dissociation  [auto-localized precursor]
IMS8_EQ8_89_step_sigma_dissociation = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]20)([H]1000001)[C]7([H]1000012)([H]1000013)[C]8([H]1000014)([H]1000015)[C]9([H]1000016)([H]1000017)[C]10([H]1000018)([H]1000019)([H]1000020))([C.]3([C]5([H]1000006)([H]1000007)([H]1000008))([H]1000002)[C]6([H]1000009)([H]1000010)([H]1000011))([H]1000000)[C]4([H]1000003)([H]1000004)([H]1000005)>>[C+]1([C]2([H]20)([H]1000001)[C]7([H]1000012)([H]1000013)[C]8([H]1000014)([H]1000015)[C]9([H]1000016)([H]1000017)[C]10([H]1000018)([H]1000019)([H]1000020))([H]1000000)[C]4([H]1000003)([H]1000004)([H]1000005).[C.]3([C]5([H]1000006)([H]1000007)([H]1000008))([H]1000002)[C]6([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.89:step_sigma_dissociation',
)

# IMS8-EQ8.89:step_hydrogen_transfer
IMS8_EQ8_89_step_hydrogen_transfer = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]20)([H]1000001)[C]7([H]1000012)([H]1000013)[C]8([H]1000014)([H]1000015)[C]9([H]1000016)([H]1000017)[C]10([H]1000018)([H]1000019)([H]1000020))([H]1000000)[C]4([H]1000003)([H]1000004)([H]1000005).[C.]3([C]5([H]1000006)([H]1000007)([H]1000008))([H]1000002)[C]6([H]1000009)([H]1000010)([H]1000011)>>[C+]1([C.]2([H]1000001)[C]7([H]1000012)([H]1000013)[C]8([H]1000014)([H]1000015)[C]9([H]1000016)([H]1000017)[C]10([H]1000018)([H]1000019)([H]1000020))([H]1000000)[C]4([H]1000003)([H]1000004)([H]1000005).[C]3([C]5([H]1000006)([H]1000007)([H]1000008))([H]20)([H]1000002)[C]6([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.89:step_hydrogen_transfer',
)

# IMS8-EQ8.8a:step_alpha_cleavage_rejected
IMS8_EQ8_8a_step_alpha_cleavage_rejected = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([O+.]3[C]4({-}2)([H]1000004)([H]1000005))([H]1000003)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2({=}[O+]3[C]4({-}2)([H]1000004)([H]1000005))([H]1000003)',
    name='IMS8-EQ8.8a:step_alpha_cleavage_rejected',
)

# IMS8-EQ8.8b:step_ring_opening
IMS8_EQ8_8b_step_ring_opening = mod.Rule.fromDFS(
    s='[C]1([H]5)([H]1000000)([H]1000001)[C]2([O+.]3[C]4({-}2)([H]1000002)([H]1000003))([H]6)>>[C]1([H]5)([H]1000000)([H]1000001)[C]2([H]6){=}[O+]3[C.]4([H]1000002)([H]1000003)',
    name='IMS8-EQ8.8b:step_ring_opening',
)

# IMS8-EQ8.8b:step_rH_to_enol_ether
IMS8_EQ8_8b_step_rH_to_enol_ether = mod.Rule.fromDFS(
    s='[C]1([H]5)([H]1000000)([H]1000001)[C]2([H]6){=}[O+]3[C.]4([H]1000002)([H]1000003)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]6)[O+.]3[C]4([H]5)([H]1000002)([H]1000003)',
    name='IMS8-EQ8.8b:step_rH_to_enol_ether',
)

# IMS8-EQ8.8b:step_rH_methyl_loss
IMS8_EQ8_8b_step_rH_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[C]2([H]6)[O+.]3[C]4([H]5)([H]1000002)([H]1000003)>>[C]1([H]6)([H]1000000)([H]1000001)[C]2{#}[O+]3.[C.]4([H]5)([H]1000002)([H]1000003)',
    name='IMS8-EQ8.8b:step_rH_methyl_loss',
)

# IMS8-EQ8.9:step_rH_rearrangement  [1 hydrogen migration(s) inferred]
IMS8_EQ8_9_step_rH_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000011)[C]5([H]1000006){=}[C]6([H]1000007)[C]7({=}[O+.]8)[C]9([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005){=}[C]5([H]1000006)[C]6([H]1000007){=}[C]7([O+.]8[H]1000011)[C]9([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQ8.9:step_rH_rearrangement',
)

# IMS8-EQ8.9:step_alpha_cleavage
IMS8_EQ8_9_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005){=}[C]5([H]1000006)[C]6([H]1000007){=}[C]7([O+.]8[H]1000008)[C]9([H]1000009)([H]1000010)([H]1000011)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[C]3([H]1000005)[C]5([H]1000006){=}[C]6([H]1000007)[C]7({=}[O+]8[H]1000008)[C]9([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.9:step_alpha_cleavage',
)

# IMS8-EQ8.90:step_rH_gamma_H_to_carbonyl_oxygen
IMS8_EQ8_90_step_rH_gamma_H_to_carbonyl_oxygen = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]10)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+.]7>>[C+]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000)[O]7[H]10',
    name='IMS8-EQ8.90:step_rH_gamma_H_to_carbonyl_oxygen',
)

# IMS8-EQ8.90:step_cyclization_to_cyclobutane_ring
IMS8_EQ8_90_step_cyclization_to_cyclobutane_ring = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000)[O]7[H]10>>[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4({-}1)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000)[O+.]7[H]10',
    name='IMS8-EQ8.90:step_cyclization_to_cyclobutane_ring',
)

# IMS8-EQ8.90:step_retro_2plus2_ethylene_loss
IMS8_EQ8_90_step_retro_2plus2_ethylene_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4({-}1)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000)[O+.]7[H]10>>[C]1({=}[C]4([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000)[O+.]7[H]10.[C]2([H]1000001)([H]1000002){=}[C]3([H]1000003)([H]1000004)',
    name='IMS8-EQ8.90:step_retro_2plus2_ethylene_loss',
)

# IMS8-EQ8.91:step_rH_1_5_delta_H_to_nitrogen
IMS8_EQ8_91_step_rH_1_5_delta_H_to_nitrogen = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]31)([H]1000005)[C]5([H]33)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]32)([H]1000000)[N+.]20([H]1000022)([H]1000023)>>[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([H]1000005)[C]5([H]33)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]32)([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)',
    name='IMS8-EQ8.91:step_rH_1_5_delta_H_to_nitrogen',
)

# IMS8-EQ8.91:step_rH_1_4_C_to_C
IMS8_EQ8_91_step_rH_1_4_C_to_C = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C.]4([H]1000005)[C]5([H]33)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]32)([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)>>[C.]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C]5([H]33)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)',
    name='IMS8-EQ8.91:step_rH_1_4_C_to_C',
)

# IMS8-EQ8.91:step_rC_1_2_alkyl_shift
IMS8_EQ8_91_step_rC_1_2_alkyl_shift = mod.Rule.fromDFS(
    s='[C.]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C]5([H]33)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)>>[C]1([C.]2([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C]5([H]33)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)',
    name='IMS8-EQ8.91:step_rC_1_2_alkyl_shift',
)

# IMS8-EQ8.91:step_rH_1_5_C_to_primary_radical
IMS8_EQ8_91_step_rH_1_5_C_to_primary_radical = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C]5([H]33)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)>>[C]1([C]2([H]33)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C.]5([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)',
    name='IMS8-EQ8.91:step_rH_1_5_C_to_primary_radical',
)

# IMS8-EQ8.91:step_rH_1_5_N_to_carbon_radical
IMS8_EQ8_91_step_rH_1_5_N_to_carbon_radical = mod.Rule.fromDFS(
    s='[C]1([C]2([H]33)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C.]5([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+]20([H]31)([H]1000022)([H]1000023)>>[C]1([C]2([H]33)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C]5([H]31)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+.]20([H]1000022)([H]1000023)',
    name='IMS8-EQ8.91:step_rH_1_5_N_to_carbon_radical',
)

# IMS8-EQ8.91:step_alpha_cleavage_to_m44
IMS8_EQ8_91_step_alpha_cleavage_to_m44 = mod.Rule.fromDFS(
    s='[C]1([C]2([H]33)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C]5([H]31)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021))([H]1000000)[N+.]20([H]1000022)([H]1000023)>>[C]1([C]2([H]33)([H]1000001)([H]1000002))([H]1000000){=}[N+]20([H]1000022)([H]1000023).[C.]3([H]1000003)([H]1000004)[C]4([H]32)([H]1000005)[C]5([H]31)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)([H]1000021)',
    name='IMS8-EQ8.91:step_alpha_cleavage_to_m44',
)

# IMS8-EQ8.92:step_rH_six_ring_to_heteroatom  [1 hydrogen migration(s) inferred]
IMS8_EQ8_92_step_rH_six_ring_to_heteroatom = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)([H]1000017))([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000018)[C]6([H]1000006)([H]1000007)([H]1000008)>>[C]1([O+]2([H]1000018)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)([H]1000017))([H]1000000){=}[C]3([H]1000001)([H]1000002).[C]4([H]1000003)([H]1000004){=}[C]5([H]1000005)[C]6([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.92:step_rH_six_ring_to_heteroatom',
)

# IMS8-EQ8.93:step_rH_six_ring_to_carbon  [1 hydrogen migration(s) inferred]
IMS8_EQ8_93_step_rH_six_ring_to_carbon = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000018)[C]10([H]1000015)([H]1000016)([H]1000017))([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)>>[C]1([O+]2{=}[C]7([H]1000010)([H]1000011))([H]1000000)([H]1000018)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009).[C]8([H]1000012)([H]1000013){=}[C]9([H]1000014)[C]10([H]1000015)([H]1000016)([H]1000017)',
    name='IMS8-EQ8.93:step_rH_six_ring_to_carbon',
)

# IMS8-EQ8.94:step_rH_alkene_loss_to_heteroatom  [1 hydrogen migration(s) inferred]
IMS8_EQ8_94_step_rH_alkene_loss_to_heteroatom = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000018)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)([H]1000017))([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)>>[C]1({=}[O+]2[H]1000018)([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009).[C]7([H]1000010)([H]1000011){=}[C]8([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)([H]1000017)',
    name='IMS8-EQ8.94:step_rH_alkene_loss_to_heteroatom',
)

# IMS8-EQ8.95:step_rH_alkene_loss_to_carbon  [1 hydrogen migration(s) inferred]
IMS8_EQ8_95_step_rH_alkene_loss_to_carbon = mod.Rule.fromDFS(
    s='[C]1({=}[O+]2[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)([H]1000017))([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000018)[C]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)([H]1000008)>>[C]1([H]1000000)([H]1000018){=}[O+]2[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)([H]1000017).[C]3([H]1000001)([H]1000002){=}[C]4([H]1000003)[C]5([H]1000004)([H]1000005)[C]6([H]1000006)([H]1000007)([H]1000008)',
    name='IMS8-EQ8.95:step_rH_alkene_loss_to_carbon',
)

# IMS8-EQ8.97:step_rH_displacement_ethylene_loss  [1 hydrogen migration(s) inferred]
IMS8_EQ8_97_step_rH_displacement_ethylene_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000010)[C]2([H]1000002)([H]1000003)[O+]3([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[O+]3([H]1000004)([H]1000010)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQ8.97:step_rH_displacement_ethylene_loss',
)

# IMS8-EQ8.98:step_rH_1_2_hydride_shift
IMS8_EQ8_98_step_rH_1_2_hydride_shift = mod.Rule.fromDFS(
    s='[C]1([H]6)([H]1000000)([H]1000001)[C]2([H]5)([H]1000002)[C]3([H]1000003){=}[O+]4[H]1000004>>[C]1([H]6)([H]1000000)([H]1000001)[C+]2([H]1000002)[C]3([H]5)([H]1000003)[O]4[H]1000004',
    name='IMS8-EQ8.98:step_rH_1_2_hydride_shift',
)

# IMS8-EQ8.98:step_rH_proton_transfer_to_hydroxyl
IMS8_EQ8_98_step_rH_proton_transfer_to_hydroxyl = mod.Rule.fromDFS(
    s='[C]1([H]6)([H]1000000)([H]1000001)[C+]2([H]1000002)[C]3([H]5)([H]1000003)[O]4[H]1000004>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]5)([H]1000003)[O+]4([H]6)([H]1000004)',
    name='IMS8-EQ8.98:step_rH_proton_transfer_to_hydroxyl',
)

# IMS8-EQ8.98:step_i_water_loss
IMS8_EQ8_98_step_i_water_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]5)([H]1000003)[O+]4([H]6)([H]1000004)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C+]3([H]5)([H]1000003).[O]4([H]6)([H]1000004)',
    name='IMS8-EQ8.98:step_i_water_loss',
)

# IMS8-EQ8.99:step_alpha_cleavage
IMS8_EQ8_99_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[N+.]1([H]1000000)([H]1000001)[C]2([C]3({=}[O]4)[O]5[C]6([H]1000003)([H]1000004)([H]1000005))([H]1000002)[C]7([H]11)([H]1000006)[C]8([H]1000007)([H]1000008)[S]9[C]10([H]1000009)([H]1000010)([H]1000011)>>[N+]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]7([H]11)([H]1000006)[C]8([H]1000007)([H]1000008)[S]9[C]10([H]1000009)([H]1000010)([H]1000011).[C.]3({=}[O]4)[O]5[C]6([H]1000003)([H]1000004)([H]1000005)',
    name='IMS8-EQ8.99:step_alpha_cleavage',
)

# IMS8-EQ8.99:step_rH_thiol_elimination
IMS8_EQ8_99_step_rH_thiol_elimination = mod.Rule.fromDFS(
    s='[N+]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]7([H]11)([H]1000006)[C]8([H]1000007)([H]1000008)[S]9[C]10([H]1000009)([H]1000010)([H]1000011).[C.]3({=}[O]4)[O]5[C]6([H]1000003)([H]1000004)([H]1000005)>>[N+]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]7([H]1000006){=}[C]8([H]1000007)([H]1000008).[C.]3({=}[O]4)[O]5[C]6([H]1000003)([H]1000004)([H]1000005).[S]9([H]11)[C]10([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.99:step_rH_thiol_elimination',
)

# IMS8-EQ8.9b:step_direct_cleavage
IMS8_EQ8_9b_step_direct_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]5([H]1000007){=}[C]6([H]1000008)[C]7({=}[O+.]8)[C]9([H]1000009)([H]1000010)([H]1000011)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C+]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[C]5([H]1000007){=}[C]6([H]1000008)[C]7({=}[O]8)[C]9([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQ8.9b:step_direct_cleavage',
)

# IMS8-EQT8.2a:step_sigma  [auto-localized precursor]
IMS8_EQT8_2a_step_sigma = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004)[C+]3([C]4([H]1000006)([H]1000007)([H]1000008))([H]1000005)[C]5([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C+]3([C]4([H]1000006)([H]1000007)([H]1000008))([H]1000005)[C]5([H]1000009)([H]1000010)([H]1000011)',
    name='IMS8-EQT8.2a:step_sigma',
)

# IMS8-EQT8.2b:step_sigma_pi  [auto-localized precursor]
IMS8_EQT8_2b_step_sigma_pi = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H.]4)([H]1000003)[F+]3>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003){=}[F+]3.[H.]4',
    name='IMS8-EQT8.2b:step_sigma_pi',
)

# IMS8-EQT8.2d:step_inductive
IMS8_EQT8_2d_step_inductive = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+.]3[C]4([H]1000005)([H]1000006)([H]1000007)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O.]3[C]4([H]1000005)([H]1000006)([H]1000007)',
    name='IMS8-EQT8.2d:step_inductive',
)

# IMS8-EQT8.2e:step_inductive
IMS8_EQT8_2e_step_inductive = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005){=}[O+.]4>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[C.]3([H]1000005){=}[O]4',
    name='IMS8-EQT8.2e:step_inductive',
)

# IMS8-EQT8.2f:step_alpha
IMS8_EQT8_2f_step_alpha = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005)([H]1000006)[O+.]4[C]5([H]1000007)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2([H]1000003)([H]1000004).[C]3([H]1000005)([H]1000006){=}[O+]4[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS8-EQT8.2f:step_alpha',
)

# IMS8-EQT8.2g:step_inductive
IMS8_EQT8_2g_step_inductive = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)([H]1000005))([C]4([H]1000006)([H]1000007)([H]1000008))[C]5([H]1000009)([H]1000010)[C+]6([H]1000011)([H]1000012)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]1000003)([H]1000004)([H]1000005))[C]4([H]1000006)([H]1000007)([H]1000008).[C]5([H]1000009)([H]1000010){=}[C]6([H]1000011)([H]1000012)',
    name='IMS8-EQT8.2g:step_inductive',
)

# IMS8-EQT8.2h:step_inductive
IMS8_EQT8_2h_step_inductive = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[O+]3{=}[C]4([H]1000005)([H]1000006)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([H]1000003)([H]1000004).[O]3{=}[C]4([H]1000005)([H]1000006)',
    name='IMS8-EQT8.2h:step_inductive',
)

# IMS8-EQT8.2i:step_rd_displacement
IMS8_EQT8_2i_step_rd_displacement = mod.Rule.fromDFS(
    s='[C]1([H]4)([H]1000000)([H]1000001)[S+.]2[H]1000002>>[C]1([H]1000000)([H]1000001){=}[S+]2[H]1000002.[H.]4',
    name='IMS8-EQT8.2i:step_rd_displacement',
)

# IMS8-EQT8.2j:step_rd_displacement
IMS8_EQT8_2j_step_rd_displacement = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010))([H]1000000)([H]1000001)[Cl+.]6>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[Cl+]6{-}1)([H]1000000)([H]1000001).[C.]5([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQT8.2j:step_rd_displacement',
)

# IMS8-EQT8.2k:step_displacement
IMS8_EQT8_2k_step_displacement = mod.Rule.fromDFS(
    s='[N]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)[N+]6([H]1000010)([H]1000011)([H]1000012)>>[N+]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5({-}1)([H]1000008)([H]1000009))([H]1000000)([H]1000001).[N]6([H]1000010)([H]1000011)([H]1000012)',
    name='IMS8-EQT8.2k:step_displacement',
)

# IMS8-EQT8.2l:step_retro_2plus2
IMS8_EQT8_2l_step_retro_2plus2 = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000003)([H]1000004)[C]4({-}1)([H]1000005)([H]1000006))([H]1000002)[O+.]6[H]1000007)([H]1000000)([H]1000001)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[O+.]6[H]1000007.[C]3([H]1000003)([H]1000004){=}[C]4([H]1000005)([H]1000006)',
    name='IMS8-EQT8.2l:step_retro_2plus2',
)

# IMS8-EQT8.2m:step_ring_contraction
IMS8_EQT8_2m_step_ring_contraction = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)[C]6({-}1)([H]1000009)([H]1000010))([H]1000000)>>[C+]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]6({-}1)([H]1000009)([H]1000010))([H]1000000).[C]4([H]1000005)([H]1000006){=}[C]5([H]1000007)([H]1000008)',
    name='IMS8-EQT8.2m:step_ring_contraction',
)

# IMS8-EQT8.2n:step_mclafferty
IMS8_EQT8_2n_step_mclafferty = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]10)([H]1000005)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+.]6>>[C]1([C.]2([H]1000001)([H]1000002))([H]1000000){=}[O+]6[H]10.[C]3([H]1000003)([H]1000004){=}[C]4([H]1000005)[C]7([H]1000006)([H]1000007)[C]8([H]1000008)([H]1000009)([H]1000010)',
    name='IMS8-EQT8.2n:step_mclafferty',
)

# IMS8-EQT8.2o:step_onium
IMS8_EQT8_2o_step_onium = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[O+]2[C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)([H]1000005)>>[C]1([H]1000000)([H]1000001){=}[O+]2[H]10.[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005)',
    name='IMS8-EQT8.2o:step_onium',
)

# IMS8-EQT8.2p:step_alpha_ring_opening
IMS8_EQT8_2p_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008)){=}[O+.]7>>[C]1([C]2([H]10)([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)([H]1000008)){#}[O+]7',
    name='IMS8-EQT8.2p:step_alpha_ring_opening',
)

# IMS8-EQT8.2p:step_rH_1_5
IMS8_EQT8_2p_step_rH_1_5 = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)([H]1000008)){#}[O+]7>>[C]1([C.]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]10)([H]1000007)([H]1000008)){#}[O+]7',
    name='IMS8-EQT8.2p:step_rH_1_5',
)

# IMS8-EQT8.2p:step_alpha_second
IMS8_EQT8_2p_step_alpha_second = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000000)[C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]10)([H]1000007)([H]1000008)){#}[O+]7>>[C]1([C]2([H]1000000){=}[C]3([H]1000001)([H]1000002)){#}[O+]7.[C.]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]10)([H]1000007)([H]1000008)',
    name='IMS8-EQT8.2p:step_alpha_second',
)

# IMS8-EQT8.2q:step_double_rH
IMS8_EQT8_2q_step_double_rH = mod.Rule.fromDFS(
    s='[C]1([H]9)([H]1000000)([H]1000001)[C]2([H]8)([H]1000002)[C]3([H]1000003)([H]1000004)[O+]4{=}[C]5([O.]6)[C]7([H]1000005)([H]1000006)([H]1000007)>>[C.]1([H]1000000)([H]1000001)[C]2([H]1000002){=}[C]3([H]1000003)([H]1000004).[O+]4([H]9){=}[C]5([O]6[H]8)[C]7([H]1000005)([H]1000006)([H]1000007)',
    name='IMS8-EQT8.2q:step_double_rH',
)

# IMS9-EQ9.10:step_alpha_ring_opening
IMS9_EQ9_10_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C+]1([C.]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000000)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005)',
    name='IMS9-EQ9.10:step_alpha_ring_opening',
)

# IMS9-EQ9.10:step_rh_1_3_hydrogen_shift  [1 hydrogen migration(s) inferred]
IMS9_EQ9_10_step_rh_1_3_hydrogen_shift = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C.]6([H]1000008)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)([H]1000009)',
    name='IMS9-EQ9.10:step_rh_1_3_hydrogen_shift',
)

# IMS9-EQ9.10:step_alpha_methyl_loss
IMS9_EQ9_10_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C.]6([H]1000009)[C]5([H]1000007)([H]1000008)[C]4([H]1000004)([H]1000005)([H]1000006)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000009){=}[C]5([H]1000007)([H]1000008).[C.]4([H]1000004)([H]1000005)([H]1000006)',
    name='IMS9-EQ9.10:step_alpha_methyl_loss',
)

# IMS9-EQ9.11:step_alpha1_ring_opening
IMS9_EQ9_11_step_alpha1_ring_opening = mod.Rule.fromDFS(
    s='[C+]1([C.]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000000)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005)',
    name='IMS9-EQ9.11:step_alpha1_ring_opening',
)

# IMS9-EQ9.11:step_alpha2_ethylene_loss
IMS9_EQ9_11_step_alpha2_ethylene_loss = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005)>>[C+]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000)[C.]6([H]1000008)([H]1000009).[C]4([H]1000004)([H]1000005){=}[C]5([H]1000006)([H]1000007)',
    name='IMS9-EQ9.11:step_alpha2_ethylene_loss',
)

# IMS9-EQ9.12:step_retro_diels_alder
IMS9_EQ9_12_step_retro_diels_alder = mod.Rule.fromDFS(
    s='[O+.]1([C]2([C]3([C]4([H]1000001)([H]1000002)[C]5([H]1000003){=}[C]6([C]7([H]1000004)([H]1000005)([H]1000006))[C]8([H]1000007)([H]1000008)[C]9({-}3)([H]1000009)[C]10(:[C]11({-}1):[C]16([H]1000012):[C]15(:[C]14([H]1000011):[C]12(:10)[O]13[H]1000010)[C]17([H]1000013)([H]1000014)[C]18([H]1000015)([H]1000016)[C]19([H]1000017)([H]1000018)[C]20([H]1000019)([H]1000020)[C]21([H]1000021)([H]1000022)([H]1000023)))([H]1000000))([C]22([H]1000024)([H]1000025)([H]1000026))[C]23([H]1000027)([H]1000028)([H]1000029))>>[O+]1([C]2([C.]3([H]1000000)[C]9([H]1000009){=}[C]10(:[C]11({=}1):[C]16([H]1000012):[C]15(:[C]14([H]1000011):[C]12(:10)[O]13[H]1000010)[C]17([H]1000013)([H]1000014)[C]18([H]1000015)([H]1000016)[C]19([H]1000017)([H]1000018)[C]20([H]1000019)([H]1000020)[C]21([H]1000021)([H]1000022)([H]1000023)))([C]22([H]1000024)([H]1000025)([H]1000026))[C]23([H]1000027)([H]1000028)([H]1000029)).[C]4([H]1000001)([H]1000002){=}[C]5([H]1000003)[C]6([C]7([H]1000004)([H]1000005)([H]1000006)){=}[C]8([H]1000007)([H]1000008)',
    name='IMS9-EQ9.12:step_retro_diels_alder',
)

# IMS9-EQ9.12:step_alpha_methyl_loss
IMS9_EQ9_12_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[O+]1([C]2([C.]3([H]1000000)[C]9([H]1000009){=}[C]10(:[C]11({=}1):[C]16([H]1000012):[C]15(:[C]14([H]1000011):[C]12(:10)[O]13[H]1000010)[C]17([H]1000013)([H]1000014)[C]18([H]1000015)([H]1000016)[C]19([H]1000017)([H]1000018)[C]20([H]1000019)([H]1000020)[C]21([H]1000021)([H]1000022)([H]1000023)))([C]22([H]1000024)([H]1000025)([H]1000026))[C]23([H]1000027)([H]1000028)([H]1000029)).[C]4([H]1000001)([H]1000002){=}[C]5([H]1000003)[C]6([C]7([H]1000004)([H]1000005)([H]1000006)){=}[C]8([H]1000007)([H]1000008)>>[O+]1(:[C]2(:[C]3([H]1000000):[C]9([H]1000009):[C]10(:[C]11(:1):[C]16([H]1000012):[C]15(:[C]14([H]1000011):[C]12(:10)[O]13[H]1000010)[C]17([H]1000013)([H]1000014)[C]18([H]1000015)([H]1000016)[C]19([H]1000017)([H]1000018)[C]20([H]1000019)([H]1000020)[C]21([H]1000021)([H]1000022)([H]1000023)))[C]23([H]1000027)([H]1000028)([H]1000029)).[C]4([H]1000001)([H]1000002){=}[C]5([H]1000003)[C]6([C]7([H]1000004)([H]1000005)([H]1000006)){=}[C]8([H]1000007)([H]1000008).[C.]22([H]1000024)([H]1000025)([H]1000026)',
    name='IMS9-EQ9.12:step_alpha_methyl_loss',
)

# IMS9-EQ9.13:step_benzylic_alpha_cleavage
IMS9_EQ9_13_step_benzylic_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([C]4([H]1000005){=}[C]5([H]1000006)[C+]6([H]1000007)[C]7([H]1000008){=}[C]8({-}3)([H]1000009))>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[C]3([C]4([H]1000005){=}[C]5([H]1000006)[C+]6([H]1000007)[C]7([H]1000008){=}[C]8({-}3)([H]1000009))',
    name='IMS9-EQ9.13:step_benzylic_alpha_cleavage',
)

# IMS9-EQ9.14:step_benzylic_alpha_cleavage
IMS9_EQ9_14_step_benzylic_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C.]3([C]4([H]1000003){=}[C]5([H]1000004)[C+]6([H]1000005)[C]7([H]1000006){=}[C]8({-}3)([H]1000007)))([C]9([H]11)([H]1000008)([H]1000009))[C]10([H]12)([H]1000010)([H]1000011)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2({=}[C]3([C]4([H]1000003){=}[C]5([H]1000004)[C+]6([H]1000005)[C]7([H]1000006){=}[C]8({-}3)([H]1000007)))([C]9([H]11)([H]1000008)([H]1000009))[C]10([H]12)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.14:step_benzylic_alpha_cleavage',
)

# IMS9-EQ9.14:step_olefin_elimination
IMS9_EQ9_14_step_olefin_elimination = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2({=}[C]3([C]4([H]1000003){=}[C]5([H]1000004)[C+]6([H]1000005)[C]7([H]1000006){=}[C]8({-}3)([H]1000007)))([C]9([H]11)([H]1000008)([H]1000009))[C]10([H]12)([H]1000010)([H]1000011)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]11)([H]12){=}[C]3([C]4([H]1000003){=}[C]5([H]1000004)[C+]6([H]1000005)[C]7([H]1000006){=}[C]8({-}3)([H]1000007)).[C]9([H]1000008)([H]1000009){=}[C]10([H]1000010)([H]1000011)',
    name='IMS9-EQ9.14:step_olefin_elimination',
)

# IMS9-EQ9.15:step_gamma_h_rearrangement
IMS9_EQ9_15_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]4)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C+]7([C.]8([H]1000010)[C]9([H]1000011){=}[C]10([H]1000012)[C]11([H]1000013){=}[C]12({-}7)([H]1000014))>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C+]7([C]8([H]4)([H]1000010)[C]9([H]1000011){=}[C]10([H]1000012)[C]11([H]1000013){=}[C]12({-}7)([H]1000014))',
    name='IMS9-EQ9.15:step_gamma_h_rearrangement',
)

# IMS9-EQ9.15:step_alpha_cleavage
IMS9_EQ9_15_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C+]7([C]8([H]4)([H]1000010)[C]9([H]1000011){=}[C]10([H]1000012)[C]11([H]1000013){=}[C]12({-}7)([H]1000014))>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C]3([H]1000005){=}[C]5([H]1000006)([H]1000007).[H]4[C]8([C+]7([C.]6([H]1000008)([H]1000009))[C]12([H]1000014){=}[C]11([H]1000013)[C]10([H]1000012){=}[C]9({-}8)([H]1000011))([H]1000010)',
    name='IMS9-EQ9.15:step_alpha_cleavage',
)

# IMS9-EQ9.16:step_ortho_h_rearrangement_with_beta_cleavage
IMS9_EQ9_16_step_ortho_h_rearrangement_with_beta_cleavage = mod.Rule.fromDFS(
    s='[C+]1([C.]2([H]1000000)[C]3([H]1000001){=}[C]4([C]5([H]1000002){=}[C]6({-}1)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006))[C]8([H]1000007)([H]1000008)[C]9([H]1000009)([H]1000010)[C]10([H]11)([H]1000011)([H]1000012)>>[C+]1([C]2([H]11)([H]1000000)[C]3([H]1000001){=}[C]4([C]5([H]1000002){=}[C]6({-}1)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006))[C.]8([H]1000007)([H]1000008).[C]9([H]1000009)([H]1000010){=}[C]10([H]1000011)([H]1000012)',
    name='IMS9-EQ9.16:step_ortho_h_rearrangement_with_beta_cleavage',
)

# IMS9-EQ9.17:step_benzylic_alpha_cleavage
IMS9_EQ9_17_step_benzylic_alpha_cleavage = mod.Rule.fromDFS(
    s='[C.]1([C+]2([H]1000000)[C]3([H]1000001){=}[C]4([H]1000002)[C]5({=}[C]6({-}1)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006))[C]8([H]1000007)([H]1000008)[C]9([H]1000009)([H]1000010)[C]10([H]1000011)([H]1000012)([H]1000013)>>[C]1([C+]2([H]1000000)[C]3([H]1000001){=}[C]4([H]1000002)[C]5({=}[C]6({-}1)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006)){=}[C]8([H]1000007)([H]1000008).[C.]9([H]1000009)([H]1000010)[C]10([H]1000011)([H]1000012)([H]1000013)',
    name='IMS9-EQ9.17:step_benzylic_alpha_cleavage',
)

# IMS9-EQ9.18a:step_alpha_butyl_loss
IMS9_EQ9_18a_step_alpha_butyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000008))([H]1000000)([H]1000001)[C]5([C]6([H]1000009)([H]1000010)([H]1000011))([C]7([H]1000012)([H]1000013)[C]8([H]10)([H]1000014)([H]1000015))[O+.]9[H]1000016>>[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000008).[C]5([C]6([H]1000009)([H]1000010)([H]1000011))([C]7([H]1000012)([H]1000013)[C]8([H]10)([H]1000014)([H]1000015)){=}[O+]9[H]1000016',
    name='IMS9-EQ9.18a:step_alpha_butyl_loss',
)

# IMS9-EQ9.18a:step_rh_ethene_loss
IMS9_EQ9_18a_step_rh_ethene_loss = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000008).[C]5([C]6([H]1000009)([H]1000010)([H]1000011))([C]7([H]1000012)([H]1000013)[C]8([H]10)([H]1000014)([H]1000015)){=}[O+]9[H]1000016>>[C.]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)([H]1000008).[C]5([C]6([H]1000009)([H]1000010)([H]1000011))([H]10){=}[O+]9[H]1000016.[C]7([H]1000012)([H]1000013){=}[C]8([H]1000014)([H]1000015)',
    name='IMS9-EQ9.18a:step_rh_ethene_loss',
)

# IMS9-EQ9.18b:step_alpha_ethyl_loss
IMS9_EQ9_18b_step_alpha_ethyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([C]7([H]1000011)([H]1000012)[C]8([H]1000013)([H]1000014)([H]1000015))[O+.]9[H]1000016>>[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)[C]5([C]6([H]1000008)([H]1000009)([H]1000010)){=}[O+]9[H]1000016.[C.]7([H]1000011)([H]1000012)[C]8([H]1000013)([H]1000014)([H]1000015)',
    name='IMS9-EQ9.18b:step_alpha_ethyl_loss',
)

# IMS9-EQ9.18b:step_rh_butene_loss
IMS9_EQ9_18b_step_rh_butene_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)[C]5([C]6([H]1000008)([H]1000009)([H]1000010)){=}[O+]9[H]1000016.[C.]7([H]1000011)([H]1000012)[C]8([H]1000013)([H]1000014)([H]1000015)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]10){=}[O+]9[H]1000016.[C.]7([H]1000011)([H]1000012)[C]8([H]1000013)([H]1000014)([H]1000015)',
    name='IMS9-EQ9.18b:step_rh_butene_loss',
)

# IMS9-EQ9.18c:step_alpha_methyl_loss
IMS9_EQ9_18c_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([C]7([H]1000011)([H]1000012)[C]8([H]11)([H]1000013)([H]1000014))[O+.]9[H]1000015>>[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)[C]5([C]7([H]1000011)([H]1000012)[C]8([H]11)([H]1000013)([H]1000014)){=}[O+]9[H]1000015.[C.]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS9-EQ9.18c:step_alpha_methyl_loss',
)

# IMS9-EQ9.18c:step_rh_butene_loss
IMS9_EQ9_18c_step_rh_butene_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007))([H]1000000)([H]1000001)[C]5([C]7([H]1000011)([H]1000012)[C]8([H]11)([H]1000013)([H]1000014)){=}[O+]9[H]1000015.[C.]6([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([C]7([H]1000011)([H]1000012)[C]8([H]11)([H]1000013)([H]1000014))([H]10){=}[O+]9[H]1000015.[C.]6([H]1000008)([H]1000009)([H]1000010)',
    name='IMS9-EQ9.18c:step_rh_butene_loss',
)

# IMS9-EQ9.18c:step_rh_ethene_loss
IMS9_EQ9_18c_step_rh_ethene_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([C]7([H]1000011)([H]1000012)[C]8([H]11)([H]1000013)([H]1000014))([H]10){=}[O+]9[H]1000015.[C.]6([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007).[C]5([H]10)([H]11){=}[O+]9[H]1000015.[C.]6([H]1000008)([H]1000009)([H]1000010).[C]7([H]1000011)([H]1000012){=}[C]8([H]1000013)([H]1000014)',
    name='IMS9-EQ9.18c:step_rh_ethene_loss',
)

# IMS9-EQ9.19a:step_alpha_ring_opening
IMS9_EQ9_19a_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000)[O+.]7[H]1000010>>[C]1([C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C]3([H]1000002)([H]1000003)[C.]2([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010',
    name='IMS9-EQ9.19a:step_alpha_ring_opening',
)

# IMS9-EQ9.19a:step_rh_c6_to_c2  [1 hydrogen migration(s) inferred]
IMS9_EQ9_19a_step_rh_c6_to_c2 = mod.Rule.fromDFS(
    s='[C]1([C]6([H]1000008)([H]1000013)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C]3([H]1000002)([H]1000003)[C.]2([H]1000001)[C]8([H]1000010)([H]1000011)([H]1000012))([H]1000000){=}[O+]7[H]1000009>>[C]1([C.]6([H]1000008)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C]3([H]1000002)([H]1000003)[C]2([H]1000001)([H]1000013)[C]8([H]1000010)([H]1000011)([H]1000012))([H]1000000){=}[O+]7[H]1000009',
    name='IMS9-EQ9.19a:step_rh_c6_to_c2',
)

# IMS9-EQ9.19a:step_alpha_loss_butyl
IMS9_EQ9_19a_step_alpha_loss_butyl = mod.Rule.fromDFS(
    s='[C]1([C.]6([H]1000009)[C]5([H]1000007)([H]1000008)[C]4([H]1000005)([H]1000006)[C]3([H]1000003)([H]1000004)[C]2([H]1000001)([H]1000002)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010>>[C]1([C]6([H]1000009){=}[C]5([H]1000007)([H]1000008))([H]1000000){=}[O+]7[H]1000010.[C]2([C]3([H]1000003)([H]1000004)[C.]4([H]1000005)([H]1000006))([H]1000001)([H]1000002)[C]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS9-EQ9.19a:step_alpha_loss_butyl',
)

# IMS9-EQ9.19b:step_alpha_ring_opening
IMS9_EQ9_19b_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000)[O+.]7[H]1000010>>[C]1([C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C]3([H]1000002)([H]1000003)[C.]2([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010',
    name='IMS9-EQ9.19b:step_alpha_ring_opening',
)

# IMS9-EQ9.19b:step_alpha_loss_propene
IMS9_EQ9_19b_step_alpha_loss_propene = mod.Rule.fromDFS(
    s='[C]1([C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C]4([H]1000004)([H]1000005)[C]3([H]1000002)([H]1000003)[C.]2([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010>>[C]1([C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005))([H]1000000){=}[O+]7[H]1000010.[C]2({=}[C]3([H]1000002)([H]1000003))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013)',
    name='IMS9-EQ9.19b:step_alpha_loss_propene',
)

# IMS9-EQ9.19b:step_alpha_loss_ethene
IMS9_EQ9_19b_step_alpha_loss_ethene = mod.Rule.fromDFS(
    s='[C]1([C]6([H]1000008)([H]1000009)[C]5([H]1000006)([H]1000007)[C.]4([H]1000004)([H]1000005))([H]1000000){=}[O+]7[H]1000010.[C]2({=}[C]3([H]1000002)([H]1000003))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013)>>[C]1([C.]6([H]1000008)([H]1000009))([H]1000000){=}[O+]7[H]1000010.[C]2({=}[C]3([H]1000002)([H]1000003))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013).[C]4([H]1000004)([H]1000005){=}[C]5([H]1000006)([H]1000007)',
    name='IMS9-EQ9.19b:step_alpha_loss_ethene',
)

# IMS9-EQ9.1a:step_sigma_cleavage_charge_retention  [auto-localized precursor]
IMS9_EQ9_1a_step_sigma_cleavage_charge_retention = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C.]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007))([C]5([H]1000008)([H]1000009)([H]1000010))[C]6([H]1000011)([H]1000012)([H]1000013)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]5([H]1000008)([H]1000009)([H]1000010))[C]6([H]1000011)([H]1000012)([H]1000013).[C.]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)([H]1000007)',
    name='IMS9-EQ9.1a:step_sigma_cleavage_charge_retention',
)

# IMS9-EQ9.2:step_sigma_cleavage_loss_of_methyl  [auto-localized precursor]
IMS9_EQ9_2_step_sigma_cleavage_loss_of_methyl = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))([C.]4([H]1000006)([H]1000007)([H]1000008))[C]5([H]1000009)([H]1000010)[C]6([C]7([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]8([H]1000015)([H]1000016)([H]1000017)>>[C+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))[C]5([H]1000009)([H]1000010)[C]6([C]7([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]8([H]1000015)([H]1000016)([H]1000017).[C.]4([H]1000006)([H]1000007)([H]1000008)',
    name='IMS9-EQ9.2:step_sigma_cleavage_loss_of_methyl',
)

# IMS9-EQ9.2:step_alpha_cleavage_olefin_loss
IMS9_EQ9_2_step_alpha_cleavage_olefin_loss = mod.Rule.fromDFS(
    s='[C+]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005))[C]5([H]1000009)([H]1000010)[C]6([C]7([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]8([H]1000015)([H]1000016)([H]1000017).[C.]4([H]1000006)([H]1000007)([H]1000008)>>[C]1([C]2([H]1000000)([H]1000001)([H]1000002))([C]3([H]1000003)([H]1000004)([H]1000005)){=}[C]5([H]1000009)([H]1000010).[C.]4([H]1000006)([H]1000007)([H]1000008).[C+]6([C]7([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]8([H]1000015)([H]1000016)([H]1000017)',
    name='IMS9-EQ9.2:step_alpha_cleavage_olefin_loss',
)

# IMS9-EQ9.20a:step_alpha_ring_opening
IMS9_EQ9_20a_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000)[O+.]7[H]1000010>>[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010',
    name='IMS9-EQ9.20a:step_alpha_ring_opening',
)

# IMS9-EQ9.20a:step_rh_c2_to_c6  [1 hydrogen migration(s) inferred]
IMS9_EQ9_20a_step_rh_c2_to_c6 = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)([H]1000008))([H]1000013)[C]8([H]1000010)([H]1000011)([H]1000012))([H]1000000){=}[O+]7[H]1000009>>[C]1([C.]2([C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000013))[C]8([H]1000010)([H]1000011)([H]1000012))([H]1000000){=}[O+]7[H]1000009',
    name='IMS9-EQ9.20a:step_rh_c2_to_c6',
)

# IMS9-EQ9.20a:step_alpha_loss_propyl
IMS9_EQ9_20a_step_alpha_loss_propyl = mod.Rule.fromDFS(
    s='[C]1([C.]2([C]3([H]1000001)([H]1000002)[C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010>>[C]1([C]2({=}[C]3([H]1000001)([H]1000002))[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010.[C.]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.20a:step_alpha_loss_propyl',
)

# IMS9-EQ9.20b:step_alpha_ring_opening
IMS9_EQ9_20b_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6({-}1)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000)[O+.]7[H]1000010>>[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010',
    name='IMS9-EQ9.20b:step_alpha_ring_opening',
)

# IMS9-EQ9.20b:step_alpha_loss_ethene_1
IMS9_EQ9_20b_step_alpha_loss_ethene_1 = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C.]6([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010>>[C]1([C]2([C]3([H]1000002)([H]1000003)[C.]4([H]1000004)([H]1000005))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010.[C]5([H]1000006)([H]1000007){=}[C]6([H]1000008)([H]1000009)',
    name='IMS9-EQ9.20b:step_alpha_loss_ethene_1',
)

# IMS9-EQ9.20b:step_alpha_loss_ethene_2
IMS9_EQ9_20b_step_alpha_loss_ethene_2 = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C.]4([H]1000004)([H]1000005))([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010.[C]5([H]1000006)([H]1000007){=}[C]6([H]1000008)([H]1000009)>>[C]1([C.]2([H]1000001)[C]8([H]1000011)([H]1000012)([H]1000013))([H]1000000){=}[O+]7[H]1000010.[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)([H]1000005).[C]5([H]1000006)([H]1000007){=}[C]6([H]1000008)([H]1000009)',
    name='IMS9-EQ9.20b:step_alpha_loss_ethene_2',
)

# IMS9-EQ9.21:step_alpha_cleavage_ring_opening
IMS9_EQ9_21_step_alpha_cleavage_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6({-}1)([H]1000007)([H]1000008))([H]1000001)[C]7([H]1000009)([H]1000010)([H]1000011))([H]1000000)[O+.]8[H]9>>[C]1([C]6([H]1000007)([H]1000008)[C]5([H]1000005)([H]1000006)[C]4([H]10)([H]1000004)[C]3([H]1000002)([H]1000003)[C.]2([H]1000001)[C]7([H]1000009)([H]1000010)([H]1000011))([H]1000000){=}[O+]8[H]9',
    name='IMS9-EQ9.21:step_alpha_cleavage_ring_opening',
)

# IMS9-EQ9.21:step_rH_oxygen_to_carbon
IMS9_EQ9_21_step_rH_oxygen_to_carbon = mod.Rule.fromDFS(
    s='[C]1([C]6([H]1000007)([H]1000008)[C]5([H]1000005)([H]1000006)[C]4([H]10)([H]1000004)[C]3([H]1000002)([H]1000003)[C.]2([H]1000001)[C]7([H]1000009)([H]1000010)([H]1000011))([H]1000000){=}[O+]8[H]9>>[C]1([C]6([H]1000007)([H]1000008)[C]5([H]1000005)([H]1000006)[C]4([H]10)([H]1000004)[C]3([H]1000002)([H]1000003)[C]2([H]9)([H]1000001)[C]7([H]1000009)([H]1000010)([H]1000011))([H]1000000){=}[O+.]8',
    name='IMS9-EQ9.21:step_rH_oxygen_to_carbon',
)

# IMS9-EQ9.21:step_mclafferty_pentene_loss
IMS9_EQ9_21_step_mclafferty_pentene_loss = mod.Rule.fromDFS(
    s='[C]1([C]6([H]1000007)([H]1000008)[C]5([H]1000005)([H]1000006)[C]4([H]10)([H]1000004)[C]3([H]1000002)([H]1000003)[C]2([H]9)([H]1000001)[C]7([H]1000009)([H]1000010)([H]1000011))([H]1000000){=}[O+.]8>>[C]1([C.]6([H]1000007)([H]1000008))([H]1000000){=}[O+]8[H]10.[C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004){=}[C]5([H]1000005)([H]1000006))([H]9)([H]1000001)[C]7([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.21:step_mclafferty_pentene_loss',
)

# IMS9-EQ9.22:step_rh_hydroxyl_to_ortho_radical
IMS9_EQ9_22_step_rh_hydroxyl_to_ortho_radical = mod.Rule.fromDFS(
    s='[C+]1([C]2({=}[C]3([H]1000000)[C]4([H]1000001){=}[C]5([H]1000002)[C.]6({-}1)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006))[O]9[H]10>>[C]1([C]2({=}[C]3([H]1000000)[C]4([H]1000001){=}[C]5([H]1000002)[C]6({-}1)([H]10)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006)){=}[O+.]9',
    name='IMS9-EQ9.22:step_rh_hydroxyl_to_ortho_radical',
)

# IMS9-EQ9.22:step_co_elimination
IMS9_EQ9_22_step_co_elimination = mod.Rule.fromDFS(
    s='[C]1([C]2({=}[C]3([H]1000000)[C]4([H]1000001){=}[C]5([H]1000002)[C]6({-}1)([H]10)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006)){=}[O+.]9>>[C-]1{#}[O+]9.[C.]2([C+]3([H]1000000)[C]4([H]1000001){=}[C]5([H]1000002)[C]6({-}2)([H]10)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006)',
    name='IMS9-EQ9.22:step_co_elimination',
)

# IMS9-EQ9.22:step_alpha_hydrogen_loss
IMS9_EQ9_22_step_alpha_hydrogen_loss = mod.Rule.fromDFS(
    s='[C-]1{#}[O+]9.[C.]2([C+]3([H]1000000)[C]4([H]1000001){=}[C]5([H]1000002)[C]6({-}2)([H]10)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006)>>[C-]1{#}[O+]9.[C]2([C+]3([H]1000000)[C]4([H]1000001){=}[C]5([H]1000002)[C]6({=}2)([H]1000003))[C]7([H]1000004)([H]1000005)([H]1000006).[H.]10',
    name='IMS9-EQ9.22:step_alpha_hydrogen_loss',
)

# IMS9-EQ9.23:step_rh_benzylic_to_oxygen
IMS9_EQ9_23_step_rh_benzylic_to_oxygen = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]7([H]8)([H]1000004)([H]1000005))[O+.]9[H]10>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C.]7([H]1000004)([H]1000005))[O+]9([H]8)([H]10)',
    name='IMS9-EQ9.23:step_rh_benzylic_to_oxygen',
)

# IMS9-EQ9.23:step_inductive_water_loss
IMS9_EQ9_23_step_inductive_water_loss = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C.]7([H]1000004)([H]1000005))[O+]9([H]8)([H]10)>>[C+]1([C]2({=}[C]3([H]1000000)[C]4([H]1000001){=}[C]5([H]1000002)[C.]6({-}1)([H]1000003))[C]7({-}1)([H]1000004)([H]1000005)).[H]8[O]9[H]10',
    name='IMS9-EQ9.23:step_inductive_water_loss',
)

# IMS9-EQ9.24:step_rh_phenol_to_ester_oxygen
IMS9_EQ9_24_step_rh_phenol_to_ester_oxygen = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[O]11[H]12)[C]7({=}[O]8)[O+.]9[C]10([H]1000004)([H]1000005)([H]1000006)>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[O.]11)[C]7({=}[O]8)[O+]9([H]12)[C]10([H]1000004)([H]1000005)([H]1000006)',
    name='IMS9-EQ9.24:step_rh_phenol_to_ester_oxygen',
)

# IMS9-EQ9.24:step_inductive_methanol_loss
IMS9_EQ9_24_step_inductive_methanol_loss = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[O.]11)[C]7({=}[O]8)[O+]9([H]12)[C]10([H]1000004)([H]1000005)([H]1000006)>>[C]1([C]2([C]3([H]1000000){=}[C]4([H]1000001)[C]5([H]1000002){=}[C]6({-}1)([H]1000003)){=}[O]11){=}[C]7{=}[O+.]8.[O]9([H]12)[C]10([H]1000004)([H]1000005)([H]1000006)',
    name='IMS9-EQ9.24:step_inductive_methanol_loss',
)

# IMS9-EQ9.25a:step_alpha_cho
IMS9_EQ9_25a_step_alpha_cho = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+.]7>>[C]1([H]1000000){#}[O+]7.[C.]2([C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.25a:step_alpha_cho',
)

# IMS9-EQ9.25b:step_rH_gamma
IMS9_EQ9_25b_step_rH_gamma = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+.]7>>[C]1([C]2([C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+]7[H]10',
    name='IMS9-EQ9.25b:step_rH_gamma',
)

# IMS9-EQ9.25b:step_alpha_butene_loss
IMS9_EQ9_25b_step_alpha_butene_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+]7[H]10>>[C]1([C.]2([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+]7[H]10.[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.25b:step_alpha_butene_loss',
)

# IMS9-EQ9.25b:step_alpha_methyl_loss
IMS9_EQ9_25b_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+]7[H]10.[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)>>[C]1([C]2([H]1000001){=}[C]8([H]1000010)([H]1000011))([H]1000000){=}[O+]7[H]10.[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009).[C.]9([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.25b:step_alpha_methyl_loss',
)

# IMS9-EQ9.25c:step_mclafferty_ethene_loss
IMS9_EQ9_25c_step_mclafferty_ethene_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000001)[C]8([H]1000011)([H]1000012)[C]9([H]11)([H]1000013)([H]1000014))([H]1000000){=}[O+.]7>>[C]1([C.]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+]7[H]11.[C]8([H]1000011)([H]1000012){=}[C]9([H]1000013)([H]1000014)',
    name='IMS9-EQ9.25c:step_mclafferty_ethene_loss',
)

# IMS9-EQ9.25c:step_alpha_propyl_loss
IMS9_EQ9_25c_step_alpha_propyl_loss = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010))([H]1000000){=}[O+]7[H]11.[C]8([H]1000011)([H]1000012){=}[C]9([H]1000013)([H]1000014)>>[C]1([C]2([H]1000001){=}[C]3([H]1000002)([H]1000003))([H]1000000){=}[O+]7[H]11.[C.]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)([H]1000010).[C]8([H]1000011)([H]1000012){=}[C]9([H]1000013)([H]1000014)',
    name='IMS9-EQ9.25c:step_alpha_propyl_loss',
)

# IMS9-EQ9.25d:step_inductive
IMS9_EQ9_25d_step_inductive = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+.]7>>[C.]1([H]1000000){=}[O]7.[C+]2([C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.25d:step_inductive',
)

# IMS9-EQ9.25e:step_sigma
IMS9_EQ9_25e_step_sigma = mod.Rule.fromDFS(
    s='[C]1([C]2([C]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009))([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O+.]7>>[C]1([C.]2([H]1000001)[C]8([H]1000010)([H]1000011)[C]9([H]1000012)([H]1000013)([H]1000014))([H]1000000){=}[O]7.[C+]3([H]1000002)([H]1000003)[C]4([H]10)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.25e:step_sigma',
)

# IMS9-EQ9.26a:step_alpha_acetyl
IMS9_EQ9_26a_step_alpha_acetyl = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){=}[O+.]9>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2{#}[O+]9.[C.]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.26a:step_alpha_acetyl',
)

# IMS9-EQ9.26b:step_alpha_methyl_loss
IMS9_EQ9_26b_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){=}[O+.]9>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){#}[O+]9',
    name='IMS9-EQ9.26b:step_alpha_methyl_loss',
)

# IMS9-EQ9.26b:step_inductive_co_loss
IMS9_EQ9_26b_step_inductive_co_loss = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){#}[O+]9>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C-]2{#}[O+]9.[C+]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.26b:step_inductive_co_loss',
)

# IMS9-EQ9.26c:step_inductive
IMS9_EQ9_26c_step_inductive = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){=}[O+.]9>>[C]1([H]1000000)([H]1000001)([H]1000002)[C.]2{=}[O]9.[C+]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.26c:step_inductive',
)

# IMS9-EQ9.26d:step_rH_gamma
IMS9_EQ9_26d_step_rH_gamma = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){=}[O+.]9>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){=}[O+]9[H]10',
    name='IMS9-EQ9.26d:step_rH_gamma',
)

# IMS9-EQ9.26d:step_alpha_alkene_loss
IMS9_EQ9_26d_step_alpha_alkene_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)){=}[O+]9[H]10>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C.]3([H]1000003)([H]1000004)){=}[O+]9[H]10.[C]4([H]1000005)([H]1000006){=}[C]5([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.26d:step_alpha_alkene_loss',
)

# IMS9-EQ9.26e:step_inductive_charge_migration
IMS9_EQ9_26e_step_inductive_charge_migration = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C.]5([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014))[O]9[H]10>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)([H]1000004))[O]9[H]10.[C+]4([H]1000005)([H]1000006)[C.]5([H]1000007)[C]6([C]7([H]1000009)([H]1000010)([H]1000011))([H]1000008)[C]8([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.26e:step_inductive_charge_migration',
)

# IMS9-EQ9.27a:step_alpha_c1_methyl_loss
IMS9_EQ9_27a_step_alpha_c1_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]12)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]11)([H]13)[C]6([H]1000006)([H]1000007)([H]1000008)){=}[O+.]7>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([C]3([H]12)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]11)([H]13)[C]6([H]1000006)([H]1000007)([H]1000008)){#}[O+]7',
    name='IMS9-EQ9.27a:step_alpha_c1_methyl_loss',
)

# IMS9-EQ9.27b:step_rH_slow_s1_s2
IMS9_EQ9_27b_step_rH_slow_s1_s2 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]12)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]11)([H]13)[C]6([H]1000006)([H]1000007)([H]1000008)){=}[O+.]7>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]12)([H]1000003)[C]4([H]1000004)([H]1000005)[C.]5([H]13)[C]6([H]1000006)([H]1000007)([H]1000008))[O]7[H]11',
    name='IMS9-EQ9.27b:step_rH_slow_s1_s2',
)

# IMS9-EQ9.27b:step_rC_s2_s3
IMS9_EQ9_27b_step_rC_s2_s3 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]12)([H]1000003)[C]4([H]1000004)([H]1000005)[C.]5([H]13)[C]6([H]1000006)([H]1000007)([H]1000008))[O]7[H]11>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]12)([H]1000003)[C]5([C.]4([H]1000004)([H]1000005))([H]13)[C]6([H]1000006)([H]1000007)([H]1000008))[O]7[H]11',
    name='IMS9-EQ9.27b:step_rC_s2_s3',
)

# IMS9-EQ9.27b:step_rH_s3_s4
IMS9_EQ9_27b_step_rH_s3_s4 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]12)([H]1000003)[C]5([C.]4([H]1000004)([H]1000005))([H]13)[C]6([H]1000006)([H]1000007)([H]1000008))[O]7[H]11>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]12)([H]1000003)[C]5([C]4([H]11)([H]1000004)([H]1000005))([H]13)[C]6([H]1000006)([H]1000007)([H]1000008)){=}[O+.]7',
    name='IMS9-EQ9.27b:step_rH_s3_s4',
)

# IMS9-EQ9.27b:step_rH_s4_s5
IMS9_EQ9_27b_step_rH_s4_s5 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]12)([H]1000003)[C]5([C]4([H]11)([H]1000004)([H]1000005))([H]13)[C]6([H]1000006)([H]1000007)([H]1000008)){=}[O+.]7>>[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]12)([H]1000003)[C.]5([C]4([H]11)([H]1000004)([H]1000005))[C]6([H]1000006)([H]1000007)([H]1000008))[O]7[H]13',
    name='IMS9-EQ9.27b:step_rH_s4_s5',
)

# IMS9-EQ9.27b:step_s5_s6
IMS9_EQ9_27b_step_s5_s6 = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C+]2([C]3([H]12)([H]1000003)[C.]5([C]4([H]11)([H]1000004)([H]1000005))[C]6([H]1000006)([H]1000007)([H]1000008))[O]7[H]13>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C]5([C]4([H]11)([H]1000004)([H]1000005))([H]12)[C]6([H]1000006)([H]1000007)([H]1000008))[O+.]7[H]13',
    name='IMS9-EQ9.27b:step_s5_s6',
)

# IMS9-EQ9.27b:step_c4_methyl_loss
IMS9_EQ9_27b_step_c4_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C]5([C]4([H]11)([H]1000004)([H]1000005))([H]12)[C]6([H]1000006)([H]1000007)([H]1000008))[O+.]7[H]13>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C+]5([H]12)[C]6([H]1000006)([H]1000007)([H]1000008))[O]7[H]13.[C.]4([H]11)([H]1000004)([H]1000005)',
    name='IMS9-EQ9.27b:step_c4_methyl_loss',
)

# IMS9-EQ9.27c:step_c6_methyl_loss
IMS9_EQ9_27c_step_c6_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C]5([C]4([H]11)([H]1000004)([H]1000005))([H]12)[C]6([H]1000006)([H]1000007)([H]1000008))[O+.]7[H]13>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)[C+]5([H]12)[C]4([H]11)([H]1000004)([H]1000005))[O]7[H]13.[C.]6([H]1000006)([H]1000007)([H]1000008)',
    name='IMS9-EQ9.27c:step_c6_methyl_loss',
)

# IMS9-EQ9.28a:step_double_bond_isomerization
IMS9_EQ9_28a_step_double_bond_isomerization = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10){=}[C]6([C]7([H]11)([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)){=}[O+.]9>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]11)[C]6({=}[C]7([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)){=}[O+.]9',
    name='IMS9-EQ9.28a:step_double_bond_isomerization',
)

# IMS9-EQ9.28a:step_mclafferty_concerted
IMS9_EQ9_28a_step_mclafferty_concerted = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]11)[C]6({=}[C]7([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)){=}[O+.]9>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C.]3([H]1000003)([H]1000004)){=}[O+]9[H]10.[C]4([H]1000005)([H]1000006){=}[C]5([H]11)[C]6({=}[C]7([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.28a:step_mclafferty_concerted',
)

# IMS9-EQ9.28b:step_double_bond_isomerization
IMS9_EQ9_28b_step_double_bond_isomerization = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10){=}[C]6([C]7([H]11)([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)){=}[O+.]9>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]11)[C]6({=}[C]7([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)){=}[O+.]9',
    name='IMS9-EQ9.28b:step_double_bond_isomerization',
)

# IMS9-EQ9.28b:step_mclafferty_charge_migration
IMS9_EQ9_28b_step_mclafferty_charge_migration = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]10)([H]11)[C]6({=}[C]7([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)){=}[O+.]9>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[C]3([H]1000003)([H]1000004))[O]9[H]10.[C+]4([H]1000005)([H]1000006)[C.]5([H]11)[C]6({=}[C]7([H]1000007)([H]1000008))[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.28b:step_mclafferty_charge_migration',
)

# IMS9-EQ9.29:step_rc_cyclization
IMS9_EQ9_29_step_rc_cyclization = mod.Rule.fromDFS(
    s='[C]1({=}[C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}1)([C]12([H]1000014)([H]1000015)([H]1000016))[C]13([H]1000017)([H]1000018)([H]1000019))[C]11([H]1000011)([H]1000012)([H]1000013))[C]7([H]1000006){=}[C]8([H]1000007)[C]9([C]10([H]1000008)([H]1000009)([H]1000010)){=}[O+.]14>>[C.]1([C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}1)([C]12([H]1000014)([H]1000015)([H]1000016))[C]13([H]1000017)([H]1000018)([H]1000019))([C]11([H]1000011)([H]1000012)([H]1000013))[O+]14{=}[C]9([C]8([H]1000007){=}[C]7({-}1)([H]1000006))[C]10([H]1000008)([H]1000009)([H]1000010))',
    name='IMS9-EQ9.29:step_rc_cyclization',
)

# IMS9-EQ9.29:step_rd_methyl_loss
IMS9_EQ9_29_step_rd_methyl_loss = mod.Rule.fromDFS(
    s='[C.]1([C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}1)([C]12([H]1000014)([H]1000015)([H]1000016))[C]13([H]1000017)([H]1000018)([H]1000019))([C]11([H]1000011)([H]1000012)([H]1000013))[O+]14{=}[C]9([C]8([H]1000007){=}[C]7({-}1)([H]1000006))[C]10([H]1000008)([H]1000009)([H]1000010))>>[C]1(:[C]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)[C]5([H]1000004)([H]1000005)[C]6({-}1)([C]12([H]1000014)([H]1000015)([H]1000016))[C]13([H]1000017)([H]1000018)([H]1000019)):[O+]14:[C]9(:[C]8([H]1000007):[C]7(:1)([H]1000006))[C]10([H]1000008)([H]1000009)([H]1000010)).[C.]11([H]1000011)([H]1000012)([H]1000013)',
    name='IMS9-EQ9.29:step_rd_methyl_loss',
)

# IMS9-EQ9.3:step_allylic_alpha_cleavage
IMS9_EQ9_3_step_allylic_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([H]1000003)([H]1000004)[C.]3([H]1000005)[C+]4([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2([H]1000003)([H]1000004){=}[C]3([H]1000005)[C+]4([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.3:step_allylic_alpha_cleavage',
)

# IMS9-EQ9.30a:step_alpha_ring_opening
IMS9_EQ9_30a_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([C]4([H]1000002)([H]1000003)[C]5([C]6({-}1)([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015))([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012)){=}[O+.]7>>[C]1([C]2([H]1000000)([H]1000001)[C]3([C]4([H]1000002)([H]1000003)[C]5([C.]6([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015))([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012)){#}[O+]7',
    name='IMS9-EQ9.30a:step_alpha_ring_opening',
)

# IMS9-EQ9.30a:step_inductive_co_loss
IMS9_EQ9_30a_step_inductive_co_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([C]4([H]1000002)([H]1000003)[C]5([C.]6([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015))([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012)){#}[O+]7>>[C-]1{#}[O+]7.[C+]2([H]1000000)([H]1000001)[C]3([C]4([H]1000002)([H]1000003)[C]5([C.]6([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015))([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012)',
    name='IMS9-EQ9.30a:step_inductive_co_loss',
)

# IMS9-EQ9.30a:step_inductive_alkene_loss
IMS9_EQ9_30a_step_inductive_alkene_loss = mod.Rule.fromDFS(
    s='[C-]1{#}[O+]7.[C+]2([H]1000000)([H]1000001)[C]3([C]4([H]1000002)([H]1000003)[C]5([C.]6([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015))([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012)>>[C-]1{#}[O+]7.[C]2([H]1000000)([H]1000001){=}[C]3([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012).[C+]4([H]1000002)([H]1000003)[C]5([C.]6([H]1000005)([H]1000006))([H]1000004)[C]10([H]1000013)([H]1000014)([H]1000015)',
    name='IMS9-EQ9.30a:step_inductive_alkene_loss',
)

# IMS9-EQ9.30b:step_alpha_ring_opening
IMS9_EQ9_30b_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([H]11)([H]1000000)[C]3([C]4([H]1000001)([H]1000002)[C]5([C]6({-}1)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)){=}[O+.]7>>[C]1([C]2([H]11)([H]1000000)[C]3([C]4([H]1000001)([H]1000002)[C]5([C.]6([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)){#}[O+]7',
    name='IMS9-EQ9.30b:step_alpha_ring_opening',
)

# IMS9-EQ9.30b:step_rH_c2_to_c6
IMS9_EQ9_30b_step_rH_c2_to_c6 = mod.Rule.fromDFS(
    s='[C]1([C]2([H]11)([H]1000000)[C]3([C]4([H]1000001)([H]1000002)[C]5([C.]6([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)){#}[O+]7>>[C]1([C.]2([H]1000000)[C]3([C]4([H]1000001)([H]1000002)[C]5([C]6([H]11)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)){#}[O+]7',
    name='IMS9-EQ9.30b:step_rH_c2_to_c6',
)

# IMS9-EQ9.30b:step_alpha_isobutyl_loss
IMS9_EQ9_30b_step_alpha_isobutyl_loss = mod.Rule.fromDFS(
    s='[C]1([C.]2([H]1000000)[C]3([C]4([H]1000001)([H]1000002)[C]5([C]6([H]11)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)){#}[O+]7>>[C]1([C]2([H]1000000){=}[C]3([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)){#}[O+]7.[C.]4([H]1000001)([H]1000002)[C]5([C]6([H]11)([H]1000004)([H]1000005))([H]1000003)[C]10([H]1000012)([H]1000013)([H]1000014)',
    name='IMS9-EQ9.30b:step_alpha_isobutyl_loss',
)

# IMS9-EQ9.30c:step_alpha_ring_opening
IMS9_EQ9_30c_step_alpha_ring_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([C]4([H]1000002)([H]1000003)[C]5([C]6({-}1)([H]11)([H]1000005))([H]1000004)[C]10([H]1000012)([H]1000013)([H]1000014))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)){=}[O+.]7>>[C]1([C]6([H]11)([H]1000005)[C]5([C]4([H]1000002)([H]1000003)[C]3([C.]2([H]1000000)([H]1000001))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011))([H]1000004)[C]10([H]1000012)([H]1000013)([H]1000014)){#}[O+]7',
    name='IMS9-EQ9.30c:step_alpha_ring_opening',
)

# IMS9-EQ9.30c:step_rH_c6_to_c2
IMS9_EQ9_30c_step_rH_c6_to_c2 = mod.Rule.fromDFS(
    s='[C]1([C]6([H]11)([H]1000005)[C]5([C]4([H]1000002)([H]1000003)[C]3([C.]2([H]1000000)([H]1000001))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011))([H]1000004)[C]10([H]1000012)([H]1000013)([H]1000014)){#}[O+]7>>[C]1([C.]6([H]1000005)[C]5([C]4([H]1000002)([H]1000003)[C]3([C]2([H]11)([H]1000000)([H]1000001))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011))([H]1000004)[C]10([H]1000012)([H]1000013)([H]1000014)){#}[O+]7',
    name='IMS9-EQ9.30c:step_rH_c6_to_c2',
)

# IMS9-EQ9.30c:step_alpha_neopentyl_loss
IMS9_EQ9_30c_step_alpha_neopentyl_loss = mod.Rule.fromDFS(
    s='[C]1([C.]6([H]1000005)[C]5([C]4([H]1000002)([H]1000003)[C]3([C]2([H]11)([H]1000000)([H]1000001))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011))([H]1000004)[C]10([H]1000012)([H]1000013)([H]1000014)){#}[O+]7>>[C]1([C]6([H]1000005){=}[C]5([H]1000004)[C]10([H]1000012)([H]1000013)([H]1000014)){#}[O+]7.[C]2([H]11)([H]1000000)([H]1000001)[C]3([C.]4([H]1000002)([H]1000003))([C]8([H]1000006)([H]1000007)([H]1000008))[C]9([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.30c:step_alpha_neopentyl_loss',
)

# IMS9-EQ9.31a:step_alpha_methoxy_loss
IMS9_EQ9_31a_step_alpha_methoxy_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034))({=}[O+.]19)[O]20[C]21([H]1000035)([H]1000036)([H]1000037)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034)){#}[O+]19.[O.]20[C]21([H]1000035)([H]1000036)([H]1000037)',
    name='IMS9-EQ9.31a:step_alpha_methoxy_loss',
)

# IMS9-EQ9.31a:step_inductive_co_loss
IMS9_EQ9_31a_step_inductive_co_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034)){#}[O+]19.[O.]20[C]21([H]1000035)([H]1000036)([H]1000037)>>[C-]1{#}[O+]19.[C+]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034).[O.]20[C]21([H]1000035)([H]1000036)([H]1000037)',
    name='IMS9-EQ9.31a:step_inductive_co_loss',
)

# IMS9-EQ9.31b:step_inductive_charge_migration
IMS9_EQ9_31b_step_inductive_charge_migration = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034))({=}[O+.]19)[O]20[C]21([H]1000035)([H]1000036)([H]1000037)>>[C.]1({=}[O]19)[O]20[C]21([H]1000035)([H]1000036)([H]1000037).[C+]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034)',
    name='IMS9-EQ9.31b:step_inductive_charge_migration',
)

# IMS9-EQ9.31d:step_alpha_alkyl_loss
IMS9_EQ9_31d_step_alpha_alkyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034))({=}[O+.]19)[O]20[C]21([H]1000035)([H]1000036)([H]1000037)>>[C]1({#}[O+]19)[O]20[C]21([H]1000035)([H]1000036)([H]1000037).[C.]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]1000004)([H]1000005)[C]5([H]1000006)([H]1000007)[C]6([H]1000008)([H]1000009)[C]7([H]1000010)([H]1000011)[C]8([H]1000012)([H]1000013)[C]9([H]1000014)([H]1000015)[C]10([H]1000016)([H]1000017)[C]11([H]1000018)([H]1000019)[C]12([H]1000020)([H]1000021)[C]13([H]1000022)([H]1000023)[C]14([H]1000024)([H]1000025)[C]15([H]1000026)([H]1000027)[C]16([H]1000028)([H]1000029)[C]17([H]1000030)([H]1000031)[C]18([H]1000032)([H]1000033)([H]1000034)',
    name='IMS9-EQ9.31d:step_alpha_alkyl_loss',
)

# IMS9-EQ9.32a:step_rH_gamma
IMS9_EQ9_32a_step_rH_gamma = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]22)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033))({=}[O+.]19)[O]20[C]21([H]1000034)([H]1000035)([H]1000036)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033))({=}[O+]19[H]22)[O]20[C]21([H]1000034)([H]1000035)([H]1000036)',
    name='IMS9-EQ9.32a:step_rH_gamma',
)

# IMS9-EQ9.32a:step_alpha_alkene_loss
IMS9_EQ9_32a_step_alpha_alkene_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033))({=}[O+]19[H]22)[O]20[C]21([H]1000034)([H]1000035)([H]1000036)>>[C]1([C.]2([H]1000000)([H]1000001))({=}[O+]19[H]22)[O]20[C]21([H]1000034)([H]1000035)([H]1000036).[C]3([H]1000002)([H]1000003){=}[C]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033)',
    name='IMS9-EQ9.32a:step_alpha_alkene_loss',
)

# IMS9-EQ9.32b:step_rH_gamma
IMS9_EQ9_32b_step_rH_gamma = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C]4([H]22)([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033))({=}[O+.]19)[O]20[C]21([H]1000034)([H]1000035)([H]1000036)>>[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033))({=}[O+]19[H]22)[O]20[C]21([H]1000034)([H]1000035)([H]1000036)',
    name='IMS9-EQ9.32b:step_rH_gamma',
)

# IMS9-EQ9.32b:step_alpha_charge_migration_rejected
IMS9_EQ9_32b_step_alpha_charge_migration_rejected = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000000)([H]1000001)[C]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033))({=}[O+]19[H]22)[O]20[C]21([H]1000034)([H]1000035)([H]1000036)>>[C]1({=}[C]2([H]1000000)([H]1000001))([O]19[H]22)[O]20[C]21([H]1000034)([H]1000035)([H]1000036).[C+]3([H]1000002)([H]1000003)[C.]4([H]1000004)[C]5([H]1000005)([H]1000006)[C]6([H]1000007)([H]1000008)[C]7([H]1000009)([H]1000010)[C]8([H]1000011)([H]1000012)[C]9([H]1000013)([H]1000014)[C]10([H]1000015)([H]1000016)[C]11([H]1000017)([H]1000018)[C]12([H]1000019)([H]1000020)[C]13([H]1000021)([H]1000022)[C]14([H]1000023)([H]1000024)[C]15([H]1000025)([H]1000026)[C]16([H]1000027)([H]1000028)[C]17([H]1000029)([H]1000030)[C]18([H]1000031)([H]1000032)([H]1000033)',
    name='IMS9-EQ9.32b:step_alpha_charge_migration_rejected',
)

# IMS9-EQ9.33:step_beta_cleavage
IMS9_EQ9_33_step_beta_cleavage = mod.Rule.fromDFS(
    s='[C]1([C.]2([C]3([H]1000000)([H]1000001)[C]4([H]1000002)([H]1000003)([H]1000004))[C]5([H]1000005)([H]1000006)([H]1000007))([O]6[H]1000008){=}[O+]7[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([C]2({=}[C]3([H]1000000)([H]1000001))[C]5([H]1000005)([H]1000006)([H]1000007))([O]6[H]1000008){=}[O+]7[C]8([H]1000009)([H]1000010)([H]1000011).[C.]4([H]1000002)([H]1000003)([H]1000004)',
    name='IMS9-EQ9.33:step_beta_cleavage',
)

# IMS9-EQ9.34a:step_rH_alkoxy_side
IMS9_EQ9_34a_step_rH_alkoxy_side = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]9)([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+]3[H]9)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34a:step_rH_alkoxy_side',
)

# IMS9-EQ9.34a:step_alpha_alkene_loss
IMS9_EQ9_34a_step_alpha_alkene_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+]3[H]9)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+]3[H]9)[O.]4.[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003){=}[C]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34a:step_alpha_alkene_loss',
)

# IMS9-EQ9.34b:step_rH_alkoxy_side
IMS9_EQ9_34b_step_rH_alkoxy_side = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]9)([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+]3[H]9)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34b:step_rH_alkoxy_side',
)

# IMS9-EQ9.34b:step_charge_localization
IMS9_EQ9_34b_step_charge_localization = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+]3[H]9)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([O]3[H]9){=}[O+]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34b:step_charge_localization',
)

# IMS9-EQ9.34b:step_inductive_acid_loss
IMS9_EQ9_34b_step_inductive_acid_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([O]3[H]9){=}[O+]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([O]3[H]9){=}[O]4.[C+]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34b:step_inductive_acid_loss',
)

# IMS9-EQ9.34c:step_rH_alkoxy_side
IMS9_EQ9_34c_step_rH_alkoxy_side = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]9)([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+]3[H]9)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34c:step_rH_alkoxy_side',
)

# IMS9-EQ9.34c:step_charge_localization
IMS9_EQ9_34c_step_charge_localization = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+]3[H]9)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([O]3[H]9){=}[O+]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34c:step_charge_localization',
)

# IMS9-EQ9.34c:step_second_rH_double_hydrogen
IMS9_EQ9_34c_step_second_rH_double_hydrogen = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([O]3[H]9){=}[O+]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C.]7([H]1000007)[C]8([H]10)([H]1000008)([H]1000009)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2([O]3[H]9){=}[O+]4[H]10.[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003){=}[C]7([H]1000007)[C.]8([H]1000008)([H]1000009)',
    name='IMS9-EQ9.34c:step_second_rH_double_hydrogen',
)

# IMS9-EQ9.35a:step_alpha_carbonyl_initiated
IMS9_EQ9_35a_step_alpha_carbonyl_initiated = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2{#}[O+]3.[O.]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.35a:step_alpha_carbonyl_initiated',
)

# IMS9-EQ9.35b:step_alpha_methyl_loss
IMS9_EQ9_35b_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O+.]3)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)>>[C.]1([H]1000000)([H]1000001)([H]1000002).[C]2({#}[O+]3)[O]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.35b:step_alpha_methyl_loss',
)

# IMS9-EQ9.35c:step_alpha_ester_o_initiated
IMS9_EQ9_35c_step_alpha_ester_o_initiated = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O]3)[O+.]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O]3)[O+]4{=}[C]5([H]1000003)[C]6([H]1000004)([H]1000005)([H]1000006).[C.]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.35c:step_alpha_ester_o_initiated',
)

# IMS9-EQ9.35d:step_alpha_ester_o_initiated_methyl_loss
IMS9_EQ9_35d_step_alpha_ester_o_initiated_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O]3)[O+.]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O]3)[O+]4{=}[C]5([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011).[C.]6([H]1000004)([H]1000005)([H]1000006)',
    name='IMS9-EQ9.35d:step_alpha_ester_o_initiated_methyl_loss',
)

# IMS9-EQ9.35e:step_inductive_charge_site
IMS9_EQ9_35e_step_inductive_charge_site = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O]3)[O+.]4[C]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)>>[C]1([H]1000000)([H]1000001)([H]1000002)[C]2({=}[O]3)[O.]4.[C+]5([C]6([H]1000004)([H]1000005)([H]1000006))([H]1000003)[C]7([H]1000007)([H]1000008)[C]8([H]1000009)([H]1000010)([H]1000011)',
    name='IMS9-EQ9.35e:step_inductive_charge_site',
)

# IMS9-EQ9.36a:step_r2H_alkyl_radical_loss
IMS9_EQ9_36a_step_r2H_alkyl_radical_loss = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O]20[C]21([H]1000019)([H]1000020)[C]22([C]23([H]1000021)([H]1000022)[C]24([H]1000023)([H]1000024)([H]1000025))([H]31)[C]25([H]1000026)([H]1000027)[C]26([H]1000028)([H]1000029)[C]27([H]1000030)([H]1000031)[C]28([H]1000032)([H]1000033)([H]1000034))[C]7({=}[O+.]8)[O]9[C]10([H]30)([H]1000004)[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))([H]29)[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018)>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O+]20([H]30)[C]21([H]1000019)([H]1000020)[C]22([C]23([H]1000021)([H]1000022)[C]24([H]1000023)([H]1000024)([H]1000025))([H]31)[C]25([H]1000026)([H]1000027)[C]26([H]1000028)([H]1000029)[C]27([H]1000030)([H]1000031)[C]28([H]1000032)([H]1000033)([H]1000034))[C]7([O]8[H]29){=}[O]9.[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018)',
    name='IMS9-EQ9.36a:step_r2H_alkyl_radical_loss',
)

# IMS9-EQ9.36a:step_rH_alkene_loss
IMS9_EQ9_36a_step_rH_alkene_loss = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O+]20([H]30)[C]21([H]1000019)([H]1000020)[C]22([C]23([H]1000021)([H]1000022)[C]24([H]1000023)([H]1000024)([H]1000025))([H]31)[C]25([H]1000026)([H]1000027)[C]26([H]1000028)([H]1000029)[C]27([H]1000030)([H]1000031)[C]28([H]1000032)([H]1000033)([H]1000034))[C]7([O]8[H]29){=}[O]9.[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018)>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O+]20([H]30)([H]31))[C]7([O]8[H]29){=}[O]9.[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018).[C]21([H]1000019)([H]1000020){=}[C]22([C]23([H]1000021)([H]1000022)[C]24([H]1000023)([H]1000024)([H]1000025))[C]25([H]1000026)([H]1000027)[C]26([H]1000028)([H]1000029)[C]27([H]1000030)([H]1000031)[C]28([H]1000032)([H]1000033)([H]1000034)',
    name='IMS9-EQ9.36a:step_rH_alkene_loss',
)

# IMS9-EQ9.36a:step_water_loss_ring_closure
IMS9_EQ9_36a_step_water_loss_ring_closure = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O+]20([H]30)([H]31))[C]7([O]8[H]29){=}[O]9.[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018).[C]21([H]1000019)([H]1000020){=}[C]22([C]23([H]1000021)([H]1000022)[C]24([H]1000023)([H]1000024)([H]1000025))[C]25([H]1000026)([H]1000027)[C]26([H]1000028)([H]1000029)[C]27([H]1000030)([H]1000031)[C]28([H]1000032)([H]1000033)([H]1000034)>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18([O+]8([H]29)[C]7({-}1){=}[O]9){=}[O]19).[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018).[O]20([H]30)([H]31).[C]21([H]1000019)([H]1000020){=}[C]22([C]23([H]1000021)([H]1000022)[C]24([H]1000023)([H]1000024)([H]1000025))[C]25([H]1000026)([H]1000027)[C]26([H]1000028)([H]1000029)[C]27([H]1000030)([H]1000031)[C]28([H]1000032)([H]1000033)([H]1000034)',
    name='IMS9-EQ9.36a:step_water_loss_ring_closure',
)

# IMS9-EQ9.36b:step_r2H_alkyl_radical_loss
IMS9_EQ9_36b_step_r2H_alkyl_radical_loss = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O]20[C]21([H]1000019)([H]1000020)[C]22([C]23([H]1000022)([H]1000023)[C]24([H]1000024)([H]1000025)([H]1000026))([H]1000021)[C]25([H]1000027)([H]1000028)[C]26([H]1000029)([H]1000030)[C]27([H]1000031)([H]1000032)[C]28([H]1000033)([H]1000034)([H]1000035))[C]7({=}[O+.]8)[O]9[C]10([H]30)([H]1000004)[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))([H]29)[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018)>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O+]20([H]30)[C]21([H]1000019)([H]1000020)[C]22([C]23([H]1000022)([H]1000023)[C]24([H]1000024)([H]1000025)([H]1000026))([H]1000021)[C]25([H]1000027)([H]1000028)[C]26([H]1000029)([H]1000030)[C]27([H]1000031)([H]1000032)[C]28([H]1000033)([H]1000034)([H]1000035))[C]7([O]8[H]29){=}[O]9.[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018)',
    name='IMS9-EQ9.36b:step_r2H_alkyl_radical_loss',
)

# IMS9-EQ9.36b:step_id_alcohol_loss
IMS9_EQ9_36b_step_id_alcohol_loss = mod.Rule.fromDFS(
    s='[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18({=}[O]19)[O+]20([H]30)[C]21([H]1000019)([H]1000020)[C]22([C]23([H]1000022)([H]1000023)[C]24([H]1000024)([H]1000025)([H]1000026))([H]1000021)[C]25([H]1000027)([H]1000028)[C]26([H]1000029)([H]1000030)[C]27([H]1000031)([H]1000032)[C]28([H]1000033)([H]1000034)([H]1000035))[C]7([O]8[H]29){=}[O]9.[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018)>>[C]1(:[C]2(:[C]3([H]1000000):[C]4([H]1000001):[C]5([H]1000002):[C]6(:1)([H]1000003))[C]18([O+]8([H]29)[C]7({-}1){=}[O]9){=}[O]19).[C.]10([H]1000004){=}[C]11([C]12([H]1000005)([H]1000006)[C]13([H]1000007)([H]1000008)([H]1000009))[C]14([H]1000010)([H]1000011)[C]15([H]1000012)([H]1000013)[C]16([H]1000014)([H]1000015)[C]17([H]1000016)([H]1000017)([H]1000018).[O]20([H]30)[C]21([H]1000019)([H]1000020)[C]22([C]23([H]1000022)([H]1000023)[C]24([H]1000024)([H]1000025)([H]1000026))([H]1000021)[C]25([H]1000027)([H]1000028)[C]26([H]1000029)([H]1000030)[C]27([H]1000031)([H]1000032)[C]28([H]1000033)([H]1000034)([H]1000035)',
    name='IMS9-EQ9.36b:step_id_alcohol_loss',
)

# IMS9-EQ9.37a:step_alpha_methyl_loss
IMS9_EQ9_37a_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009))([H]1000000)([H]1000001)[O+.]6[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[C]9([H]1000014)([H]1000015)([H]1000016)>>[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009))([H]1000000)([H]1000001)[O+]6{=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013).[C.]9([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.37a:step_alpha_methyl_loss',
)

# IMS9-EQ9.37a:step_rH_pentene_loss
IMS9_EQ9_37a_step_rH_pentene_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009))([H]1000000)([H]1000001)[O+]6{=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013).[C.]9([H]1000014)([H]1000015)([H]1000016)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009).[O+]6([H]10){=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013).[C.]9([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.37a:step_rH_pentene_loss',
)

# IMS9-EQ9.37b:step_alpha_methyl_loss
IMS9_EQ9_37b_step_alpha_methyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009))([H]1000000)([H]1000001)[O+.]6[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[C]9([H]1000014)([H]1000015)([H]1000016)>>[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009))([H]1000000)([H]1000001)[O+]6{=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013).[C.]9([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.37b:step_alpha_methyl_loss',
)

# IMS9-EQ9.37b:step_inductive_aldehyde_loss
IMS9_EQ9_37b_step_inductive_aldehyde_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009))([H]1000000)([H]1000001)[O+]6{=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013).[C.]9([H]1000014)([H]1000015)([H]1000016)>>[C+]1([H]1000000)([H]1000001)[C]2([H]10)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009).[O]6{=}[C]7([H]1000010)[C]8([H]1000011)([H]1000012)([H]1000013).[C.]9([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.37b:step_inductive_aldehyde_loss',
)

# IMS9-EQ9.37c:step_alpha_butyl_loss
IMS9_EQ9_37c_step_alpha_butyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010))([H]1000000)([H]1000001)[O+.]6[C]7([C]8([H]11)([H]1000012)([H]1000013))([H]1000011)[C]9([H]1000014)([H]1000015)([H]1000016)>>[C]1([H]1000000)([H]1000001){=}[O+]6[C]7([C]8([H]11)([H]1000012)([H]1000013))([H]1000011)[C]9([H]1000014)([H]1000015)([H]1000016).[C.]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010)',
    name='IMS9-EQ9.37c:step_alpha_butyl_loss',
)

# IMS9-EQ9.37c:step_rH_propene_loss
IMS9_EQ9_37c_step_rH_propene_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[O+]6[C]7([C]8([H]11)([H]1000012)([H]1000013))([H]1000011)[C]9([H]1000014)([H]1000015)([H]1000016).[C.]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001){=}[O+]6[H]11.[C.]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010).[C]7({=}[C]8([H]1000012)([H]1000013))([H]1000011)[C]9([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.37c:step_rH_propene_loss',
)

# IMS9-EQ9.37d:step_alpha_butyl_loss
IMS9_EQ9_37d_step_alpha_butyl_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010))([H]1000000)([H]1000001)[O+.]6[C]7([C]8([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]9([H]1000015)([H]1000016)([H]1000017)>>[C]1([H]1000000)([H]1000001){=}[O+]6[C]7([C]8([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]9([H]1000015)([H]1000016)([H]1000017).[C.]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010)',
    name='IMS9-EQ9.37d:step_alpha_butyl_loss',
)

# IMS9-EQ9.37d:step_inductive_formaldehyde_loss
IMS9_EQ9_37d_step_inductive_formaldehyde_loss = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[O+]6[C]7([C]8([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]9([H]1000015)([H]1000016)([H]1000017).[C.]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010)>>[C]1([H]1000000)([H]1000001){=}[O]6.[C.]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010).[C+]7([C]8([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]9([H]1000015)([H]1000016)([H]1000017)',
    name='IMS9-EQ9.37d:step_inductive_formaldehyde_loss',
)

# IMS9-EQ9.37e:step_inductive_charge_site
IMS9_EQ9_37e_step_inductive_charge_site = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010))([H]1000000)([H]1000001)[O+.]6[C]7([C]8([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]9([H]1000015)([H]1000016)([H]1000017)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([H]1000008)([H]1000009)([H]1000010))([H]1000000)([H]1000001)[O.]6.[C+]7([C]8([H]1000012)([H]1000013)([H]1000014))([H]1000011)[C]9([H]1000015)([H]1000016)([H]1000017)',
    name='IMS9-EQ9.37e:step_inductive_charge_site',
)

# IMS9-EQ9.37f:step_inductive_charge_site
IMS9_EQ9_37f_step_inductive_charge_site = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]12)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009))([H]1000000)([H]1000001)[O+.]6[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[C]9([H]1000014)([H]1000015)([H]1000016)>>[C+]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]12)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009).[O.]6[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[C]9([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.37f:step_inductive_charge_site',
)

# IMS9-EQ9.37f:step_inductive_ethylene_loss
IMS9_EQ9_37f_step_inductive_ethylene_loss = mod.Rule.fromDFS(
    s='[C+]1([H]1000000)([H]1000001)[C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]12)([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009).[O.]6[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[C]9([H]1000014)([H]1000015)([H]1000016)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)([H]1000003).[C]3([H]12)([H]1000004)([H]1000005)[C+]4([H]1000006)[C]5([H]1000007)([H]1000008)([H]1000009).[O.]6[C]7([C]8([H]1000011)([H]1000012)([H]1000013))([H]1000010)[C]9([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.37f:step_inductive_ethylene_loss',
)

# IMS9-EQ9.4a:step_allylic_alpha_cleavage_retarded
IMS9_EQ9_4a_step_allylic_alpha_cleavage_retarded = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3({=}[C]4([H]1000003)[C]5([H]1000004)([H]1000005)[C.]6([H]1000006)[C+]7([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012))[C]10([H]1000013)([H]1000014)([H]1000015)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3({=}[C.]4[H]1000003)[C]10([H]1000013)([H]1000014)([H]1000015).[C]5([H]1000004)([H]1000005){=}[C]6([H]1000006)[C+]7([C]8([H]1000007)([H]1000008)([H]1000009))[C]9([H]1000010)([H]1000011)([H]1000012)',
    name='IMS9-EQ9.4a:step_allylic_alpha_cleavage_retarded',
)

# IMS9-EQ9.4b:step_doubly_allylic_alpha_cleavage
IMS9_EQ9_4b_step_doubly_allylic_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([C]4([H]1000003)([H]1000004)[C]5([H]1000005)([H]1000006)[C.]6([H]1000007)[C+]7([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013)){=}[C]10([H]1000014)([H]1000015)>>[C]1([H]1000000)([H]1000001){=}[C]2([H]1000002)[C]3([C.]4([H]1000003)([H]1000004)){=}[C]10([H]1000014)([H]1000015).[C]5([H]1000005)([H]1000006){=}[C]6([H]1000007)[C+]7([C]8([H]1000008)([H]1000009)([H]1000010))[C]9([H]1000011)([H]1000012)([H]1000013)',
    name='IMS9-EQ9.4b:step_doubly_allylic_alpha_cleavage',
)

# IMS9-EQ9.6a:step_gamma_h_rearrangement
IMS9_EQ9_6a_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C+]2([C]3([H]1000002)([H]1000003)([H]1000004))[C]4([H]1000005)([H]1000006)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007)[C]7([H]8)([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)>>[C]1([H]8)([H]1000000)([H]1000001)[C+]2([C]3([H]1000002)([H]1000003)([H]1000004))[C]4([H]1000005)([H]1000006)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007)[C.]7([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.6a:step_gamma_h_rearrangement',
)

# IMS9-EQ9.6a:step_alpha_cleavage
IMS9_EQ9_6a_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]8)([H]1000000)([H]1000001)[C+]2([C]3([H]1000002)([H]1000003)([H]1000004))[C]4([H]1000005)([H]1000006)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007)[C.]7([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)>>[C]1([H]8)([H]1000000)([H]1000001)[C+]2([C]3([H]1000002)([H]1000003)([H]1000004))[C.]4([H]1000005)([H]1000006).[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007){=}[C]7([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.6a:step_alpha_cleavage',
)

# IMS9-EQ9.6b:step_gamma_h_rearrangement
IMS9_EQ9_6b_step_gamma_h_rearrangement = mod.Rule.fromDFS(
    s='[C.]1([H]1000000)([H]1000001)[C+]2([C]3([H]1000002)([H]1000003)([H]1000004))[C]4([H]1000005)([H]1000006)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007)[C]7([H]8)([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)>>[C]1([H]8)([H]1000000)([H]1000001)[C+]2([C]3([H]1000002)([H]1000003)([H]1000004))[C]4([H]1000005)([H]1000006)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007)[C.]7([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.6b:step_gamma_h_rearrangement',
)

# IMS9-EQ9.6b:step_i_cleavage
IMS9_EQ9_6b_step_i_cleavage = mod.Rule.fromDFS(
    s='[C]1([H]8)([H]1000000)([H]1000001)[C+]2([C]3([H]1000002)([H]1000003)([H]1000004))[C]4([H]1000005)([H]1000006)[C]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007)[C.]7([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)>>[C]1([H]8)([H]1000000)([H]1000001)[C]2([C]3([H]1000002)([H]1000003)([H]1000004)){=}[C]4([H]1000005)([H]1000006).[C+]5([C]6([H]1000008)([H]1000009)([H]1000010))([H]1000007)[C.]7([H]1000011)[C]9([H]1000012)([H]1000013)[C]10([H]1000014)([H]1000015)([H]1000016)',
    name='IMS9-EQ9.6b:step_i_cleavage',
)

# IMS9-EQ9.7:step_sigma_ionization  [auto-localized precursor]
IMS9_EQ9_7_step_sigma_ionization = mod.Rule.fromDFS(
    s='[C+]1([C.]2([H]1000001)([H]1000002)[C]3([H]1000003)([H]1000004)[C]4([H]1000005)([H]1000006)[C]5([H]1000007)([H]1000008)[C]6({-}1)([H]1000009)([H]1000010))([H]1000000)[C]7([H]1000011)([H]1000012)([H]1000013)>>[C+]1([C]6([H]1000009)([H]1000010)[C]5([H]1000007)([H]1000008)[C]4([H]1000005)([H]1000006)[C]3([H]1000003)([H]1000004)[C.]2([H]1000001)([H]1000002))([H]1000000)[C]7([H]1000011)([H]1000012)([H]1000013)',
    name='IMS9-EQ9.7:step_sigma_ionization',
)

# IMS9-EQ9.7:step_alpha_cleavage
IMS9_EQ9_7_step_alpha_cleavage = mod.Rule.fromDFS(
    s='[C+]1([C]6([H]1000009)([H]1000010)[C]5([H]1000007)([H]1000008)[C]4([H]1000005)([H]1000006)[C]3([H]1000003)([H]1000004)[C.]2([H]1000001)([H]1000002))([H]1000000)[C]7([H]1000011)([H]1000012)([H]1000013)>>[C+]1([C]6([H]1000009)([H]1000010)[C]5([H]1000007)([H]1000008)[C.]4([H]1000005)([H]1000006))([H]1000000)[C]7([H]1000011)([H]1000012)([H]1000013).[C]2([H]1000001)([H]1000002){=}[C]3([H]1000003)([H]1000004)',
    name='IMS9-EQ9.7:step_alpha_cleavage',
)

# IMS9-EQ9.8:step_alpha_ring_d_opening  [auto-localized precursor]
IMS9_EQ9_8_step_alpha_ring_d_opening = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000028)([H]1000029)([H]1000030))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C]16([H]1000022)([H]1000023)[C.]17({-}13)([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000013))([H]1000008))([H]1000000)([H]1000001)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000028)([H]1000029)([H]1000030))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C]16([H]1000022)([H]1000023)[C.]17([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000013))([H]1000008))([H]1000000)([H]1000001)',
    name='IMS9-EQ9.8:step_alpha_ring_d_opening',
)

# IMS9-EQ9.8:step_rH_c18_to_c17  [1 hydrogen migration(s) inferred]
IMS9_EQ9_8_step_rH_c18_to_c17 = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000027)([H]1000028)([H]1000029))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C]16([H]1000022)([H]1000023)[C.]17([H]1000024)[C]20([H]1000030)([H]1000031)[C]21([H]1000032)([H]1000033)([H]1000034))[C]18([H]1000025)([H]1000026)([H]1000035))([H]1000013))([H]1000008))([H]1000000)([H]1000001)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000027)([H]1000028)([H]1000029))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C]16([H]1000022)([H]1000023)[C]17([H]1000024)([H]1000035)[C]20([H]1000030)([H]1000031)[C]21([H]1000032)([H]1000033)([H]1000034))[C.]18([H]1000025)([H]1000026))([H]1000013))([H]1000008))([H]1000000)([H]1000001)',
    name='IMS9-EQ9.8:step_rH_c18_to_c17',
)

# IMS9-EQ9.8:step_rH_c16_to_c18  [1 hydrogen migration(s) inferred]
IMS9_EQ9_8_step_rH_c16_to_c18 = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000027)([H]1000028)([H]1000029))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C]16([H]1000022)([H]1000035)[C]17([H]1000023)([H]1000024)[C]20([H]1000030)([H]1000031)[C]21([H]1000032)([H]1000033)([H]1000034))[C.]18([H]1000025)([H]1000026))([H]1000013))([H]1000008))([H]1000000)([H]1000001)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000027)([H]1000028)([H]1000029))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C.]16([H]1000022)[C]17([H]1000023)([H]1000024)[C]20([H]1000030)([H]1000031)[C]21([H]1000032)([H]1000033)([H]1000034))[C]18([H]1000025)([H]1000026)([H]1000035))([H]1000013))([H]1000008))([H]1000000)([H]1000001)',
    name='IMS9-EQ9.8:step_rH_c16_to_c18',
)

# IMS9-EQ9.8:step_alpha_c14_c15_cleavage
IMS9_EQ9_8_step_alpha_c14_c15_cleavage = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000028)([H]1000029)([H]1000030))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C.]16([H]1000022)[C]17([H]1000023)([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000013))([H]1000008))([H]1000000)([H]1000001)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000028)([H]1000029)([H]1000030))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C.]14({-}8)([H]1000019))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000013))([H]1000008))([H]1000000)([H]1000001).[C]15([H]1000020)([H]1000021){=}[C]16([H]1000022)[C]17([H]1000023)([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035)',
    name='IMS9-EQ9.8:step_alpha_c14_c15_cleavage',
)

# IMS9-EQ9.9:step_alpha_c4h8_loss
IMS9_EQ9_9_step_alpha_c4h8_loss = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000028)([H]1000029)([H]1000030))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C]15([H]1000020)([H]1000021)[C]16([H]1000022)([H]1000023)[C.]17([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000013))([H]1000008))([H]1000000)([H]1000001)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000028)([H]1000029)([H]1000030))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C.]15([H]1000020)([H]1000021))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000013))([H]1000008))([H]1000000)([H]1000001).[C]16([H]1000022)([H]1000023){=}[C]17([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035)',
    name='IMS9-EQ9.9:step_alpha_c4h8_loss',
)

# IMS9-EQ9.9:step_c19_methyl_loss_rearrangement_alpha
IMS9_EQ9_9_step_c19_methyl_loss_rearrangement_alpha = mod.Rule.fromDFS(
    s='[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([C]9([C]10({-}1)({-}5)[C]19([H]1000028)([H]1000029)([H]1000030))([H]1000014)[C]11([H]1000015)([H]1000016)[C]12([H]1000017)([H]1000018)[C+]13([C]14({-}8)([H]1000019)[C.]15([H]1000020)([H]1000021))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000013))([H]1000008))([H]1000000)([H]1000001).[C]16([H]1000022)([H]1000023){=}[C]17([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035)>>[C]1([C]2([H]1000002)([H]1000003)[C]3([H]1000004)([H]1000005)[C]4([H]1000006)([H]1000007)[C]5([C]6([H]1000009)([H]1000010)[C]7([H]1000011)([H]1000012)[C]8([H]1000013){=}[C]14([H]1000019)[C]15([H]1000020)([H]1000021)[C+]13([C]12([H]1000017)([H]1000018)[C]11([H]1000015)([H]1000016)[C]9([H]1000014){=}[C]10({-}1)({-}5))[C]18([H]1000025)([H]1000026)([H]1000027))([H]1000008))([H]1000000)([H]1000001).[C]16([H]1000022)([H]1000023){=}[C]17([H]1000024)[C]20([H]1000031)([H]1000032)[C]21([H]1000033)([H]1000034)([H]1000035).[C.]19([H]1000028)([H]1000029)([H]1000030)',
    name='IMS9-EQ9.9:step_c19_methyl_loss_rearrangement_alpha',
)

fragmentation = [
    IMS4_EQ4_10_step_alpha_cleavage,
    IMS4_EQ4_11_step_alpha_cleavage,
    IMS4_EQ4_12_step_alpha_cleavage,
    IMS4_EQ4_13_step_alpha_cleavage,
    IMS4_EQ4_14_step_alpha_cleavage,
    IMS4_EQ4_15a_step_allylic_alpha_cleavage,
    IMS4_EQ4_15b_step_benzylic_alpha_cleavage,
    IMS4_EQ4_17a_step_alpha_cleavage_loss_propyl,
    IMS4_EQ4_17b_step_alpha_cleavage_loss_ethyl,
    IMS4_EQ4_17c_step_alpha_cleavage_loss_methyl,
    IMS4_EQ4_18_step_inductive_cleavage,
    IMS4_EQ4_19_step_inductive_cleavage,
    IMS4_EQ4_20_step_inductive_cleavage,
    IMS4_EQ4_21_step_inductive_cleavage,
    IMS4_EQ4_22_step_inductive_cleavage,
    IMS4_EQ4_23_step_inductive_cleavage,
    IMS4_EQ4_24_step_inductive_cleavage,
    IMS4_EQ4_25_step_inductive_cleavage,
    IMS4_EQ4_26_step_alpha_cleavage,
    IMS4_EQ4_26_step_inductive_cleavage,
    IMS4_EQ4_27_step_alpha_cleavage,
    IMS4_EQ4_27_step_inductive_cleavage,
    IMS4_EQ4_28_step_inductive_cleavage,
    IMS4_EQ4_29_step_inductive_cleavage,
    IMS4_EQ4_30_step_alpha_cleavage,
    IMS4_EQ4_31_step_alpha1_ring_opening,
    IMS4_EQ4_31_step_alpha2_charge_retention,
    IMS4_EQ4_32_step_alpha1_ring_opening,
    IMS4_EQ4_32_step_inductive_charge_migration,
    IMS4_EQ4_33_step_gamma_h_rearrangement,
    IMS4_EQ4_33_step_beta_cleavage_alpha,
    IMS4_EQ4_34_step_inductive_cleavage,
    IMS4_EQ4_35_step_gamma_h_rearrangement,
    IMS4_EQ4_35_step_beta_cleavage_alpha,
    IMS4_EQ4_36_step_gamma_h_rearrangement,
    IMS4_EQ4_36_step_beta_cleavage_alpha,
    IMS4_EQ4_37_step_rH_hydrogen_rearrangement,
    IMS4_EQ4_37_step_rd_displacement_charge_retention,
    IMS4_EQ4_38a_step_rH_hydrogen_rearrangement,
    IMS4_EQ4_38a_step_i_inductive_water_loss_charge_migration,
    IMS4_EQ4_38b_step_i_inductive_ethylene_loss,
    IMS4_EQ4_39_step_rH,
    IMS4_EQ4_39_step_alpha,
    IMS4_EQ4_3a_step_sigma_cleavage,
    IMS4_EQ4_3b_step_sigma_cleavage,
    IMS4_EQ4_40_step_rH,
    IMS4_EQ4_40_step_ind,
    IMS4_EQ4_41_step_rH,
    IMS4_EQ4_41_step_elimination,
    IMS4_EQ4_42_step_displacement,
    IMS4_EQ4_43_step_alpha_cleavage,
    IMS4_EQ4_43_step_h_rearrangement,
    IMS4_EQ4_44_step_inductive_cleavage,
    IMS4_EQ4_44_step_h_rearrangement,
    IMS4_EQ4_45_step_rH,
    IMS4_EQ4_45_step_alpha_cleavage,
    IMS4_EQ4_46_step_rH_first,
    IMS4_EQ4_46_step_rH_second,
    IMS4_EQ4_4a_step_retro_2plus2,
    IMS4_EQ4_4c_step_water_elimination,
    IMS4_EQ4_5_step_three_bond_cleavage,
    IMS4_EQ4_6a_step_inductive_cleavage,
    IMS4_EQ4_6b_step_hydrogen_rearrangement,
    IMS4_EQ4_6d_step_retro_2plus2,
    IMS4_EQ4_7_step_sigma_dissociation,
    IMS4_EQ4_8_step_sigma_dissociation,
    IMS4_EQ4_9_step_alpha_cleavage,
    IMS4_FIG4_4a_step_alpha_cleavage_ch3,
    IMS4_FIG4_4b_step_alpha_cleavage_h,
    IMS8_EQ8_10_step_inductive_cleavage,
    IMS8_EQ8_100_step_alpha_cleavage,
    IMS8_EQ8_100_step_rH_methane_loss,
    IMS8_EQ8_101a_step_gamma_H_transfer,
    IMS8_EQ8_101a_step_mclafferty_cleavage,
    IMS8_EQ8_101b_step_beta_H_transfer,
    IMS8_EQ8_101b_step_rH_1_2_to_enediol,
    IMS8_EQ8_101b_step_alpha_methyl_loss,
    IMS8_EQ8_101c_step_rC_1_2_carboxyl_migration,
    IMS8_EQ8_101c_step_rH_1_2_to_isobutyric_enediol,
    IMS8_EQ8_101c_step_rH_1_4_to_isobutyric_acid_ion,
    IMS8_EQ8_101d_step_rH_1_4_from_C4,
    IMS8_EQ8_101d_step_rC_1_2_reverse_migration,
    IMS8_EQ8_101d_step_rH_1_2_to_alpha_radical,
    IMS8_EQ8_101d_step_alpha_methyl_loss,
    IMS8_EQ8_102_step_gamma_h_rearrangement,
    IMS8_EQ8_102_step_ring_closure_carboxyl_detachment,
    IMS8_EQ8_102_step_carboxyl_reattachment,
    IMS8_EQ8_102_step_alpha_cleavage_ethylene_loss,
    IMS8_EQ8_103_step_rd_displacement,
    IMS8_EQ8_104_step_rd_displacement_distonic,
    IMS8_EQ8_105_step_charge_site_displacement,
    IMS8_EQ8_106a_step_re_elimination_charge_on_AD,
    IMS8_EQ8_106b_step_re_elimination_charge_on_ring,
    IMS8_EQ8_107_step_rd_phenonium,
    IMS8_EQ8_108_step_rd_cyclization_to_nitrogen,
    IMS8_EQ8_109_step_rd_ring_closure_loss_of_X,
    IMS8_EQ8_11_step_hydrogen_rearrangement,
    IMS8_EQ8_110_step_rH_beta_hydrogen,
    IMS8_EQ8_110_step_rd_ethyl_radical_loss,
    IMS8_EQ8_110_step_retro_2plus2_ketene_loss,
    IMS8_EQ8_111_step_rH_six_membered,
    IMS8_EQ8_111_step_rd_lactone_closure,
    IMS8_EQ8_112_step_alpha_cleavage,
    IMS8_EQ8_112_step_rd_amide_oxygen_displacement,
    IMS8_EQ8_113_step_rd_phenyl_migration,
    IMS8_EQ8_114_step_alpha_cleavage,
    IMS8_EQ8_114_step_re_methoxyl_migration,
    IMS8_EQ8_115a_step_ring_b_cleavage_double_h_transfer,
    IMS8_EQ8_115b_step_remote_tms_migration_and_ring_b_cleavage,
    IMS8_EQ8_116_step_ring_closure,
    IMS8_EQ8_116_step_ring_opening,
    IMS8_EQ8_117_step_re_silyl_migration_with_elimination,
    IMS8_EQ8_118_step_re_double_silyl_migration,
    IMS8_EQ8_119_step_re_methoxyl_migration_with_elimination,
    IMS8_EQ8_12_step_inductive_cleavage,
    IMS8_EQ8_120_step_re_double_acetyl_migration,
    IMS8_EQ8_121_step_co_loss_1,
    IMS8_EQ8_121_step_co_loss_2,
    IMS8_EQ8_122_step_ortho_cyclization,
    IMS8_EQ8_122_step_co_elimination,
    IMS8_EQ8_122_step_hydrogen_atom_loss,
    IMS8_EQ8_123_step_h3po4_elimination,
    IMS8_EQ8_124_step_phenyl_migration,
    IMS8_EQ8_13_step_hydrogen_rearrangement,
    IMS8_EQ8_14a_step_hydrogen_rearrangement,
    IMS8_EQ8_14b_step_inductive_cleavage,
    IMS8_EQ8_15a_step_hydrogen_rearrangement,
    IMS8_EQ8_15b_step_hydrogen_rearrangement,
    IMS8_EQ8_16a_step_rH_hydroxyl_H_rearrangement,
    IMS8_EQ8_16b_step_rH_gamma_CH_rearrangement,
    IMS8_EQ8_17_step_rH_hydroxyl_H_to_ester_carbonyl,
    IMS8_EQ8_17_step_alpha_cleavage_to_aldehyde,
    IMS8_EQ8_18a_step_heterolytic_cleavage,
    IMS8_EQ8_19_step_gamma_H_transfer,
    IMS8_EQ8_1a_step_h_shift_1_3,
    IMS8_EQ8_1b_step_alpha_cleavage,
    IMS8_EQ8_1c_step_methane_loss,
    IMS8_EQ8_1d_step_alpha_cleavage,
    IMS8_EQ8_1f_step_h_shift_1_5,
    IMS8_EQ8_1g_step_alpha_cleavage,
    IMS8_EQ8_20a_step_rH_six_membered_formaldehyde_loss,
    IMS8_EQ8_20b_step_rH_four_membered_formaldehyde_loss,
    IMS8_EQ8_21a_step_gamma_H_beta_cleavage,
    IMS8_EQ8_21b_step_alpha_cleavage,
    IMS8_EQ8_22_step_rH,
    IMS8_EQ8_22_step_ring_walk,
    IMS8_EQ8_22_step_i,
    IMS8_EQ8_24a_step_cl_loss,
    IMS8_EQ8_24b_step_cl_loss,
    IMS8_EQ8_24c_step_cl_loss,
    IMS8_EQ8_24d_step_cl_loss,
    IMS8_EQ8_25a_step_retro_da,
    IMS8_EQ8_25b_step_retro_da,
    IMS8_EQ8_26a_step_hydrogen_rearrangement,
    IMS8_EQ8_26a_step_inductive_cleavage,
    IMS8_EQ8_26b_step_hydrogen_rearrangement,
    IMS8_EQ8_26b_step_inductive_cleavage,
    IMS8_EQ8_29a_step_anchimeric_displacement,
    IMS8_EQ8_29b_step_inductive_cleavage,
    IMS8_EQ8_2a_step_alpha_1_1,
    IMS8_EQ8_2b_step_inductive_2_1,
    IMS8_EQ8_2c_step_alpha_0_7,
    IMS8_EQ8_2d_step_gamma_H_rearrangement,
    IMS8_EQ8_2d_step_alpha_0_6,
    IMS8_EQ8_2e_step_gamma_H_rearrangement,
    IMS8_EQ8_2e_step_inductive_1_6,
    IMS8_EQ8_2f_step_inductive_4_5,
    IMS8_EQ8_2g_step_inductive_3_1,
    IMS8_EQ8_2h_step_inductive_2_7,
    IMS8_EQ8_2i_step_rH_2_0,
    IMS8_EQ8_2j_step_alpha_3_8,
    IMS8_EQ8_30a_step_ring_opening,
    IMS8_EQ8_30a_step_retro_ene_elimination,
    IMS8_EQ8_30d_step_inductive_ethanol_loss,
    IMS8_EQ8_31a_step_methanol_elimination,
    IMS8_EQ8_31b_step_methanol_elimination,
    IMS8_EQ8_33_step_inductive_cleavage,
    IMS8_EQ8_34_step_alpha_cleavage,
    IMS8_EQ8_34_step_retro_diels_alder,
    IMS8_EQ8_35_step_gamma_d_rearrangement,
    IMS8_EQ8_35_step_beta_cleavage,
    IMS8_EQ8_36_step_charge_remote_fragmentation,
    IMS8_EQ8_37a_step_sigma_cleavage,
    IMS8_EQ8_37b_step_alpha_cleavage,
    IMS8_EQ8_37c_step_sigma_cleavage,
    IMS8_EQ8_38a_step_sigma_cleavage,
    IMS8_EQ8_38b_step_sigma_cleavage,
    IMS8_EQ8_39_step_hydride_shift,
    IMS8_EQ8_3a_step_inductive_cleavage,
    IMS8_EQ8_3c_step_inductive_cleavage,
    IMS8_EQ8_3d_step_alpha_cleavage,
    IMS8_EQ8_40a_step_alpha_cleavage_ch,
    IMS8_EQ8_40b_step_alpha_cleavage_cc,
    IMS8_EQ8_41_step_alpha_cleavage,
    IMS8_EQ8_42a_step_alpha_cleavage,
    IMS8_EQ8_42b_step_sigma_cleavage,
    IMS8_EQ8_43a_step_inductive_cleavage,
    IMS8_EQ8_43b_step_inductive_cleavage,
    IMS8_EQ8_44a_step_inductive_cleavage,
    IMS8_EQ8_44b_step_inductive_cleavage,
    IMS8_EQ8_45a_step_inductive_cleavage,
    IMS8_EQ8_45b_step_alpha_cleavage,
    IMS8_EQ8_45c_step_sigma_dissociation,
    IMS8_EQ8_46a_step_alpha_cleavage,
    IMS8_EQ8_46b_step_inductive_cleavage,
    IMS8_EQ8_46c_step_inductive_cleavage,
    IMS8_EQ8_47_step_neighboring_group_displacement,
    IMS8_EQ8_48_step_alpha_heteroalkene,
    IMS8_EQ8_49_step_alpha_ring_opening,
    IMS8_EQ8_49_step_inductive_cleavage,
    IMS8_EQ8_4a_step_inductive_cleavage,
    IMS8_EQ8_4b_step_alpha_cleavage,
    IMS8_EQ8_50_step_alpha_ethylene_loss,
    IMS8_EQ8_51_step_double_inductive_ring_cleavage,
    IMS8_EQ8_52_step_double_inductive_retro_cleavage,
    IMS8_EQ8_53a_step_alpha_ring_opening,
    IMS8_EQ8_53a_step_alpha_homolytic_ring_closure,
    IMS8_EQ8_53b_step_alpha_ring_opening,
    IMS8_EQ8_53b_step_alpha_loss_c2h4,
    IMS8_EQ8_53b_step_alpha_loss_cnh2n,
    IMS8_EQ8_54_step_alpha_ring_opening,
    IMS8_EQ8_54_step_rh_to_alpha_position,
    IMS8_EQ8_54_step_alpha_alkyl_loss,
    IMS8_EQ8_55a_step_ring_opening_alpha,
    IMS8_EQ8_55b_step_alpha_ethylene_loss,
    IMS8_EQ8_55c_step_random_h_rearrangement,
    IMS8_EQ8_55d_step_alpha_methyl_loss,
    IMS8_EQ8_56a_step_alpha_ring_opening,
    IMS8_EQ8_56b_step_inductive_ch2o_loss,
    IMS8_EQ8_56c_step_alpha_central_cc_cleavage,
    IMS8_EQ8_56d_step_alpha_ethylene_loss,
    IMS8_EQ8_56e_step_alpha_second_ethylene_loss,
    IMS8_EQ8_57_step_alpha_ring_opening,
    IMS8_EQ8_57_step_alpha_alkene_loss,
    IMS8_EQ8_58a_step_alpha_cleavage_ring_opening,
    IMS8_EQ8_58a_step_alpha_cleavage_alkene_loss,
    IMS8_EQ8_58a_step_resonance_to_ketene,
    IMS8_EQ8_58b_step_alpha_cleavage_ring_opening,
    IMS8_EQ8_58b_step_alpha_cleavage_alkene_loss,
    IMS8_EQ8_58b_step_resonance_to_ketene,
    IMS8_EQ8_59_step_co_loss_alpha_inductive,
    IMS8_EQ8_5a_step_mclafferty_alpha_i,
    IMS8_EQ8_5b_step_mclafferty_alpha_alpha,
    IMS8_EQ8_5c_step_mclafferty_alpha_i,
    IMS8_EQ8_5d_step_mclafferty_alpha_alpha,
    IMS8_EQ8_6_step_alpha1_ring_opening,
    IMS8_EQ8_6_step_alpha2_charge_retention,
    IMS8_EQ8_60_step_alpha2_ring_cleavage,
    IMS8_EQ8_61_step_alpha_cleavage,
    IMS8_EQ8_61_step_retro_diels_alder,
    IMS8_EQ8_62_step_alpha_cleavage,
    IMS8_EQ8_62_step_ring_co_cleavage,
    IMS8_EQ8_63_step_alpha_ring_opening,
    IMS8_EQ8_63_step_h_rearrangement,
    IMS8_EQ8_63_step_alpha_ethyl_loss,
    IMS8_EQ8_64_step_alpha_ring_opening,
    IMS8_EQ8_64_step_h_rearrangement,
    IMS8_EQ8_64_step_alpha_butyl_loss,
    IMS8_EQ8_65a_step_alpha_cleavage_ring_opening,
    IMS8_EQ8_65a_step_hydrogen_rearrangement,
    IMS8_EQ8_65b_step_alpha_cleavage_ring_opening,
    IMS8_EQ8_65b_step_hydrogen_rearrangement,
    IMS8_EQ8_65c_step_alpha_cleavage_ring_opening,
    IMS8_EQ8_65c_step_hydrogen_rearrangement,
    IMS8_EQ8_66_step_alpha_ring_opening,
    IMS8_EQ8_66_step_rh_to_enol_ion,
    IMS8_EQ8_67_step_alpha_ring_opening,
    IMS8_EQ8_67_step_rh_with_beta_cleavage,
    IMS8_EQ8_68a_step_double_ring_cleavage_to_mz83,
    IMS8_EQ8_68b_step_alpha_cleavage_ring_opening,
    IMS8_EQ8_68b_step_h_transfer_and_beta_cleavage,
    IMS8_EQ8_69_step_double_ring_cleavage_to_mz125,
    IMS8_EQ8_70a_step_gamma_h_rearrangement,
    IMS8_EQ8_70a_step_beta_cleavage_charge_retention,
    IMS8_EQ8_70b_step_gamma_h_rearrangement,
    IMS8_EQ8_70b_step_beta_cleavage_charge_migration,
    IMS8_EQ8_71a_step_h_rearrangement_to_saturated_y,
    IMS8_EQ8_71a_step_ring_closure_charge_retention,
    IMS8_EQ8_71b_step_h_rearrangement_to_saturated_y,
    IMS8_EQ8_71b_step_cy_cleavage_charge_migration,
    IMS8_EQ8_72_step_double_hydrogen_rearrangement,
    IMS8_EQ8_73_step_h_h_rearrangement,
    IMS8_EQ8_74a_step_gamma_h_rearrangement,
    IMS8_EQ8_74b_step_ring_alpha_cleavage,
    IMS8_EQ8_75a_step_rH_hydroxyl_charge_retention,
    IMS8_EQ8_75b_step_rH_methyl_charge_migration,
    IMS8_EQ8_76a_step_mclafferty,
    IMS8_EQ8_76b_step_consecutive_rearrangement,
    IMS8_EQ8_77_step_radical_site_displacement,
    IMS8_EQ8_78_step_rH_1_delta_to_carbonyl_oxygen,
    IMS8_EQ8_78_step_rH_2_alpha_to_delta_carbon,
    IMS8_EQ8_78_step_alpha_cleavage,
    IMS8_EQ8_79_step_rH_gamma,
    IMS8_EQ8_79_step_alpha_beta_cleavage,
    IMS8_EQ8_79_step_third_bond_cleavage,
    IMS8_EQ8_7a_step_gamma_h_transfer,
    IMS8_EQ8_7b_step_beta_cleavage_high_energy,
    IMS8_EQ8_7c_step_beta_cleavage_low_energy,
    IMS8_EQ8_7d_step_intracomplex_proton_transfer,
    IMS8_EQ8_7e_step_intracomplex_h_transfer,
    IMS8_EQ8_80_step_triple_h_rearrangement,
    IMS8_EQ8_81a_step_rH_epsilon_H_to_alkoxy_O,
    IMS8_EQ8_81a_step_rd_methanol_displacement,
    IMS8_EQ8_81b_step_rH_i_enol_loss,
    IMS8_EQ8_82a_step_rH_hydroxyl_to_ester_oxygen,
    IMS8_EQ8_82b_step_alpha_loss_of_R,
    IMS8_EQ8_82c_step_rH_proton_transfer,
    IMS8_EQ8_82d_step_alpha_loss_of_R_from_alkoxy,
    IMS8_EQ8_82e_step_alpha_loss_of_RCHO,
    IMS8_EQ8_82f_step_rH_alpha_backbite,
    IMS8_EQ8_82g_step_inductive_loss_of_methanol,
    IMS8_EQ8_82h_step_inductive_loss_of_methanol_55,
    IMS8_EQ8_83a_step_rH_to_beta_carbon,
    IMS8_EQ8_83b_step_rH_inductive_styrene_loss,
    IMS8_EQ8_84a_step_1_2_alkyl_shift,
    IMS8_EQ8_84b_step_1_2_alkyl_shift,
    IMS8_EQ8_84c_step_1_2_H_shift,
    IMS8_EQ8_84d_step_1_2_H_shift,
    IMS8_EQ8_84e_step_1_2_alkyl_shift,
    IMS8_EQ8_84f_step_1_2_alkyl_shift,
    IMS8_EQ8_85a_step_inductive_CO_cleavage,
    IMS8_EQ8_85b_step_proton_transfer_elimination,
    IMS8_EQ8_85c_step_complex_formation,
    IMS8_EQ8_85c_step_1_2_hydride_shift,
    IMS8_EQ8_85c_step_complex_collapse,
    IMS8_EQ8_86a_step_rH_proton_transfer_to_remote_ether,
    IMS8_EQ8_86a_step_rd_displacement_of_methanol,
    IMS8_EQ8_86b_step_rH_hydride_shift_to_carbenium,
    IMS8_EQ8_86b_step_rH_proton_transfer_to_remote_ether,
    IMS8_EQ8_86b_step_rd_displacement_of_methanol,
    IMS8_EQ8_87_step_delta_rH_to_carbonyl_oxygen,
    IMS8_EQ8_87_step_alpha_cleavage_isobutene_loss,
    IMS8_EQ8_88a_step_rH_to_Y,
    IMS8_EQ8_88b_step_rH_to_X,
    IMS8_EQ8_89_step_sigma_dissociation,
    IMS8_EQ8_89_step_hydrogen_transfer,
    IMS8_EQ8_8a_step_alpha_cleavage_rejected,
    IMS8_EQ8_8b_step_ring_opening,
    IMS8_EQ8_8b_step_rH_to_enol_ether,
    IMS8_EQ8_8b_step_rH_methyl_loss,
    IMS8_EQ8_9_step_rH_rearrangement,
    IMS8_EQ8_9_step_alpha_cleavage,
    IMS8_EQ8_90_step_rH_gamma_H_to_carbonyl_oxygen,
    IMS8_EQ8_90_step_cyclization_to_cyclobutane_ring,
    IMS8_EQ8_90_step_retro_2plus2_ethylene_loss,
    IMS8_EQ8_91_step_rH_1_5_delta_H_to_nitrogen,
    IMS8_EQ8_91_step_rH_1_4_C_to_C,
    IMS8_EQ8_91_step_rC_1_2_alkyl_shift,
    IMS8_EQ8_91_step_rH_1_5_C_to_primary_radical,
    IMS8_EQ8_91_step_rH_1_5_N_to_carbon_radical,
    IMS8_EQ8_91_step_alpha_cleavage_to_m44,
    IMS8_EQ8_92_step_rH_six_ring_to_heteroatom,
    IMS8_EQ8_93_step_rH_six_ring_to_carbon,
    IMS8_EQ8_94_step_rH_alkene_loss_to_heteroatom,
    IMS8_EQ8_95_step_rH_alkene_loss_to_carbon,
    IMS8_EQ8_97_step_rH_displacement_ethylene_loss,
    IMS8_EQ8_98_step_rH_1_2_hydride_shift,
    IMS8_EQ8_98_step_rH_proton_transfer_to_hydroxyl,
    IMS8_EQ8_98_step_i_water_loss,
    IMS8_EQ8_99_step_alpha_cleavage,
    IMS8_EQ8_99_step_rH_thiol_elimination,
    IMS8_EQ8_9b_step_direct_cleavage,
    IMS8_EQT8_2a_step_sigma,
    IMS8_EQT8_2b_step_sigma_pi,
    IMS8_EQT8_2d_step_inductive,
    IMS8_EQT8_2e_step_inductive,
    IMS8_EQT8_2f_step_alpha,
    IMS8_EQT8_2g_step_inductive,
    IMS8_EQT8_2h_step_inductive,
    IMS8_EQT8_2i_step_rd_displacement,
    IMS8_EQT8_2j_step_rd_displacement,
    IMS8_EQT8_2k_step_displacement,
    IMS8_EQT8_2l_step_retro_2plus2,
    IMS8_EQT8_2m_step_ring_contraction,
    IMS8_EQT8_2n_step_mclafferty,
    IMS8_EQT8_2o_step_onium,
    IMS8_EQT8_2p_step_alpha_ring_opening,
    IMS8_EQT8_2p_step_rH_1_5,
    IMS8_EQT8_2p_step_alpha_second,
    IMS8_EQT8_2q_step_double_rH,
    IMS9_EQ9_10_step_alpha_ring_opening,
    IMS9_EQ9_10_step_rh_1_3_hydrogen_shift,
    IMS9_EQ9_10_step_alpha_methyl_loss,
    IMS9_EQ9_11_step_alpha1_ring_opening,
    IMS9_EQ9_11_step_alpha2_ethylene_loss,
    IMS9_EQ9_12_step_retro_diels_alder,
    IMS9_EQ9_12_step_alpha_methyl_loss,
    IMS9_EQ9_13_step_benzylic_alpha_cleavage,
    IMS9_EQ9_14_step_benzylic_alpha_cleavage,
    IMS9_EQ9_14_step_olefin_elimination,
    IMS9_EQ9_15_step_gamma_h_rearrangement,
    IMS9_EQ9_15_step_alpha_cleavage,
    IMS9_EQ9_16_step_ortho_h_rearrangement_with_beta_cleavage,
    IMS9_EQ9_17_step_benzylic_alpha_cleavage,
    IMS9_EQ9_18a_step_alpha_butyl_loss,
    IMS9_EQ9_18a_step_rh_ethene_loss,
    IMS9_EQ9_18b_step_alpha_ethyl_loss,
    IMS9_EQ9_18b_step_rh_butene_loss,
    IMS9_EQ9_18c_step_alpha_methyl_loss,
    IMS9_EQ9_18c_step_rh_butene_loss,
    IMS9_EQ9_18c_step_rh_ethene_loss,
    IMS9_EQ9_19a_step_alpha_ring_opening,
    IMS9_EQ9_19a_step_rh_c6_to_c2,
    IMS9_EQ9_19a_step_alpha_loss_butyl,
    IMS9_EQ9_19b_step_alpha_ring_opening,
    IMS9_EQ9_19b_step_alpha_loss_propene,
    IMS9_EQ9_19b_step_alpha_loss_ethene,
    IMS9_EQ9_1a_step_sigma_cleavage_charge_retention,
    IMS9_EQ9_2_step_sigma_cleavage_loss_of_methyl,
    IMS9_EQ9_2_step_alpha_cleavage_olefin_loss,
    IMS9_EQ9_20a_step_alpha_ring_opening,
    IMS9_EQ9_20a_step_rh_c2_to_c6,
    IMS9_EQ9_20a_step_alpha_loss_propyl,
    IMS9_EQ9_20b_step_alpha_ring_opening,
    IMS9_EQ9_20b_step_alpha_loss_ethene_1,
    IMS9_EQ9_20b_step_alpha_loss_ethene_2,
    IMS9_EQ9_21_step_alpha_cleavage_ring_opening,
    IMS9_EQ9_21_step_rH_oxygen_to_carbon,
    IMS9_EQ9_21_step_mclafferty_pentene_loss,
    IMS9_EQ9_22_step_rh_hydroxyl_to_ortho_radical,
    IMS9_EQ9_22_step_co_elimination,
    IMS9_EQ9_22_step_alpha_hydrogen_loss,
    IMS9_EQ9_23_step_rh_benzylic_to_oxygen,
    IMS9_EQ9_23_step_inductive_water_loss,
    IMS9_EQ9_24_step_rh_phenol_to_ester_oxygen,
    IMS9_EQ9_24_step_inductive_methanol_loss,
    IMS9_EQ9_25a_step_alpha_cho,
    IMS9_EQ9_25b_step_rH_gamma,
    IMS9_EQ9_25b_step_alpha_butene_loss,
    IMS9_EQ9_25b_step_alpha_methyl_loss,
    IMS9_EQ9_25c_step_mclafferty_ethene_loss,
    IMS9_EQ9_25c_step_alpha_propyl_loss,
    IMS9_EQ9_25d_step_inductive,
    IMS9_EQ9_25e_step_sigma,
    IMS9_EQ9_26a_step_alpha_acetyl,
    IMS9_EQ9_26b_step_alpha_methyl_loss,
    IMS9_EQ9_26b_step_inductive_co_loss,
    IMS9_EQ9_26c_step_inductive,
    IMS9_EQ9_26d_step_rH_gamma,
    IMS9_EQ9_26d_step_alpha_alkene_loss,
    IMS9_EQ9_26e_step_inductive_charge_migration,
    IMS9_EQ9_27a_step_alpha_c1_methyl_loss,
    IMS9_EQ9_27b_step_rH_slow_s1_s2,
    IMS9_EQ9_27b_step_rC_s2_s3,
    IMS9_EQ9_27b_step_rH_s3_s4,
    IMS9_EQ9_27b_step_rH_s4_s5,
    IMS9_EQ9_27b_step_s5_s6,
    IMS9_EQ9_27b_step_c4_methyl_loss,
    IMS9_EQ9_27c_step_c6_methyl_loss,
    IMS9_EQ9_28a_step_double_bond_isomerization,
    IMS9_EQ9_28a_step_mclafferty_concerted,
    IMS9_EQ9_28b_step_double_bond_isomerization,
    IMS9_EQ9_28b_step_mclafferty_charge_migration,
    IMS9_EQ9_29_step_rc_cyclization,
    IMS9_EQ9_29_step_rd_methyl_loss,
    IMS9_EQ9_3_step_allylic_alpha_cleavage,
    IMS9_EQ9_30a_step_alpha_ring_opening,
    IMS9_EQ9_30a_step_inductive_co_loss,
    IMS9_EQ9_30a_step_inductive_alkene_loss,
    IMS9_EQ9_30b_step_alpha_ring_opening,
    IMS9_EQ9_30b_step_rH_c2_to_c6,
    IMS9_EQ9_30b_step_alpha_isobutyl_loss,
    IMS9_EQ9_30c_step_alpha_ring_opening,
    IMS9_EQ9_30c_step_rH_c6_to_c2,
    IMS9_EQ9_30c_step_alpha_neopentyl_loss,
    IMS9_EQ9_31a_step_alpha_methoxy_loss,
    IMS9_EQ9_31a_step_inductive_co_loss,
    IMS9_EQ9_31b_step_inductive_charge_migration,
    IMS9_EQ9_31d_step_alpha_alkyl_loss,
    IMS9_EQ9_32a_step_rH_gamma,
    IMS9_EQ9_32a_step_alpha_alkene_loss,
    IMS9_EQ9_32b_step_rH_gamma,
    IMS9_EQ9_32b_step_alpha_charge_migration_rejected,
    IMS9_EQ9_33_step_beta_cleavage,
    IMS9_EQ9_34a_step_rH_alkoxy_side,
    IMS9_EQ9_34a_step_alpha_alkene_loss,
    IMS9_EQ9_34b_step_rH_alkoxy_side,
    IMS9_EQ9_34b_step_charge_localization,
    IMS9_EQ9_34b_step_inductive_acid_loss,
    IMS9_EQ9_34c_step_rH_alkoxy_side,
    IMS9_EQ9_34c_step_charge_localization,
    IMS9_EQ9_34c_step_second_rH_double_hydrogen,
    IMS9_EQ9_35a_step_alpha_carbonyl_initiated,
    IMS9_EQ9_35b_step_alpha_methyl_loss,
    IMS9_EQ9_35c_step_alpha_ester_o_initiated,
    IMS9_EQ9_35d_step_alpha_ester_o_initiated_methyl_loss,
    IMS9_EQ9_35e_step_inductive_charge_site,
    IMS9_EQ9_36a_step_r2H_alkyl_radical_loss,
    IMS9_EQ9_36a_step_rH_alkene_loss,
    IMS9_EQ9_36a_step_water_loss_ring_closure,
    IMS9_EQ9_36b_step_r2H_alkyl_radical_loss,
    IMS9_EQ9_36b_step_id_alcohol_loss,
    IMS9_EQ9_37a_step_alpha_methyl_loss,
    IMS9_EQ9_37a_step_rH_pentene_loss,
    IMS9_EQ9_37b_step_alpha_methyl_loss,
    IMS9_EQ9_37b_step_inductive_aldehyde_loss,
    IMS9_EQ9_37c_step_alpha_butyl_loss,
    IMS9_EQ9_37c_step_rH_propene_loss,
    IMS9_EQ9_37d_step_alpha_butyl_loss,
    IMS9_EQ9_37d_step_inductive_formaldehyde_loss,
    IMS9_EQ9_37e_step_inductive_charge_site,
    IMS9_EQ9_37f_step_inductive_charge_site,
    IMS9_EQ9_37f_step_inductive_ethylene_loss,
    IMS9_EQ9_4a_step_allylic_alpha_cleavage_retarded,
    IMS9_EQ9_4b_step_doubly_allylic_alpha_cleavage,
    IMS9_EQ9_6a_step_gamma_h_rearrangement,
    IMS9_EQ9_6a_step_alpha_cleavage,
    IMS9_EQ9_6b_step_gamma_h_rearrangement,
    IMS9_EQ9_6b_step_i_cleavage,
    IMS9_EQ9_7_step_sigma_ionization,
    IMS9_EQ9_7_step_alpha_cleavage,
    IMS9_EQ9_8_step_alpha_ring_d_opening,
    IMS9_EQ9_8_step_rH_c18_to_c17,
    IMS9_EQ9_8_step_rH_c16_to_c18,
    IMS9_EQ9_8_step_alpha_c14_c15_cleavage,
    IMS9_EQ9_9_step_alpha_c4h8_loss,
    IMS9_EQ9_9_step_c19_methyl_loss_rearrangement_alpha,
]

__all__ = ["fragmentation"]
