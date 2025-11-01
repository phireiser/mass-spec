"""
FRAG: Fragment-Aided Bidirectional Model (vocab-less path)
================================================================

Summary
-------
Learning *molecule <-> spectrum* mappings with fragment-level assistance.
The current entrypoint trains a **vocabulary-less** path that embeds (i)
molecular graphs and (ii) *sets* of fragment graphs, aligns spectrum and
molecule latents, builds a retrieval index, and runs lightweight demos
(reconstruction, retrieval, ablation, noise robustness, and plotting).

Pipeline (what actually runs)
-----------------------------
Phase A (forward):
    z_m = EncMol(molecule_graphs)
    z_f = FragSetEncoderVocabless(fragment_graph_set, optional local adj + masses)
    z   = (z_m + z_f) / 2
    spec_hat = DecSpecLatent(Head_fwd(z))
    Loss = cosine(spec_hat·mask(parent_mass), true_spec) + forbidden-penalty

Phase B (backward/alignment):
    z_s  = EncSpec(binned_spectrum)
    z_m  = EncMol(molecule_graphs)
    Loss = cosine(DecSpecLatent(Head_bwd(z_s))·mask, true_spec)
         + InfoNCE(z_bwd=z_s→Head_bwd, z_m)

Retrieval:
    • Build a cosine index over normalized EncMol embeddings (train set).
    • Query: z_q = EncSpec(spec) → top-K by cosine in the index.
    • Re-rank: run forward model for each candidate and score by spectrum-cosine
      after parent-mass masking.

Main components (used by default)
---------------------------------
Encoders / Decoders:
    - EncMol(d_latent): GCN -> global mean pool for molecular graphs.
    - FragSetEncoderVocabless(enc_mol, d_latent): encodes *lists* of fragment
      graphs with attention pooling; optionally smooths with local adjacency and
      injects per-fragment normalized mass.
    - EncSpec(spectrum_bins, d_latent): MLP over binned spectra.
    - TaskHeads(d_latent): small projections for forward/backward heads.
    - DecSpecLatent(d_in, spectrum_bins): MLP to reconstruct spectra from a latent.

Utilities:
    - RealDataset: builds samples from `frag_coll` + raw peak lists; bins spectra,
      assembles per-molecule fragment graph lists, local fragment adjacency, and
      normalized fragment masses.
    - LatentIndex: in-memory cosine index for molecule retrieval.
    - Losses: `cosine_loss`, `info_nce`; masking helpers for parent mass.
    - Demos: `demo_compare_spectrum`, `demo_retrieval_metrics`,
      `demo_ablate_adjacency`, `demo_noise_robustness`, `demo_visualize_reconstructions`.
    - `train_test_split` helper for lists / dicts.

Data expectations
-----------------
- `frag_coll: Dict[str, Tuple[List[FWD], List[BWD]]]`
  where each FWD/BWD item is `(frag_smiles, exact_mass, targets_dict, rules_dict)`.
- `real_spectra_per_mol: List[List[Tuple[m/z, intensity]]]` (same order as `frag_coll` keys).
- Spectra are binned to length `floor((mz_max - mz_min) / bin_width)`; defaults:
  `mz_min=1.0, mz_max=1000.0, bin_width=1.0`, with sqrt+L2 normalization.

CLI (example)
-------------
    python this_file.py --epochs_fwd 3 --epochs_bwd 3 --latent 128

Key arguments:
    --epochs_fwd / --epochs_bwd   Training epochs for Phase A / B.
    --batch                       Batch size (default 128).
    --latent                      Latent dimensionality (default 128).
    --lr                          Learning rate (default 2e-4).
    --device                      "cuda" or "cpu".
    --seed                        RNG seed.

Outputs
-------
- Console logs of per-epoch losses and demo metrics.
- Retrieval printout with top-K candidate SMILES and scores.
- Figures: `noise_robustness.png`, `recon_*.png`.
- Checkpoint: `frag_checkpoint.pt` containing state dicts for Encoders,
  Heads, and DecSpecLatent, plus CLI args.

Dependencies
------------
- PyTorch, PyTorch Geometric
- `mod` (MØD Python bindings) for molecule parsing/mass, plus project modules:
  `mass_spec_modeling.machine_learning.utils_mod`,
  `mass_spec_modeling.mod_fragmentation.utils`,
  `mass_spec_modeling.machine_learning.featurizers.GraphFeaturizerMOD`
- Matplotlib (optional; for plots)

Author
------
(c) 2025 Philipp Reiser
"""


import argparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Union, Any

from pathlib import Path
import numpy as np
import random

import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
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

def mlp(
    d_in: int,
    d_hidden: int,
    d_out: int
    ) -> nn.Sequential:
    """
    Builds a small feed-forward MLP block.
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
    def __init__(
        self,
        d_node_in: int = 3,
        d_latent: int = 128,
        dropout: float = 0.1
        ) -> None:
        super().__init__()
        self.gnn1 = GCNConv(d_node_in, 64)
        self.gnn2 = GCNConv(64, d_latent)
        self.dropout = nn.Dropout(dropout)
        self.global_mean_pool = global_mean_pool

    def forward(
        self,
        batch_graphs: List[GeometricData]
        ):
        """
        Compute molecule embeddings from a batch of graphs.
        """
        device = next(self.parameters()).device
        batch = Batch.from_data_list(batch_graphs).to(device)
        x = batch.x.float()
        edge_index = batch.edge_index
        x1 = F.relu(self.gnn1(x, edge_index))
        x1 = self.dropout(x1)
        x2 = self.gnn2(x1, edge_index)
        pooled = self.global_mean_pool(x2, batch.batch)
        return pooled

class EncSpec(nn.Module):
    """
    Encodes a binned mass spectrum  into latent space.
    """
    def __init__(self, spectrum_bins_size,  d_latent=128):
        super().__init__()
        self.net = mlp(spectrum_bins_size , 512, d_latent)

    def forward(self, spec):
        return self.net(spec.float())


class TaskHeads(nn.Module):
    """
    Shared trunk heads for forward and backward tasks.

    Each head is a lightweight residual block: Linear -> ReLU -> (+ residual) -> LayerNorm.
    If d_task != d_latent, the residual path uses a linear projection.
    """
    def __init__(
        self,
        d_latent: int = 128,
        d_task: int = 128
        ) -> None:
        super().__init__()
        # Forward head
        self.fwd_fc = nn.Linear(d_latent, d_task)
        self.fwd_ln = nn.LayerNorm(d_task)
        self.fwd_res = nn.Identity() if d_task == d_latent else nn.Linear(d_latent, d_task, bias=False)
        # Backward head
        self.bwd_fc = nn.Linear(d_latent, d_task)
        self.bwd_ln = nn.LayerNorm(d_task)
        self.bwd_res = nn.Identity() if d_task == d_latent else nn.Linear(d_latent, d_task, bias=False)

        # Initialize residual projections conservatively if used
        if not isinstance(self.fwd_res, nn.Identity):
            nn.init.xavier_uniform_(self.fwd_res.weight)
        if not isinstance(self.bwd_res, nn.Identity):
            nn.init.xavier_uniform_(self.bwd_res.weight)

    def forward(
        self,
        z: torch.Tensor
        ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute forward and backward head outputs.
        """
        # Forward path
        h_f = F.relu(self.fwd_fc(z))
        y_f = self.fwd_ln(h_f + self.fwd_res(z))
        # Backward path
        h_b = F.relu(self.bwd_fc(z))
        y_b = self.bwd_ln(h_b + self.bwd_res(z))
        return y_f, y_b

