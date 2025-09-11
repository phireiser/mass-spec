"""trainer supervised"""
from __future__ import annotations
from typing import Optional
import torch
from torch import nn
from torch import Tensor
import torch.nn.functional as F
from torch_geometric.loader import DataLoader as PyGDataLoader
from torch_geometric.data import Data

from .config import FullConfig
from .models import ForwardPredictor
from .models import BackwardPredictorBins
from .losses import spectral_losses
from .utils_mod import build_fragment_catalog, peaks_to_mask_batch


def train_forward_supervised(
    dataset,
    node_dim: int,
    edge_dim: int,
    cfg: Optional[FullConfig] = None,
):
    if cfg is None:
        cfg = FullConfig()

    device = torch.device(
        cfg.train.device if torch.cuda.is_available() and cfg.train.device == "cuda" else "cpu"
    )

    # External label stores (stay in Python lists)
    binned = [torch.as_tensor(ex["binned"], dtype=torch.float32) for ex in dataset]  # [N, n_bins]
    peaks  = [ex["peaks"] for ex in dataset]  # list of [(mz, inten), ...] per sample

    # Build fragment catalog once from all peaks (or load from cfg)
    if getattr(cfg.model, "fragment_catalog_mz", None) is not None:
        catalog_mz = cfg.model.fragment_catalog_mz.to(dtype=torch.float32)
    else:
        all_frag_lists = [[float(mz) for mz, _inten in ex["peaks"]] for ex in dataset]
        catalog_mz = build_fragment_catalog(all_frag_lists, ppm_merge=getattr(cfg.model, "ppm_merge", 5.0))
        cfg.model.fragment_catalog_mz = catalog_mz
    K = int(catalog_mz.numel())

    # Prepare Data list; store only an index to re-align labels later
    data_list = []
    for i, ex in enumerate(dataset):
        d = ex["graph"]                     # this is a PyG Data
        d.sample_idx = torch.tensor(i)      # <- keep sample index as tensor
        data_list.append(d)

    pyg_loader = PyGDataLoader(
        data_list,
        batch_size=cfg.train.batch_size,
        shuffle=True,
    )

    model = ForwardPredictor(
        node_dim=node_dim,
        edge_dim=edge_dim,
        d_model=cfg.model.d_model,
        n_layers=cfg.model.gnn_layers,
        n_bins=cfg.data.n_bins,
        frag_catalog_size=K,
        dropout=cfg.model.dropout,
    ).to(device)

    opt = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.train.lr,
        weight_decay=cfg.train.weight_decay
    )

    ppm_merge = getattr(cfg.model, "ppm_merge", 5.0)
    catalog_mz = catalog_mz.to(device)

    for epoch in range(1, cfg.train.epochs + 1):
        model.train()
        total = 0.0

        for pyg_batch in pyg_loader:
            pyg_batch = pyg_batch.to(device)

            # Re-align labels using indices from the batch
            idxs = pyg_batch.sample_idx.detach().cpu().tolist()
            true_bins = torch.stack([binned[i] for i in idxs], dim=0).to(device)  # [B, n_bins]
            peaks_batch = [peaks[i] for i in idxs]                                 # list length B

            # Build catalog-wide mask [B, K] from raw peaks
            true_mask = peaks_to_mask_batch(peaks_batch, catalog_mz, ppm_merge=ppm_merge)  # [B, K]

            # Forward + loss
            pred_bins, pred_frags = model(pyg_batch)  # pred_frags: [B, K]
            loss = spectral_losses(pred_bins, true_bins, pred_frags, true_mask, catalog_mz)

            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), cfg.train.grad_clip)
            opt.step()

            total += float(loss.item())

        print(f"[FWD-SUP] epoch={epoch} loss={total / max(1, len(pyg_loader)):.4f}")

    return model


