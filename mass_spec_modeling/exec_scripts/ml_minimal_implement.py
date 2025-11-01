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


from torch_geometric.nn import global_mean_pool
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data as GeometricData
from torch_geometric.data import Batch

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
        self.gnn1 = GCNConv(3, 64)
        self.gnn2 = GCNConv(64, d_latent)
        self.global_mean_pool = global_mean_pool

    def forward(self, batch_graphs):
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

class FragSetEncoderVocabless(nn.Module):
    """
    Encode a variable-size set of fragment graphs using EncMol as a backbone
    and attention pooling; optionally smooth with local adjacency and inject
    per-fragment normalized mass as a feature.
    """
    def __init__(self, enc_mol: "EncMol", d_latent: int):
        super().__init__()
        self.enc_mol = enc_mol
        self.mass_mlp = nn.Sequential(nn.Linear(1, d_latent), nn.Tanh())
        self.att = nn.Sequential(
            nn.Linear(d_latent, d_latent // 2), nn.Tanh(),
            nn.Linear(d_latent // 2, 1)
        )

    def _encode_fragments(self, frags: List[GeometricData]) -> torch.Tensor:
        if len(frags) == 0:
            # return a zero vector if no fragments
            d = self.enc_mol.gnn2.out_channels
            return torch.zeros(1, d, device=next(self.parameters()).device)
        # enc_mol pools per graph, so on a list of fragment graphs we get one row per fragment
        return self.enc_mol(frags)  # [n_frag, d_latent]

    def forward(
        self,
        frag_graphs_batch: List[List[GeometricData]],
        adj_batch: Optional[List[torch.Tensor]] = None,
        mass_batch: Optional[List[torch.Tensor]] = None,
    ) -> torch.Tensor:
        device = next(self.parameters()).device
        outs: List[torch.Tensor] = []
        for i, frags in enumerate(frag_graphs_batch):
            z_i = self._encode_fragments(frags).to(device)  # [n_i, d]
            n_i = z_i.size(0)
            # mass feature
            if mass_batch is not None and i < len(mass_batch) and mass_batch[i] is not None:
                m = mass_batch[i].to(device).view(-1, 1)
                if m.size(0) != n_i:
                    if m.size(0) < n_i:
                        pad = n_i - m.size(0)
                        m = torch.cat([m, torch.zeros(pad, 1, device=device)], dim=0)
                    else:
                        m = m[:n_i]
                z_i = z_i + self.mass_mlp(m)
            # adjacency smoothing
            if adj_batch is not None and i < len(adj_batch) and adj_batch[i] is not None and adj_batch[i].numel() > 0:
                A = adj_batch[i].to(device).float()
                n = A.size(0)
                if n != n_i:
                    if n < n_i:
                        pad = n_i - n
                        A = F.pad(A, (0, pad, 0, pad))
                    else:
                        A = A[:n_i, :n_i]
                I = torch.eye(z_i.size(0), device=device)
                A_hat = A + I
                Dinv = torch.diag(1.0 / A_hat.sum(-1).clamp_min(1.0))
                z_i = Dinv @ (A_hat @ z_i)
            # attention pooling
            a = torch.softmax(self.att(z_i).squeeze(-1), dim=-1)  # [n_i]
            z = (a.unsqueeze(-1) * z_i).sum(0, keepdim=True)      # [1, d]
            outs.append(z)
        return torch.cat(outs, dim=0)  # [B, d]

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

    def aggregate(
        self: "EncFragGraph",
        x: torch.Tensor, # [B, V, d_h]
        edges: Optional[torch.Tensor] = None,
        adjacency: Optional[torch.Tensor] = None
        ) -> torch.Tensor: #  [B, V, d_h]
        """
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


class DecSpecLatent(nn.Module):
    """
    Decode a latent vector into a spectrum (no fragment bag input).
    Typically fed with the forward head output of the combined latent.
    """
    def __init__(self, d_in: int, spectrum_bins_size: int):
        super().__init__()
        self.net = mlp(d_in, 512, spectrum_bins_size)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if z.dim() == 1:
            z = z.unsqueeze(0)
        return F.relu(self.net(z))


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


# --------------------------- Parent mass mask ---------------------------
def make_parent_mass_mask_vec(precursor_mass: float, mz_min: float, mz_max: float, bin_width: float, device=None) -> torch.Tensor:
    """Create a hard mask [bins] with 1.0 for bins at or below precursor mass, 0.0 above.

    Bins are interpreted at their lower edges: mz_i = mz_min + i*bin_width.
    """
    n_bins = int((mz_max - mz_min) / bin_width)
    if device is None:
        device = torch.device('cpu')
    edges = torch.arange(n_bins, device=device, dtype=torch.float32) * bin_width + float(mz_min)
    mask = (edges <= float(precursor_mass) + 1e-6).float()
    return mask


def make_parent_mass_mask_batch(smiles_list: List[str], mz_min: float, mz_max: float, bin_width: float, device=None) -> torch.Tensor:
    """Build a [B, bins] hard mask using exact mass from SMILES for each sample."""
    if device is None:
        device = torch.device('cpu')
    masks: List[torch.Tensor] = []
    for s in smiles_list:
        try:
            m = float(mod.Graph.fromSMILES(s).exactMass)
        except Exception:
            m = mz_max  # fallback: no masking
        masks.append(make_parent_mass_mask_vec(m, mz_min, mz_max, bin_width, device=device))
    return torch.stack(masks, dim=0)


def jaccard_binary(a, b, eps=1e-6):
    """
    Computes Jaccard similarity between two binary fragment vectors.
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
    # Vocab-agnostic additions (may be None if not requested)
    frag_graphs: Optional[List[GeometricData]] = None
    frag_adj_local: Optional[torch.Tensor] = None
    frag_masses: Optional[torch.Tensor] = None


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
            mol = mod.Graph.fromSMILES(list(self.frag_coll.keys())[idx])
            graph_feats = self.graph_featurizer(mol)
            specs = self._make_spec(idx)
            # build legacy features lazily
            bags = self._make_frag_bag(idx)
            adjs_fwd, adjs_bwd = self._make_frag_adj(idx)

        # Vocab-agnostic extras
        frag_smiles = self._frag_smiles_for_idx(idx)
        frag_graphs = []
        for smi in frag_smiles:
            try:
                frag_graphs.append(self.graph_featurizer(mod.Graph.fromSMILES(smi)))
            except Exception:
                # skip malformed fragments
                print(f"Warning: mod could not parse fragment SMILES '{smi}'")
                pass
        frag_adj_local = self._local_adj_for_idx(idx)
        frag_masses = self._frag_masses_for_idx(idx)

        return Sample(
            graph_feat=graph_feats,
            frag_bag=bags,  # legacy bag (unused in vocab-less path)
            true_spectrum=specs,
            fragment_adjacency_bwd=adjs_bwd,
            fragment_adjacency_fwd=adjs_fwd,
            smiles=list(self.frag_coll.keys())[idx],
            frag_graphs=frag_graphs,
            frag_adj_local=frag_adj_local,
            frag_masses=frag_masses,
        )

    def _make_frag_adj(
        self,
        idx: int
        ) -> List[torch.Tensor]:
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

    def _make_frag_graph(
        self,
        idx: int,
        direction: str = 'fwd'
        ) -> torch.Tensor:
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

    def _make_frag_bag(
        self,
        idx: int
        ) -> torch.Tensor:
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

    def _make_spec(
        self,
        idx: int
        ) -> torch.Tensor:
        """
        Create a spectral representation for a specific molecule.
        """
        return bin_spectrum(
            self.real_spectra_per_mol[idx],
            self.mz_min,
            self.mz_max,
            self.bin_width
            )

    # ------------------- Vocab-less helpers -------------------
    def _frag_smiles_for_idx(
        self,
        idx: int
        ) -> List[str]:
        fwd_coll, _ = list(self.frag_coll.values())[idx]
        return [t[0] for t in fwd_coll]

    def _frag_masses_for_idx(
        self,
        idx: int
        ) -> torch.Tensor:
        fwd_coll, _ = list(self.frag_coll.values())[idx]
        masses = []
        for frag_smi, exact_mass, _t, _r in fwd_coll:
            m = float(exact_mass)
            if not (m > 0.0):
                try:
                    m = float(mod.Graph.fromSMILES(frag_smi).exactMass)
                except Exception:
                    m = 0.0
            masses.append(m)
        masses_t = torch.tensor(masses, dtype=torch.float32)
        denom = torch.tensor(self.mz_max if self.mz_max > 0 else 1000.0, dtype=torch.float32)
        return (masses_t / denom).clamp_min(0.0)

    def _local_adj_for_idx(
        self,
        idx: int
        ) -> torch.Tensor:
        frag_smiles = self._frag_smiles_for_idx(idx)
        m = {s: i for i, s in enumerate(frag_smiles)}
        n = len(frag_smiles)
        A = torch.zeros(n, n, dtype=torch.float32)
        fwd, _ = list(self.frag_coll.values())[idx]
        for src_smi, _mass, targets, _rules in fwd:
            if src_smi not in m:
                continue
            si = m[src_smi]
            for lst in targets.values():
                for dst in lst:
                    if dst in m:
                        A[si, m[dst]] = 1.0
        return A

    def _precompute_all(self):
        """Materialize tensors to speed up training."""
        graph_feats = []
        bags = []
        specs = []
        adjs_fwd = []
        adjs_bwd = []
        for i in range(len(self)):
            mol = mod.Graph.fromSMILES(list(self.frag_coll.keys())[i])
            graph_feats.append(self.graph_featurizer(mol))
            bags.append(self._make_frag_bag(i))
            specs.append(self._make_spec(i))
            fwd, bwd = self._make_frag_adj(i)
            adjs_fwd.append(fwd)
            adjs_bwd.append(bwd)

        self._cache = list(zip(graph_feats, bags, specs, adjs_fwd, adjs_bwd))
# --- end RealDataset ----------------------------------------------------------



def collate(
    batch: List[Sample]
    ) -> Tuple[List[GeometricData], torch.Tensor, torch.Tensor, List[str], torch.Tensor, torch.Tensor]:
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


def collate_vlex(batch: List[Sample]):
    """
    Collate function for the vocabulary-agnostic path.
    Keeps variable-length fragment lists and returns per-sample adjacency/mass.
    """
    graph_feats = [b.graph_feat for b in batch]
    true_spectrum = torch.stack([b.true_spectrum for b in batch])
    smiles = [b.smiles for b in batch]
    frag_graphs = [b.frag_graphs or [] for b in batch]
    frag_adj_local = [b.frag_adj_local if b.frag_adj_local is not None else torch.zeros(0, 0) for b in batch]
    frag_masses = [b.frag_masses if b.frag_masses is not None else torch.zeros(0) for b in batch]
    return graph_feats, frag_graphs, frag_masses, true_spectrum, smiles, frag_adj_local


# ---------------------------------------------------------------------------
# Training loops
# ---------------------------------------------------------------------------

def train_epoch_phase_a(
    loader: DataLoader,
    device: torch.device,
    enc_mol: EncMol,
    frag_set_enc: FragSetEncoderVocabless,
    heads: TaskHeads,
    dec_spec: DecSpecLatent,
    opt: torch.optim.Optimizer,
    alpha: float = 1.0,
    mz_min: float = 1.0,
    mz_max: float = 1000.0,
    bin_width: float = 1.0,
    beta_forbidden: float = 0.1
) -> float:
    """
    Phase A (vocab-agnostic): molecule + fragment set -> spectrum reconstruction.
    """
    enc_mol.train(); frag_set_enc.train(); dec_spec.train(); heads.train()
    total = 0.0

    for graph_feats, frag_graphs, frag_masses, true_spectrum, smiles, adj_local in loader:
        true_spectrum = true_spectrum.to(device)
        opt.zero_grad()
        z_m = enc_mol(graph_feats)  # [B, d]
        z_f = frag_set_enc(frag_graphs, adj_batch=adj_local, mass_batch=frag_masses)  # [B, d]
        z = (z_m + z_f) / 2
        z_fwd, _ = heads(z)
        spec_hat = dec_spec(z_fwd)
        # parent-mass mask (hard) and forbidden-region penalty
        mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
        spec_hat_masked = spec_hat * mask
        L_spec = cosine_loss(spec_hat_masked, true_spectrum)
        L_forb = (spec_hat * (1.0 - mask)).mean()
        loss = L_spec + beta_forbidden * L_forb
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


def train_epoch_phase_b(
        loader: DataLoader,
        device: torch.device,
        enc_spec: EncSpec,
        enc_mol: EncMol,
        heads: TaskHeads,
        dec_spec: DecSpecLatent,
        opt: torch.optim.Optimizer,
        lam: float = 0.1,
        mz_min: float = 1.0,
        mz_max: float = 1000.0,
        bin_width: float = 1.0,
        beta_forbidden: float = 0.1
        ) -> float:
    """
    Phase B (vocab-agnostic): align spectrum latent with molecular latent and
    reconstruct spectra from the spectrum latent.
    """
    enc_spec.train(); enc_mol.train(); dec_spec.train(); heads.train()
    total = 0.0
    for graph_feats, _frag_graphs, _frag_masses, spec, smiles, _adj_local in loader:
        spec = spec.to(device)
        opt.zero_grad()
        z_m = enc_mol(graph_feats)
        z_s = enc_spec(spec)
        _, z_bwd = heads(z_s)
        L_con = info_nce(z_bwd, z_m)
        spec_hat = dec_spec(z_bwd)
        mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
        spec_hat_masked = spec_hat * mask
        L_spec = cosine_loss(spec_hat_masked, spec)
        L_forb = (spec_hat * (1.0 - mask)).mean()
        loss = L_spec + lam * L_con + beta_forbidden * L_forb
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
    graph_feat: GeometricData
    true_spectrum: torch.Tensor
    # Vocab-agnostic fragment info (optional)
    frag_graphs: Optional[List[GeometricData]] = None
    frag_adj_local: Optional[torch.Tensor] = None
    # Legacy fields (unused in vocab-less path)
    frag_bag: Optional[torch.Tensor] = None
    fragment_adjacency_fwd: Optional[torch.Tensor] = None
    fragment_adjacency_bwd: Optional[torch.Tensor] = None


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
            loader = DataLoader(dataset, batch_size=256, shuffle=False, collate_fn=collate_vlex)
            with torch.no_grad():
                for graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local in loader:
                    z = enc_mol(graph_feats)                     # [B, d]
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


def rerank_candidates(spec_q: torch.Tensor,
                      candidates: List[IndexItem],
                      device,
                      enc_mol: EncMol,
                      frag_set_enc: FragSetEncoderVocabless,
                      heads: TaskHeads,
                      dec_spec: DecSpecLatent,
                      mz_min: float,
                      mz_max: float,
                      bin_width: float) -> List[Tuple[str, float]]:
    """
    Rerank by forward-model spectrum reconstruction cosine similarity.
    """
    enc_mol.eval(); frag_set_enc.eval(); dec_spec.eval(); heads.eval()
    scores: List[Tuple[str, float]] = []
    with torch.no_grad():
        spec_q_n = F.normalize(spec_q.cpu(), dim=-1)
        for it in candidates:
            # recompute candidate latent using stored graph + fragment set
            z_m_c = enc_mol([it.graph_feat.to(device) if hasattr(it.graph_feat, 'to') else it.graph_feat]).squeeze(0)
            frag_graphs_c = it.frag_graphs or []
            adj_c = [it.frag_adj_local.to(device) if (it.frag_adj_local is not None) else torch.zeros(0,0, device=device)]
            z_f_c = frag_set_enc([frag_graphs_c], adj_batch=adj_c)  # [1, d]
            z_c = (z_m_c.unsqueeze(0) + z_f_c) / 2
            z_fwd, _ = heads(z_c)
            spec_hat = dec_spec(z_fwd).cpu().squeeze(0)
            # apply hard parent-mass mask for the candidate before scoring
            try:
                pmass = float(mod.Graph.fromSMILES(it.smiles).exactMass)
            except Exception:
                pmass = mz_max
            mask = make_parent_mass_mask_vec(pmass, mz_min, mz_max, bin_width, device=spec_hat.device)
            spec_hat = spec_hat * mask
            cos = F.cosine_similarity(F.normalize(spec_hat, dim=-1).unsqueeze(0),
                                      spec_q_n.unsqueeze(0), dim=-1).item()
            scores.append((it.smiles, cos))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def infer_mol_to_spec(graph_feat: GeometricData,
                      frag_graphs: List[GeometricData],
                      frag_adj_local: Optional[torch.Tensor],
                      frag_masses: Optional[torch.Tensor],
                      device: torch.device,
                      enc_mol: EncMol,
                      frag_set_enc: FragSetEncoderVocabless,
                      dec_spec: DecSpecLatent,
                      heads: TaskHeads,
                      smiles: Optional[str] = None,
                      mz_min: Optional[float] = None,
                      mz_max: Optional[float] = None,
                      bin_width: Optional[float] = None):
    enc_mol.eval(); frag_set_enc.eval(); dec_spec.eval(); heads.eval()
    with torch.no_grad():
        z_m = enc_mol([graph_feat])  # [1, d]
        adj_batch = [frag_adj_local.to(device)] if (frag_adj_local is not None) else None
        mass_batch = [frag_masses.to(device)] if (frag_masses is not None) else None
        z_f = frag_set_enc([frag_graphs], adj_batch=adj_batch, mass_batch=mass_batch)  # [1, d]
        z = (z_m + z_f) / 2
        z_fwd, _ = heads(z)
        spec_hat = dec_spec(z_fwd).cpu().squeeze(0)
        # optional hard masking at inference
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
                      enc_spec: "EncSpec",
                      enc_mol: "EncMol",
                      frag_set_enc: FragSetEncoderVocabless,
                      heads: TaskHeads,
                      dec_spec: "DecSpecLatent",
                      mz_min: float,
                      mz_max: float,
                      bin_width: float,
                      topk: int = 10) -> List[Tuple[str, float]]:
    """Retrieve and rerank candidate molecules for a given spectrum."""
    enc_spec.eval()
    with torch.no_grad():
        z_q = enc_spec(spec.to(device).unsqueeze(0)).squeeze(0)
        z_q_n = F.normalize(z_q, dim=-1).cpu()
    cands = index.topk(z_q_n, k=topk)
    ranked = rerank_candidates(spec, cands, device, enc_mol, frag_set_enc, heads, dec_spec, mz_min, mz_max, bin_width)
    return ranked


# ----------------------------- DEMOS ---------------------------------

def vec_to_peaks(vec: torch.Tensor, mz_min: float, bin_width: float, top_k: int = 10) -> List[Tuple[float, float]]:
    """Convert a binned spectrum vector into top-K (m/z, intensity) peaks."""
    v = vec.detach().cpu().numpy()
    top_idx = np.argsort(-v)[:max(1, min(top_k, v.shape[0]))]
    peaks = [(mz_min + int(i) * bin_width, float(v[i])) for i in top_idx]
    peaks.sort(key=lambda x: x[0])
    return peaks

def demo_compare_spectrum(graph_feat: GeometricData,
                          frag_graphs: List[GeometricData],
                          frag_masses: torch.Tensor,
                          adj_local: torch.Tensor,
                          true_spec: torch.Tensor,
                          device,
                          enc_mol: "EncMol",
                          frag_set_enc: FragSetEncoderVocabless,
                          dec_spec: "DecSpecLatent",
                          heads: TaskHeads,
                          mz_min: float,
                          bin_width: float,
                          smiles: Optional[str] = None,
                          mz_max: Optional[float] = None,
                          top_k: int = 10) -> Dict[str, Any]:
    """
    Predict spectrum and compare to ground truth:
    - print top-K peaks for prediction and truth
    - report cosine similarity and L1 error
    """
    spec_hat = infer_mol_to_spec(graph_feat, frag_graphs, adj_local, frag_masses, device, enc_mol, frag_set_enc, dec_spec, heads,
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

def demo_retrieval_metrics(index, loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, topk_list=(1,5,10), max_batches=None):
    """Compute Recall@K and MRR on a loader using a train-built index (vocab-agnostic)."""
    enc_spec.eval()
    hits = {k: 0 for k in topk_list}
    mrr = 0.0
    n = 0
    # Infer dataset binning parameters
    try:
        ds = loader.dataset
        mz_min = float(ds.mz_min)
        mz_max = float(ds.mz_max)
        bin_width = float(ds.bin_width)
    except Exception:
        # Fallback guesses if dataset unavailable
        mz_min, mz_max, bin_width = 1.0, 1000.0, 1.0
    with torch.no_grad():
        for bi, (graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local) in enumerate(loader):
            if max_batches is not None and bi >= max_batches:
                break
            B = len(smiles)
            _ = enc_spec(spec.to(device))  # forward pass for completeness
            for i in range(B):
                ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec,
                                           mz_min=mz_min, mz_max=mz_max, bin_width=bin_width,
                                           topk=max(topk_list))
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


def demo_ablate_adjacency(graph_feat: GeometricData,
                          frag_graphs: List[GeometricData],
                          adj_local: torch.Tensor,
                          frag_masses: torch.Tensor,
                          true_spec: torch.Tensor,
                          smiles: Optional[str],
                          mz_min: float,
                          mz_max: float,
                          bin_width: float,
                          device,
                          enc_mol: "EncMol",
                          frag_set_enc: FragSetEncoderVocabless,
                          dec_spec: "DecSpecLatent",
                          heads: TaskHeads):
    """Compare spectrum reconstruction with local adjacency vs zero adjacency smoothing."""
    with torch.no_grad():
        spec_hat_graph = infer_mol_to_spec(graph_feat, frag_graphs, adj_local, frag_masses, device, enc_mol, frag_set_enc, dec_spec, heads,
                                           smiles=smiles, mz_min=mz_min, mz_max=mz_max, bin_width=bin_width)
        spec_hat_none = infer_mol_to_spec(graph_feat, frag_graphs, torch.zeros_like(adj_local), frag_masses, device, enc_mol, frag_set_enc, dec_spec, heads,
                                          smiles=smiles, mz_min=mz_min, mz_max=mz_max, bin_width=bin_width)
        cos_graph = F.cosine_similarity(F.normalize(spec_hat_graph, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
        cos_none = F.cosine_similarity(F.normalize(spec_hat_none, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
    return {"cos_with_adj": cos_graph, "cos_no_adj": cos_none, "diff": cos_graph - cos_none}


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


def demo_noise_robustness(index, loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5):
    """Add Gaussian noise to spectra and plot/return Recall@K vs noise level."""
    results = {}
    # Infer dataset binning parameters
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
            for bi, (graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local) in enumerate(loader):
                if bi >= max_batches:
                    break
                B = len(smiles)
                spec_noisy = spec + s * torch.randn_like(spec)
                # normalize
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
    graph_feats, frag_graphs, frag_masses, true_spec, smiles, adj_local, device,
    enc_mol, frag_set_enc, dec_spec, heads, n_samples=3
    ) -> bool:
    """Plot true vs reconstructed spectra for n_samples molecules."""
    n = min(n_samples, len(smiles))
    for i in range(n):
        # Try to infer dataset binning from vector length and assume mz_min=1.0, bin_width=1.0 if unavailable
        # Call without mask to keep this lightweight visualization generic
        spec_hat = infer_mol_to_spec(graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], device, enc_mol, frag_set_enc, dec_spec, heads)
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
        mol = mod.Graph.fromSMILES(smi, name=name)
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
        test_size=0.2,
        random_state=42,
        shuffle=False
        )
    train_frags, test_frags = train_test_split(
        data = frag_coll,
        test_size=0.2,
        random_state=42,
        shuffle=False
    )

    train_spect, vali_spect = train_test_split(
        train_spect,
        test_size=.3,
        random_state=42,
        shuffle=False
    )
    train_frags, vali_frags = train_test_split(
        train_frags,
        test_size=0.3,
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
    spectrum_bins_size = train_ds.spectrum_bins_size


    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=False, drop_last=False, collate_fn=collate_vlex)
    val_loader   = DataLoader(vali_ds, batch_size=args.batch, shuffle=False, collate_fn=collate_vlex)
    test_loader  = DataLoader(test_ds, batch_size=args.batch, shuffle=False, collate_fn=collate_vlex)

    # Models
    enc_mol  = EncMol(args.latent).to(device)
    frag_set_enc = FragSetEncoderVocabless(enc_mol, d_latent=args.latent).to(device)
    enc_spec = EncSpec(spectrum_bins_size, args.latent).to(device)
    dec_spec = DecSpecLatent(d_in=args.latent, spectrum_bins_size=spectrum_bins_size).to(device)
    # Task heads (shared trunk projections)
    heads = TaskHeads(d_latent=args.latent, d_task=args.latent).to(device)
    # expose for helper functions (script-level convenience)
    globals()['heads'] = heads

    # Optimizers (separate per phase keeps it simple)
    opt_a = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(frag_set_enc.parameters()) +
                             list(dec_spec.parameters()) +
                             list(heads.parameters()), lr=args.lr)
    opt_b = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(enc_spec.parameters()) +
                             list(dec_spec.parameters()) +
                             list(heads.parameters()), lr=args.lr)

    # ----------------- Phase A -----------------
    print("== Phase A: train forward (vocab-agnostic) ==")
    for epoch in range(1, args.epochs_fwd + 1):
        loss = train_epoch_phase_a(
            train_loader, device, enc_mol, frag_set_enc, heads, dec_spec, opt_a,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1
        )
        print(f"[A] epoch {epoch:02d} loss {loss:.4f}")

    # ----------------- Phase B -----------------
    print("== Phase B: align spec latent + spectrum recon (vocab-agnostic) ==")
    for epoch in range(1, args.epochs_bwd + 1):
        loss = train_epoch_phase_b(
            train_loader, device, enc_spec, enc_mol, heads, dec_spec, opt_b,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1
        )
        print(f"[B] epoch {epoch:02d} loss {loss:.4f}")

    # ----------------- Build retrieval index -----------------
    print("== Building retrieval index on TRAIN set ==")
    index = LatentIndex(d=args.latent)
    index.build(train_ds, device, enc_mol)


    # ----------------- Demo: Structure - > Spectrum -----------------
    graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local = next(iter(test_loader))
    i = 0
    spec_hat = infer_mol_to_spec(
        graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], device,
        enc_mol, frag_set_enc, dec_spec, heads,
        smiles=smiles[i], mz_min=test_ds.mz_min, mz_max=test_ds.mz_max, bin_width=test_ds.bin_width
    )
    cos_sim = F.cosine_similarity(
        F.normalize(spec_hat, dim=-1).unsqueeze(0),
        F.normalize(spec[i], dim=-1).unsqueeze(0),
        dim=-1
    ).item()
    print(f"Mol->Spec for {smiles[i]} | cosine={cos_sim:.3f}")

    # ----------------- Demo: Compare to ground truth spectrum -----------------
    print("== Demo: Compare predicted vs ground truth (TEST sample) ==")
    _ = demo_compare_spectrum(
        graph_feats[i], frag_graphs[i], frag_masses[i], adj_local[i], spec[i], device,
        enc_mol, frag_set_enc, dec_spec, heads,
        mz_min=test_ds.mz_min, bin_width=test_ds.bin_width, smiles=smiles[i], mz_max=test_ds.mz_max, top_k=10
    )

    # ----------------- Demo: Spectrum - > Structure -----------------
    print("== Demo: Spec -> Mol retrieval + re-ranking on the same VAL sample ==")
    ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec,
                               mz_min=test_ds.mz_min, mz_max=test_ds.mz_max, bin_width=test_ds.bin_width, topk=10)
    print("Top-5 candidates:")
    print(f"{'SMILES':>40s} | {'Score':>8s}")
    print("-" * 50)
    for s, sc in ranked[:5]:
        print(f"{s:>40s} | {sc:8.3f}")

    # ----------------- Demo: Retrieval metrics on VAL/TEST -----------------
    print("== Retrieval metrics (VAL) ==")
    val_metrics = demo_retrieval_metrics(index, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, topk_list=(1,5,10), max_batches=5)
    print(val_metrics)
    print("== Retrieval metrics (TEST) ==")
    test_metrics = demo_retrieval_metrics(index, test_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, topk_list=(1,5,10), max_batches=5)
    print(test_metrics)
    # ----------------- Demo: Fragment graph ablation -----------------
    print("== Graph ablation on one VAL sample ==")
    ablation = demo_ablate_adjacency(graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], spec[i],
                                     smiles[i], test_ds.mz_min, test_ds.mz_max, test_ds.bin_width,
                                     device, enc_mol, frag_set_enc, dec_spec, heads)
    print(ablation)

    # ----------------- Demo: Spectrum noise robustness -----------------
    print("== Spectrum noise robustness (VAL subset) ==")
    noise_res = demo_noise_robustness(index, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5)
    print(noise_res)

    # ----------------- Demo: Visualization of reconstructions -----------------
    print("== Visualization: saving recon plots for a few VAL samples ==")
    _ = demo_visualize_reconstructions(graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, device, enc_mol, frag_set_enc, dec_spec, heads, n_samples=3)

    # save checkpoint
    ckpt = {
        "enc_mol": enc_mol.state_dict(),
        "frag_set_enc": frag_set_enc.state_dict(),
        "enc_spec": enc_spec.state_dict(),
        "dec_spec": dec_spec.state_dict(),
        "heads": heads.state_dict(),
        "args": vars(args),
    }
    torch.save(ckpt, "mini_frag_checkpoint.pt")
    print("Saved checkpoint to mini_frag_checkpoint.pt")

if __name__ == "__main__":
    main()
