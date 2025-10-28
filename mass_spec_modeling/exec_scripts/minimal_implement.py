"""
Fragment-Aided Bidirectional Model
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
    - All three views share a latent embedding space.
    - Forward modeling predicts the spectrum from the latent + fragments.
    - Inverse modeling retrieves candidate molecules via latent similarity
      and fragment consistency, then re-ranks by forward-model reconstruction.

Components
----------
Encoders:
    EncMol   - Encodes molecules into latent space.
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

Usage
-----
Example command line:
    $ python minimal_implement.py --epochs_fwd 3 --epochs_bwd 3 --latent 128

This will:
    1. Train the forward and fragment models (Phase A).
    2. Train spectrum embeddings with molecule embeddings (Phase B).
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
from typing import List, Optional, Dict, Callable, Tuple, Union, Any

import re
import hashlib
from collections import Counter
from pathlib import Path
import numpy as np
import random


import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt


from torch_geometric.nn import GCNConv
from torch_geometric.data import Data as GeometricData

import mod
from mass_spec_modeling.machine_learning import utils_mod
from mass_spec_modeling.mod_fragmentation import utils
from mass_spec_modeling.machine_learning.featurizers import GraphFeaturizerMOD


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
    def __init__(self, fragment_vocab_size, d_latent=128):
        super().__init__()
        if GCNConv is None:
            raise ImportError("torch_geometric is required for GNN fragment encoder.")
        self.fragment_vocab_size = fragment_vocab_size
        self.d_latent = d_latent
        self.gnn1 = GCNConv(1, 32)
        self.gnn2 = GCNConv(32, d_latent)

    def forward(self, bag: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        bag: Binary or count-based fragment vector [N, fragment_vocab_size].
        Returns Latent representation [N, d_latent].
        """
        # bag: [N, fragment_vocab_size] -> process each sample as a graph
        outs = []
        for i in range(bag.size(0)):
            x = bag[i].unsqueeze(-1)  # [fragment_vocab_size, 1]
            # fragment_vocab_sizeor demonstration, use identity matrix as edge_index (no real edges)
            edge_index = torch.arange(self.fragment_vocab_size).unsqueeze(0).repeat(2, 1)
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
    def __init__(self, spectrum_bins_size,  d_latent=128):
        super().__init__()
        self.net = mlp(spectrum_bins_size , 512, d_latent)

    def forward(self, spec):
        """
        Parameters
        ----------
        spec : torch.Tensor
            Spectrum intensity vector [N, spectrum_bins_size].

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
    def __init__(self, d_latent, fragment_vocab_size):
        super().__init__()
        self.net = mlp(d_latent, 128, fragment_vocab_size)

    def forward(self, z):
        """
        Parameters
        ----------
        z : torch.Tensor
            Latent embedding [N, d_latent] or [d_latent].

        Returns
        -------
        torch.Tensor
            Predicted fragment probabilities [N, fragment_vocab_size] or [fragment_vocab_size], range (0,1).
        """
        if z.dim() == 1:
            z = z.unsqueeze(0)
        return torch.sigmoid(self.net(z))


class DecSpec(nn.Module):
    """
    Decodes latent embeddings and fragment information into a predicted spectrum.
    """
    def __init__(self, d_latent, fragment_vocab_size, spectrum_bins_size):
        super().__init__()
        self.net = mlp(d_latent + fragment_vocab_size, 512, spectrum_bins_size)

    def forward(self, z, frag):
        """
        Parameters
        ----------
        z : torch.Tensor
            Latent embedding [N, d_latent].
        frag : torch.Tensor
            fragment_vocab_sizeragment vector [N, fragment_vocab_size].

        Returns
        -------
        torch.Tensor
            Predicted intensity vector [N, spectrum_bins_size], non-negative values.
        """
        x = torch.cat([z, frag], -1)
        return F.relu(self.net(x))


class TaskHeads(nn.Module):
    """Shared trunk heads for forward and backward tasks.

    Provides separate small projection heads for forward (mol->spec)
    and backward (spec->mol) operations. Also exposes learned
    log-variance parameters for uncertainty weighting of losses.
    """
    def __init__(self, d_latent=128, d_task=128):
        super().__init__()
        self.fwd = nn.Sequential(nn.Linear(d_latent, d_task), nn.ReLU())
        self.bwd = nn.Sequential(nn.Linear(d_latent, d_task), nn.ReLU())
        # learned log-variances for uncertainty weighting
        self.logvar_spec = nn.Parameter(torch.zeros(1))
        self.logvar_frag = nn.Parameter(torch.zeros(1))
        self.logvar_con = nn.Parameter(torch.zeros(1))

    def forward(self, z):
        return self.fwd(z), self.bwd(z)

class EncFragGraph(nn.Module):
    """
    Graph-aware fragment encoder.
    frag_bag: [B, V] with V fragments as nodes.
    adjacency: [B, V, V] (preferred) or [V, V] (will be expanded).
    """
    def __init__(self, fragment_vocab_size, d_latent=128, d_h=256, R=None, mass_vocab: Optional[torch.Tensor]=None):
        super().__init__()
        self.fragment_vocab_size = fragment_vocab_size
        # Two-channel node features: [presence, normalized_mass]
        self.lin0 = nn.Linear(2, d_h)          # per-node projection: 2 -> d_h
        self.lin1 = nn.Linear(d_h, d_latent)   # per-node -> latent
        self.rule_emb = nn.Embedding(R, d_h) if R is not None else None
        # Register mass vocabulary (normalized) as a buffer so it moves with .to(device)
        if mass_vocab is not None:
            mass_vocab = mass_vocab.detach().clone().float()
            if mass_vocab.dim() != 1 or mass_vocab.numel() != fragment_vocab_size:
                raise ValueError("mass_vocab must be a 1D tensor of length fragment_vocab_size")
            self.register_buffer('mass_vocab', mass_vocab)
        else:
            self.register_buffer('mass_vocab', None)

    def aggregate(self, x, edges=None, adjacency=None):
        """
        x: [B, V, d_h]
        returns: [B, V, d_h]
        """
        if adjacency is not None:
            # ensure 3D batch adjacency
            if adjacency.dim() == 2:
                adjacency = adjacency.unsqueeze(0)            # [1, V, V]
            B, V, H = x.shape
            if adjacency.size(0) == 1:
                adjacency = adjacency.expand(B, V, V)         # broadcast to batch
            I = torch.eye(V, device=x.device).unsqueeze(0).expand(B, V, V)
            A = adjacency + I                                 # add self-loops
            return torch.bmm(A, x)                            # [B, V, d_h]

        elif edges is not None:
            # simple scatter-add; edges: (src, dst, b[, rule_type])
            for (src, dst, b, *rest) in edges:
                rule_bias = self.rule_emb(rest[0]) if (self.rule_emb and rest) else 0.0
                x[b, dst] = x[b, dst] + x[b, src] + rule_bias
            return x

        raise ValueError("Either adjacency or edges must be provided for aggregation.")

    def forward(self, frag_bag, edges=None, adjacency=None, mass: Optional[torch.Tensor]=None):
        """
        frag_bag: [B, V]
        returns: [B, d_latent]
        """
        B, V = frag_bag.size(0), frag_bag.size(1)
        # Prepare mass channel
        if mass is not None:
            m = mass
            if m.dim() == 1:
                m = m.unsqueeze(0)
            if m.size(-1) != V:
                raise ValueError("mass vector length must match frag_bag width")
            if m.size(0) == 1 and B > 1:
                m = m.expand(B, V)
        elif self.mass_vocab is not None:
            m = self.mass_vocab
            if m.dim() == 1:
                m = m.unsqueeze(0)
            if m.size(0) == 1 and B > 1:
                m = m.expand(B, V)
        else:
            m = torch.zeros_like(frag_bag)

        # [B, V, 2] -> [B, V, d_h]
        x_in = torch.stack([frag_bag, m], dim=-1)
        x0 = torch.tanh(self.lin0(x_in))
        x_aggr = self.aggregate(x0, edges=edges, adjacency=adjacency)  # [B, V, d_h]
        z_nodes = self.lin1(x_aggr)                                    # [B, V, d_latent]
        return z_nodes.mean(dim=1)                                     # [B, d_latent]


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
        Binary fragment presence vectors [N, fragment_vocab_size].
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
    """Container for one dataset sample. So one molecule with its derivation graph"""
    graph_feat: GeometricData
    frag_bag: torch.Tensor
    true_spectrum: torch.Tensor
    smiles: str
    fragment_adjacency_fwd: torch.Tensor  # forward
    fragment_adjacency_bwd: torch.Tensor  # backward


# ---------------------------------------------------------------------------
# RealDataset + helpers
# ---------------------------------------------------------------------------

# ---------- Fragment vocab ----------
def build_fragment_vocab(
    frag_coll: Dict[
        str,
        Tuple[
            List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]],  # fwd
            List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]]   # bwd
        ]
    ],
    existing_frag_to_id: Optional[Dict[str, int]] = None
) -> Dict[str, int]:
    """Build a {fragment_smiles -> id} mapping.

    If an existing mapping is provided, return a copy WITHOUT extending it.
    This guarantees a fixed fragment dimension across train/val/test so that
    decoders initialized with train-time F remain compatible.
    """
    if existing_frag_to_id is not None:
        return existing_frag_to_id.copy()

    ctr = Counter()
    for _smile_of_mol, (fwd, bwd) in frag_coll.items():
        for item in fwd:
            frag_smi = item[0]
            ctr.update([frag_smi])
        for item in bwd:
            frag_smi = item[0]
            ctr.update([frag_smi])

    frag_to_id: Dict[str, int] = {}
    idx = 0
    for frag in ctr.keys():
        if frag not in frag_to_id:
            frag_to_id[frag] = idx
            idx += 1
    return frag_to_id

def frag_bag_from_list(
    frag_list: List[str], # list of fragment SMILES
    frag_to_id: Dict[str, int],
    fragment_vocab_size: int
) -> torch.Tensor:
    bag = torch.zeros(fragment_vocab_size, dtype=torch.float32)
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
    spectrum_bins_size = floor((mz_max - mz_min) / bin_width)
    """
    spectrum_bins_size = int((mz_max - mz_min) / bin_width)
    vec = torch.zeros(spectrum_bins_size, dtype=torch.float32)
    for mz, inten in peaks:
        bi = compute_bin_index(mz, mz_min, mz_max, bin_width)
        if bi is not None and 0 <= bi < spectrum_bins_size:
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
    Dataset that handles forward and backward derivation graphs
    """
    def __init__(
        self,
        frag_coll: Dict[
            str,
            Tuple[
                List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]],  # fwd
                List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]]   # bwd
            ]
        ],
        real_spectra_per_mol: List[List[Tuple[float, float]]],
        *,
        mz_min: float = 1.0,
        mz_max: float = 1000.0,
        bin_width: float = 1.0,
        frag_to_id: Optional[Dict[str, int]] = None, # Fragment vocabulary handling
        precompute: bool = True, # Pre-build for speed
    ):
        self.real_spectra_per_mol = real_spectra_per_mol # ground truth spectra
        self.frag_coll = frag_coll

        self.mz_min = float(mz_min)
        self.mz_max = float(mz_max)
        self.bin_width = float(bin_width)
        self.spectrum_bins_size = int((self.mz_max - self.mz_min) / self.bin_width)  # spectrum length

        assert len(frag_coll.keys()) == len(real_spectra_per_mol), \
            "Fragment collections and spectra must have the same number of molecules."

        # Build/keep fragment vocabulary
        if frag_to_id is None:
            self.frag_to_id = build_fragment_vocab(self.frag_coll)
        else:
            self.frag_to_id = build_fragment_vocab(self.frag_coll, existing_frag_to_id=frag_to_id)

        self.fragment_vocab_size = len(self.frag_to_id)
        self.graph_featurizer = GraphFeaturizerMOD()
        self._cache = None
        if precompute:
            self._precompute_all()
        # Build mass vocabulary aligned with frag_to_id and normalize by mz_max
        self.mass_vocab_norm = self._build_mass_vocab()

    def __len__(self) -> int:
        return len(self.frag_coll.keys())

    def __getitem__(self, idx: int):
        if self._cache is not None:
            graph_feats, bags, specs, adjs_fwd, adjs_bwd = self._cache[idx]
        else:
            mol = mod.smiles(list(self.frag_coll.keys())[idx])
            graph_feats = self.graph_featurizer(mol)
            spec_vec = self._make_spec(idx)

        return Sample(
            graph_feat=graph_feats,
            frag_bag=bags,  # forward
            true_spectrum=specs,
            fragment_adjacency_bwd=adjs_bwd,
            fragment_adjacency_fwd=adjs_fwd,
            smiles=list(self.frag_coll.keys())[idx]
        )

    def _make_frag_adj(self, idx: int) -> List[torch.Tensor]:
        """
    Build [fragment_vocab_size, fragment_vocab_size] adjacency from fwd_coll and bwd_coll for this molecule.
        """
        fragment_vocab_size = self.fragment_vocab_size
        fragment_adjacency_fwd = None
        fragment_adjacency_bwd = None
        fwd, bwd = list(self.frag_coll.values())[idx]
        for derivation_graph in (fwd, bwd):
            adj = torch.zeros(fragment_vocab_size, fragment_vocab_size, dtype=torch.float32)
            for src_smi, _mass, targets, _rules in derivation_graph:
                src_idx = self.frag_to_id.get(src_smi)
                if src_idx is None:
                    continue
                for dst_smi in targets.values():
                    for dst in dst_smi:
                        dst_idx = self.frag_to_id.get(dst)
                        if dst_idx is not None:
                            adj[src_idx, dst_idx] = 1.0
            if derivation_graph is fwd:
                fragment_adjacency_fwd = adj
            else:
                fragment_adjacency_bwd = adj

        return fragment_adjacency_fwd, fragment_adjacency_bwd

    def _build_mass_vocab(self) -> torch.Tensor:
        """
        Construct a [V] tensor of per-fragment exact masses aligned to frag_to_id.
        If a fragment appears multiple times, the first observed mass is used.
        Masses are normalized by mz_max to be ~[0,1]. Missing masses -> 0.
        """
        V = self.fragment_vocab_size
        masses = torch.zeros(V, dtype=torch.float32)
        seen = set()
        for _mol_smi, (fwd, bwd) in self.frag_coll.items():
            for frag_smi, exact_mass, _t, _r in fwd:
                fid = self.frag_to_id.get(frag_smi)
                if fid is not None and fid not in seen:
                    masses[fid] = float(exact_mass)
                    seen.add(fid)
            for frag_smi, exact_mass, _t, _r in bwd:
                fid = self.frag_to_id.get(frag_smi)
                if fid is not None and fid not in seen:
                    masses[fid] = float(exact_mass)
                    seen.add(fid)
        # Normalize by mz_max (avoid div by zero)
        denom = torch.tensor(self.mz_max if self.mz_max > 0 else 1000.0, dtype=torch.float32)
        masses = masses / denom
        return masses

    def _make_frag_graph(self, idx: int, direction: str = 'fwd') -> torch.Tensor:
        """
        Generate graph-aware fragment representation for a molecule.
        """
        if direction == 'fwd':
            frag_bag = frag_bag_from_list(
                self.frag_coll.keys(),
                self.frag_to_id,
                self.fragment_vocab_size
                )
        else:
            frag_bag = frag_bag_from_list(
                self.frag_coll.keys(),
                self.frag_to_id,
                self.fragment_vocab_size
                )
        frag_adj = self._make_frag_adj(idx)
        return self.graph_featurizer.aggregate(frag_bag, frag_adj)

    def _make_frag_bag(self, idx: int) -> torch.Tensor:
        """
        Create a fragment bag tensor for a specific molecule.
        """
        mol = list(self.frag_coll.values())[idx]

        # get only fragment SMILES list from fwd_coll
        fwd_coll, _ = list(self.frag_coll.values())[idx]  # fwd_coll: List[(frag_smiles, targets, rules), ...]
        frag_smiles = [t[0] for t in fwd_coll]  # extract only the fragment SMILES strings
        return frag_bag_from_list(
            frag_smiles,
            self.frag_to_id,
            self.fragment_vocab_size
            )

    def _make_spec(self, idx: int) -> torch.Tensor:
        """
        Create a spectral representation for a specific molecule.
        """
        return bin_spectrum(
            self.real_spectra_per_mol[idx],
            self.mz_min,
            self.mz_max,
            self.bin_width
            )

    def _precompute_all(self):
        """Materialize tensors to speed up training."""
        graph_feats = []
        bags = []
        specs = []
        adjs_fwd = []
        adjs_bwd = []
        for i in range(len(self)):
            mol = mod.smiles(list(self.frag_coll.keys())[i])
            graph_feats.append(self.graph_featurizer(mol))
            bags.append(self._make_frag_bag(i))
            specs.append(self._make_spec(i))
            fwd, bwd = self._make_frag_adj(i)
            adjs_fwd.append(fwd)
            adjs_bwd.append(bwd)

        self._cache = list(zip(graph_feats, bags, specs, adjs_fwd, adjs_bwd))
# --- end RealDataset ----------------------------------------------------------



def collate(batch: List[Sample]):
    """
    Collate function for DataLoader batching.
    """
    graph_feats = [b.graph_feat for b in batch]
    fragments = torch.stack([b.frag_bag for b in batch])
    true_spectrum = torch.stack([b.true_spectrum for b in batch])
    smiles = [b.smiles for b in batch]
    fragment_adjacency_fwd = torch.stack([b.fragment_adjacency_fwd for b in batch])
    fragment_adjacency_bwd = torch.stack([b.fragment_adjacency_bwd for b in batch])
    return graph_feats, fragments, true_spectrum, smiles, fragment_adjacency_fwd, fragment_adjacency_bwd


# ---------------------------------------------------------------------------
# Training loops
# ---------------------------------------------------------------------------

def train_epoch_phase_a(loader, device, enc_mol, enc_frag, heads, dec_frag, dec_spec,
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

    for graph_feats, frag_bag, true_spectrum, smiles, adj_fwd, adj_bwd in loader:
        #TODO here
        # check adj_fwd is empty or not
        if adj_fwd.sum() > 0:
            print("Adjacency matrix is not empty")
        else:
            print("Adjacency matrix is empty")

        frag_bag = frag_bag.to(device)
        true_spectrum = true_spectrum.to(device)
        adj_fwd = adj_fwd.to(device)  # use forward DG for Phase A

        opt.zero_grad()
        z_m = enc_mol(graph_feats)
        z_f = enc_frag(frag_bag, adjacency=adj_fwd)   # <-- uses [B,V,V]
        z = (z_m + z_f) / 2
        z_fwd, _ = heads(z)
        p_frag = dec_frag(z_fwd)
        spec_hat = dec_spec(z_fwd, frag_bag)
        # losses
        L_spec = cosine_loss(spec_hat, true_spectrum) + 0.0 * F.mse_loss(spec_hat, true_spectrum)
        L_frag = F.binary_cross_entropy(p_frag, frag_bag)
        # uncertainty weighting
        s_spec = heads.logvar_spec
        s_frag = heads.logvar_frag
        loss = torch.exp(-s_spec) * L_spec + s_spec + torch.exp(-s_frag) * L_frag + s_frag
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


def train_epoch_phase_b(loader, device, enc_spec, enc_mol, heads, dec_frag, dec_spec,
                        opt, alpha=1.0, beta=0.1, lam=0.1, tau=0.5
                        ) -> float: # average epoch loss
    """
    Phase B: trains spectrum latent alignment and inverse consistency.
    Returns Average epoch loss.
    """
    enc_spec.train(); enc_mol.train(); dec_frag.train(); dec_spec.train()
    total = 0.0
    for graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd in loader:
        frag_bag, spec = frag_bag.to(device), spec.to(device)
        frag_adj = adj_bwd.to(device)
         # spectrum-anchored learning
        opt.zero_grad()
        z_m = enc_mol(graph_feats)
        z_s = enc_spec(spec)
        # use backward head for spec-anchored tasks
        _, z_bwd = heads(z_s)
        l_con = info_nce(z_bwd, z_m)
        p_frag = dec_frag(z_bwd)
        spec_hat = dec_spec(z_bwd, (p_frag > tau).float())
        # losses
        L_spec = cosine_loss(spec_hat, spec) + 0.0 * F.mse_loss(spec_hat, spec)
        L_frag = F.binary_cross_entropy(p_frag, frag_bag)
        L_con = l_con
        # uncertainty weighting
        s_spec = heads.logvar_spec
        s_frag = heads.logvar_frag
        s_con = heads.logvar_con
        loss = torch.exp(-s_spec) * L_spec + s_spec \
               + torch.exp(-s_frag) * L_frag + s_frag \
               + torch.exp(-s_con) * L_con + s_con
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
    fragment_adjacency_fwd: torch.Tensor
    fragment_adjacency_bwd: torch.Tensor
    true_spectrum: torch.Tensor

class LatentIndex:
    """
    Simple in-memory cosine-similarity index for molecule retrieval.
    """
    def __init__(self, d):
        self.d = d
        self.embs: List[torch.Tensor] = []
        self.items: List[IndexItem] = []

    def build(self, dataset: Dataset, device, enc_mol: EncMol):
            self.embs.clear(); self.items.clear()
            enc_mol.eval()
            loader = DataLoader(dataset, batch_size=256, shuffle=False, collate_fn=collate)
            with torch.no_grad():
                for graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd in loader:
                    z = enc_mol(graph_feats)                     # [B, d]
                    z = F.normalize(z, dim=-1).cpu()
                    for i in range(z.size(0)):
                        self.embs.append(z[i])
                        self.items.append(IndexItem(
                            z=z[i],
                            smiles=smiles[i],
                            frag_bag=frag_bag[i].cpu(),
                            graph_feat=graph_feats[i],
                            fragment_adjacency_fwd=adj_fwd[i].cpu(),
                            fragment_adjacency_bwd=adj_bwd[i].cpu(),
                            true_spectrum=spec[i].cpu(),
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
        # z_q is spectrum latent; project to backward head if available
        # assume caller passes z_q from enc_spec (pre-head); try to detect heads
        try:
            # if heads exist in closure (updated below), use them
            fwd_h, bwd_h = rerank_candidates.__globals__.get('heads', (None, None))
        except Exception:
            fwd_h = bwd_h = None
        if 'heads' in rerank_candidates.__globals__ and rerank_candidates.__globals__['heads'] is not None:
            _, z_use = rerank_candidates.__globals__['heads'](z_q.to(device))
        else:
            z_use = z_q.to(device)
        frag_pred = dec_frag(z_use).cpu()
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


def infer_mol_to_spec(graph_feat, frag_bag, device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=None):
    enc_mol.eval(); enc_frag.eval(); dec_spec.eval(); dec_frag.eval()
    with torch.no_grad():
        # Encode molecule
        z_m = enc_mol([graph_feat])  # [1, d]

        # Determine expected fragment dimension for the current dec_spec
        # First layer of dec_spec takes [d_latent + F] features
        expected_in = dec_spec.net[0].in_features
        d_lat = z_m.size(-1)
        expected_F = max(expected_in - d_lat, 0)

        # Align fragment bag (and adjacency) to expected_F by padding/truncation
        bag = frag_bag.to(device)
        if bag.dim() == 1:
            bag = bag.unsqueeze(0)
        cur_F = bag.size(-1)
        if cur_F != expected_F and expected_F > 0:
            if cur_F < expected_F:
                pad = expected_F - cur_F
                bag_aligned = F.pad(bag, (0, pad))
            else:
                bag_aligned = bag[:, :expected_F]
        else:
            bag_aligned = bag

        # Align adjacency if provided
        adj_aligned = None
        if frag_adj is not None:
            adj = frag_adj.to(device)
            if adj.dim() == 2:
                adj = adj.unsqueeze(0)
            F_src = adj.size(-1)
            if F_src != expected_F and expected_F > 0:
                if F_src < expected_F:
                    pad_f = expected_F - F_src
                    adj_aligned = F.pad(adj, (0, pad_f, 0, pad_f))
                else:
                    adj_aligned = adj[:, :expected_F, :expected_F]
            else:
                adj_aligned = adj

        # Encode fragments graph-aware with aligned inputs
        z_f = enc_frag(bag_aligned, adjacency=adj_aligned)
        z = (z_m + z_f) / 2
        z_fwd, _ = globals().get('heads')(z) if globals().get('heads') else (z, z)

        # Use the same aligned fragment vector for spectrum decoder
        spec_hat = dec_spec(z_fwd, bag_aligned).cpu().squeeze(0)
        frag_pred = dec_frag(z_fwd).cpu().squeeze(0)
    return spec_hat, frag_pred



def infer_spec_to_mol(spec, index, device, enc_spec, dec_spec, dec_frag, topk=10, tau=0.5):
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
    ranked = rerank_candidates(spec, z_q, cands, device, enc_spec, dec_spec, dec_frag, tau=tau)
    return ranked


# ----------------------------- DEMOS ---------------------------------

def demo_retrieval_metrics(index, loader, device, enc_spec, dec_spec, dec_frag, topk_list=(1,5,10), tau=0.5, max_batches=None):
    """Compute Recall@K and MRR on a loader using a train-built index."""
    enc_spec.eval()
    hits = {k: 0 for k in topk_list}
    mrr = 0.0
    n = 0
    with torch.no_grad():
        for bi, (graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd) in enumerate(loader):
            if max_batches is not None and bi >= max_batches:
                break
            B = len(smiles)
            z_q = enc_spec(spec.to(device))  # [B, d]
            for i in range(B):
                ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, dec_spec, dec_frag, topk=max(topk_list), tau=tau)
                preds = [s for s, _ in ranked]
                n += 1
                for k in topk_list:
                    if smiles[i] in preds[:k]:
                        hits[k] += 1
                # MRR
                rank = next((ri + 1 for ri, s in enumerate(preds) if s == smiles[i]), None)
                if rank is not None:
                    mrr += 1.0 / rank
    out = {f"R@{k}": (hits[k] / max(n, 1)) for k in topk_list}
    out["MRR"] = mrr / max(n, 1)
    out["N"] = n
    return out


def demo_tau_sweep(index, loader, device, enc_spec, dec_spec, dec_frag, taus=(0.2,0.4,0.6,0.8), topk_list=(1,5,10), max_batches=5):
    """Evaluate retrieval metrics across tau thresholds; return per-tau metrics and best tau per K."""
    results = {}
    for t in taus:
        metrics = demo_retrieval_metrics(index, loader, device, enc_spec, dec_spec, dec_frag, topk_list=topk_list, tau=t, max_batches=max_batches)
        results[t] = metrics
    # pick best per K by R@K, tie-breaker MRR
    best = {}
    for k in topk_list:
        key = f"R@{k}"
        best_tau = max(taus, key=lambda tau: (results[tau][key], results[tau]["MRR"]))
        best[key] = {"tau": best_tau, "metric": results[best_tau][key]}
    return results, best


def demo_ablate_adjacency(graph_feat, frag_bag, adj, true_spec, device, enc_mol, enc_frag, dec_spec, dec_frag):
    """Compare spectrum reconstruction with graph-aware adjacency vs bag-only (zero adjacency)."""
    print("adjacency matrix:", adj)
    if adj.sum() > 0:
        print("adjacency matrix has edges")
    else:
        print("adjacency matrix is empty")
    with torch.no_grad():
        spec_hat_graph, _ = infer_mol_to_spec(graph_feat, frag_bag, device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=adj)
        spec_hat_bag, _ = infer_mol_to_spec(graph_feat, frag_bag, device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=torch.zeros_like(adj))
        cos_graph = F.cosine_similarity(F.normalize(spec_hat_graph, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
        cos_bag = F.cosine_similarity(F.normalize(spec_hat_bag, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
    return {"cos_graph": cos_graph, "cos_bag": cos_bag}


def demo_heads_comparison(loader, device, enc_mol, heads, dec_spec, dec_frag, n_batches=3):
    """Run DecSpec/DecFrag with z_fwd vs z_bwd to quantify head specialization (mol->spec reconstruction)."""
    enc_mol.eval(); dec_spec.eval(); dec_frag.eval()
    stats = {"cos_fwd": [], "cos_bwd": [], "bce_fwd": [], "bce_bwd": []}
    with torch.no_grad():
        for bi, (graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd) in enumerate(loader):
            if bi >= n_batches:
                break
            frag_bag = frag_bag.to(device); spec = spec.to(device)
            z_m = enc_mol(graph_feats)
            z_fwd, z_bwd = heads(z_m)
            spec_hat_fwd = dec_spec(z_fwd, frag_bag)
            spec_hat_bwd = dec_spec(z_bwd, frag_bag)
            p_frag_fwd = dec_frag(z_fwd)
            p_frag_bwd = dec_frag(z_bwd)
            stats["cos_fwd"].append(F.cosine_similarity(F.normalize(spec_hat_fwd, dim=-1), F.normalize(spec, dim=-1), dim=-1).mean().item())
            stats["cos_bwd"].append(F.cosine_similarity(F.normalize(spec_hat_bwd, dim=-1), F.normalize(spec, dim=-1), dim=-1).mean().item())
            stats["bce_fwd"].append(F.binary_cross_entropy(p_frag_fwd, frag_bag).item())
            stats["bce_bwd"].append(F.binary_cross_entropy(p_frag_bwd, frag_bag).item())
    # averages
    return {k: float(np.mean(v)) if len(v) else float("nan") for k, v in stats.items()}


def demo_fragment_perturbation(graph_feat, frag_bag, true_spec, device, enc_mol, enc_frag, dec_spec, dec_frag, index, adj=None, top_n=5):
    """Add/drop top-N fragments (by predicted prob) and observe spectrum shift and retrieval rank change."""
    with torch.no_grad():
        spec_hat, p_frag = infer_mol_to_spec(graph_feat, frag_bag, device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=adj)
        base_cos = F.cosine_similarity(F.normalize(spec_hat, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
        probs = p_frag.clone()
        top_idx = torch.topk(probs, k=min(top_n, probs.numel())).indices
        # Drop: set selected fragments to 0
        frag_drop = frag_bag.clone()
        frag_drop[top_idx] = 0.0
        spec_drop, _ = infer_mol_to_spec(graph_feat, frag_drop, device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=adj)
        cos_drop = F.cosine_similarity(F.normalize(spec_drop, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
        # Add: set selected fragments to 1
        frag_add = frag_bag.clone()
        frag_add[top_idx] = 1.0
        spec_add, _ = infer_mol_to_spec(graph_feat, frag_add, device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=adj)
        cos_add = F.cosine_similarity(F.normalize(spec_add, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
    return {"base_cos": base_cos, "cos_drop": cos_drop, "cos_add": cos_add}


def demo_noise_robustness(index, loader, device, enc_spec, dec_spec, dec_frag, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5):
    """Add Gaussian noise to spectra and plot/return Recall@K vs noise level."""
    results = {}
    for s in noise_levels:
        hits = {k: 0 for k in topk_list}
        n = 0
        with torch.no_grad():
            for bi, (graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd) in enumerate(loader):
                if bi >= max_batches:
                    break
                B = len(smiles)
                spec_noisy = spec + s * torch.randn_like(spec)
                # normalize
                spec_noisy = F.normalize(spec_noisy, dim=-1)
                for i in range(B):
                    ranked = infer_spec_to_mol(spec_noisy[i], index, device, enc_spec, dec_spec, dec_frag, topk=max(topk_list))
                    preds = [p for p, _ in ranked]
                    n += 1
                    for k in topk_list:
                        if smiles[i] in preds[:k]:
                            hits[k] += 1
        results[s] = {f"R@{k}": hits[k] / max(n, 1) for k in topk_list}
        results[s]["N"] = n
    # optional plot
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
            plt.savefig("noise_robustness.png", dpi=150)
        except Exception:
            pass
        plt.clf()
    return results


def demo_visualize_reconstructions(
    graph_feats, frag_bag, true_spec, smiles, adj, device,
    enc_mol, enc_frag, dec_spec, dec_frag, n_samples=3
    ) -> bool: # success
    """Plot true vs reconstructed spectra for n_samples molecules."""
    n = min(n_samples, len(smiles))
    for i in range(n):
        spec_hat, _ = infer_mol_to_spec(graph_feats[i], frag_bag[i], device, enc_mol, enc_frag, dec_spec, dec_frag, frag_adj=adj[i].unsqueeze(0))
        plt.figure()
        plt.plot(true_spec[i].cpu().numpy(), label="true")
        plt.plot(spec_hat.cpu().numpy(), label="pred")
        plt.title(f"Recon: {smiles[i]}")
        plt.legend()
        plt.tight_layout()
        try:
            plt.savefig(f"recon_{i}.png", dpi=150)
        except Exception:
            pass
        plt.close()
    return True



def train_test_split(
    data: Union[List[Any], Dict[Any, Any]],
    test_size: float = 0.2,
    train_size: float = None,
    shuffle: bool = True,
    random_state: int = None
) -> Tuple[Union[List[Any], Dict[Any, Any]], Union[List[Any], Dict[Any, Any]]]:
    """
    Split a list or dict into train and test subsets.

    Parameters
    ----------
    data : list or dict
        The data to split.
    test_size : float, optional
        Proportion of the dataset to include in the test split (default=0.2).
    train_size : float, optional
        Proportion of the dataset to include in the train split.
        If None, uses the complement of `test_size`.
    shuffle : bool, optional
        Whether to shuffle the data before splitting (default=True).
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    train_data, test_data : same type as input
        The split datasets.
    """
    if random_state is not None:
        random.seed(random_state)

    # Convert dict to list of keys if needed
    if isinstance(data, dict):
        keys = list(data.keys())
        if shuffle:
            random.shuffle(keys)
        n_total = len(keys)
        n_test = int(n_total * test_size) if train_size is None else int(n_total * (1 - train_size))
        test_keys = set(keys[:n_test])
        train = {k: v for k, v in data.items() if k not in test_keys}
        test = {k: v for k, v in data.items() if k in test_keys}
        return train, test

    elif isinstance(data, list):
        indices = list(range(len(data)))
        if shuffle:
            random.shuffle(indices)
        n_total = len(data)
        n_test = int(n_total * test_size) if train_size is None else int(n_total * (1 - train_size))
        test_idx = indices[:n_test]
        train_idx = indices[n_test:]
        train = [data[i] for i in train_idx]
        test = [data[i] for i in test_idx]
        return train, test

    else:
        raise TypeError("Input data must be a list or dict.")


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
    p.add_argument("--epochs_fwd", type=int, default=100, help="Phase A epochs (mol+frag -> spec)")
    p.add_argument("--epochs_bwd", type=int, default=100, help="Phase B epochs (align spec latent)")
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
    frag_coll: Dict[
        str,
        Tuple[
            List[  # forward
                Tuple[
                    str, # frag_smiles
                    float, # exact mass
                    Dict[int, List[str]], # targets
                    Dict[int, List[str]]  # rules
                    ]
                ],
            List[   # backward
                Tuple[
                    str, # frag_smiles
                    float, # exact mass
                    Dict[int, List[str]], # targets
                    Dict[int, List[str]]  # rules
                    ]
                ]
        ]
    ] = {}
    real_spectra_per_mol: List[List[Tuple[float, float]]] = []

    for name, smi in mols_definitions:
        mol = mod.smiles(smi, name=name)
        fwd_dg, _rule_db = utils.load_derivation_graph(name, path=LOAD_PATH / "fwd")
        bwd_dg, _rule_db = utils.load_derivation_graph(name, path=LOAD_PATH / "bwd")

        fwd_coll = []
        for graph_term in fwd_dg.graphDatabase: # when loading DG len(createdGraphs)=0
            graph = utils.graph_from_term(graph_term)
            if graph.isMolecule:
                dg_v = fwd_dg.findVertex(graph_term)
                targets = dict()
                rules = dict()
                for edge in dg_v.outEdges:
                    targets[edge.id] = [utils.graph_from_term(t.graph).smiles for t in edge.targets]
                    rules[edge.id] = [rule for rule in edge.rules]
                fwd_coll.append((graph.smiles, graph.exactMass, targets, rules))



        bwd_coll = []
        for graph_term in bwd_dg.graphDatabase: # when loading DG len(createdGraphs)=0
            graph = utils.graph_from_term(graph_term)
            if graph.isMolecule:
                dg_v = bwd_dg.findVertex(graph_term)
                try:
                    targets = dict()
                    rules = dict()
                    for edge in dg_v.outEdges:
                        targets[edge.id] = [utils.graph_from_term(t.graph).smiles for t in edge.targets]
                        rules[edge.id] = [rule for rule in edge.rules]
                    bwd_coll.append((graph.smiles, graph.exactMass, targets, rules))
                except mod.libpymod.LogicError:
                    #bwd_coll.append((graph.smiles, dict(), dict()))
                    print("empty edges for ", graph.smiles)

        frag_coll[smi] = (fwd_coll, bwd_coll)

        real_spectra = utils.get_spectra_from_local_jdx(name)
        real_spectra_per_mol.append(real_spectra)

    train_spect, test_spect = train_test_split(
        data= real_spectra_per_mol,
        test_size=0.1,
        random_state=42,
        shuffle=False
        )
    train_frags, test_frags = train_test_split(
        data = frag_coll,
        test_size=0.1,
        random_state=42,
        shuffle=False
    )

    train_spect, vali_spect = train_test_split(
        train_spect,
        test_size=0.15,
        random_state=42,
        shuffle=False
    )
    train_frags, vali_frags = train_test_split(
        train_frags,
        test_size=0.15,
        random_state=42,
        shuffle=False
    )

    # Build dataset
    train_ds = RealDataset(
        train_frags, train_spect,
        precompute=True
        )

    vali_ds = RealDataset(
        vali_frags, vali_spect,
        frag_to_id=train_ds.frag_to_id,  # ensure consistent fragment vocab across splits
        precompute=True
        )

    test_ds = RealDataset(
        test_frags, test_spect,
        frag_to_id=train_ds.frag_to_id,
        precompute=True
        )

    # Use dataset to configure the model:
    fragment_vocab_size = train_ds.fragment_vocab_size # number of fragments
    spectrum_bins_size = train_ds.spectrum_bins_size


    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=False, drop_last=False, collate_fn=collate)
    val_loader   = DataLoader(vali_ds, batch_size=args.batch, shuffle=False, collate_fn=collate)
    test_loader  = DataLoader(test_ds, batch_size=args.batch, shuffle=False, collate_fn=collate)

    # Add after DataLoader creation
    # ...existing code...
    def pct_non_empty(loader):
        c = 0; n = 0
        for _, _, _, _, adj_fwd, _ in loader:
            s = (adj_fwd.sum(dim=(1,2)) > 0).float()
            c += s.sum().item(); n += s.numel()
        return 100.0 * c / max(n, 1)

    print(f"Non-empty adj (train): {pct_non_empty(train_loader):.1f}%")
    print(f"Non-empty adj (val):   {pct_non_empty(val_loader):.1f}%")
    print(f"Non-empty adj (test):  {pct_non_empty(test_loader):.1f}%")

    # Models
    enc_mol  = EncMol(args.latent).to(device)
    enc_frag = EncFragGraph(fragment_vocab_size, args.latent, mass_vocab=train_ds.mass_vocab_norm).to(device)
    enc_spec = EncSpec(spectrum_bins_size, args.latent).to(device)
    dec_frag = DecFrag(args.latent, fragment_vocab_size).to(device)
    dec_spec = DecSpec(args.latent, fragment_vocab_size, spectrum_bins_size).to(device)
    # Task heads (shared trunk projections)
    heads = TaskHeads(d_latent=args.latent, d_task=args.latent).to(device)
    # expose for helper functions (script-level convenience)
    globals()['heads'] = heads

    # Optimizers (separate per phase keeps it simple)
    opt_a = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(enc_frag.parameters()) +
                             list(dec_frag.parameters()) +
                             list(dec_spec.parameters()) +
                             list(heads.parameters()), lr=args.lr)
    opt_b = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(enc_spec.parameters()) +
                             list(dec_frag.parameters()) +
                             list(dec_spec.parameters()) +
                             list(heads.parameters()), lr=args.lr)

    # ----------------- Phase A -----------------
    print("== Phase A: train forward & fragments ==")
    for epoch in range(1, args.epochs_fwd + 1):
        loss = train_epoch_phase_a(train_loader, device, enc_mol, enc_frag, heads, dec_frag, dec_spec, opt_a)
        print(f"[A] epoch {epoch:02d} loss {loss:.4f}")

    # ----------------- Phase B -----------------
    print("== Phase B: align spec latent + spectrum-anchored recon ==")
    for epoch in range(1, args.epochs_bwd + 1):
        loss = train_epoch_phase_b(train_loader, device, enc_spec, enc_mol, heads, dec_frag, dec_spec, opt_b)
        print(f"[B] epoch {epoch:02d} loss {loss:.4f}")

    # ----------------- Build retrieval index -----------------
    print("== Building retrieval index on TRAIN set ==")
    index = LatentIndex(d=args.latent)
    index.build(train_ds, device, enc_mol)


    # ----------------- Demo: Structure - > Spectrum -----------------
    graph_feats, frag_bag, spec, smiles, adj_fwd, adj_bwd = next(iter(val_loader))
    # why are the adjacency matrices empty?
    i = 0
    spec_hat, frag_pred = infer_mol_to_spec(
        graph_feats[i], frag_bag[i], device,
        enc_mol, enc_frag, dec_spec, dec_frag,
        frag_adj=adj_fwd[i].unsqueeze(0)
    )
    cos_sim = F.cosine_similarity(
        F.normalize(spec_hat, dim=-1).unsqueeze(0),
        F.normalize(spec[i], dim=-1).unsqueeze(0),
        dim=-1
    ).item()
    print(f"Mol- >Spec for {smiles[i]} | cosine={cos_sim:.3f} | frag_pred_mean={frag_pred.mean().item():.3f}")

    for x in adj_bwd:
        if x.sum() > 0:
            print("adjacency matrix has edges")
        else:
            print("adjacency matrix is empty")

    # ----------------- Demo: Spectrum - > Structure -----------------
    print("== Demo: Spec -> Mol retrieval + re-ranking on the same VAL sample ==")
    ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, dec_spec, dec_frag, topk=10)
    print("Top-5 candidates:")
    print(f"{'SMILES':>40s} | {'Score':>8s}")
    print("-" * 50)
    for s, sc in ranked[:5]:
        print(f"{s:>40s} | {sc:8.3f}")

    # ----------------- Demo: Retrieval metrics on VAL/TEST -----------------
    print("== Retrieval metrics (VAL) ==")
    val_metrics = demo_retrieval_metrics(index, val_loader, device, enc_spec, dec_spec, dec_frag, topk_list=(1,5,10), tau=0.5, max_batches=5)
    print(val_metrics)
    print("== Retrieval metrics (TEST) ==")
    test_metrics = demo_retrieval_metrics(index, test_loader, device, enc_spec, dec_spec, dec_frag, topk_list=(1,5,10), tau=0.5, max_batches=5)
    print(test_metrics)

    # ----------------- Demo: Tau sweep for reranking -----------------
    print("== Tau sweep on VAL (subset) ==")
    tau_results, tau_best = demo_tau_sweep(index, val_loader, device, enc_spec, dec_spec, dec_frag, taus=(0.2,0.4,0.6,0.8), topk_list=(1,5,10), max_batches=5)
    print("tau_results:", tau_results)
    print("best per K:", tau_best)

    # ----------------- Demo: Fragment graph ablation -----------------
    print("== Graph ablation on one VAL sample ==")
    ablation = demo_ablate_adjacency(graph_feats[i], frag_bag[i], adj_fwd[i].unsqueeze(0), spec[i], device, enc_mol, enc_frag, dec_spec, dec_frag)
    print(ablation)

    # ----------------- Demo: Head comparison (fwd vs bwd) -----------------
    print("== Head comparison (forward vs backward) on VAL subset ==")
    heads_stats = demo_heads_comparison(val_loader, device, enc_mol, heads, dec_spec, dec_frag, n_batches=3)
    print(heads_stats)

    # ----------------- Demo: Fragment perturbation sensitivity -----------------
    print("== Fragment perturbation sensitivity on one VAL sample ==")
    pert = demo_fragment_perturbation(graph_feats[i], frag_bag[i].clone(), spec[i], device, enc_mol, enc_frag, dec_spec, dec_frag, index, adj=adj_fwd[i].unsqueeze(0), top_n=5)
    print(pert)

    # ----------------- Demo: Spectrum noise robustness -----------------
    print("== Spectrum noise robustness (VAL subset) ==")
    noise_res = demo_noise_robustness(index, val_loader, device, enc_spec, dec_spec, dec_frag, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5)
    print(noise_res)

    # ----------------- Demo: Visualization of reconstructions -----------------
    print("== Visualization: saving recon plots for a few VAL samples ==")
    _ = demo_visualize_reconstructions(graph_feats, frag_bag, spec, smiles, adj_fwd, device, enc_mol, enc_frag, dec_spec, dec_frag, n_samples=3)

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
