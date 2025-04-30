hTransition_unsaturated = Rule.fromDFS(
	s =
	"[H]1[C]2[C]3[C]4[C]5{=}[O+.]6" +
	">>" +
	"[C.]2[C]3[C]4[C]5{=}[O+]6[H]1", 
	name = "H transition receptor site unsaturated" +
	" ^Y6"
)

hTransition_unsaturated_alpha = Rule.fromDFS(
	s =
	"[C.]2[C]3[C]4[C]5{=}[O+]6[H]1" +
	">>" +
	"[C]2{=}[C]3.[C.]4[C]5{=}[O+]6[H]1",
	name = "H transition receptor site unsaturated" +
	" ^Y6"
)

hTransition_unsaturated_bidirect = Rule.fromDFS(
	s =
	"[C.]2[C]3[C]4[C]5{=}[O+]6[H]1" +
	">>" +
	"[C.]2[C]3[C]4[C+]5[O]6[H]1", 
	name = "H transition receptor site unsaturated" +
	" ^Y6"
)

hTransition_unsaturated_inductive = Rule.fromDFS(
	s =
	"[C.]2[C]3[C]4[C]5{=}[O+]6[H]1" +
	">>" +
	"[C.]2[C+]3.[C]4{=}[C]5[O]6[H]1", 
	name = "H transition receptor site unsaturated" +
	" ^Y6"
)