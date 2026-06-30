"""Evaluation and plotting helpers for the machine-learning pipeline."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from torch_geometric.data import Data as GeometricData

from src.machine_learning.retrieval import infer_mol_to_spec, infer_spec_to_mol

_script_path = Path(__file__).resolve()
OUT_DIR = next((p for p in _script_path.parents if p.name == "mol"), _script_path.parent) / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def vec_to_peaks(vec: torch.Tensor, mz_min: float, bin_width: float, top_k: int = 10) -> List[Tuple[float, float]]:
    """Convert a binned spectrum vector into top-K (m/z, intensity) peaks."""
    v = vec.detach().cpu().numpy()
    top_idx = np.argsort(-v)[:max(1, min(top_k, v.shape[0]))]
    peaks = [(mz_min + int(i) * bin_width, float(v[i])) for i in top_idx]
    peaks.sort(key=lambda x: x[0])
    return peaks


def demo_compare_spectrum(graph_feat: GeometricData,
                          true_spec: torch.Tensor,
                          enc_mol,
                          frag_set_enc,
                          dec_spec,
                          heads,
                          mz_min: float,
                          bin_width: float,
                          smiles: Optional[str] = None,
                          mz_max: Optional[float] = None,
                          top_k: int = 10) -> Dict[str, Any]:
    """Predict spectrum and compare to ground truth."""
    spec_hat = infer_mol_to_spec(graph_feat, enc_mol, frag_set_enc, dec_spec, heads,
                                 smiles=smiles, mz_min=mz_min, mz_max=(mz_max if mz_max is not None else mz_min + true_spec.numel()*bin_width), bin_width=bin_width)
    true_spec = true_spec.detach().cpu()
    cos = F.cosine_similarity(F.normalize(spec_hat, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
    l1 = torch.mean(torch.abs(spec_hat - true_spec)).item()

    pred_peaks = vec_to_peaks(spec_hat, mz_min, bin_width, top_k=top_k)
    true_peaks = vec_to_peaks(true_spec, mz_min, bin_width, top_k=top_k)

    print("Ground truth top peaks (m/z, intensity):")
    for mz, inten in true_peaks:
        print(f"  {mz:8.1f}, {inten:.4f}")
    print("Predicted   top peaks (m/z, intensity):")
    for mz, inten in pred_peaks:
        print(f"  {mz:8.1f}, {inten:.4f}")
    print(f"Cosine similarity: {cos:.4f} | L1 error: {l1:.4f}")

    return {"cosine": cos, "l1": l1, "true_peaks": true_peaks, "pred_peaks": pred_peaks}


def demo_retrieval_metrics(index, loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, topk_list=(1, 5, 10), max_batches=None, skip_reranking=True):
    """Compute Recall@K and MRR on a loader using a train-built index."""
    enc_spec.eval()
    hits = {k: 0 for k in topk_list}
    mrr = 0.0
    n = 0
    try:
        ds = loader.dataset
        mz_min = float(ds.mz_min)
        mz_max = float(ds.mz_max)
        bin_width = float(ds.bin_width)
    except Exception:
        mz_min, mz_max, bin_width = 1.0, 1000.0, 1.0
    with torch.no_grad():
        for bi, (graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, _, _) in enumerate(loader):
            if max_batches is not None and bi >= max_batches:
                break
            B = len(smiles)
            _ = enc_spec(spec.to(device))
            for i in range(B):
                ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec,
                                           mz_min=mz_min, mz_max=mz_max, bin_width=bin_width,
                                           topk=max(topk_list), skip_reranking=skip_reranking)
                preds = [s for s, _ in ranked]
                n += 1
                for k in topk_list:
                    if smiles[i] in preds[:k]:
                        hits[k] += 1
                rank = next((ri + 1 for ri, s in enumerate(preds) if s == smiles[i]), None)
                if rank is not None:
                    mrr += 1.0 / rank
    out = {f"R@{k}": (hits[k] / max(n, 1)) for k in topk_list}
    out["MRR"] = mrr / max(n, 1)
    out["N"] = n
    return out


def demo_noise_robustness(index, loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1, 5, 10), max_batches=5):
    """Add Gaussian noise to spectra and return Recall@K vs noise level."""
    results = {}
    try:
        ds = loader.dataset
        mz_min = float(ds.mz_min)
        mz_max = float(ds.mz_max)
        bin_width = float(ds.bin_width)
    except Exception:
        mz_min, mz_max, bin_width = 1.0, 1000.0, 1.0
    for s in noise_levels:
        hits = {k: 0 for k in topk_list}
        n = 0
        with torch.no_grad():
            for bi, (graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, _, _) in enumerate(loader):
                if bi >= max_batches:
                    break
                B = len(smiles)
                spec_noisy = spec + s * torch.randn_like(spec)
                spec_noisy = F.normalize(spec_noisy, dim=-1)
                for i in range(B):
                    ranked = infer_spec_to_mol(spec_noisy[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec,
                                               mz_min=mz_min, mz_max=mz_max, bin_width=bin_width,
                                               topk=max(topk_list))
                    preds = [p for p, _ in ranked]
                    n += 1
                    for k in topk_list:
                        if smiles[i] in preds[:k]:
                            hits[k] += 1
        results[s] = {f"R@{k}": hits[k] / max(n, 1) for k in topk_list}
        results[s]["N"] = n
    if plt is not None:
        for k in topk_list:
            xs = list(results.keys())
            ys = [results[s][f"R@{k}"] for s in xs]
            plt.plot(xs, ys, marker='o', label=f"R@{k}")
        plt.xlabel("Noise sigma")
        plt.ylabel("Recall@K")
        plt.title("Noise robustness (VAL subset)")
        plt.legend()
        plt.tight_layout()
        try:
            plt.savefig(OUT_DIR / "noise_robustness.png", dpi=150)
        except Exception:
            pass
        plt.clf()
    return results


def demo_visualize_reconstructions(
    graph_feats, true_spec, smiles,
    enc_mol, frag_set_enc, dec_spec, heads, n_samples=3
    ) -> bool:
    """Plot true vs reconstructed spectra for n_samples molecules."""
    n = min(n_samples, len(smiles))
    for i in range(n):
        spec_hat = infer_mol_to_spec(graph_feats[i], enc_mol, frag_set_enc, dec_spec, heads)
        plt.figure()
        plt.plot(true_spec[i].cpu().numpy(), label="true")
        plt.plot(spec_hat.cpu().numpy(), label="pred")
        plt.title(f"Recon: {smiles[i]}")
        plt.legend()
        plt.tight_layout()
        try:
            plt.savefig(OUT_DIR / f"recon_{i}.png", dpi=150)
        except Exception:
            pass
        plt.close()
    return True


__all__ = [
    "vec_to_peaks",
    "demo_compare_spectrum",
    "demo_retrieval_metrics",
    "demo_noise_robustness",
    "demo_visualize_reconstructions",
]