def normalize_feature_dims(graphs):

    bad = [i for i, g in enumerate(graphs) if not isinstance(g, Data)]
    if bad:
        raise TypeError(f"'graphs' must be List[Data]; bad indices: {bad}")

    # find target dims
    node_dim = max(g.x.size(1) for g in graphs)
    edge_dim = max((g.edge_attr.size(1) if hasattr(g, "edge_attr") and g.edge_attr is not None else 0)
                   for g in graphs)

    for g in graphs:
        # nodes
        if g.x.dtype != torch.float32:
            g.x = g.x.float()
        if g.x.size(1) < node_dim:
            pad = torch.zeros(g.x.size(0), node_dim - g.x.size(1), dtype=g.x.dtype, device=g.x.device)
            g.x = torch.cat([g.x, pad], dim=1)

        # edges
        if not hasattr(g, "edge_attr") or g.edge_attr is None:
            g.edge_attr = torch.zeros(g.edge_index.size(1), max(1, edge_dim), dtype=torch.float32)
        else:
            if g.edge_attr.dtype != torch.float32:
                g.edge_attr = g.edge_attr.float()
            if g.edge_attr.ndim == 1:
                g.edge_attr = g.edge_attr.view(-1, 1)
            if g.edge_attr.size(1) < edge_dim:
                pad = torch.zeros(g.edge_attr.size(0), edge_dim - g.edge_attr.size(1),
                                  dtype=g.edge_attr.dtype, device=g.edge_attr.device)
                g.edge_attr = torch.cat([g.edge_attr, pad], dim=1)

    # if no graph had edge_attr, we gave them a single zero feature
    if edge_dim == 0:
        edge_dim = 1
    return node_dim, edge_dim



def train_backward_supervised(
    dataset,                          # SpectraDataset (uses ex["binned"], ex["peaks"])
    *,
    catalog_mz: Optional[Tensor] = None,     # if None we build from peaks
    ppm_merge: float = 5.0,                  # for catalog build
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    epochs: int = 10,
    batch_size: int = 32,
    device: str = "cuda",
    dropout: float = 0.1,
):
    """
    Backward supervised: predict fragment catalog multi-labels from binned spectra.
    Returns (model, catalog_mz) so you can reuse the same catalog at inference.
    """
    # Prepare X (binned) and raw peaks for label construction
    binned_list = [torch.as_tensor(ex["binned"], dtype=torch.float32) for ex in dataset]
    peaks_list  = [ex["peaks"] for ex in dataset]  # list of [N_i,2] tensors

    X = torch.stack(binned_list, dim=0)  # [N, n_bins]
    N, n_bins = X.size(0), X.size(1)

    # Build or reuse catalog
    if catalog_mz is None:
        all_frag_lists = [[float(mz) for mz, _inten in ex["peaks"]] for ex in dataset]
        catalog_mz = build_fragment_catalog(all_frag_lists, ppm_merge=ppm_merge)
    catalog_mz = catalog_mz.to(torch.float32).to(device)
    K = int(catalog_mz.numel())
    if K == 0:
        raise ValueError("Empty fragment catalog: cannot train backward predictor.")

    # Build labels once: [N,K]
    Y = peaks_to_mask_batch(peaks_list, catalog_mz, ppm_merge=ppm_merge)  # on device
    # Move X to device lazily per batch (saves memory)
    model = BackwardPredictorBins(n_bins=n_bins, out_dim=K, d=1024, dropout=dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    def bce_logits(logits, targets):
        return F.binary_cross_entropy_with_logits(logits, targets)

    # Training
    for epoch in range(1, epochs + 1):
        model.train()
        perm = torch.randperm(N)
        total = 0.0
        for i in range(0, N, batch_size):
            idx = perm[i:i+batch_size]
            xb = X[idx].to(device)     # [B, n_bins]
            yb = Y[idx]                # already on device [B, K]

            logits = model(xb)         # [B, K]
            loss = bce_logits(logits, yb)

            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()

            total += float(loss.item())

        avg = total / max(1, (N + batch_size - 1) // batch_size)
        print(f"[BWD-SUP] epoch={epoch:03d} loss_bce={avg:.4f}")

    return model, catalog_mz
