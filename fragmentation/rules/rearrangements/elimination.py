# rearrangements from mcLafferty book cover

elimination = Rule.fromDFS( # siehe 4.45
	"[C]1[C]2[C]4[C+]5[O]6" +
	">>" +
	"[C]2[C]4{-}2.[C]1[C]5[O+]6",
	"Elimination" +
	" ^R1S2-4R5Y6"
)