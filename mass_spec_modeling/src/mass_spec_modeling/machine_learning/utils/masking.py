from typing import List, Tuple
import torch


def frags_to_mask(frag_masses: torch.Tensor, catalog: torch.Tensor, ppm_tol: float = 10.0) -> torch.Tensor:
    """
    Map fragment masses to a binary mask over the catalog within ppm tolerance.
    """
    if len(frag_masses) == 0 or len(catalog) == 0:
        return torch.zeros(len(catalog), dtype=torch.float32)
    fm = frag_masses.view(-1, 1)
    cm = catalog.view(1, -1)
    ppm = (fm - cm).abs() / cm.clamp(min=1e-6) * 1e6
    hits = (ppm <= ppm_tol).any(dim=0)
    return hits.float()


def frags_to_soft_mask(
    frag_mz_int: torch.Tensor,
    catalog: torch.Tensor,
    ppm_tol: float = 10.0,
    p: float = 1.0,
) -> torch.Tensor:
    """
    Intensity-weighted matching of fragments to catalog bins.
    Returns [K] in [0,1], normalized. `p` controls sharpness (1 linear, 2 quadratic).
    """
    if frag_mz_int.numel() == 0 or len(catalog) == 0:
        return torch.zeros(len(catalog), dtype=torch.float32)
    fm = frag_mz_int[:, 0].view(-1, 1)
    fi = frag_mz_int[:, 1].view(-1, 1)
    cm = catalog.view(1, -1)
    ppm = (fm - cm).abs() / cm.clamp(min=1e-6) * 1e6
    w = (ppm <= ppm_tol).float() * (fi ** p)
    v = w.sum(dim=0)
    if v.sum() > 0:
        v = v / v.sum()
    return v.to(torch.float32)


@torch.no_grad()
def peaks_to_mask_batch(
    peaks_batch: List,
    catalog_mz: torch.Tensor,
    ppm_merge: float = 5.0,
) -> torch.Tensor:
    """
    Convert a batch of peak lists/tensors to a mask over the catalog bins.

    peaks_batch: List of per-sample peaks. Each item can be:
      - List[Tuple[mz, inten]]  (preferred)
      - List[mz]                (mz only)
      - Tensor[F, 2]            (mz,inten)
      - Tensor[F] or Tensor[F,1](mz only)
      - None or empty
    catalog_mz: Tensor[K] (sorted, on any device/dtype)
    returns: Tensor[B, K] float mask on same device as catalog_mz
    """
    device = catalog_mz.device
    K = int(catalog_mz.numel())
    B = len(peaks_batch)
    mask = torch.zeros((B, K), dtype=torch.float32, device=device)

    cat_dtype = catalog_mz.dtype

    def is_empty(x) -> bool:
        if x is None:
            return True
        if isinstance(x, (list, tuple)):
            return len(x) == 0
        if torch.is_tensor(x):
            return x.numel() == 0
        return False

    for b, pairs in enumerate(peaks_batch):
        if is_empty(pairs):
            continue

        if isinstance(pairs, (list, tuple)):
            if len(pairs) > 0 and isinstance(pairs[0], (list, tuple)) and len(pairs[0]) >= 1:
                mzs = [float(p[0]) for p in pairs]
            else:
                mzs = [float(p) for p in pairs]
            frags = torch.tensor(mzs, dtype=cat_dtype, device=device)
        elif torch.is_tensor(pairs):
            t = pairs.to(device)
            if t.ndim == 1:
                frags = t.to(dtype=cat_dtype)
            elif t.ndim == 2:
                frags = t[:, 0].to(dtype=cat_dtype)
            else:
                continue
        else:
            continue

        if frags.numel() == 0:
            continue

        frags = frags.contiguous()
        tol = (ppm_merge * 1e-6) * frags
        left = torch.searchsorted(catalog_mz, frags - tol)
        right = torch.searchsorted(catalog_mz, frags + tol, right=True)

        for i in range(frags.numel()):
            l = int(left[i])
            r = int(right[i])
            if l >= r:
                continue
            seg = catalog_mz[l:r]
            k = l + int(torch.argmin((seg - frags[i]).abs()))
            mask[b, k] = 1.0

    return mask