class FragSetEncoderVocabless(nn.Module):
    """
    Encode a variable-size set of fragment graphs using EncMol as a backbone
    and attention pooling; optionally smooth with local adjacency and inject
    per-fragment normalized mass as a feature.
    """
    def __init__(
        self,
        enc_mol: "EncMol",
        d_latent: int,
        adj_beta: float = 1.5,
        adj_gamma: float = 0.2,
        capture_diag: bool = False
        ) -> None:
        super().__init__()
        self.enc_mol = enc_mol
        # Adjacency smoothing hyperparameters
        # beta: self-loop weight (A_tilde = A + beta*I)
        # gamma: residual gate for smoothing strength (z <- (1-gamma) z + gamma z_smooth)
        self.adj_beta = float(adj_beta)
        self.adj_gamma = float(adj_gamma)
        # Diagnostics capture (lightweight)
        self.capture_diag = bool(capture_diag)
        self._last_diag: List[Dict[str, float]] = []
        self.mass_mlp = nn.Sequential(nn.Linear(1, d_latent), nn.Tanh())
        # Gated attention: slightly stronger than narrower bottleneck
        self.att = nn.Sequential(
            nn.Linear(d_latent, d_latent), nn.Tanh(),
            nn.Linear(d_latent, 1)
        )

    def _encode_fragments(
        self,
        frags: List[GeometricData]
        ) -> torch.Tensor:
        """
        Encode a list of fragment graphs into latent vectors.
        """
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
        ) -> torch.Tensor:   # [B, d]
        """
        Encode a batch of fragment graph sets into latent vectors.
        """
        device = next(self.parameters()).device
        outs: List[torch.Tensor] = []
        for i, frags in enumerate(frag_graphs_batch):
            z_i = self._encode_fragments(frags).to(device)  # [n_i, d]
            n_i = z_i.size(0)
            # track pre-smoothing variance
            var_pre = float(z_i.var().detach().cpu().item()) if n_i > 0 else 0.0
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
            # adjacency smoothing (symmetric normalization + gated residual)
            mean_deg = 0.0
            if (
                adj_batch is not None and i < len(adj_batch) and adj_batch[i] is not None and
                adj_batch[i].numel() > 0 and n_i > 0 and self.adj_gamma > 0.0
            ):
                A = adj_batch[i].to(device).float()
                n = A.size(0)
                if n != n_i:
                    if n < n_i:
                        pad = n_i - n
                        A = F.pad(A, (0, pad, 0, pad))
                    else:
                        A = A[:n_i, :n_i]
                # compute degree on original A (no self) for diagnostics
                if n_i > 0:
                    mean_deg = float(A.sum(-1).mean().detach().cpu().item())
                I = torch.eye(n_i, device=device)
                A_tilde = A + self.adj_beta * I
                deg = A_tilde.sum(-1).clamp_min(1.0)
                D_inv_sqrt = torch.diag(torch.pow(deg, -0.5))
                z_smooth = D_inv_sqrt @ (A_tilde @ (D_inv_sqrt @ z_i))
                # gated residual blend
                gamma = self.adj_gamma
                z_i = (1.0 - gamma) * z_i + gamma * z_smooth
            # attention pooling
            a = torch.softmax(self.att(z_i).squeeze(-1), dim=-1)  # [n_i]
            z = (a.unsqueeze(-1) * z_i).sum(0, keepdim=True)      # [1, d]
            if self.capture_diag:
                # avoid log(0)
                ent = float((-(a + 1e-8).log() * a).sum().detach().cpu().item()) if n_i > 0 else 0.0
                var_post = float(z_i.var().detach().cpu().item()) if n_i > 0 else 0.0
                self._last_diag.append({
                    "n_frag": float(n_i),
                    "att_entropy": ent,
                    "var_pre": var_pre,
                    "var_post": var_post,
                    "mean_degree": mean_deg,
                    "adj_beta": float(self.adj_beta),
                    "adj_gamma": float(self.adj_gamma),
                })
            outs.append(z)
        return torch.cat(outs, dim=0)

    def get_and_clear_diagnostics(
        self
        ) -> List[Dict[str, float]]:
        out = self._last_diag
        self._last_diag = []
        return out


class DecSpecLatent(nn.Module):
    """
    Decode a latent vector into a spectrum (no fragment bag input).
    Typically fed with the forward head output of the combined latent.
    """
    def __init__(
        self,
        d_in: int,
        spectrum_bins_size: int
        ) -> None:
        super().__init__()
        self.net = mlp(d_in, 512, spectrum_bins_size)

    def forward(
        self,
        z: torch.Tensor
        ) -> torch.Tensor:
        """
        Decode latent vector into spectrum bins.
        """
        if z.dim() == 1:
            z = z.unsqueeze(0)
        return F.relu(self.net(z))


# ---------------------------------------------------------------------------
# Loss and similarity utilities
# ---------------------------------------------------------------------------

def cosine_loss(
    x: torch.Tensor,
    y: torch.Tensor
    ) -> float:
    """
    Computes 1 - mean cosine similarity between two tensors.
    """
    x_n = F.normalize(x, dim=-1)
    y_n = F.normalize(y, dim=-1)
    return 1.0 - (x_n * y_n).sum(dim=-1).mean()


def info_nce(
    z_q: torch.Tensor,
    z_k: torch.Tensor,
    T: float =0.07
    ):
    """
    InfoNCE contrastive loss between query and key embeddings.
    """
    z_q = F.normalize(z_q, dim=-1)
    z_k = F.normalize(z_k, dim=-1)
    logits = z_q @ z_k.T / T
    labels = torch.arange(z_q.size(0), device=z_q.device)
    return F.cross_entropy(logits, labels)


# --------------------------- Parent mass mask ---------------------------
def make_parent_mass_mask_vec(
    precursor_mass: float,
    mz_min: float,
    mz_max: float,
    bin_width: float,
    device=None
    ) -> torch.Tensor:
    """
    Create a hard mask [bins] with 1.0 for bins at or below precursor mass, 0.0 above.
    Bins are interpreted at their lower edges: mz_i = mz_min + i*bin_width.
    """
    n_bins = int((mz_max - mz_min) / bin_width)
    if device is None:
        device = torch.device('cpu')
    edges = torch.arange(n_bins, device=device, dtype=torch.float32) * bin_width + float(mz_min)
    mask = (edges <= float(precursor_mass) + 1e-6).float()
    return mask


def make_parent_mass_mask_batch(
    smiles_list: List[str],
    mz_min: float,
    mz_max: float,
    bin_width: float,
    device: Optional[torch.device] = None
    ) -> torch.Tensor:
    """
    Build a [B, bins] hard mask using exact mass from SMILES for each sample.
    """
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


def get_binning_from_loader(
    loader: DataLoader
    ) -> Tuple[float, float, float]:
    """
    Extract (mz_min, mz_max, bin_width) from a DataLoader's dataset with safe fallback.
    """
    try:
        ds = loader.dataset
        return float(ds.mz_min), float(ds.mz_max), float(ds.bin_width)
    except Exception:
        return 1.0, 1000.0, 1.0

