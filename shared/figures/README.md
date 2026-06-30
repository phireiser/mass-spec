# shared/figures

Figures used by **both** the report and the slides live here (single source of
truth). Both documents add this directory to their `\graphicspath`, so a file
placed here is referenced by bare name from either document:

    \includegraphics[width=\linewidth]{toluene_spectrum.png}
    \input{../shared/figures/predicate-alkyl.tikz.tex}

For a shared TikZ snippet that itself `\input`s sub-files or images, use the
`import` package so nested paths resolve relative to this folder regardless of
which document compiles it (this is how `dataGenOverview` pulls in
`fragmentationTree`):

    \import{../shared/figures/}{dataGenOverview.tikz.tex}

## Currently consolidated here

| file                          | used by                |
|-------------------------------|------------------------|
| architecture_diagram.tikz.tex | report (ch3) + slides  |
| dataGenOverview.tikz.tex      | report (ch3) + slides  |
| fragmentationTree.tikz.tex    | helper of dataGenOverview |
| predicate-filter.tikz.tex     | report (ch3) + slides  |
| predicate-alkyl.tikz.tex      | report (ch3) + slides  |
| predicate-heteroatom.tikz.tex | report (ch3) + slides  |
| predicate-saturation.tikz.tex | report (ch3) + slides  |

The report (`../report/`) versions are the canonical originals; the older
slide-local copies (`alkyl-group`, `heteroatom-group`, `saturation-example`,
etc.) were removed when these were adopted.
