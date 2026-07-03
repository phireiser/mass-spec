"""Feasibility — cheap, no-ML gates for the EI spectrum-to-structure thesis.

Two questions, no model required. (1) The MØD *explainability ceiling*: the
intensity-weighted, null-subtracted fraction of high-intensity EI peaks that the
MØD rule library can produce a charged fragment for (``ceiling_metrics`` for the
pure metrics, ``run_ceiling`` for the corpus runner). (2) The per-molecule
enumeration *cost* and the full-enumeration budget crossover (``cost_analysis``).
Together they decide whether the rule library is adequate and whether full
enumeration is affordable before any modeling work starts.
"""