@dataclass
class Sample:
    """
    Container for one dataset sample. So one molecule with its derivation graph
    """
    graph_feat: GeometricData
    true_spectrum: torch.Tensor
    smiles: str
    frag_graphs: Optional[List[GeometricData]] = None
    frag_adj_local: Optional[torch.Tensor] = None
    frag_masses: Optional[torch.Tensor] = None


# ---------------------------------------------------------------------------
# RealDataset + helpers
# ---------------------------------------------------------------------------

# ---------- Spectrum binning ----------
def compute_bin_index(
    mz: float,
    mz_min: float,
    mz_max: float,
    bin_width: float
    ) -> Optional[int]:
    """
    Compute the bin index for a given m/z value.
    """
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
        precompute: bool = True, # Pre-build for speed
        ) -> None:
        """
        Initialize the dataset.
        """
        self.real_spectra_per_mol = real_spectra_per_mol # ground truth spectra
        self.frag_coll = frag_coll

        self.mz_min = float(mz_min)
        self.mz_max = float(mz_max)
        self.bin_width = float(bin_width)
        self.spectrum_bins_size = int((self.mz_max - self.mz_min) / self.bin_width)  # spectrum length

        assert len(frag_coll.keys()) == len(real_spectra_per_mol), \
            "Fragment collections and spectra must have the same number of molecules."
        self.graph_featurizer = GraphFeaturizerMOD()
        self._cache = None
        if precompute:
            self._precompute_all()

    def __len__(
        self
        ) -> int:
        return len(self.frag_coll.keys())

    def __getitem__(
        self,
        idx: int
        ) -> Sample:
        if self._cache is not None:
            graph_feats, specs = self._cache[idx]
        else:
            mol = mod.Graph.fromSMILES(list(self.frag_coll.keys())[idx])
            graph_feats = self.graph_featurizer(mol)
            specs = self._make_spec(idx)

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
            true_spectrum=specs,
            smiles=list(self.frag_coll.keys())[idx],
            frag_graphs=frag_graphs,
            frag_adj_local=frag_adj_local,
            frag_masses=frag_masses,
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
        """
        Get fragment SMILES for a specific molecule.
        """
        fwd_coll, _ = list(self.frag_coll.values())[idx]
        return [t[0] for t in fwd_coll]

    def _frag_masses_for_idx(
        self,
        idx: int
        ) -> torch.Tensor:
        """
        Get normalized (to 1.0) fragment masses for a specific molecule.
        """
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

    def _precompute_all(
        self
        ) -> None:
        """
        Precompute all graph features and spectra for speed.
        """
        graph_feats = []
        specs = []
        for i in range(len(self)):
            mol = mod.Graph.fromSMILES(list(self.frag_coll.keys())[i])
            graph_feats.append(self.graph_featurizer(mol))
            specs.append(self._make_spec(i))
        self._cache = list(zip(graph_feats, specs))
# --- end RealDataset ----------------------------------------------------------



def collate_vlex(
    batch: List[Sample]
    ) -> Tuple[
        List[GeometricData],
        List[List[GeometricData]],
        List[torch.Tensor],
        torch.Tensor,
        List[str],
        List[torch.Tensor]
        ]:
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
    dec_spec_fwd: DecSpecLatent,
    opt: torch.optim.Optimizer,
    scaler: torch.cuda.amp.GradScaler,
    alpha: float = 1.0,
    mz_min: float = 1.0,
    mz_max: float = 1000.0,
    bin_width: float = 1.0,
    beta_forbidden: float = 0.1
    ) -> float:
    """
    Phase A (vocab-agnostic): molecule + fragment set -> spectrum reconstruction.
    """
    enc_mol.train(); frag_set_enc.train(); dec_spec_fwd.train(); heads.train()
    total = 0.0

    for graph_feats, frag_graphs, frag_masses, true_spectrum, smiles, adj_local in loader:
        true_spectrum = true_spectrum.to(device)
        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type='cuda', enabled=(device.type == "cuda")):
            z_m = enc_mol(graph_feats)  # [B, d]
            z_f = frag_set_enc(frag_graphs, adj_batch=adj_local, mass_batch=frag_masses)  # [B, d]
            z = (z_m + z_f) / 2
            z_fwd, _ = heads(z)
            spec_hat = dec_spec_fwd(z_fwd)
            # parent-mass mask (hard) and forbidden-region penalty
            mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
            spec_hat_masked = spec_hat * mask
            L_spec = cosine_loss(spec_hat_masked, true_spectrum)
            L_forb = (spec_hat * (1.0 - mask)).mean()
            loss = L_spec + beta_forbidden * L_forb
        scaler.scale(loss).backward()
        # Unscale for clipping
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(
            list(enc_mol.parameters()) + list(frag_set_enc.parameters()) + list(dec_spec_fwd.parameters()) + list(heads.parameters()),
            max_norm=1.0
        )
        scaler.step(opt)
        scaler.update()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


def train_epoch_phase_b(
    loader: DataLoader,
    device: torch.device,
    enc_spec: EncSpec,
    enc_mol: EncMol,
    frag_set_enc: FragSetEncoderVocabless,
    heads: TaskHeads,
    dec_spec_bwd: DecSpecLatent,
    dec_spec_fwd: DecSpecLatent,
    opt: torch.optim.Optimizer,
    scaler: torch.cuda.amp.GradScaler,
    lam_con: float = 0.1,
    lam_latent: float = 0.0,
    lam_fwd_in_b: float = 0.0,
    mz_min: float = 1.0,
    mz_max: float = 1000.0,
    bin_width: float = 1.0,
    beta_forbidden: float = 0.1
    ) -> float:
    """
    Phase B: Backward:

    """
    enc_spec.train(); enc_mol.train(); dec_spec_bwd.train(); heads.train()
    total = 0.0
    for graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local in loader:
        spec = spec.to(device)
        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type='cuda', enabled=(device.type == "cuda")):
            z_m = enc_mol(graph_feats)
            z_s = enc_spec(spec)
            # Backward: spec -> latent
            _, z_bwd = heads(z_s)
            L_con = info_nce(z_bwd, z_m)
            spec_hat_bwd = dec_spec_bwd(z_bwd)
            mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
            spec_hat_bwd_masked = spec_hat_bwd * mask
            L_spec_bwd = cosine_loss(spec_hat_bwd_masked, spec)
            L_forb = (spec_hat_bwd * (1.0 - mask)).mean()

            # Optional: forward latent from mol+frags for consistency and/or extra recon
            loss_extra = 0.0
            if (lam_latent > 0.0) or (lam_fwd_in_b > 0.0):
                z_f = frag_set_enc(frag_graphs, adj_batch=adj_local, mass_batch=frag_masses)
                z_mf = (z_m + z_f) / 2
                z_fwd, _ = heads(z_mf)
                if lam_latent > 0.0:
                    L_lat = cosine_loss(z_fwd, z_bwd)
                    loss_extra = loss_extra + lam_latent * L_lat
                if lam_fwd_in_b > 0.0:
                    # Use the forward decoder here but do not update its params in Phase B
                    spec_hat_fwd = dec_spec_fwd(z_fwd)
                    spec_hat_fwd_masked = spec_hat_fwd * mask
                    L_spec_fwd = cosine_loss(spec_hat_fwd_masked, spec)
                    L_forb = L_forb + (spec_hat_fwd * (1.0 - mask)).mean()
                    loss_extra = loss_extra + lam_fwd_in_b * L_spec_fwd

            loss = L_spec_bwd + lam_con * L_con + loss_extra + beta_forbidden * L_forb
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(
            list(enc_mol.parameters()) +
            list(enc_spec.parameters()) +
            list(dec_spec_bwd.parameters()) +
            list(heads.parameters()),
            max_norm=1.0
        )
        scaler.step(opt)
        scaler.update()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


