"""
Minimal Fragment-Aided Bidirectional Model (Mini-FRAG)
======================================================

This script implements a lightweight prototype for bidirectional modeling
between molecular structures and mass spectra, aided by fragment-level
intermediates.  It is designed as a minimal, runnable baseline to test the
concept of fragment integration before connecting to a full MØD-based
graph-transformation pipeline.

Overview
--------
The model learns three related mappings:
    * Molecule -> Spectrum  (forward prediction)
    * Spectrum -> Molecule  (inverse retrieval)
    * Fragment prediction  (auxiliary interpretability task)

Key ideas:
    - Molecules are represented by graph-based embeddings.
    - Fragments are represented as binary "bag-of-fragments" vectors.
    - Spectra are represented as binned intensity vectors.
    - All three views share a latent embedding space (Mini-FRAG latent z).
    - Forward modeling predicts the spectrum from the latent + fragments.
    - Inverse modeling retrieves candidate molecules via latent similarity
      and fragment consistency, then re-ranks by forward-model reconstruction.

Components
----------
Encoders:
    EncMol   - Encodes molecular fingerprints into latent space.
    EncFrag  - Encodes fragment bags into latent space.
    EncSpec  - Encodes binned spectra into latent space.

Decoders:
    DecFrag  - Predicts fragment presence from latent vectors.
    DecSpec  - Predicts full spectra given latent vectors and fragment info.

Training phases:
    Phase A - Forward learning (molecule+fragment -> spectrum).
    Phase B - Latent alignment (spectrum latent <-> molecule latent) and
              contrastive training for inverse retrieval.

Retrieval:
    LatentIndex builds an embedding index of training molecules.
    Given a query spectrum, the model retrieves top-K molecules by cosine
    similarity and re-ranks them using fragment Jaccard and forward-model
    cosine similarity.

Dataset:
    ToyDataset provides random synthetic data for testing the pipeline
    without external files.  Replace this with a real dataset loader
    returning (ECFP, fragment vector, spectrum, SMILES).

Usage
-----
Example command line:
    $ python minimal_implement.py --epochs_fwd 3 --epochs_bwd 3 --latent 128

This will:
    1. Train the forward and fragment models (Phase A).
    2. Align spectrum embeddings with molecule embeddings (Phase B).
    3. Build a retrieval index over training molecules.
    4. Demonstrate molecule- >spectrum prediction and spectrum- >molecule retrieval.
    5. Save a checkpoint ``mini_frag_checkpoint.pt``.

Outputs:
    • Console logs with per-epoch losses.
    • Retrieval demo showing top-K candidate SMILES.
    • Saved model checkpoint for later reuse or fine-tuning.

Author:
    (c) 2025 Philipp Reiser / Mass-Spec Modeling project
"""

import argparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Callable, Tuple

import re
import hashlib
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split


import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from torch_geometric.nn import GCNConv
from torch_geometric.data import Data as GeometricData

import mod
from mass_spec_modeling.machine_learning import utils_mod
from mass_spec_modeling.mod_fragmentation import utils
from mass_spec_modeling.machine_learning.featurizers import GraphFeaturizerMOD




