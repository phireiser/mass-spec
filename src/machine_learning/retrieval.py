"""Latent retrieval, reranking, and inference helpers."""

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch_geometric.data import Data as GeometricData
import faiss
import mod

from src.machine_learning.data import collate_vlex
from src.machine_learning.models import EncMol, EncSpec, DecSpecLatent, TaskHeads
from src.machine_learning.spectrum import make_parent_mass_mask_vec


@dataclass
class IndexItem:
    """Entry in the molecule latent index."""

    z: torch.Tensor
    smiles: str
    graph_feat: GeometricData
    true_spectrum: torch.Tensor
    score: Optional[float] = None
    frag_graphs: Optional[List[GeometricData]] = None
    frag_adj_local: Optional[torch.Tensor] = None
    frag_deriv_tree_fwd: Optional[GeometricData] = None
    frag_deriv_tree_bwd: Optional[GeometricData] = None
    frag_bag: Optional[torch.Tensor] = None
    fragment_adjacency_fwd: Optional[torch.Tensor] = None
    fragment_adjacency_bwd: Optional[torch.Tensor] = None


class LatentIndex:
    """Simple in-memory cosine-similarity index for molecule retrieval."""

    def __init__(self, d):
        self.d = d
        self.embs: List[torch.Tensor] = []
        self.items: List[IndexItem] = []

    def build(self, dataset: Dataset, device, enc_mol: EncMol):
        self.embs.clear()
        self.items.clear()
        enc_mol.eval()
        loader = DataLoader(dataset, batch_size=256, shuffle=False, collate_fn=collate_vlex)
        with torch.no_grad():
            for batch_data in loader:
                if len(batch_data) == 8:
                    graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, deriv_trees_fwd, deriv_trees_bwd = batch_data
                else:
                    graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local = batch_data
                    deriv_trees_fwd = [None] * len(smiles)
                    deriv_trees_bwd = [None] * len(smiles)

                z = enc_mol(graph_feats)
                z = F.normalize(z, dim=-1).cpu()
                B = z.size(0)
                for i in range(B):
                    self.embs.append(z[i])
                    self.items.append(IndexItem(
                        z=z[i],
                        smiles=smiles[i],
                        graph_feat=graph_feats[i],
                        frag_graphs=frag_graphs[i],
                        frag_adj_local=(adj_local[i].cpu() if isinstance(adj_local[i], torch.Tensor) else None),
                        frag_deriv_tree_fwd=(deriv_trees_fwd[i] if deriv_trees_fwd[i] is not None else None),
                        frag_deriv_tree_bwd=(deriv_trees_bwd[i] if deriv_trees_bwd[i] is not None else None),
                        true_spectrum=spec[i].cpu(),
                    ))
        self.embs = torch.stack(self.embs, 0)

    def topk(self, z_query: torch.Tensor, k=10) -> List[IndexItem]:
        sims = (self.embs @ z_query)
        topv, topi = torch.topk(sims, k=min(k, sims.numel()))
        ranked: List[IndexItem] = []
        for j, i in enumerate(topi.tolist()):
            it = self.items[i]
            it.score = float(topv[j].item())
            ranked.append(it)
        return ranked


class FaissLatentIndex(LatentIndex):
    """FAISS-backed cosine similarity index for large-scale retrieval."""

    def __init__(self, d):
        super().__init__(d)
        self.index = faiss.IndexFlatIP(d)

    def build(self, dataset: Dataset, device, enc_mol: EncMol):
        self.embs.clear()
        self.items.clear()
        enc_mol.eval()
        loader = DataLoader(dataset, batch_size=256, shuffle=False, collate_fn=collate_vlex)
        vecs = []
        with torch.no_grad():
            for batch_data in loader:
                if len(batch_data) == 8:
                    graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, deriv_trees_fwd, deriv_trees_bwd = batch_data
                else:
                    graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local = batch_data
                    deriv_trees_fwd = [None] * len(smiles)
                    deriv_trees_bwd = [None] * len(smiles)

                z = enc_mol(graph_feats)
                z = F.normalize(z, dim=-1).cpu()
                B = z.size(0)
                for i in range(B):
                    self.items.append(IndexItem(
                        z=z[i],
                        smiles=smiles[i],
                        graph_feat=graph_feats[i],
                        frag_graphs=frag_graphs[i],
                        frag_adj_local=(adj_local[i].cpu() if isinstance(adj_local[i], torch.Tensor) else None),
                        frag_deriv_tree_fwd=(deriv_trees_fwd[i] if deriv_trees_fwd[i] is not None else None),
                        frag_deriv_tree_bwd=(deriv_trees_bwd[i] if deriv_trees_bwd[i] is not None else None),
                        true_spectrum=spec[i].cpu(),
                    ))
                    vecs.append(z[i].numpy())
        self.embs = torch.stack([torch.from_numpy(v) for v in vecs], 0) if vecs else torch.zeros((0, self.d), dtype=torch.float32)
        self.index = faiss.IndexFlatIP(self.d)
        if len(vecs) > 0:
            self.index.add(np.asarray(vecs, dtype="float32"))

    def topk(self, z_query: torch.Tensor, k=10) -> List[IndexItem]:
        zq = z_query.detach().cpu().numpy().astype("float32").reshape(1, -1)
        scores, idxs = self.index.search(zq, k=min(k, len(self.items)))
        ranked: List[IndexItem] = []
        for score, idx in zip(scores[0], idxs[0]):
            it = self.items[int(idx)]
            it.score = float(score)
            ranked.append(it)
        return ranked


