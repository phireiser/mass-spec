"""Discrimination — the Phase-1 make-or-break gate.

True-vs-same-formula-decoy discrimination at unit resolution. Given the observed
EI spectrum of a target molecule and the same-formula decoys present in the NIST
store, how spectrally separable are the isomers?

A structure->spectrum predictor identifies the true molecule over a decoy iff
``cosine(observed_true, predicted_true) > cosine(observed_true, predicted_decoy)``.
Using each candidate's *real* NIST spectrum as a perfect-predictor stand-in, the
right-hand side is ``cosine(observed_true, observed_decoy)`` -- so the
**best-decoy cosine is exactly the bar the MØD forward model must clear** to
identify that molecule. This baseline needs no new MØD compute; it is the cheap
gate that must pass before the expensive decoy-enumeration half of Phase 1.

``spectrum_ops`` holds the pure (stdlib) preprocessing + cosine; ``discriminate``
is the corpus runner over the Parquet spectra store.
"""
