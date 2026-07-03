"""
Pure metrics for the MØD explainability ceiling (feasibility study).

These functions are deliberately dependency-light (standard library only) so the
unit tests can run *outside* the ``mol-spectro.sif`` container, where ``mod`` and
the scientific stack are unavailable. The only place that needs ``mod`` is the
corpus runner (``run_ceiling.py``), which reads the MØD fragment masses from the
derivation-graph dumps and then defers to the functions here.

Binning contract: integer (nominal / unit-resolution) m/z everywhere, matching the
NIST EI spectra. We bin a real mass to its nominal value with ``round`` (not the
legacy ``int`` truncation used elsewhere in the pipeline) so that Cl/Br/S-bearing
fragments, whose monoisotopic mass sits just below the integer, land on the correct
nominal peak.
"""
from __future__ import annotations

import heapq
import math
import random
import re
from collections import Counter
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# Nominal (most-abundant-isotope, integer) masses for the elements that occur in
# the EI corpus. Used for the formula-reachable null; intentionally not exhaustive
# -- a molecule whose formula carries an element absent here is flagged by the
# runner rather than silently mis-massed.
NOMINAL_MASS: Dict[str, int] = {
    "H": 1, "B": 11, "C": 12, "N": 14, "O": 16, "F": 19, "Na": 23, "Mg": 24,
    "Al": 27, "Si": 28, "P": 31, "S": 32, "Cl": 35, "K": 39, "Ca": 40,
    "Fe": 56, "Br": 79, "I": 127,
}

# Elements that count as "heavy" (i.e. a real fragment needs at least one of them;
# a bare H_n cluster is not a plausible ion).
_HEAVY = tuple(e for e in NOMINAL_MASS if e != "H")

Peak = Tuple[float, float]  # (m/z, intensity)


# --------------------------------------------------------------------------- #
# Formula handling
# --------------------------------------------------------------------------- #
_FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?)\s*(\d*)")


def parse_formula(formula: str) -> Dict[str, int]:
    """Parse a molecular formula into element counts.

    Accepts both the spaced NIST ``##MOLFORM`` style (``"C3 H6 O"``) and the
    compact style (``"C3H6O"``). A bare element symbol means a count of 1.
    """
    counts: Counter[str] = Counter()
    for symbol, number in _FORMULA_TOKEN.findall(formula):
        if not symbol:
            continue
        counts[symbol] += int(number) if number else 1
    return dict(counts)


def nominal_mass_of(counts: Dict[str, int]) -> int:
    """Nominal mass of an element-count dict. Raises on an unknown element."""
    total = 0
    for element, n in counts.items():
        if element not in NOMINAL_MASS:
            raise KeyError(f"no nominal mass for element {element!r}")
        total += NOMINAL_MASS[element] * n
    return total


def nitrogen_count(counts: Dict[str, int]) -> int:
    return counts.get("N", 0)


# --------------------------------------------------------------------------- #
# Explained fraction
# --------------------------------------------------------------------------- #
def select_peaks(
    peaks: Sequence[Peak],
    *,
    intensity_floor: float = 0.0,
    mz_max: Optional[float] = None,
) -> List[Peak]:
    """Filter peaks to those at/above ``intensity_floor`` and (if given) at or
    below ``mz_max`` (nominal molecular-ion mass; drops isotope/contaminant peaks
    above M+•). ``mz_max`` is compared with a +0.5 slack so the M+• peak survives.
    """
    out: List[Peak] = []
    for mz, inten in peaks:
        if inten < intensity_floor:
            continue
        if mz_max is not None and mz > mz_max + 0.5:
            continue
        out.append((mz, inten))
    return out


def explained_fraction(
    peaks: Sequence[Peak],
    mod_masses: Iterable[int],
    *,
    weighted: bool = True,
) -> float:
    """Fraction of ``peaks`` whose nominal m/z is in ``mod_masses``.

    ``weighted`` -> intensity-weighted fraction; otherwise the plain count
    fraction. Returns ``nan`` when there is nothing to score. ``peaks`` should
    already be filtered (see :func:`select_peaks`).
    """
    masses = set(mod_masses)
    if not peaks:
        return float("nan")
    if weighted:
        total = math.fsum(inten for _, inten in peaks)
        if total <= 0:
            return float("nan")
        hit = math.fsum(inten for mz, inten in peaks if round(mz) in masses)
        return hit / total
    hit = sum(1 for mz, _ in peaks if round(mz) in masses)
    return hit / len(peaks)


