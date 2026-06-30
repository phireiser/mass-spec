# shared/figures

**All** figures for both documents live here — the report (`../report/`) and the
slides (`../slides/`) keep no figures of their own. This folder is the single
source of truth; a figure used by one document or by both is stored here once.

Both documents add this directory to their `\graphicspath`, so an image placed
here is referenced by bare name from either document:

    \includegraphics[width=\linewidth]{toluene-qm.png}

TikZ snippets are pulled in with an explicit relative path (`\input` ignores
`\graphicspath`):

    \input{../shared/figures/wasserstein_expl.tikz.tex}

SVGs and PDFs are likewise referenced with the relative path so they resolve
regardless of which document compiles:

    \includesvg[width=\linewidth]{../shared/figures/cosine_mrr.svg}
    \includepdf[pages=-]{../shared/figures/Titelblatt.pdf}

For a shared TikZ snippet that itself `\input`s sub-files or images, use the
`import` package so nested paths resolve relative to this folder regardless of
which document compiles it (this is how `dataGenOverview` pulls in
`fragmentationTree`):

    \import{../shared/figures/}{dataGenOverview.tikz.tex}

## Contents

- Report-only figures (mass-spec schematics, GNN pipeline, loss illustrations,
  result plots, `Titelblatt.pdf`, the toluene QM data behind `toluene-qm.png`).
- Slides-only figures (`motivation`, `MassSpec_*`, `TolueneFragmentation.svg`, …).
- Figures shared by both (`architecture_diagram`, `dataGenOverview`,
  `fragmentationTree`, the `predicate-*` snippets, `dg_toluene.pdf`).
