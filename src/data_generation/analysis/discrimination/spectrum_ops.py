"""Pure spectrum preprocessing + similarity for the discrimination gate.

Stdlib only (no numpy/torch), so :mod:`unit_test_discrimination` runs bare,
outside ``mol-spectro.sif``. The binning here mirrors
:func:`machine_learning.data.bin_spectrum` exactly (floor bin index, sqrt of
summed intensity, L2 normalisation) so the Phase-1 baseline and the learned
forward model share one spectrum representation. The frozen contract is integer
m/z (``bin_width=1.0``), sqrt-intensity, dot-product cosine.
"""
from __future__ import annotations

import math
from typing import List, Sequence, Tuple

Peaks = Sequence[Tuple[float, float]]

# Frozen preprocessing contract (see machine_learning.data defaults).
MZ_MIN = 0.0
MZ_MAX = 1000.0
BIN_WIDTH = 1.0


def bin_spectrum(
    peaks: Peaks,
    mz_min: float = MZ_MIN,
    mz_max: float = MZ_MAX,
    bin_width: float = BIN_WIDTH,
    sqrt_and_l2: bool = True,
) -> List[float]:
    """Bin ``(m/z, intensity)`` peaks into a fixed-width vector.

    Semantics match ``machine_learning.data.bin_spectrum``: a peak lands in bin
    ``int((mz - mz_min) / bin_width)`` and is dropped if ``mz < mz_min`` or
    ``mz >= mz_max``; intensities in a bin are summed; with ``sqrt_and_l2`` the
    vector is sqrt-transformed then L2-normalised.
    """
    n_bins = int((mz_max - mz_min) / bin_width)
    vec = [0.0] * n_bins
    for mz, inten in peaks:
        if mz < mz_min or mz >= mz_max:
            continue
        bi = int((mz - mz_min) / bin_width)
        if 0 <= bi < n_bins:
            vec[bi] += float(inten)
    if sqrt_and_l2:
        vec = [math.sqrt(v) if v > 0.0 else 0.0 for v in vec]
        norm = math.sqrt(math.fsum(v * v for v in vec))
        if norm > 0.0:
            vec = [v / norm for v in vec]
    return vec


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity of two vectors; 0.0 if either is all-zero."""
    dot = math.fsum(x * y for x, y in zip(a, b))
    na = math.sqrt(math.fsum(x * x for x in a))
    nb = math.sqrt(math.fsum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def cosine_from_peaks(p: Peaks, q: Peaks, **binning) -> float:
    """Convenience: bin both peak lists with the frozen contract, then cosine."""
    return cosine(bin_spectrum(p, **binning), bin_spectrum(q, **binning))


__all__ = ["MZ_MIN", "MZ_MAX", "BIN_WIDTH", "bin_spectrum", "cosine", "cosine_from_peaks"]
