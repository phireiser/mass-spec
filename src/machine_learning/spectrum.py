"""Spectrum-domain helper functions shared across training and retrieval."""

from typing import List

import torch

import mod


def make_parent_mass_mask_vec(precursor_mass: float, mz_min: float, mz_max: float, bin_width: float, device=None) -> torch.Tensor:
    """Build a [bins] mask that allows peaks below the precursor mass."""
    bins = int((mz_max - mz_min) / bin_width)
    if precursor_mass <= 0:
        return torch.ones(bins, dtype=torch.float32, device=device)
    mask = torch.ones(bins, dtype=torch.float32, device=device)
    for i in range(bins):
        mz = mz_min + i * bin_width
        if mz >= precursor_mass:
            mask[i] = 0.0
    return mask


def make_parent_mass_mask_batch(smiles_list: List[str], mz_min: float, mz_max: float, bin_width: float, device=None) -> torch.Tensor:
    """Build a [B, bins] hard mask using exact mass from SMILES for each sample."""
    masks = []
    for smi in smiles_list:
        try:
            m = float(mod.Graph.fromSMILES(smi).exactMass)
        except Exception:
            m = mz_max
        masks.append(make_parent_mass_mask_vec(m, mz_min, mz_max, bin_width, device=device))
    return torch.stack(masks, dim=0)


__all__ = ["make_parent_mass_mask_vec", "make_parent_mass_mask_batch"]
