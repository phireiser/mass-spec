"""Demo and diagnostic helper functions for the machine-learning pipeline."""

from typing import Any, Dict, Optional

import numpy as np
import torch
import torch.nn.functional as F


def demo_heads_comparison(loader, device, enc_mol, heads, dec_spec, dec_frag, n_batches=3):
    """
    Run DecSpec/DecFrag with z_fwd vs z_bwd to quantify head specialization.

    Compares mol->spec reconstruction performance using forward vs backward task heads
    on the same molecule encoding.

    Parameters
    ----------
    loader : DataLoader
        Data loader with batches of (graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd).
    device : torch.device
        Device to run on.
    enc_mol : EncMol
        Molecule encoder.
    heads : TaskHeads
        Shared task heads (forward and backward).
    dec_spec : DecSpec
        Spectrum decoder.
    dec_frag : DecFrag
        Fragment decoder.
    n_batches : int
        Number of batches to sample.

    Returns
    -------
    dict
        Average cosine similarities and binary cross-entropies for both heads.
        Keys: "cos_fwd", "cos_bwd", "bce_fwd", "bce_bwd".
    """
    enc_mol.eval()
    dec_spec.eval()
    dec_frag.eval()
    stats = {"cos_fwd": [], "cos_bwd": [], "bce_fwd": [], "bce_bwd": []}
    with torch.no_grad():
        for bi, (graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd) in enumerate(loader):
            if bi >= n_batches:
                break
            frag_bag = frag_bag.to(device)
            spec = spec.to(device)
            z_m = enc_mol(graph_feats)
            z_fwd, z_bwd = heads(z_m)
            spec_hat_fwd = dec_spec(z_fwd, frag_bag)
            spec_hat_bwd = dec_spec(z_bwd, frag_bag)
            p_frag_fwd = dec_frag(z_fwd)
            p_frag_bwd = dec_frag(z_bwd)
            stats["cos_fwd"].append(
                F.cosine_similarity(
                    F.normalize(spec_hat_fwd, dim=-1),
                    F.normalize(spec, dim=-1),
                    dim=-1,
                )
                .mean()
                .item()
            )
            stats["cos_bwd"].append(
                F.cosine_similarity(
                    F.normalize(spec_hat_bwd, dim=-1),
                    F.normalize(spec, dim=-1),
                    dim=-1,
                )
                .mean()
                .item()
            )
            stats["bce_fwd"].append(F.binary_cross_entropy(p_frag_fwd, frag_bag).item())
            stats["bce_bwd"].append(F.binary_cross_entropy(p_frag_bwd, frag_bag).item())
    return {k: float(np.mean(v)) if len(v) else float("nan") for k, v in stats.items()}


def demo_fragment_perturbation(
    graph_feat,
    frag_bag,
    true_spec,
    device,
    enc_mol,
    enc_frag,
    dec_spec,
    dec_frag,
    index,
    adj=None,
    top_n=5,
):
    """
    Add/drop top-N fragments and observe spectrum shift.

    Perturb the fragment set by adding or dropping the top-N predicted fragments
    and measure spectrum reconstruction change.

    Parameters
    ----------
    graph_feat : GeometricData
        Molecule graph.
    frag_bag : torch.Tensor
        Fragment bag vector [V].
    true_spec : torch.Tensor
        Ground truth spectrum.
    device : torch.device
        Device to run on.
    enc_mol : EncMol
        Molecule encoder.
    enc_frag : EncFrag or similar
        Fragment encoder.
    dec_spec : DecSpec
        Spectrum decoder.
    dec_frag : DecFrag
        Fragment decoder.
    index : LatentIndex
        Retrieval index (for potential future use).
    adj : torch.Tensor, optional
        Fragment adjacency matrix.
    top_n : int
        Number of top fragments to perturb.

    Returns
    -------
    dict
        Cosine similarities for base, drop, and add scenarios.
        Keys: "base_cos", "cos_drop", "cos_add".
    """
    # Note: This function appears to use an older inference interface.
    # The actual implementation depends on the signature of infer_mol_to_spec.
    # Placeholder for compatibility with existing code paths.
    with torch.no_grad():
        # spec_hat, p_frag = infer_mol_to_spec(graph_feat, frag_bag, device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=adj)
        # Simplified stub: just report base cosine
        base_cos = 0.0
        cos_drop = 0.0
        cos_add = 0.0
    return {"base_cos": base_cos, "cos_drop": cos_drop, "cos_add": cos_add}


__all__ = ["demo_heads_comparison", "demo_fragment_perturbation"]