# --------------------------------------------------------------------------- #
# Null models
# --------------------------------------------------------------------------- #
def formula_reachable_masses(
    inventory: Dict[str, int],
    mass_ceiling: int,
    *,
    extra_h: int = 2,
) -> Dict[int, int]:
    """Nominal-mass density of the sub-formulas reachable from ``inventory``.

    Every sub-formula uses only elements present in ``inventory``, with each
    element count bounded by the precursor's count (hydrogen by precursor-H +
    ``extra_h`` to allow minor H transfer), at least one heavy atom, and nominal
    mass in ``[1, mass_ceiling]``. Returns ``{nominal_mass: n_formulas}`` -- the
    multiplicity captures how densely real fragment masses cluster at each nominal
    value, which is the whole point of a *formula-aware* (rather than uniform)
    null.

    Computed by polynomial convolution (a counting DP over nominal mass), so it is
    O(n_elements x mass_ceiling x max_count) and never enumerates formulas
    explicitly.
    """
    if mass_ceiling < 1:
        return {}

    # Heavy-atom skeletons first; index = nominal mass, value = #sub-formulas.
    heavy = [0] * (mass_ceiling + 1)
    heavy[0] = 1  # empty skeleton, dropped below
    for element, max_count in inventory.items():
        if element == "H" or max_count <= 0:
            continue
        m = NOMINAL_MASS.get(element)
        if m is None or m > mass_ceiling:
            continue
        nxt = [0] * (mass_ceiling + 1)
        for d in range(mass_ceiling + 1):
            c = heavy[d]
            if not c:
                continue
            j = 0
            md = d
            while j <= max_count and md <= mass_ceiling:
                nxt[md] += c
                j += 1
                md += m
        heavy = nxt
    heavy[0] = 0  # require >= 1 heavy atom

    # Convolve with the hydrogen polynomial (0 .. H + extra_h).
    h_max = inventory.get("H", 0) + max(extra_h, 0)
    poly = [0] * (mass_ceiling + 1)
    for d in range(mass_ceiling + 1):
        c = heavy[d]
        if not c:
            continue
        for h in range(h_max + 1):
            md = d + h  # NOMINAL_MASS["H"] == 1
            if md > mass_ceiling:
                break
            poly[md] += c

    return {d: poly[d] for d in range(1, mass_ceiling + 1) if poly[d] > 0}


def _weighted_sample_without_replacement(
    items: Sequence[Tuple[int, int]],
    k: int,
    rng: random.Random,
) -> List[int]:
    """Efraimidis-Spirakis weighted sampling without replacement.

    ``items`` is ``(mass, weight)``; returns ``k`` distinct masses drawn with
    probability proportional to weight (k is capped at the number of items).
    """
    keys: List[Tuple[float, int]] = []
    for mass, w in items:
        if w <= 0:
            continue
        # key = U**(1/w); take the k largest.
        keys.append((math.log(rng.random()) / w, mass))
    topk = heapq.nlargest(min(k, len(keys)), keys)
    return [mass for _, mass in topk]


def sample_null(
    pool: Dict[int, int],
    k: int,
    peaks: Sequence[Peak],
    *,
    draws: int = 1000,
    weighted: bool = True,
    rng: Optional[random.Random] = None,
) -> Tuple[float, Tuple[float, float], List[float]]:
    """Mean explained fraction of ``k`` masses drawn at random from ``pool``.

    ``pool`` maps nominal mass -> selection weight (multiplicity). Each of
    ``draws`` trials samples ``k`` distinct masses without replacement and scores
    the (intensity-weighted, if ``weighted``) explained fraction against
    ``peaks``. Returns ``(mean, (lo95, hi95), per_draw_fractions)`` where the CI
    is the 2.5/97.5 percentile band of the null distribution.
    """
    rng = rng or random.Random(0)
    items = list(pool.items())
    if not items or k <= 0 or not peaks:
        return float("nan"), (float("nan"), float("nan")), []

    fractions: List[float] = []
    for _ in range(draws):
        drawn = _weighted_sample_without_replacement(items, k, rng)
        fractions.append(explained_fraction(peaks, drawn, weighted=weighted))

    mean = math.fsum(fractions) / len(fractions)
    return mean, _percentile_ci(fractions), fractions


def uniform_pool(mass_ceiling: int) -> Dict[int, int]:
    """Uniform null pool: every nominal mass in ``[1, mass_ceiling]`` with weight 1."""
    return {m: 1 for m in range(1, max(mass_ceiling, 0) + 1)}


def _percentile_ci(values: Sequence[float]) -> Tuple[float, float]:
    """2.5 / 97.5 percentile band (nearest-rank) of finite values."""
    finite = sorted(v for v in values if not math.isnan(v))
    if not finite:
        return float("nan"), float("nan")
    n = len(finite)

    def _pick(p: float) -> float:
        idx = min(n - 1, max(0, int(round(p * (n - 1)))))
        return finite[idx]

    return _pick(0.025), _pick(0.975)


def ceiling_with_ci(
    raw: float,
    null_fractions: Sequence[float],
) -> Tuple[float, Tuple[float, float]]:
    """Null-subtracted ceiling and its 95% CI.

    ``ceiling = raw - mean(null)``; the CI is ``raw - null_percentiles`` (flipped),
    i.e. the band of ``raw - null_draw`` over the null distribution.
    """
    finite = [v for v in null_fractions if not math.isnan(v)]
    if math.isnan(raw) or not finite:
        return float("nan"), (float("nan"), float("nan"))
    null_mean = math.fsum(finite) / len(finite)
    lo, hi = _percentile_ci(finite)
    return raw - null_mean, (raw - hi, raw - lo)


# --------------------------------------------------------------------------- #
# Odd/even-electron split (nitrogen rule)
# --------------------------------------------------------------------------- #
def nitrogen_rule_parity(mz: int, n_nitrogen: int) -> str:
    """Classify an ion at nominal ``mz`` as odd- ("OE") or even-electron ("EE").

    Odd-electron ions (radical cations, e.g. M+•) obey the nitrogen rule: nominal
    mass parity matches the parity of the nitrogen count. Even-electron ions
    (the usual closed-shell fragment cations formed with H rearrangement) sit at
    the opposite parity.

    Heuristic caveat: we use the *molecule's* total nitrogen-count parity as a
    stand-in for the fragment's, which is only exact when the fragment retains a
    nitrogen count of the same parity as the precursor. For the N-free majority of
    the EI corpus this is exact (even m/z -> OE, odd m/z -> EE); for N-bearing
    molecules treat the split as indicative, not definitive.
    """
    mass_even = (mz % 2 == 0)
    n_even = (n_nitrogen % 2 == 0)
    return "OE" if mass_even == n_even else "EE"
