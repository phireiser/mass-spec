# rearrangements from mcLafferty book cover
elimination = Rule.fromDFS( # siehe 4.45
	"[C]1[C]2[C]3[C]4[C+]5[*]6" +
	">>" +
	"[C]2[C]3[C]4{-}2.[C]1[C]5[*+]6",
	"Elimination" +
	" §R1S3R5Y6"
)