from __future__ import annotations
import torch
from torch import Tensor
import torch.nn.functional as F

def cosine_loss(pred: Tensor, target: Tensor) -> Tensor:
    pred = F.normalize(pred, dim=-1)
    target = F.normalize(target, dim=-1)
    return 1.0 - (pred * target).sum(dim=-1).mean()

def spectral_losses(pred_bins, true_bins, pred_frags, true_frags_batch, catalog_mz, ppm_merge=5.0):
    """
    pred_frags: Tensor[B, K] logits over fragment catalog
    true_frags_batch: List[...] raw fragment masses per sample (variable length)
    catalog_mz: Tensor[K] (sorted)
    """

    mse = F.mse_loss(pred_bins, true_bins)
    cos = cosine_loss(pred_bins, true_bins)

    true_mask = build_true_mask(true_frags_batch, catalog_mz, ppm_merge=ppm_merge)
    bce = F.binary_cross_entropy_with_logits(pred_frags, true_mask)
    return mse + cos + 0.5 * bce

#def spectral_losses(
#    pred_bins: Tensor, true_bins: Tensor,
#    pred_frags: Tensor | None, true_frag_mask: Tensor | None
#    ) -> Tensor:
#    """
#    Combined regression (bins) + optional fragment BCE.
#    """
#    mse = F.mse_loss(pred_bins, true_bins)
#    cos = cosine_loss(pred_bins, true_bins)
#    if pred_frags is not None and true_frag_mask is not None:
#        bce = F.binary_cross_entropy_with_logits(pred_frags, true_frag_mask.float())
#        return mse + cos + 0.5 * bce
#    return mse + cos

def spectral_similarity(pred_bins: Tensor, true_bins: Tensor) -> Tensor:
    """
    Cosine similarity in [0,1]
    """
    pred_n = F.normalize(pred_bins, dim=-1)
    true_n = F.normalize(true_bins, dim=-1)
    return (pred_n * true_n).sum(dim=-1)

@torch.no_grad()
def build_true_mask(true_frags_batch, catalog_mz: torch.Tensor, ppm_merge: float = 5.0) -> torch.Tensor:
    """
    true_frags_batch: List[Tensor[Fi]] or List[List[float]] of fragment masses per sample
    catalog_mz: Tensor[K], sorted ascending
    returns: Tensor[B, K] with 1.0 where catalog entries are present in the target
    """
    device = catalog_mz.device
    K = catalog_mz.numel()
    B = len(true_frags_batch)
    mask = torch.zeros((B, K), dtype=torch.float32, device=device)

    # For fast windowing, keep catalog on device and use searchsorted
    for b, frags in enumerate(true_frags_batch):
        if frags is None:
            continue
        frags = torch.as_tensor(frags, dtype=torch.float64, device=device).view(-1)
        if frags.numel() == 0:
            continue

        # ppm window per fragment → [Fi, 1]
        tol = (ppm_merge * 1e-6) * frags
        left  = torch.searchsorted(catalog_mz, (frags - tol))
        right = torch.searchsorted(catalog_mz, (frags + tol), right=True)

        # Pick the nearest within [left, right) if any
        for i in range(frags.numel()):
            l = int(left[i].item())
            r = int(right[i].item())
            if l >= r:  # no candidate in window
                continue
            # find nearest index in catalog segment
            seg = catalog_mz[l:r]
            diffs = (seg - frags[i]).abs()
            j = int(torch.argmin(diffs).item())
            k = l + j
            mask[b, k] = 1.0

    return mask
