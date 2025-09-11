from __future__ import annotations
from typing import List, Optional, Sequence, Tuple
import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader
import torch.nn.functional as F

from .models.backward import BackwardPredictorBins

# --- RDKit fingerprint util ---
def ecfp_bits_from_smiles(smiles: str, fp_dim: int = 2048, radius: int = 2) -> Tensor:
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
    except Exception as e:
        raise ImportError("RDKit is required for backward supervised pretrain.") from e
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    bitvect = AllChem.GetMorganFingerprintAsBitVect(mol, radius=radius, nBits=fp_dim)
    arr = torch.zeros(fp_dim, dtype=torch.float32)
    onbits = list(bitvect.GetOnBits())
    if onbits:
        arr[torch.tensor(onbits, dtype=torch.long)] = 1.0
    return arr

def build_fp_targets_from_graphs(mol_graphs: List, fp_dim: int = 2048, radius: int = 2) -> List[Tensor]:
    fps = []
    for g in mol_graphs:
        smi = getattr(g, "smiles", None)
        if smi is None:
            raise ValueError("PyG Data object missing .smiles; set it in your featurizer.")
        fps.append(ecfp_bits_from_smiles(smi, fp_dim=fp_dim, radius=radius))
    return fps

# --- Trainer ---
def train_backward_supervised(
    dataset,                      # SpectraDataset (uses dataset[i]["binned"])
    mol_graphs: List,             # aligned to dataset order; each has .smiles
    *,
    fp_dim: int = 2048,
    radius: int = 2,
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    epochs: int = 10,
    batch_size: int = 32,
    device: str = "cuda",
):
    # Build fingerprint targets once
    fp_targets = build_fp_targets_from_graphs(mol_graphs, fp_dim=fp_dim, radius=radius)
    assert len(fp_targets) == len(dataset)

    # Pack tensors for fast indexing
    binned_list = [ex["binned"] for ex in dataset]
    X = torch.stack(binned_list)           # [N, n_bins]
    Y = torch.stack(fp_targets)            # [N, fp_dim]

    n_bins = X.size(1)
    model = BackwardPredictorBins(n_bins=n_bins, fp_dim=fp_dim).to(device)

    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    # Simple tensor-dataset loader
    N = X.size(0)
    idxs = torch.arange(N)

    def bce_logits(logits, targets):
        return F.binary_cross_entropy_with_logits(logits, targets)

    for epoch in range(1, epochs+1):
        model.train()
        perm = torch.randperm(N)
        total = 0.0
        for i in range(0, N, batch_size):
            batch_idx = perm[i:i+batch_size]
            xb = X[batch_idx].to(device)
            yb = Y[batch_idx].to(device)

            logits = model(xb)
            loss = bce_logits(logits, yb)

            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()

            total += float(loss.item())

        avg = total / max(1, (N + batch_size - 1) // batch_size)
        # optional: precision@k metrics could be added here
        print(f"[BACKWARD-SUP] epoch={epoch:03d} loss_bce={avg:.4f}")

    return model