def rerank_candidates(spec_q: torch.Tensor,
                      candidates: List[IndexItem],
                      device,
                      enc_mol: EncMol,
                      frag_set_enc: Any,
                      heads: TaskHeads,
                      dec_spec: DecSpecLatent,
                      mz_min: float,
                      mz_max: float,
                      bin_width: float) -> List[Tuple[str, float]]:
    enc_mol.eval(); frag_set_enc.eval(); dec_spec.eval(); heads.eval()
    scores: List[Tuple[str, float]] = []

    with torch.no_grad():
        spec_q_n = F.normalize(spec_q.cpu(), dim=-1)
        for it in candidates:
            z_m_c = enc_mol([it.graph_feat.to(device) if hasattr(it.graph_feat, 'to') else it.graph_feat]).squeeze(0)
            trees_c = [it.frag_deriv_tree_fwd]
            z_f_c = frag_set_enc(deriv_tree_batch=trees_c)
            z_c = (z_m_c.unsqueeze(0) + z_f_c) / 2
            z_fwd, _ = heads(z_c)
            spec_hat = dec_spec(z_fwd).cpu().squeeze(0)
            try:
                pmass = float(mod.Graph.fromSMILES(it.smiles).exactMass)
            except Exception:
                pmass = mz_max
            mask = make_parent_mass_mask_vec(pmass, mz_min, mz_max, bin_width, device=spec_hat.device)
            spec_hat = spec_hat * mask
            cos = F.cosine_similarity(F.normalize(spec_hat, dim=-1).unsqueeze(0), spec_q_n.unsqueeze(0), dim=-1).item()
            scores.append((it.smiles, cos))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def infer_mol_to_spec(graph_feat: GeometricData,
                      enc_mol: EncMol,
                      frag_set_enc: Any,
                      dec_spec: DecSpecLatent,
                      heads: TaskHeads,
                      smiles: Optional[str] = None,
                      mz_min: Optional[float] = None,
                      mz_max: Optional[float] = None,
                      bin_width: Optional[float] = None,
                      frag_deriv_tree: Optional[GeometricData] = None):

    enc_mol.eval(); frag_set_enc.eval(); dec_spec.eval(); heads.eval()

    with torch.no_grad():
        z_m = enc_mol([graph_feat])
        z_f = frag_set_enc(deriv_tree_batch=[frag_deriv_tree])
        z = (z_m + z_f) / 2
        z_fwd, _ = heads(z)
        spec_hat = dec_spec(z_fwd).cpu().squeeze(0)
        if (smiles is not None) and (mz_min is not None) and (mz_max is not None) and (bin_width is not None):
            try:
                pmass = float(mod.Graph.fromSMILES(smiles).exactMass)
            except Exception:
                pmass = mz_max
            mask = make_parent_mass_mask_vec(pmass, mz_min, mz_max, bin_width, device=spec_hat.device)
            spec_hat = spec_hat * mask
    return spec_hat


def infer_spec_to_mol(spec: torch.Tensor,
                      index: LatentIndex,
                      device,
                      enc_spec: EncSpec,
                      enc_mol: EncMol,
                      frag_set_enc: Any,
                      heads: TaskHeads,
                      dec_spec: DecSpecLatent,
                      mz_min: float,
                      mz_max: float,
                      bin_width: float,
                      topk: int = 10,
                      skip_reranking: bool = False) -> List[Tuple[str, float]]:
    enc_spec.eval(); heads.eval()
    with torch.no_grad():
        z_s = enc_spec(spec.to(device).unsqueeze(0))
        _, z_bwd = heads(z_s)
        z_q_n = F.normalize(z_bwd.squeeze(0), dim=-1).cpu()
    cands = index.topk(z_q_n, k=topk)
    if skip_reranking:
        return [(it.smiles, it.score) for it in cands]
    ranked = rerank_candidates(spec, cands, device, enc_mol, frag_set_enc, heads, dec_spec, mz_min, mz_max, bin_width)
    return ranked


__all__ = ["IndexItem", "LatentIndex", "FaissLatentIndex", "rerank_candidates", "infer_mol_to_spec", "infer_spec_to_mol"]
