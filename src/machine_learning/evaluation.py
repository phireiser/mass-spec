"""Evaluation and plotting helpers for the machine-learning pipeline."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from torch_geometric.data import Data as GeometricData

from src.machine_learning.retrieval import infer_mol_to_spec, infer_spec_to_mol
from src.machine_learning.spectrum import make_parent_mass_mask_vec
from src.project_paths import shared_path

# Where plot demos land by default. Resolved via shared_path so it points at
# outputs/plots both locally and inside the /app container bind. Callers
# (e.g. main.py) may override with an explicit out_dir.
DEFAULT_PLOTS_DIR = shared_path("PLOTS_DIR_REL")


def _resolve_plots_dir(out_dir: Optional[Path]) -> Path:
    out_dir = Path(out_dir) if out_dir is not None else DEFAULT_PLOTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


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
                          top_k: int = 10,
                          frag_deriv_tree=None) -> Dict[str, Any]:
    """Predict spectrum and compare to ground truth."""
    spec_hat = infer_mol_to_spec(graph_feat, enc_mol, frag_set_enc, dec_spec, heads,
                                 smiles=smiles, mz_min=mz_min, mz_max=(mz_max if mz_max is not None else mz_min + true_spec.numel()*bin_width), bin_width=bin_width,
                                 frag_deriv_tree=frag_deriv_tree)
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


def mass_controlled_retrieval_metrics(
    index, loader, device, enc_spec, enc_mol, heads, mass_by_smiles,
    mz_min, mz_max, bin_width, topk_list=(1, 5, 10, 20), windows=(5.0,), max_batches=None,
):
    """Mass-controlled spectrum->molecule retrieval scorecard.

    The learned encoder retrieval ``cos(z_spec, z_mol)`` is reported *next to*
    mass-only baselines and against random chance inside a mass window, so a result
    only counts as "learned chemistry" if it beats mass. This exists because the
    forward-collapse audit showed the old headline MRR reduced entirely to
    parent-mass filtering; here mass is the bar, not an unmeasured confound.

    Methods (full gallery = the retrieval index, i.e. train+val):
      * ``learned``       -- cos(z_spec, z_mol) from the aligned encoders
      * ``mass_implied``  -- rank by |gallery_mass - precursor implied by the query
                             spectrum's top peak|  (honest, spectrum-only)
      * ``mass_true``     -- rank by |gallery_mass - query's true parent mass|  (oracle)
      * ``mask_cosine``   -- cos(normalized parent-mass mask, query)  (mass support only)
    Plus, per window W: learned retrieval restricted to molecules within +/-W Da of
    the query's true mass, vs analytic random chance (the decisive beyond-mass test).
    """
    enc_spec.eval(); enc_mol.eval(); heads.eval()
    N = len(index.items)
    gal_smiles = [it.smiles for it in index.items]
    gal_mass = torch.tensor([float(mass_by_smiles.get(s, mz_max)) for s in gal_smiles])
    bins = int((mz_max - mz_min) / bin_width)
    gal_mask_n = F.normalize(
        torch.stack([make_parent_mass_mask_vec(m.item(), mz_min, mz_max, bin_width) for m in gal_mass], 0),
        dim=-1,
    )
    smiles_to_gidx: Dict[str, int] = {}
    for j, s in enumerate(gal_smiles):
        smiles_to_gidx.setdefault(s, j)

    def implied_precursor(spec_i):
        nz = torch.nonzero(spec_i > 0).flatten()
        return mz_max if nz.numel() == 0 else mz_min + int(nz.max().item()) * bin_width

    def rank_of(order_gidx, tg):
        pos = np.nonzero(np.asarray(order_gidx) == tg)[0]
        return int(pos[0]) + 1 if pos.size else None

    ranks: Dict[str, List] = {m: [] for m in ("learned", "mass_implied", "mass_true", "mask_cosine")}
    win_rows = {W: [] for W in windows}  # (rank, poolsize, chance_mrr)
    n = 0
    with torch.no_grad():
        for bi, batch in enumerate(loader):
            if max_batches is not None and bi >= max_batches:
                break
            graph_feats, _fg, _fm, spec, smiles, _adj, _tf, _tb = batch
            spec = spec.to(device)
            _, z_bwd = heads(enc_spec(spec))
            z_q = F.normalize(z_bwd, dim=-1).cpu()
            for i in range(len(smiles)):
                tg = smiles_to_gidx.get(smiles[i])
                if tg is None:  # true molecule not in gallery (e.g. test split); skip
                    continue
                n += 1
                tm = gal_mass[tg].item()
                sims = index.embs @ z_q[i]
                ranks["learned"].append(rank_of(torch.argsort(sims, descending=True).numpy(), tg))
                pmz = implied_precursor(spec[i].cpu())
                ranks["mass_implied"].append(rank_of(torch.argsort(torch.abs(gal_mass - pmz)).numpy(), tg))
                ranks["mass_true"].append(rank_of(torch.argsort(torch.abs(gal_mass - tm)).numpy(), tg))
                mc = gal_mask_n @ F.normalize(spec[i].cpu(), dim=-1)
                ranks["mask_cosine"].append(rank_of(torch.argsort(mc, descending=True).numpy(), tg))
                for W in windows:
                    win = torch.nonzero(torch.abs(gal_mass - tm) <= W).flatten()
                    m = win.numel()
                    if m == 0:
                        continue
                    wsims = index.embs[win] @ z_q[i]
                    order = win[torch.argsort(wsims, descending=True)].numpy()
                    Hm = float(np.sum(1.0 / np.arange(1, m + 1)))
                    win_rows[W].append((rank_of(order, tg), m, Hm / m))

    def summ(rk):
        a = np.array([r for r in rk if r is not None])
        d = {f"R@{k}": float((a <= k).mean()) if a.size else 0.0 for k in topk_list}
        d["MRR"] = float((1.0 / a).mean()) if a.size else 0.0
        return d

    out: Dict[str, Any] = {"N": n}
    per = {m: summ(rk) for m, rk in ranks.items()}
    for m, d in per.items():
        for k, v in d.items():
            out[f"{m}/{k}"] = v
    out["delta_MRR_vs_mass_implied"] = per["learned"]["MRR"] - per["mass_implied"]["MRR"]
    out["delta_MRR_vs_mass_true"] = per["learned"]["MRR"] - per["mass_true"]["MRR"]

    print(f"== Mass-controlled retrieval (N={n}, gallery={N}) ==")
    hdr = "  ".join(f"R@{k}" for k in topk_list)
    print(f"{'method':>13s} |  {hdr}  |   MRR")
    for m in ("learned", "mass_implied", "mass_true", "mask_cosine"):
        row = "  ".join(f"{per[m][f'R@{k}']:.3f}" for k in topk_list)
        print(f"{m:>13s} |  {row}  | {per[m]['MRR']:.4f}")
    print(f"  delta MRR (learned - mass_implied) = {out['delta_MRR_vs_mass_implied']:+.4f}  "
          f"(learned - mass_true) = {out['delta_MRR_vs_mass_true']:+.4f}")
    for W in windows:
        rows = win_rows[W]
        a = np.array([r for (r, _m, _c) in rows if r is not None])
        pools = np.array([m for (_r, m, _c) in rows]) if rows else np.array([0])
        lm = float((1.0 / a).mean()) if a.size else 0.0
        cm = float(np.mean([c for (_r, _m, c) in rows])) if rows else 0.0
        out[f"window{W}/learned_MRR"] = lm
        out[f"window{W}/chance_MRR"] = cm
        out[f"window{W}/delta_MRR"] = lm - cm
        out[f"window{W}/mean_pool"] = float(pools.mean())
        print(f"  mass-window +/-{W} Da: learned MRR={lm:.4f} vs chance={cm:.4f} "
              f"(delta {lm - cm:+.4f}, mean pool={pools.mean():.1f})")
    return out


def demo_noise_robustness(index, loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1, 5, 10), max_batches=5, out_dir=None):
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
            plt.savefig(_resolve_plots_dir(out_dir) / "noise_robustness.png", dpi=150)
        except Exception:
            pass
        plt.clf()
    return results


def demo_visualize_reconstructions(
    graph_feats, true_spec, smiles,
    enc_mol, frag_set_enc, dec_spec, heads, n_samples=3, deriv_trees=None, out_dir=None
    ) -> bool:
    """Plot true vs reconstructed spectra for n_samples molecules."""
    plots_dir = _resolve_plots_dir(out_dir)
    n = min(n_samples, len(smiles))
    for i in range(n):
        tree_i = deriv_trees[i] if deriv_trees is not None else None
        spec_hat = infer_mol_to_spec(graph_feats[i], enc_mol, frag_set_enc, dec_spec, heads,
                                     frag_deriv_tree=tree_i)
        plt.figure()
        plt.plot(true_spec[i].cpu().numpy(), label="true")
        plt.plot(spec_hat.cpu().numpy(), label="pred")
        plt.title(f"Recon: {smiles[i]}")
        plt.legend()
        plt.tight_layout()
        try:
            plt.savefig(plots_dir / f"recon_{i}.png", dpi=150)
        except Exception:
            pass
        plt.close()
    return True


__all__ = [
    "vec_to_peaks",
    "demo_compare_spectrum",
    "demo_retrieval_metrics",
    "mass_controlled_retrieval_metrics",
    "demo_noise_robustness",
    "demo_visualize_reconstructions",
]
