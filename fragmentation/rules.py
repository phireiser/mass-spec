include("rules/alpha.py")
include("rules/benzylAllyl_ringGeneral.py")
include("rules/deprotonation.py")
include("rules/IMS_examples.py")
include("rules/inductive.py")
include("rules/mcLafferty.py")
include("rules/retroDielsAlder.py")
include("rules/sigma.py")

include("rules/rearrangements/hTransition_saturated.py")
include("rules/rearrangements/hTransition_unsaturated.py")
include("rules/rearrangements/h2Transition.py")
include("rules/rearrangements/substituion.py")
include("rules/rearrangements/elimination.py")

rearrangements = [
	hTransition_unsaturated,
	hTransition_unsaturated_alpha,
	hTransition_unsaturated_bidirect,
	hTransition_unsaturated_inductive,

	hTransition_saturated_1,
	hTransition_saturated_1_alpha,
	hTransition_saturated_1_inductive_1,
	hTransition_saturated_1_inductive_2,

	hTransition_saturated_2,
	hTransition_saturated_2_alpha,

	hTransition_saturated_3,
	hTransition_saturated_3_alpha,

	hTransition_saturated_4,
	hTransition_saturated_4_alpha,

	hTransition_saturated_5_inductive_1,
	hTransition_saturated_5_inductive_2,
	hTransition_saturated_5_inductive_3,

	h2Transiton_1,
	h2Transiton_2,
	h2Transiton_3,
	substituion,
	elimination,
]

rearrangements = flatten_list(rearrangements)

# TODO heterocyclic ring fission (HRF)
# TODO benzofuran forming fission (BFF)
# TODO quinone methide (QM) fission