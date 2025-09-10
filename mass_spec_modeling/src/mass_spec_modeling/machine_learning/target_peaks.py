"""target peak tensors.py"""
from __future__ import annotations
from typing import Iterable, List, Sequence, Tuple, Optional, Dict, Union
from collections import defaultdict
from math import isfinite

import torch

def clean_spectra(
    spectra: List[Tuple[int, Union[List[Tuple[float, float]], Tuple[float, float], float]]]
    ) -> List[Tuple[int, float]]:
    """
    Combine and clean PubChem GC-MS peak lists.

    - Flattens all reference spectra into one set of peaks.
    - Bins m/z to nearest integer (common for EI spectra tables).
    - Sums intensities for identical bins across references.
    - Normalizes intensities so the base peak is 100.0.
    - Returns peaks sorted by m/z.
    """
    bins: Dict[int, float] = defaultdict(float)

    for _ref_id, peaks in spectra:
        # normalize peaks into a list of (mz, inten)
        if isinstance(peaks, tuple) and len(peaks) == 2:
            peaks = [peaks]
        elif isinstance(peaks, (int, float)):
            # skip invalid case: just a single number
            continue

        if not isinstance(peaks, list):
            continue

        for mz, inten in peaks:
            # sanity checks
            if not (isinstance(mz, (int, float)) and isinstance(inten, (int, float))):
                continue
            if not (isfinite(mz) and isfinite(inten)):
                continue
            if inten <= 0:
                continue
            mz_bin = int(round(mz))
            if mz_bin <= 0:
                continue
            bins[mz_bin] += float(inten)

    if not bins:
        return []

    base = max(bins.values())
    if base <= 0:
        return []

    cleaned = [(mzi, (inten / base) * 100.0) for mzi, inten in bins.items()]
    cleaned.sort(key=lambda x: x[0])  # sort by m/z
    return cleaned



def make_peaks_tensor(
    peaks: Sequence[Tuple[float, float]],
    *,
    sort_by_mz: bool = True,
    drop_below: float = 0.0,          # drop peaks with intensity <= this
    mz_min: Optional[float] = None,   # optional clip window
    mz_max: Optional[float] = None,
    normalize: Optional[str] = "sum", # "sum", "max", or None
    topk: Optional[int] = None,       # keep K most intense peaks
    dedup_ppm: Optional[float] = None,# merge peaks within ppm window
    device: Optional[torch.device] = None,
    dtype: torch.dtype = torch.float32,
    ) -> torch.Tensor:
    """
    Build a clean [N,2] tensor from a list of (m/z, intensity) pairs.
    """
    if len(peaks) == 0:
        return torch.zeros((0, 2), dtype=dtype, device=device)

    t = torch.tensor(peaks, dtype=dtype, device=device)  # [N,2]
    # sanitize
    mz = t[:, 0]
    I  = t[:, 1].clamp(min=0)          # no negative intensities
    if mz_min is not None or mz_max is not None:
        keep = torch.ones_like(I, dtype=torch.bool)
        if mz_min is not None: keep &= (mz >= mz_min)
        if mz_max is not None: keep &= (mz <  mz_max)
        mz, I = mz[keep], I[keep]
    if drop_below is not None and drop_below > 0:
        keep = I > drop_below
        mz, I = mz[keep], I[keep]
    if mz.numel() == 0:
        return torch.zeros((0, 2), dtype=dtype, device=device)

    # optional deduplication/merging within ppm window
    if dedup_ppm is not None and dedup_ppm > 0:
        # sort by m/z first
        order = torch.argsort(mz)
        mz, I = mz[order], I[order]
        merged_mz = []
        merged_I  = []
        cur_mz, cur_I = mz[0].item(), I[0].item()
        for j in range(1, mz.numel()):
            ppm = abs(mz[j].item() - cur_mz) / max(cur_mz, 1e-9) * 1e6
            if ppm <= dedup_ppm:
                # merge into current bin (intensity sum; centroid as I-weighted mean)
                total_I = cur_I + I[j].item()
                cur_mz  = (cur_mz * cur_I + mz[j].item() * I[j].item()) / max(total_I, 1e-12)
                cur_I   = total_I
            else:
                merged_mz.append(cur_mz)
                merged_I.append(cur_I)
                cur_mz, cur_I = mz[j].item(), I[j].item()
        merged_mz.append(cur_mz)
        merged_I.append(cur_I)
        mz = torch.tensor(merged_mz, dtype=dtype, device=device)
        I  = torch.tensor(merged_I,  dtype=dtype, device=device)

    # keep top-K by intensity (after dedup/clip)
    if topk is not None and topk > 0 and I.numel() > topk:
        top_idx = torch.topk(I, k=topk, largest=True).indices
        mz, I = mz[top_idx], I[top_idx]

    # final sort by m/z (recommended for downstream encoders)
    if sort_by_mz:
        order = torch.argsort(mz)
        mz, I = mz[order], I[order]

    # normalize intensities
    if normalize == "sum" and I.sum() > 0:
        I = I / I.sum()
    elif normalize == "max" and I.max() > 0:
        I = I / I.max()

    return torch.stack([mz, I], dim=1)  # [N,2]


def pack_peaks_list(
    spectra: Iterable[Sequence[Tuple[float, float]]],
    **kwargs
) -> List[torch.Tensor]:
    """
    Build a List[Tensor[N_i,2]] suitable for SpectraDataset(peaks_list=...).
    kwargs are passed to make_peaks_tensor (e.g., normalize="sum", dedup_ppm=5, topk=200).
    """
    return [make_peaks_tensor(peaks, **kwargs) for peaks in spectra]