# ---------------------------------------------------------------------------
# Retrieval and inference helpers
# ---------------------------------------------------------------------------

@dataclass
class IndexItem:
    """
    Entry in the molecule latent index.
    """
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
    def __init__(
        self,
        d: int
        ) -> None:
        self.d = d
        self.embs: List[torch.Tensor] = []
        self.items: List[IndexItem] = []

    def build(
        self,
        dataset: Dataset,
        device: torch.device,
        enc_mol: EncMol
        ) -> None:
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
                        adj = adj_local[i]
                        if not isinstance(adj, torch.Tensor):
                            adj = torch.zeros(0, 0)
                        self.items.append(IndexItem(
                            z=z[i],
                            smiles=smiles[i],
                            graph_feat=graph_feats[i],
                            frag_graphs=frag_graphs[i],
                            frag_adj_local=adj.cpu(),
                            true_spectrum=spec[i].cpu(),
                        ))
            self.embs = torch.stack(self.embs, 0)

    def topk(
        self,
        z_query: torch.Tensor,
        k: int =10
        ) -> List[IndexItem]:
        """
        Retrieves the top-k most similar molecules by cosine similarity.
        """
        sims = (self.embs @ z_query)
        topv, topi = torch.topk(sims, k=min(k, sims.numel()))
        return [self.items[i] for i in topi.tolist()]


def rerank_candidates(
    spec_q: torch.Tensor,
    candidates: List[IndexItem],
    device,
    enc_mol: EncMol,
    frag_set_enc: FragSetEncoderVocabless,
    heads: TaskHeads,
    dec_spec_fwd: DecSpecLatent,
    mz_min: float,
    mz_max: float,
    bin_width: float
    ) -> List[Tuple[str, float]]:
    """
    Rerank by forward-model spectrum reconstruction cosine similarity.
    """
    enc_mol.eval(); frag_set_enc.eval(); dec_spec_fwd.eval(); heads.eval()
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
            spec_hat = dec_spec_fwd(z_fwd).cpu().squeeze(0)
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


def infer_mol_to_spec(
    graph_feat: GeometricData,
    frag_graphs: List[GeometricData],
    frag_adj_local: Optional[torch.Tensor],
    frag_masses: Optional[torch.Tensor],
    device: torch.device,
    enc_mol: EncMol,
    frag_set_enc: FragSetEncoderVocabless,
    dec_spec_fwd: DecSpecLatent,
    heads: TaskHeads,
    smiles: Optional[str] = None,
    mz_min: Optional[float] = None,
    mz_max: Optional[float] = None,
    bin_width: Optional[float] = None
    ) -> torch.Tensor:
    """
    Predict spectrum from molecule and fragment set.
    """
    enc_mol.eval(); frag_set_enc.eval(); dec_spec_fwd.eval(); heads.eval()
    with torch.no_grad():
        z_m = enc_mol([graph_feat])  # [1, d]
        adj_batch = [frag_adj_local.to(device)] if (frag_adj_local is not None) else None
        mass_batch = [frag_masses.to(device)] if (frag_masses is not None) else None
        z_f = frag_set_enc([frag_graphs], adj_batch=adj_batch, mass_batch=mass_batch)  # [1, d]
        z = (z_m + z_f) / 2
        z_fwd, _ = heads(z)
        spec_hat = dec_spec_fwd(z_fwd).cpu().squeeze(0)
        # optional hard masking at inference
        if (smiles is not None) and (mz_min is not None) and (mz_max is not None) and (bin_width is not None):
            try:
                pmass = float(mod.Graph.fromSMILES(smiles).exactMass)
            except Exception:
                pmass = mz_max
            mask = make_parent_mass_mask_vec(pmass, mz_min, mz_max, bin_width, device=spec_hat.device)
            spec_hat = spec_hat * mask
    return spec_hat



def infer_spec_to_mol(
    spec: torch.Tensor,
    index: LatentIndex,
    device,
    enc_spec: "EncSpec",
    enc_mol: "EncMol",
    frag_set_enc: FragSetEncoderVocabless,
    heads: TaskHeads,
    dec_spec_fwd: "DecSpecLatent",
    mz_min: float,
    mz_max: float,
    bin_width: float,
    topk: int = 10
    ) -> List[Tuple[str, float]]:
    """
    Retrieve and rerank candidate molecules for a given spectrum.
    """
    enc_spec.eval()
    with torch.no_grad():
        z_q = enc_spec(spec.to(device).unsqueeze(0)).squeeze(0)
        z_q_n = F.normalize(z_q, dim=-1).cpu()
    cands = index.topk(z_q_n, k=topk)
    ranked = rerank_candidates(spec, cands, device, enc_mol, frag_set_enc, heads, dec_spec_fwd, mz_min, mz_max, bin_width)
    return ranked


# ----------------------------- DEMOS ---------------------------------

def vec_to_peaks(
    vec: torch.Tensor,
    mz_min: float,
    bin_width: float,
    top_k: int = 10
    ) -> List[Tuple[float, float]]:
    """
    Convert a binned spectrum vector into top-K (m/z, intensity) peaks.
    """
    v = vec.detach().cpu().numpy()
    top_idx = np.argsort(-v)[:max(1, min(top_k, v.shape[0]))]
    peaks = [(mz_min + int(i) * bin_width, float(v[i])) for i in top_idx]
    peaks.sort(key=lambda x: x[0])
    return peaks

