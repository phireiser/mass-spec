from __future__ import annotations
from typing import List, Any, Optional
import torch
from torch import Tensor
from torch.utils.data import Dataset

def bin_spectrum(
    peaks: Tensor,  # shape [N, 2] as (mz, intensity)
    n_bins: int,
    mz_min: float,
    mz_max: float,
    intensity_norm: str = "sum",
) -> Tensor:
    """
    Bin spectrum into a fixed-length vector of size n_bins.
    peaks[:,0]=m/z, peaks[:,1]=intensity
    """
    device = peaks.device
    bins = torch.zeros(n_bins, device=device)
    if peaks.numel() == 0:
        return bins

    mz = peaks[:, 0].clamp(mz_min, mz_max - 1e-9)
    intens = peaks[:, 1].clamp(min=0.0)

    bin_width = (mz_max - mz_min) / n_bins
    idx = torch.floor((mz - mz_min) / bin_width).long()
    idx = torch.clamp(idx, 0, n_bins - 1)

    # scatter-add intensities
    bins.index_add_(0, idx, intens)

    if intensity_norm == "sum" and bins.sum() > 0:
        bins = bins / bins.sum()
    elif intensity_norm == "max" and bins.max() > 0:
        bins = bins / bins.max()
    return bins

def match_peaks_ppm(
    pred_mz: Tensor, true_mz: Tensor, ppm_tol: float
) -> Tensor:
    """
    Return boolean match mask (pred_mz matched to any true_mz within ppm).
    """
    if pred_mz.numel() == 0 or true_mz.numel() == 0:
        return torch.zeros(pred_mz.shape[0], dtype=torch.bool, device=pred_mz.device)
    # Compute |pred-true| / true * 1e6 <= ppm_tol
    pred_exp = pred_mz.unsqueeze(1)            # [P,1]
    true_exp = true_mz.unsqueeze(0)            # [1,T]
    ppm = (pred_exp - true_exp).abs() / true_exp.clamp(min=1e-9) * 1e6
    return (ppm <= ppm_tol).any(dim=1)

class SpectraDataset(Dataset):
    """
    Minimal paired dataset:
      - mol_graphs: list of PyG Data objects (atom/bond features)
      - peaks_list: list of tensors [N_i, 2] with (mz, intensity)
      - frag_catalog_mask: optional multi-hot over fragment catalog [K]
    """
    def __init__(
        self,
        mol_graphs: List[Any],
        peaks_list: List[Tensor],
        n_bins: int,
        mz_min: float,
        mz_max: float,
        intensity_norm: str = "sum",
        frag_catalog_masks: Optional[List[Tensor]] = None,
    ):
        assert len(mol_graphs) == len(peaks_list)
        if frag_catalog_masks is not None:
            assert len(frag_catalog_masks) == len(mol_graphs)
        self.mol_graphs = mol_graphs
        self.peaks_list = peaks_list
        self.n_bins = n_bins
        self.mz_min = mz_min
        self.mz_max = mz_max
        self.intensity_norm = intensity_norm
        self.frag_catalog_masks = frag_catalog_masks

    def __len__(self):
        return len(self.mol_graphs)

    def __getitem__(self, idx: int):
        g = self.mol_graphs[idx]
        peaks = self.peaks_list[idx]
        binned = bin_spectrum(peaks, self.n_bins, self.mz_min, self.mz_max, self.intensity_norm)
        out = {
            "graph": g,
            "peaks": peaks,
            "binned": binned,
        }
        if self.frag_catalog_masks is not None:
            out["frag_mask"] = self.frag_catalog_masks[idx]
        return out
