from typing import List, Tuple
import torch
import pandas as pd
from ..target_peaks import clean_spectra, make_peaks_tensor


def spectra_to_tensor(cleaned: List[Tuple[float, float]]) -> torch.Tensor:
    """
    Convert cleaned spectra into a 2D torch tensor.

    Parameters
    ----------
    cleaned : List[Tuple[float, float]]
        List of (m/z, intensity) pairs.

    Returns
    -------
    torch.Tensor
        shape (N, 2), dtype float32
    """
    if not cleaned:
        return torch.empty((0, 2), dtype=torch.float32)

    tensor = torch.tensor(cleaned, dtype=torch.float32)
    return tensor


def build_fragment_catalog(all_frag_lists, ppm_merge: float = 5.0) -> torch.Tensor:
    """
    Build a merged, sorted fragment m/z catalog from multiple fragment lists,
    merging entries within `ppm_merge` tolerance.
    """
    flat = []
    for frags in all_frag_lists:
        for m in frags:
            if isinstance(m, torch.Tensor):
                if m.ndim == 0:
                    flat.append(float(m.item()))
                else:
                    flat.extend(float(x) for x in m.reshape(-1).tolist())
            else:
                flat.append(float(m))
    if not flat:
        return torch.empty(0, dtype=torch.float32)

    masses = torch.tensor(flat, dtype=torch.float64)
    masses, _ = torch.sort(masses)

    keep = [0]
    for i in range(1, masses.numel()):
        m_prev = masses[keep[-1]]
        ppm = (masses[i] - m_prev).abs() / max(float(m_prev), 1e-9) * 1e6
        if ppm > ppm_merge:
            keep.append(i)
    catalog = masses[keep].to(torch.float32)
    return catalog


def clean_spectra_tensor(spectra, *, device=None, dtype=torch.float32):
    """
    Clean raw spectra via `clean_spectra` and convert to a peaks tensor
    with `make_peaks_tensor`.
    """
    cleaned = clean_spectra(spectra)
    return make_peaks_tensor(cleaned, device=device, dtype=dtype, normalize="max")