def smiles_ngram_fp(smiles: str, n_bits: int = 2048,
                    kmin: int = 1, kmax: int = 4,
                    replace_ring_digits: bool = True,
                    binary: bool = True) -> torch.Tensor:
    """
    RDKit-free, deterministic hashed n-gram fingerprint over SMILES chars.
    Produces a float32 vector of length n_bits (binary or counts).
    """
    s = smiles.strip()
    if replace_ring_digits:
        # SMILES ring indices (1..9, 10= %10 etc.) - > '#'
        s = re.sub(r"%\d{2}", "#", s)   # %10, %11 ...
        s = re.sub(r"\d", "#", s)       # 0-9

    shingles = []
    # simple char-level n-grams; you can swap to token-level later
    for k in range(kmin, kmax + 1):
        for i in range(0, max(0, len(s) - k + 1)):
            shingles.append(s[i:i+k])

    vec = np.zeros(n_bits, dtype=np.float32)
    for sh in shingles:
        h = hashlib.blake2b(sh.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(h, "little") % n_bits
        if binary:
            vec[idx] = 1.0
        else:
            vec[idx] += 1.0

    # optional norm (helps cosine loss)
    # vec /= (np.linalg.norm(vec) + 1e-8)
    return torch.from_numpy(vec)



# ---------------------------------------------------------------------------
# Helper: simple multilayer perceptron builder
# ---------------------------------------------------------------------------

def mlp(d_in, d_hidden, d_out):
    """
    Builds a small feed-forward MLP block.

    Parameters
    ----------
    d_in : int
        Input feature dimension.
    d_hidden : int
        Hidden layer dimension.
    d_out : int
        Output feature dimension.

    Returns
    -------
    torch.nn.Sequential
        A sequential model with Linear -> ReLU -> Linear layers.
    """
    return nn.Sequential(
        nn.Linear(d_in, d_hidden), nn.ReLU(),
        nn.Linear(d_hidden, d_out)
    )


# ---------------------------------------------------------------------------
# Encoder and decoder modules
# ---------------------------------------------------------------------------

class EncMol(nn.Module):
    """
    Encodes molecule graphs (MOD) into a latent vector using a GNN.
    """
    def __init__(self, d_latent=128):
        super().__init__()
        from torch_geometric.nn import GCNConv, global_mean_pool
        self.gnn1 = GCNConv(3, 64)
        self.gnn2 = GCNConv(64, d_latent)
        self.global_mean_pool = global_mean_pool

    def forward(self, batch_graphs):
        from torch_geometric.data import Batch
        batch = Batch.from_data_list(batch_graphs)
        x = batch.x.float()
        edge_index = batch.edge_index
        x1 = F.relu(self.gnn1(x, edge_index))
        x2 = self.gnn2(x1, edge_index)
        pooled = self.global_mean_pool(x2, batch.batch)
        return pooled



# --- GNN-based fragment encoder ---
class EncFrag(nn.Module):
    """
    Encodes a bag-of-fragments vector into a latent embedding using a GNN.
    """
    def __init__(self, F, d_latent=128):
        super().__init__()
        if GCNConv is None:
            raise ImportError("torch_geometric is required for GNN fragment encoder.")
        self.F = F
        self.d_latent = d_latent
        self.gnn1 = GCNConv(1, 32)
        self.gnn2 = GCNConv(32, d_latent)

    def forward(self, bag):
        """
        Parameters
        ----------
        bag : torch.Tensor
            Binary or count-based fragment vector [N, F].

        Returns
        -------
        torch.Tensor
            Latent representation [N, d_latent].
        """
        # bag: [N, F] -> process each sample as a graph
        outs = []
        for i in range(bag.size(0)):
            x = bag[i].unsqueeze(-1)  # [F, 1]
            # For demonstration, use identity matrix as edge_index (no real edges)
            edge_index = torch.arange(self.F).unsqueeze(0).repeat(2, 1)
            # If you have a fragment co-occurrence graph, replace edge_index accordingly
            x1 = F.relu(self.gnn1(x, edge_index))
            x2 = self.gnn2(x1, edge_index)
            # Pool: mean over fragments
            out = x2.mean(dim=0)
            outs.append(out)
        return torch.stack(outs, 0)


class EncSpec(nn.Module):
    """
    Encodes a binned mass spectrum  into latent space.
    """
    def __init__(self, B,  d_latent=128):
        super().__init__()
        self.net = mlp(B , 512, d_latent)

    def forward(self, spec):
        """
        Parameters
        ----------
        spec : torch.Tensor
            Spectrum intensity vector [N, B].

        Returns
        -------
        torch.Tensor
            Latent representation [N, d_latent].
        """
        return self.net(spec.float())


class DecFrag(nn.Module):
    """
    Decodes latent embeddings back into fragment presence probabilities.
    """
    def __init__(self, d_latent, F):
        super().__init__()
        self.net = mlp(d_latent, 128, F)

    def forward(self, z):
        """
        Parameters
        ----------
        z : torch.Tensor
            Latent embedding [N, d_latent] or [d_latent].

        Returns
        -------
        torch.Tensor
            Predicted fragment probabilities [N, F] or [F], range (0,1).
        """
        if z.dim() == 1:
            z = z.unsqueeze(0)
        return torch.sigmoid(self.net(z))


class DecSpec(nn.Module):
    """
    Decodes latent embeddings and fragment information into a predicted spectrum.
    """
    def __init__(self, d_latent, F, B):
        super().__init__()
        self.net = mlp(d_latent + F, 512, B)

    def forward(self, z, frag):
        """
        Parameters
        ----------
        z : torch.Tensor
            Latent embedding [N, d_latent].
        frag : torch.Tensor
            Fragment vector [N, F].

        Returns
        -------
        torch.Tensor
            Predicted intensity vector [N, B], non-negative values.
        """
        x = torch.cat([z, frag], -1)
        return F.relu(self.net(x))


# ---------------------------------------------------------------------------
# Loss and similarity utilities
# ---------------------------------------------------------------------------

def cosine_loss(x, y):
    """
    Computes 1 - mean cosine similarity between two tensors.

    Parameters
    ----------
    x, y : torch.Tensor
        Input tensors of identical shape.

    Returns
    -------
    torch.Tensor
        Scalar loss value.
    """
    x_n = F.normalize(x, dim=-1)
    y_n = F.normalize(y, dim=-1)
    return 1.0 - (x_n * y_n).sum(dim=-1).mean()


def info_nce(z_q, z_k, T=0.07):
    """
    InfoNCE contrastive loss between query and key embeddings.

    Parameters
    ----------
    z_q, z_k : torch.Tensor
        Query and key embeddings of shape [N, d].
    T : float
        Temperature scaling factor.

    Returns
    -------
    torch.Tensor
        Scalar contrastive loss.
    """
    z_q = F.normalize(z_q, dim=-1)
    z_k = F.normalize(z_k, dim=-1)
    logits = z_q @ z_k.T / T
    labels = torch.arange(z_q.size(0), device=z_q.device)
    return F.cross_entropy(logits, labels)


def jaccard_binary(a, b, eps=1e-6):
    """
    Computes Jaccard similarity between two binary fragment vectors.

    Parameters
    ----------
    a, b : torch.Tensor
        Binary fragment presence vectors [N, F].
    eps : float
        Numerical stability constant.

    Returns
    -------
    torch.Tensor
        Jaccard similarity score(s).
    """
    inter = (a * b).sum(dim=-1)
    union = (a + b - a * b).sum(dim=-1) + eps
    return inter / union


@dataclass
class Sample:
    """Container for one dataset sample."""
    graph_feat: object  # torch_geometric.data.Data
    frag_bag: torch.Tensor
    spec: torch.Tensor
    smiles: str


# ---------------------------------------------------------------------------
# RealDataset + helpers
# ---------------------------------------------------------------------------

# ---------- Fragment vocab ----------
def build_fragment_vocab(
    fragments_per_mol: List[List[str]],
    top_k: Optional[int] = None
) -> Dict[str, int]:
    """Build a {fragment_smiles -> id} mapping. If top_k is set, keep the most frequent K."""
    ctr = Counter()
    for frags in fragments_per_mol:
        ctr.update(set(frags))  # presence, not counts, for vocab
    items = ctr.most_common(top_k) if top_k is not None else ctr.items()
    return {frag: i for i, (frag, _) in enumerate(items)}

def frag_bag_from_list(
    frag_list: List[str],
    frag_to_id: Dict[str, int],
    Fdim: int
) -> torch.Tensor:
    bag = torch.zeros(Fdim, dtype=torch.float32)
    for f in frag_list:
        idx = frag_to_id.get(f)
        if idx is not None:
            bag[idx] = 1.0
    return bag

# ---------- Spectrum binning ----------
def compute_bin_index(mz: float, mz_min: float, mz_max: float, bin_width: float) -> Optional[int]:
    if (mz < mz_min) or (mz >= mz_max):
        return None
    return int((mz - mz_min) / bin_width)

def bin_spectrum(
    peaks: List[Tuple[float, float]],
    mz_min: float,
    mz_max: float,
    bin_width: float,
    sqrt_and_l2: bool = True
) -> torch.Tensor:
    """
    Bin (mz, intensity) peaks into a fixed-length vector.
    B = number of bins = floor((mz_max - mz_min) / bin_width)
    """
    B = int((mz_max - mz_min) / bin_width)
    vec = torch.zeros(B, dtype=torch.float32)
    for mz, inten in peaks:
        bi = compute_bin_index(mz, mz_min, mz_max, bin_width)
        if bi is not None and 0 <= bi < B:
            vec[bi] += float(inten)
    if sqrt_and_l2:
        vec = torch.sqrt(vec.clamp_min(0))
        norm = vec.norm(p=2)
        if norm > 0:
            vec = vec / norm
    return vec

# ---------- RealDataset ----------
class RealDataset(Dataset):
    """
    Minimal dataset that returns (ECFP-2048, fragment-bag, binned spectrum, smiles)
    compatible with the earlier Mini-FRAG pipeline.
    """
    def __init__(
        self,
        smiles_list: List[str],
        fragments_per_mol: List[List[str]],
        spectra_per_mol: List[List[Tuple[float, float]]],
        *,
        mz_min: float = 0.0,
        mz_max: float = 1000.0,
        bin_width: float = 0.1,
        # Fragment vocabulary handling:
        frag_to_id: Optional[Dict[str, int]] = None,
        top_k_frag: Optional[int] = None,   # if frag_to_id is None, keep most frequent K fragments
        # Pre-build for speed (optional):
        precompute: bool = True,
    ):
        assert len(smiles_list) == len(fragments_per_mol) == len(spectra_per_mol), \
            "Input lists must have the same length."
        self.smiles_list = smiles_list
        self.fragments_per_mol = fragments_per_mol
        self.spectra_per_mol = spectra_per_mol

        self.mz_min = float(mz_min)
        self.mz_max = float(mz_max)
        self.bin_width = float(bin_width)
        self.B = int((self.mz_max - self.mz_min) / self.bin_width)  # spectrum length

        # Build/keep fragment vocab
        if frag_to_id is None:
            self.frag_to_id = build_fragment_vocab(fragments_per_mol, top_k=top_k_frag)
        else:
            self.frag_to_id = frag_to_id
        self.Fdim = len(self.frag_to_id)

        self.graph_featurizer = GraphFeaturizerMOD()

        self._cache = None
        if precompute:
            self._precompute_all()

    def __len__(self) -> int:
        return len(self.smiles_list)

    def __getitem__(self, idx: int):
        if self._cache is not None:
            graph_feat, frag_bag, spec_vec = self._cache[idx]
        else:
            mol = mod.smiles(self.smiles_list[idx])
            graph_feat = self.graph_featurizer(mol)
            frag_bag = self._make_frag_bag(idx)
            spec_vec = self._make_spec(idx)

        return Sample(
            graph_feat=graph_feat,  # ecfp now holds graph_feat
            frag_bag=frag_bag,
            spec=spec_vec,
            smiles=self.smiles_list[idx],
        )

    def _make_frag_bag(self, idx: int) -> torch.Tensor:
        return frag_bag_from_list(self.fragments_per_mol[idx], self.frag_to_id, self.Fdim)

    def _make_spec(self, idx: int) -> torch.Tensor:
        return bin_spectrum(self.spectra_per_mol[idx], self.mz_min, self.mz_max, self.bin_width)

    def _precompute_all(self):
        """Materialize tensors to speed up training."""
        graph_feats = []
        bags = []
        specs = []
        for i in range(len(self)):
            mol = mod.smiles(self.smiles_list[i])
            graph_feats.append(self.graph_featurizer(mol))
            bags.append(self._make_frag_bag(i))
            specs.append(self._make_spec(i))
        self._cache = list(zip(graph_feats, bags, specs))
# --- end RealDataset ----------------------------------------------------------



def collate(batch: List[Sample]):
    """
    Collate function for DataLoader batching.

    Returns
    -------
    Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[str]]
        Batched ECFP, fragments, spectra, and SMILES strings.
    """
    graph_feats = [b.graph_feat for b in batch]
    frag = torch.stack([b.frag_bag for b in batch], 0)
    spec = torch.stack([b.spec for b in batch], 0)
    smiles = [b.smiles for b in batch]
    return graph_feats, frag, spec, smiles


# ---------------------------------------------------------------------------
# Training loops
# ---------------------------------------------------------------------------

def train_epoch_phase_a(loader, device, enc_mol, enc_frag, dec_frag, dec_spec,
                        opt, alpha=1.0, beta=0.1):
    """
    Phase A: trains molecule + fragment - > spectrum reconstruction.

    Parameters
    ----------
    loader : DataLoader
        Training data loader.
    device : torch.device
        Target device (CPU/GPU).
    enc_mol, enc_frag, dec_frag, dec_spec : nn.Module
        Model components.
    opt : torch.optim.Optimizer
        Optimizer instance.
    alpha, beta : float
        Weighting for cosine and MSE losses.

    Returns
    -------
    float
        Average epoch loss.
    """
    enc_mol.train(); enc_frag.train(); dec_frag.train(); dec_spec.train()
    total = 0.0
    for graph_feats, frag_bag, spec, _ in loader:
        frag_bag, spec = frag_bag.to(device), spec.to(device)
        opt.zero_grad()
        z_m = enc_mol(graph_feats)
        z_f = enc_frag(frag_bag)
        z = (z_m + z_f) / 2
        p_frag = dec_frag(z)
        spec_hat = dec_spec(z, frag_bag)
        loss = alpha * cosine_loss(spec_hat, spec) + beta * F.mse_loss(spec_hat, spec) \
               + F.binary_cross_entropy(p_frag, frag_bag)
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


def train_epoch_phase_b(loader, device, enc_spec, enc_mol, dec_frag, dec_spec,
                        opt, alpha=1.0, beta=0.1, lam=0.1, tau=0.5):
    """
    Phase B: trains spectrum latent alignment and inverse consistency.

    Adds contrastive (InfoNCE) loss between molecule and spectrum
    latents to enable spectrum- >molecule retrieval.

    Returns
    -------
    float
        Average epoch loss.
    """
    enc_spec.train(); enc_mol.train(); dec_frag.train(); dec_spec.train()
    total = 0.0
    for graph_feats, frag_bag, spec, _ in loader:
        frag_bag, spec = frag_bag.to(device), spec.to(device)
        opt.zero_grad()
        z_m = enc_mol(graph_feats)
        z_s = enc_spec(spec)
        l_con = info_nce(z_s, z_m)
        p_frag = dec_frag(z_s)
        spec_hat = dec_spec(z_s, (p_frag > tau).float())
        loss = alpha * cosine_loss(spec_hat, spec) + beta * F.mse_loss(spec_hat, spec) \
               + F.binary_cross_entropy(p_frag, frag_bag) + lam * l_con
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


# ---------------------------------------------------------------------------
# Retrieval and inference helpers
# ---------------------------------------------------------------------------

@dataclass
class IndexItem:
    """Entry in the molecule latent index."""
    z: torch.Tensor
    smiles: str
    frag_bag: torch.Tensor
    graph_feat: torch.Tensor


class LatentIndex:
    """
    Simple in-memory cosine-similarity index for molecule retrieval.
    """
    def __init__(self, d):
        self.d = d
        self.embs: List[torch.Tensor] = []
        self.items: List[IndexItem] = []

    def build(self, dataset: Dataset, device, enc_mol: EncMol):
        """
        Encodes all molecules in a dataset and stores normalized latents.
        """
        self.embs.clear(); self.items.clear()
        enc_mol.eval()
        loader = DataLoader(dataset, batch_size=256, shuffle=False, collate_fn=collate)
        with torch.no_grad():
            for graph_feats, frag_bag, spec, smiles in loader:
                z = enc_mol(graph_feats)
                z = F.normalize(z, dim=-1).cpu()
                for i in range(z.size(0)):
                    self.embs.append(z[i])
                    self.items.append(IndexItem(
                        z=z[i],
                        smiles=smiles[i],
                        frag_bag=frag_bag[i].clone(),
                        graph_feat=None
                    ))
        self.embs = torch.stack(self.embs, 0)

    def topk(self, z_query: torch.Tensor, k=10) -> List[IndexItem]:
        """
        Retrieves the top-k most similar molecules by cosine similarity.
        """
        sims = (self.embs @ z_query)
        topv, topi = torch.topk(sims, k=min(k, sims.numel()))
        return [self.items[i] for i in topi.tolist()]


def rerank_candidates(spec_q, z_q, candidates, device,
                      enc_spec, dec_spec, dec_frag, w_cos=0.6, w_jacc=0.4, tau=0.5):
    """
    Reranks retrieved molecules using forward-model cosine similarity
    and fragment Jaccard agreement.

    Returns
    -------
    List[Tuple[str, float]]
        Candidate SMILES strings and composite scores.
    """
    enc_spec.eval(); dec_spec.eval(); dec_frag.eval()
    with torch.no_grad():
        frag_pred = dec_frag(z_q.to(device)).sigmoid().cpu()
        frag_pred_bin = (frag_pred > tau).float()
        scores = []
        for it in candidates:
            z_c = it.z.to(device)
            spec_hat = dec_spec(z_c.unsqueeze(0), it.frag_bag.unsqueeze(0).to(device)).cpu().squeeze(0)
            cos = F.cosine_similarity(
                F.normalize(spec_hat, dim=-1).unsqueeze(0),
                F.normalize(spec_q.cpu(), dim=-1).unsqueeze(0),
                dim=-1
            ).item()
            jacc = jaccard_binary(frag_pred_bin.unsqueeze(0), it.frag_bag.unsqueeze(0)).item()
            score = w_cos * cos + w_jacc * jacc
            scores.append((it.smiles, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


def infer_mol_to_spec(graph_feat, frag_bag, device, enc_mol, enc_frag, dec_spec, dec_frag):
    """
    Predicts a mass spectrum and fragment probabilities from a given molecule.

    Returns
    -------
    spec_hat : torch.Tensor
        Predicted intensity vector [B].
    frag_pred : torch.Tensor
        Predicted fragment probabilities [F].
    """
    enc_mol.eval(); enc_frag.eval(); dec_spec.eval(); dec_frag.eval()
    with torch.no_grad():
        z_m = enc_mol([graph_feat])
        z_f = enc_frag(frag_bag.to(device).unsqueeze(0))
        z = (z_m + z_f) / 2
        spec_hat = dec_spec(z, frag_bag.to(device).unsqueeze(0)).cpu().squeeze(0)
        frag_pred = dec_frag(z).cpu().squeeze(0)
    return spec_hat, frag_pred


def infer_spec_to_mol(spec, index, device, enc_spec, dec_spec, dec_frag, topk=10):
    """
    Retrieves likely molecular structures from a given mass spectrum.

    Returns
    -------
    List[Tuple[str, float]]
        Top-K candidate SMILES strings and composite scores.
    """
    enc_spec.eval()
    with torch.no_grad():
        z_q = enc_spec(spec.to(device).unsqueeze(0)).squeeze(0)
        z_q_n = F.normalize(z_q, dim=-1).cpu()
    cands = index.topk(z_q_n, k=topk)
    ranked = rerank_candidates(spec, z_q, cands, device, enc_spec, dec_spec, dec_frag)
    return ranked


def main():
    """
    Entry point for training and demonstrating the Mini-FRAG model.

    Steps
    -----
    1. Build dataset.
    2. Train forward & fragment models (Phase A).
    3. Train spectrum alignment (Phase B).
    4. Build latent retrieval index.
    5. Demonstrate molecule- >spectrum and spectrum- >molecule examples.
    6. Save model checkpoint.
    """
    p = argparse.ArgumentParser()
    p.add_argument("--epochs_fwd", type=int, default=10, help="Phase A epochs (mol+frag -> spec)")
    p.add_argument("--epochs_bwd", type=int, default=10, help="Phase B epochs (align spec latent)")
    p.add_argument("--batch", type=int, default=128)
    p.add_argument("--latent", type=int, default=128)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    torch.manual_seed(args.seed)
    device = torch.device(args.device)

    # Load Data into mem
    MOL_DEF_PATH = Path("/home/mescalin/reiserp/Nextcloud/studium/computationalScience/thesis/mol/" \
            + "mass_spec_modeling/exec_scripts/ms_data/compounds.csv")
    LOAD_PATH = Path("/home/mescalin/reiserp/Nextcloud/studium/computationalScience/thesis/mol/dump/")

    mols_definitions = utils_mod.read_mols_csv(MOL_DEF_PATH)
    mol_list: List[str] = []
    fragments_per_mol: List[List[str]] = []
    real_spectra_per_mol: List[List[Tuple[float, float]]] = []

    for name, smi in mols_definitions:
        mol_list.append(smi)
        mol = mod.smiles(smi, name=name)
        fwd_dg, _rule_db = utils.load_derivation_graph(name, path=LOAD_PATH / "fwd")
        bwd_dg, _rule_db = utils.load_derivation_graph(name, path=LOAD_PATH / "bwd")

        fwd_smis = []
        for graph_term in fwd_dg.graphDatabase: # when loading DG len(createdGraphs)=0
            graph = utils.graph_from_term(graph_term)
            if graph.isMolecule:
                fwd_smis.append(graph.smiles)


        bwd_smis = []
        for graph_term in bwd_dg.graphDatabase: # when loading DG len(createdGraphs)=0
            graph = utils.graph_from_term(graph_term)
            if graph.isMolecule:
                bwd_smis.append(graph.smiles)

        fragments_per_mol.append(fwd_smis + bwd_smis)

        real_spectra = utils.get_spectra_from_local_jdx(name)
        real_spectra_per_mol.append(real_spectra)


    train_mols, test_mols, \
    train_frags,  test_frags,  \
    train_specs,  test_specs   = train_test_split(
        mol_list,
        fragments_per_mol,
        real_spectra_per_mol,
        test_size=0.2,      # 20% test
        random_state=42,    # reproducible
        shuffle=False
    )

    # Build dataset
    train_ds = RealDataset(
        train_mols, train_frags, train_specs,
        mz_min=0.0, mz_max=1000.0, bin_width=0.25,
        precompute=True
        )

    test_ds = RealDataset(
        test_mols, test_frags, test_specs,
        mz_min=0.0, mz_max=1000.0, bin_width=0.25,
        frag_to_id=train_ds.frag_to_id,
        precompute=True
        )

    # Use dataset to configure the model:
    fragment_vocab_size = train_ds.Fdim
    spectrum_bins_size = train_ds.B


    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=False, drop_last=False, collate_fn=collate)
    val_loader   = DataLoader(test_ds, batch_size=args.batch, shuffle=False, collate_fn=collate)

    # Models
    enc_mol  = EncMol(args.latent).to(device)
    enc_frag = EncFrag(fragment_vocab_size, args.latent).to(device)
    enc_spec = EncSpec(spectrum_bins_size, args.latent).to(device)
    dec_frag = DecFrag(args.latent, fragment_vocab_size).to(device)
    dec_spec = DecSpec(args.latent, fragment_vocab_size, spectrum_bins_size).to(device)

    # Optimizers (separate per phase keeps it simple)
    opt_a = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(enc_frag.parameters()) +
                             list(dec_frag.parameters()) +
                             list(dec_spec.parameters()), lr=args.lr)
    opt_b = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(enc_spec.parameters()) +
                             list(dec_frag.parameters()) +
                             list(dec_spec.parameters()), lr=args.lr)

    # ----------------- Phase A -----------------
    print("== Phase A: train forward & fragments ==")
    for epoch in range(1, args.epochs_fwd + 1):
        loss = train_epoch_phase_a(train_loader, device, enc_mol, enc_frag, dec_frag, dec_spec, opt_a)
        print(f"[A] epoch {epoch:02d} loss {loss:.4f}")

    # ----------------- Phase B -----------------
    print("== Phase B: align spec latent + spectrum-anchored recon ==")
    for epoch in range(1, args.epochs_bwd + 1):
        loss = train_epoch_phase_b(train_loader, device, enc_spec, enc_mol, dec_frag, dec_spec, opt_b)
        print(f"[B] epoch {epoch:02d} loss {loss:.4f}")

    # ----------------- Build retrieval index -----------------
    print("== Building retrieval index on TRAIN set ==")
    index = LatentIndex(d=args.latent)
    index.build(train_ds, device, enc_mol)


    # ----------------- Demo: Structure - > Spectrum -----------------
    print("== Demo: Mol - > Spec on a VAL sample ==")
    graph_feats, frag_bag, spec, smiles = next(iter(val_loader))
    i = 0
    spec_hat, frag_pred = infer_mol_to_spec(graph_feats[i], frag_bag[i], device, enc_mol, enc_frag, dec_spec, dec_frag)
    cos_sim = F.cosine_similarity(
        F.normalize(spec_hat, dim=-1).unsqueeze(0),
        F.normalize(spec[i], dim=-1).unsqueeze(0),
        dim=-1
    ).item()
    print(f"Mol- >Spec for {smiles[i]} | cosine={cos_sim:.3f} | frag_pred_mean={frag_pred.mean().item():.3f}")


    # ----------------- Demo: Spectrum - > Structure -----------------
    print("== Demo: Spec -> Mol retrieval + re-ranking on the same VAL sample ==")
    ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, dec_spec, dec_frag, topk=10)
    print("Top-5 candidates:")
    print(f"{'SMILES':>40s} | {'Score':>8s}")
    print("-" * 50)
    for s, sc in ranked[:5]:
        print(f"{s:>40s} | {sc:8.3f}")

    # save checkpoint
    ckpt = {
        "enc_mol": enc_mol.state_dict(),
        "enc_frag": enc_frag.state_dict(),
        "enc_spec": enc_spec.state_dict(),
        "dec_frag": dec_frag.state_dict(),
        "dec_spec": dec_spec.state_dict(),
        "args": vars(args),
    }
    torch.save(ckpt, "mini_frag_checkpoint.pt")
    print("Saved checkpoint to mini_frag_checkpoint.pt")

if __name__ == "__main__":
    main()