def demo_compare_spectrum(
    graph_feat: GeometricData,
    frag_graphs: List[GeometricData],
    frag_masses: torch.Tensor,
    adj_local: torch.Tensor,
    true_spec: torch.Tensor,
    device,
    enc_mol: "EncMol",
    frag_set_enc: FragSetEncoderVocabless,
    dec_spec_fwd: "DecSpecLatent",
    heads: TaskHeads,
    mz_min: float,
    bin_width: float,
    smiles: Optional[str] = None,
    mz_max: Optional[float] = None,
    top_k: int = 10
    ) -> Dict[str, Any]:
    """
    Predict spectrum and compare to ground truth:
    - print top-K peaks for prediction and truth
    - report cosine similarity and L1 error
    """
    spec_hat = infer_mol_to_spec(graph_feat, frag_graphs, adj_local, frag_masses, device, enc_mol, frag_set_enc, dec_spec_fwd, heads,
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

def demo_retrieval_metrics(
    index,
    loader,
    device,
    enc_spec,
    enc_mol,
    frag_set_enc,
    heads,
    dec_spec_fwd,
    topk_list=(1,5,10),
    max_batches=None
    ) -> Dict[str, float]:

    """
    Compute Recall@K and MRR on a loader using a train-built index (vocab-agnostic).
    """
    enc_spec.eval()
    hits = {k: 0 for k in topk_list}
    mrr = 0.0
    n = 0
    # Infer dataset binning parameters
    mz_min, mz_max, bin_width = get_binning_from_loader(loader)
    with torch.no_grad():
        for bi, (graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local) in enumerate(loader):
            if max_batches is not None and bi >= max_batches:
                break
            B = len(smiles)
            _ = enc_spec(spec.to(device))  # forward pass for completeness
            for i in range(B):
                ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd,
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
                          dec_spec_fwd: "DecSpecLatent",
                          heads: TaskHeads):
    """
    Compare spectrum reconstruction with local adjacency vs zero adjacency smoothing.
    """
    with torch.no_grad():
        spec_hat_graph = infer_mol_to_spec(graph_feat, frag_graphs, adj_local, frag_masses, device, enc_mol, frag_set_enc, dec_spec_fwd, heads,
                                           smiles=smiles, mz_min=mz_min, mz_max=mz_max, bin_width=bin_width)
        spec_hat_none = infer_mol_to_spec(graph_feat, frag_graphs, torch.zeros_like(adj_local), frag_masses, device, enc_mol, frag_set_enc, dec_spec_fwd, heads,
                                          smiles=smiles, mz_min=mz_min, mz_max=mz_max, bin_width=bin_width)
        cos_graph = F.cosine_similarity(F.normalize(spec_hat_graph, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
        cos_none = F.cosine_similarity(F.normalize(spec_hat_none, dim=-1), F.normalize(true_spec, dim=-1), dim=-1).item()
    return {"cos_with_adj": cos_graph, "cos_no_adj": cos_none, "diff": cos_graph - cos_none}

def demo_noise_robustness(index, loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5):
    """
    Add Gaussian noise to spectra and plot/return Recall@K vs noise level.
    """
    results = {}
    # Infer dataset binning parameters
    mz_min, mz_max, bin_width = get_binning_from_loader(loader)
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
                    ranked = infer_spec_to_mol(spec_noisy[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd,
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


def run_frag_encoder_diagnostics(loader: DataLoader, frag_set_enc: FragSetEncoderVocabless, max_samples: int = 128) -> Dict[str, Any]:
    """
    Collect lightweight diagnostics from FragSetEncoderVocabless across a few batches.
    Returns aggregate statistics: means and simple correlations (if enough data).
    """
    frag_set_enc.eval()
    prev_capture = frag_set_enc.capture_diag
    frag_set_enc.capture_diag = True
    all_diags: List[Dict[str, float]] = []
    n_seen = 0
    with torch.no_grad():
        for graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local in loader:
            # Just run the fragment encoder to emit diagnostics; no need to compute losses
            _ = frag_set_enc(frag_graphs, adj_batch=adj_local, mass_batch=frag_masses)
            diags = frag_set_enc.get_and_clear_diagnostics()
            all_diags.extend(diags)
            n_seen += len(diags)
            if n_seen >= max_samples:
                break
    frag_set_enc.capture_diag = prev_capture
    if len(all_diags) == 0:
        return {"N": 0}
    # Aggregate
    n_frag = np.array([d["n_frag"] for d in all_diags], dtype=float)
    att_ent = np.array([d["att_entropy"] for d in all_diags], dtype=float)
    var_pre = np.array([d["var_pre"] for d in all_diags], dtype=float)
    var_post = np.array([d["var_post"] for d in all_diags], dtype=float)
    mean_deg = np.array([d.get("mean_degree", 0.0) for d in all_diags], dtype=float)
    out = {
        "N": int(len(all_diags)),
        "att_entropy_mean": float(att_ent.mean()),
        "att_entropy_std": float(att_ent.std()),
        "var_pre_mean": float(var_pre.mean()),
        "var_post_mean": float(var_post.mean()),
        "var_delta_mean": float((var_post - var_pre).mean()),
        "mean_degree_mean": float(mean_deg.mean()),
        "n_frag_mean": float(n_frag.mean()),
        "n_frag_median": float(np.median(n_frag)),
    }
    # Simple correlations (defensive against zero variance)
    def safe_corr(x, y):
        if x.std() == 0 or y.std() == 0 or x.size < 3:
            return float('nan')
        return float(np.corrcoef(x, y)[0, 1])
    out["corr_nfrag_att_entropy"] = safe_corr(n_frag, att_ent)
    out["corr_degree_att_entropy"] = safe_corr(mean_deg, att_ent)
    out["corr_nfrag_var_delta"] = safe_corr(n_frag, var_post - var_pre)
    return out


def run_mass_adj_ablation_diagnostics(loader: DataLoader, frag_set_enc: FragSetEncoderVocabless, max_samples: int = 128) -> Dict[str, Any]:
    """
    Compare attention/variance diagnostics across:
    - adj ON + mass ON (current)
    - adj OFF + mass ON (gamma=0)
    - adj ON + mass OFF (mass_batch=None)
    Returns a dict with means and diffs to identify whether adjacency inflates attention entropy and how mass interacts.
    """
    def collect(adj_gamma_override: Optional[float], use_mass: bool):
        prev_capture = frag_set_enc.capture_diag
        prev_gamma = frag_set_enc.adj_gamma
        frag_set_enc.capture_diag = True
        if adj_gamma_override is not None:
            frag_set_enc.adj_gamma = float(adj_gamma_override)
        all_diags: List[Dict[str, float]] = []
        n_seen = 0
        with torch.no_grad():
            for graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local in loader:
                mb = frag_masses if use_mass else None
                _ = frag_set_enc(frag_graphs, adj_batch=adj_local, mass_batch=mb)
                diags = frag_set_enc.get_and_clear_diagnostics()
                all_diags.extend(diags)
                n_seen += len(diags)
                if n_seen >= max_samples:
                    break
        frag_set_enc.capture_diag = prev_capture
        frag_set_enc.adj_gamma = prev_gamma
        if len(all_diags) == 0:
            return {"N": 0}
        n_frag = np.array([d["n_frag"] for d in all_diags], dtype=float)
        att_ent = np.array([d["att_entropy"] for d in all_diags], dtype=float)
        var_pre = np.array([d["var_pre"] for d in all_diags], dtype=float)
        var_post = np.array([d["var_post"] for d in all_diags], dtype=float)
        mean_deg = np.array([d.get("mean_degree", 0.0) for d in all_diags], dtype=float)
        return {
            "N": int(len(all_diags)),
            "att_entropy_mean": float(att_ent.mean()),
            "att_entropy_std": float(att_ent.std()),
            "var_pre_mean": float(var_pre.mean()),
            "var_post_mean": float(var_post.mean()),
            "var_delta_mean": float((var_post - var_pre).mean()),
            "mean_degree_mean": float(mean_deg.mean()),
            "n_frag_mean": float(n_frag.mean()),
        }

    g_cur = float(frag_set_enc.adj_gamma)
    on_mass_on = collect(adj_gamma_override=g_cur, use_mass=True)
    off_mass_on = collect(adj_gamma_override=0.0, use_mass=True)
    on_mass_off = collect(adj_gamma_override=g_cur, use_mass=False)

    def diff(a, b, key):
        if a.get("N", 0) == 0 or b.get("N", 0) == 0:
            return float("nan")
        return float(a.get(key, float("nan")) - b.get(key, float("nan")))

    return {
        "adj_on_mass_on": on_mass_on,
        "adj_off_mass_on": off_mass_on,
        "adj_on_mass_off": on_mass_off,
        "delta_att_entropy_adj_on_minus_off": diff(on_mass_on, off_mass_on, "att_entropy_mean"),
        "delta_att_entropy_mass_on_minus_off": diff(on_mass_on, on_mass_off, "att_entropy_mean"),
        "note": "Positive delta_att_entropy_adj_on_minus_off indicates adjacency increases attention entropy (more uniform). Positive delta_att_entropy_mass_on_minus_off indicates mass features make attention more uniform when adjacency is on.",
    }


def evaluate_forward_cosine(
    loader: DataLoader,
    device: torch.device,
    enc_mol: "EncMol",
    frag_set_enc: FragSetEncoderVocabless,
    heads: TaskHeads,
    dec_spec_fwd: "DecSpecLatent",
    mz_min: float,
    mz_max: float,
    bin_width: float,
    max_batches: Optional[int] = None,
) -> float:
    """
    Compute mean masked cosine similarity (mol+frag -> spec) on a loader.
    """
    enc_mol.eval(); frag_set_enc.eval(); heads.eval(); dec_spec_fwd.eval()
    cos_sum = 0.0
    n = 0
    with torch.no_grad():
        for bi, (graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local) in enumerate(loader):
            if (max_batches is not None) and (bi >= max_batches):
                break
            spec = spec.to(device)
            z_m = enc_mol(graph_feats)
            z_f = frag_set_enc(frag_graphs, adj_batch=adj_local, mass_batch=frag_masses)
            z = (z_m + z_f) / 2
            z_fwd, _ = heads(z)
            spec_hat = dec_spec_fwd(z_fwd)
            mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
            spec_hat = spec_hat * mask
            # cosine per sample
            cs = F.cosine_similarity(F.normalize(spec_hat, dim=-1), F.normalize(spec, dim=-1), dim=-1)
            cos_sum += float(cs.sum().cpu().item())
            n += cs.numel()
    return cos_sum / max(n, 1)


def evaluate_ablation_delta_cosine(
    loader: DataLoader,
    device: torch.device,
    enc_mol: "EncMol",
    frag_set_enc: FragSetEncoderVocabless,
    heads: TaskHeads,
    dec_spec_fwd: "DecSpecLatent",
    mz_min: float,
    mz_max: float,
    bin_width: float,
    max_batches: Optional[int] = None,
) -> float:
    """Average (cos_with_adj - cos_no_adj) across a loader."""
    enc_mol.eval(); frag_set_enc.eval(); heads.eval(); dec_spec_fwd.eval()
    total = 0.0
    n = 0
    with torch.no_grad():
        for bi, (graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local) in enumerate(loader):
            if (max_batches is not None) and (bi >= max_batches):
                break
            spec = spec.to(device)
            # With adjacency
            z_m = enc_mol(graph_feats)
            z_f = frag_set_enc(frag_graphs, adj_batch=adj_local, mass_batch=frag_masses)
            z = (z_m + z_f) / 2
            z_fwd, _ = heads(z)
            spec_hat = dec_spec_fwd(z_fwd)
            mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
            spec_hat = spec_hat * mask
            cos_with = F.cosine_similarity(F.normalize(spec_hat, dim=-1), F.normalize(spec, dim=-1), dim=-1)
            # Without adjacency: zeros like adj
            adj_off = [torch.zeros_like(a) if isinstance(a, torch.Tensor) else torch.zeros(0, 0, device=device) for a in adj_local]
            z_f_off = frag_set_enc(frag_graphs, adj_batch=adj_off, mass_batch=frag_masses)
            z_off = (z_m + z_f_off) / 2
            z_fwd_off, _ = heads(z_off)
            spec_hat_off = dec_spec_fwd(z_fwd_off) * mask
            cos_off = F.cosine_similarity(F.normalize(spec_hat_off, dim=-1), F.normalize(spec, dim=-1), dim=-1)
            d = (cos_with - cos_off).sum().cpu().item()
            total += float(d)
            n += cos_with.numel()
    return total / max(n, 1)


def demo_visualize_reconstructions(
    graph_feats, frag_graphs, frag_masses, true_spec, smiles, adj_local, device,
    enc_mol, frag_set_enc, dec_spec_fwd, heads, n_samples=3
    ) -> bool:
    """
    Plot true vs reconstructed spectra for n_samples molecules.
    """
    n = min(n_samples, len(smiles))
    for i in range(n):
        # Try to infer dataset binning from vector length and assume mz_min=1.0, bin_width=1.0 if unavailable
        # Call without mask to keep this lightweight visualization generic
        spec_hat = infer_mol_to_spec(graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], device, enc_mol, frag_set_enc, dec_spec_fwd, heads)
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


def split_indices(n: int, test_size: float = 0.2, val_size: float = 0.3, shuffle: bool = False, seed: int = 42):
    """Create aligned train/val/test index splits.

    val_size is taken as a fraction of the remaining (non-test) set, matching the previous two-step split behavior.
    """
    idx = list(range(n))
    if shuffle:
        random.Random(seed).shuffle(idx)
    n_test = int(n * test_size)
    test_idx = idx[:n_test]
    rest = idx[n_test:]
    n_val = int(len(rest) * val_size)
    val_idx = rest[:n_val]
    train_idx = rest[n_val:]
    return train_idx, val_idx, test_idx


def main():
    """
    Entry point for training and demonstrating the FRAG model.

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
    # Fragment adjacency smoothing hyperparameters
    p.add_argument("--adj_gamma", type=float, default=0.0, help="Gated residual weight for adjacency smoothing (0 disables smoothing)")
    p.add_argument("--adj_beta", type=float, default=1.0, help="Self-loop weight for symmetric normalization (A_tilde = A + beta*I)")
    # Upgrades: Phase-B combination weights
    p.add_argument("--lam_con", type=float, default=0.1, help="Weight for InfoNCE loss in Phase B")
    p.add_argument("--lam_latent", type=float, default=0.07, help="Weight for latent consistency (z_fwd vs z_bwd)")
    p.add_argument("--lam_fwd_in_b", type=float, default=0.05, help="Weight to include forward recon inside Phase B")
    # Diagnostics
    p.add_argument("--diag_samples", type=int, default=0, help="If >0, run fragment-encoder diagnostics on this many VAL samples after training")
    p.add_argument("--diag_mass_adj", action="store_true", help="Run mass vs adjacency ablation diagnostics on VAL and print summary")
    # Early stopping and tuning
    p.add_argument("--early_stop", action="store_true", help="Enable early stopping based on VAL metric")
    p.add_argument("--es_metric", type=str, default="cosine", choices=["cosine", "MRR", "R@1", "R@5", "R@10"], help="Validation metric to monitor for early stopping")
    p.add_argument("--es_patience", type=int, default=5, help="Early stopping patience in epochs")
    p.add_argument("--tune_adj", action="store_true", help="Run a tiny grid search over adj_gamma and adj_beta using VAL metrics (no retraining)")
    p.add_argument("--tune_adj_gamma", type=float, nargs="*", default=None, help="Candidate values for adj_gamma (overrides current when tuning)")
    p.add_argument("--tune_adj_beta", type=float, nargs="*", default=None, help="Candidate values for adj_beta (overrides current when tuning)")
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
                try:
                    targets = dict()
                    rules = dict()
                    for edge in dg_v.outEdges:
                        targets[edge.id] = [utils.graph_from_term(t.graph).smiles for t in edge.targets]
                        rules[edge.id] = [rule for rule in edge.rules]
                    fwd_coll.append((graph.smiles, graph.exactMass, targets, rules))
                except mod.libpymod.LogicError:
                    fwd_coll.append((graph.smiles, graph.exactMass, dict(), dict()))
                    # final vertex has no outEdges



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
                    bwd_coll.append((graph.smiles, graph.exactMass, dict(), dict()))
                    # final vertex has no outEdges
            else:
                print("Warning: non-molecule in backward DG:", graph.smiles)

        frag_coll[smi] = (fwd_coll, bwd_coll)

        real_spectra = utils.get_spectra_from_local_jdx(name)
        real_spectra_per_mol.append(real_spectra)

    # Create aligned splits based on indices to avoid any misalignment
    mol_keys = list(frag_coll.keys())  # insertion order preserved
    assert len(mol_keys) == len(real_spectra_per_mol)

    train_idx, val_idx, test_idx = split_indices(
        len(mol_keys), test_size=0.2, val_size=0.3, shuffle=False, seed=42
    )

    def subset_dict(d, idxs):
        keys = [mol_keys[i] for i in idxs]
        return {k: d[k] for k in keys}

    def subset_list(L, idxs):
        return [L[i] for i in idxs]

    train_frags = subset_dict(frag_coll, train_idx)
    vali_frags  = subset_dict(frag_coll, val_idx)
    test_frags  = subset_dict(frag_coll, test_idx)

    train_spect = subset_list(real_spectra_per_mol, train_idx)
    vali_spect  = subset_list(real_spectra_per_mol, val_idx)
    test_spect  = subset_list(real_spectra_per_mol, test_idx)

    # Build dataset
    train_ds = RealDataset(
        train_frags, train_spect,
        precompute=True
        )

    vali_ds = RealDataset(
        vali_frags, vali_spect,
        precompute=True
        )

    test_ds = RealDataset(
        test_frags, test_spect,
        precompute=True
        )

    # Use dataset to configure the model:
    spectrum_bins_size = train_ds.spectrum_bins_size


    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch,
        shuffle=True,
        drop_last=False,
        collate_fn=collate_vlex,
        num_workers=4,
        pin_memory=(device.type == "cuda"),
        persistent_workers=True,
    )
    val_loader   = DataLoader(
        vali_ds,
        batch_size=args.batch,
        shuffle=False,
        collate_fn=collate_vlex,
        num_workers=4,
        pin_memory=(device.type == "cuda"),
        persistent_workers=True,
    )
    test_loader  = DataLoader(
        test_ds,
        batch_size=args.batch,
        shuffle=False,
        collate_fn=collate_vlex,
        num_workers=4,
        pin_memory=(device.type == "cuda"),
        persistent_workers=True,
    )

    # Models
    # Probe node feature dimension dynamically from first batch
    probe_batch = next(iter(train_loader))
    probe_graph = probe_batch[0][0]  # first GeometricData in graph_feats list
    d_node_in = int(probe_graph.x.size(-1))
    enc_mol  = EncMol(d_node_in=d_node_in, d_latent=args.latent).to(device)
    frag_set_enc = FragSetEncoderVocabless(enc_mol, d_latent=args.latent, adj_beta=args.adj_beta, adj_gamma=args.adj_gamma).to(device)
    enc_spec = EncSpec(spectrum_bins_size, args.latent).to(device)
    dec_spec_fwd = DecSpecLatent(d_in=args.latent, spectrum_bins_size=spectrum_bins_size).to(device)
    dec_spec_bwd = DecSpecLatent(d_in=args.latent, spectrum_bins_size=spectrum_bins_size).to(device)
    # Task heads (shared trunk projections)
    heads = TaskHeads(d_latent=args.latent, d_task=args.latent).to(device)

    # Optimizers (separate per phase keeps it simple)
    # Avoid duplicate parameters: frag_set_enc registers enc_mol as a submodule,
    # so its parameters already include enc_mol's parameters.
    opt_a = torch.optim.Adam(list(frag_set_enc.parameters()) +
                             list(dec_spec_fwd.parameters()) +
                             list(heads.parameters()), lr=args.lr)
    opt_b = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(enc_spec.parameters()) +
                             list(dec_spec_bwd.parameters()) +
                             list(heads.parameters()), lr=args.lr)

    # Mixed precision scaler (enabled on CUDA)
    scaler = torch.amp.GradScaler(enabled=(device.type == "cuda"))

    # ----------------- Phase A -----------------
    print("== Phase A: train forward (vocab-agnostic) ==")
    best_a = -float('inf')
    best_state_a = None
    no_improve = 0
    for epoch in range(1, args.epochs_fwd + 1):
        loss = train_epoch_phase_a(
            train_loader, device, enc_mol, frag_set_enc, heads, dec_spec_fwd, opt_a, scaler,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1
        )
        # Evaluate VAL forward cosine for early stopping
        val_cos = evaluate_forward_cosine(val_loader, device, enc_mol, frag_set_enc, heads, dec_spec_fwd,
                                          mz_min=vali_ds.mz_min, mz_max=vali_ds.mz_max, bin_width=vali_ds.bin_width)
        print(f"[A] epoch {epoch:02d} loss {loss:.4f} | VAL cosine {val_cos:.4f}")
        if args.early_stop:
            if val_cos > best_a:
                best_a = val_cos
                no_improve = 0
                best_state_a = {
                    "enc_mol": enc_mol.state_dict(),
                    "frag_set_enc": frag_set_enc.state_dict(),
                    "dec_spec_fwd": dec_spec_fwd.state_dict(),
                    "heads": heads.state_dict(),
                }
            else:
                no_improve += 1
                if no_improve >= args.es_patience:
                    print(f"[A] Early stopping at epoch {epoch}, best VAL cosine {best_a:.4f}")
                    if best_state_a is not None:
                        enc_mol.load_state_dict(best_state_a["enc_mol"])
                        frag_set_enc.load_state_dict(best_state_a["frag_set_enc"])
                        dec_spec_fwd.load_state_dict(best_state_a["dec_spec_fwd"])
                        heads.load_state_dict(best_state_a["heads"])
                    break

    # ----------------- Phase B -----------------
    print("== Phase B: align spec latent + spectrum recon (vocab-agnostic, upgrades enabled if weights > 0) ==")
    best_b = -float('inf')
    best_state_b = None
    no_improve_b = 0
    for epoch in range(1, args.epochs_bwd + 1):
        loss = train_epoch_phase_b(
            train_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_bwd, dec_spec_fwd, opt_b, scaler,
            lam_con=args.lam_con, lam_latent=args.lam_latent, lam_fwd_in_b=args.lam_fwd_in_b,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1
        )
        # Monitor chosen VAL metric for early stopping
        metric_val = None
        if args.es_metric == "cosine":
            metric_val = evaluate_forward_cosine(val_loader, device, enc_mol, frag_set_enc, heads, dec_spec_fwd,
                                                 mz_min=vali_ds.mz_min, mz_max=vali_ds.mz_max, bin_width=vali_ds.bin_width)
            print(f"[B] epoch {epoch:02d} loss {loss:.4f} | VAL cosine {metric_val:.4f}")
        else:
            # Build retrieval index and evaluate MRR/R@K (costlier)
            index_tmp = LatentIndex(d=args.latent)
            index_tmp.build(train_ds, device, enc_mol)
            r = demo_retrieval_metrics(index_tmp, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd, topk_list=(1,5,10), max_batches=5)
            if args.es_metric == "MRR":
                metric_val = float(r.get("MRR", 0.0))
            elif args.es_metric == "R@1":
                metric_val = float(r.get("R@1", 0.0))
            elif args.es_metric == "R@5":
                metric_val = float(r.get("R@5", 0.0))
            elif args.es_metric == "R@10":
                metric_val = float(r.get("R@10", 0.0))
            print(f"[B] epoch {epoch:02d} loss {loss:.4f} | VAL {args.es_metric} {metric_val:.4f}")
        if args.early_stop and metric_val is not None:
            if metric_val > best_b:
                best_b = metric_val
                no_improve_b = 0
                best_state_b = {
                    "enc_mol": enc_mol.state_dict(),
                    "enc_spec": enc_spec.state_dict(),
                    "dec_spec_bwd": dec_spec_bwd.state_dict(),
                    "heads": heads.state_dict(),
                }
            else:
                no_improve_b += 1
                if no_improve_b >= args.es_patience:
                    print(f"[B] Early stopping at epoch {epoch}, best VAL {args.es_metric} {best_b:.4f}")
                    if best_state_b is not None:
                        enc_mol.load_state_dict(best_state_b["enc_mol"])
                        enc_spec.load_state_dict(best_state_b["enc_spec"])
                        dec_spec_bwd.load_state_dict(best_state_b["dec_spec_bwd"])
                        heads.load_state_dict(best_state_b["heads"])
                    break

    # ----------------- Build retrieval index -----------------
    print("== Building retrieval index on TRAIN set ==")
    index = LatentIndex(d=args.latent)
    index.build(train_ds, device, enc_mol)


    # ----------------- Demo: Structure - > Spectrum -----------------
    graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local = next(iter(test_loader))
    i = 0
    spec_hat = infer_mol_to_spec(
        graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], device,
        enc_mol, frag_set_enc, dec_spec_fwd, heads,
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
        enc_mol, frag_set_enc, dec_spec_fwd, heads,
        mz_min=test_ds.mz_min, bin_width=test_ds.bin_width, smiles=smiles[i], mz_max=test_ds.mz_max, top_k=10
    )

    # ----------------- Demo: Spectrum - > Structure -----------------
    print("== Demo: Spec -> Mol retrieval + re-ranking on the same TEST sample ==")
    ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd,
                               mz_min=test_ds.mz_min, mz_max=test_ds.mz_max, bin_width=test_ds.bin_width, topk=10)
    print("Top-5 candidates:")
    print(f"{'SMILES':>40s} | {'Score':>8s}")
    print("-" * 50)
    for s, sc in ranked[:5]:
        print(f"{s:>40s} | {sc:8.3f}")

    # ----------------- Demo: Retrieval metrics on VAL/TEST -----------------
    print("== Retrieval metrics (VAL) ==")
    val_metrics = demo_retrieval_metrics(index, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd, topk_list=(1,5,10), max_batches=5)
    print(val_metrics)
    print("== Retrieval metrics (TEST) ==")
    test_metrics = demo_retrieval_metrics(index, test_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd, topk_list=(1,5,10), max_batches=5)
    print(test_metrics)
    # ----------------- Demo: Fragment graph ablation -----------------
    print("== Graph ablation on one VAL sample ==")
    ablation = demo_ablate_adjacency(graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], spec[i],
                                     smiles[i], test_ds.mz_min, test_ds.mz_max, test_ds.bin_width,
                                     device, enc_mol, frag_set_enc, dec_spec_fwd, heads)
    print(ablation)

    # ----------------- Demo: Spectrum noise robustness -----------------
    print("== Spectrum noise robustness (VAL subset) ==")
    noise_res = demo_noise_robustness(index, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec_fwd, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5)
    print(noise_res)

    # ----------------- Demo: Visualization of reconstructions -----------------
    print("== Visualization: saving recon plots for a few VAL samples ==")
    _ = demo_visualize_reconstructions(graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, device, enc_mol, frag_set_enc, dec_spec_fwd, heads, n_samples=3)

    # ----------------- Diagnostics (optional) -----------------
    if args.diag_samples and args.diag_samples > 0:
        print("== Fragment encoder diagnostics (VAL) ==")
        diag = run_frag_encoder_diagnostics(val_loader, frag_set_enc, max_samples=args.diag_samples)
        print(diag)
    if args.diag_mass_adj:
        print("== Mass vs Adjacency ablation diagnostics (VAL) ==")
        diag_ablate = run_mass_adj_ablation_diagnostics(val_loader, frag_set_enc, max_samples=max(16, args.diag_samples or 16))
        print(diag_ablate)

    # ----------------- Tiny grid tuner for adjacency (no retraining) -----------------
    if args.tune_adj:
        gammas = args.tune_adj_gamma if (args.tune_adj_gamma is not None and len(args.tune_adj_gamma) > 0) else [frag_set_enc.adj_gamma]
        betas = args.tune_adj_beta if (args.tune_adj_beta is not None and len(args.tune_adj_beta) > 0) else [frag_set_enc.adj_beta]
        print(f"== Tuning adjacency on VAL over gamma={gammas}, beta={betas} ==")
        best_combo = None
        best_score = -float('inf')
        results = []
        for g in gammas:
            for b in betas:
                # set, evaluate cosine and ablation delta
                frag_set_enc.adj_gamma = float(g)
                frag_set_enc.adj_beta = float(b)
                val_cos = evaluate_forward_cosine(val_loader, device, enc_mol, frag_set_enc, heads, dec_spec_fwd,
                                                  mz_min=vali_ds.mz_min, mz_max=vali_ds.mz_max, bin_width=vali_ds.bin_width, max_batches=10)
                delta = evaluate_ablation_delta_cosine(val_loader, device, enc_mol, frag_set_enc, heads, dec_spec_fwd,
                                                       mz_min=vali_ds.mz_min, mz_max=vali_ds.mz_max, bin_width=vali_ds.bin_width, max_batches=5)
                results.append({"gamma": g, "beta": b, "val_cos": val_cos, "delta_cos": delta})
                score = val_cos  # choose cosine as primary
                if score > best_score:
                    best_score = score
                    best_combo = (g, b)
        print("Adjacency tuning results (top few):")
        results.sort(key=lambda r: r["val_cos"], reverse=True)
        for r in results[:5]:
            print(r)
        if best_combo is not None:
            frag_set_enc.adj_gamma = float(best_combo[0])
            frag_set_enc.adj_beta = float(best_combo[1])
            print(f"Selected gamma={best_combo[0]}, beta={best_combo[1]} (VAL cosine={best_score:.4f})")

    # save checkpoint
    ckpt = {
        "enc_mol": enc_mol.state_dict(),
        "frag_set_enc": frag_set_enc.state_dict(),
        "enc_spec": enc_spec.state_dict(),
        "dec_spec_fwd": dec_spec_fwd.state_dict(),
        "dec_spec_bwd": dec_spec_bwd.state_dict(),
        "heads": heads.state_dict(),
        "args": vars(args),
    }
    torch.save(ckpt, "frag_checkpoint.pt")
    print("Saved checkpoint to frag_checkpoint.pt")

if __name__ == "__main__":
    main()
