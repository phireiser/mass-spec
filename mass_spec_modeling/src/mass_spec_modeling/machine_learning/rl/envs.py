"""Enironments"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional

import torch
from torch import Tensor
from torch_geometric.data import Data
import mod
from ..datasets.spectra_dataset import bin_spectrum
from ..losses import spectral_similarity, tanimoto_smiles_token
from .mod_engine_adapter import DGState, ModEngineAdapter


class ForwardFragEnv:
    """
    RL environment for rule-based fragmentation to explain a spectrum.
    It assumes a `mod_engine` object with:
      - enumerate_applications(G) -> List[Tuple[rule_id, site]]
      - apply(rule_id, site, G) -> (ok: bool, new_frags: List[float])  # fragment masses (Da)
    """
    def __init__(
        self,
        mod_engine: ModEngineAdapter,
        featurizer,
        target_peaks: Tensor,    # [N,2] (mz, intensity)
        n_bins: int,
        mz_min: float,
        mz_max: float,
        ppm_tol: float = 10.0,
        max_depth: int = 6,
        device: str = "cpu",
    ):
        self.adapter = mod_engine
        self.featurizer = featurizer
        self.target_peaks = target_peaks.to(device)
        self.device = device
        self.n_bins = n_bins
        self.mz_min = mz_min
        self.mz_max = mz_max
        self.ppm_tol = ppm_tol
        self.max_depth = max_depth

        self.depth = 0
        self.frag_masses: List[float] = []
        self.state = None
        self.target_bins = bin_spectrum(
            self.target_peaks,
            n_bins, mz_min,
            mz_max,
            intensity_norm="sum"
            )
        self.pred_bins = torch.zeros(self.n_bins, device=self.device)
        self.prev_sim = 0.0
        self.pyg_batch: Optional[Data] = None

    def reset(self, dg: mod.DG, mol_graph: mod.Graph) -> DGState:
        self.depth = 0
        self.frag_masses = []
        self.pyg_batch = None
        self.state = DGState(dg=dg, mol_graph = mol_graph)
        self.prev_sim = 0.0
        return self.state

    # ---------- Core API ----------
    def step(
        self,
        action_edge_id: int # aka edge_ids
        ) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:

        ok, new_frags, next_edge_id, _smi = self.adapter.apply(action_edge_id, self.state)
        if not ok:
            # invalid action ends the episode with penalty
            return self.state, -1.0, True, {"invalid": True}

        self.depth += 1
        self.frag_masses.extend(new_frags)

        # Reward: improvement in spectral cosine similarity
        self.pred_bins = self.simulate_bins_from_frags()
        sim = spectral_similarity(self.pred_bins.unsqueeze(0), self.target_bins.unsqueeze(0))[0]
        reward = sim.item() - self.prev_sim #reward = float(sim.item())
        self.prev_sim = sim

        done = (self.depth >= self.max_depth) or (len(self.adapter.enumerate_applications(self.state)) == 0)
        self.state.node_id = next_edge_id
        info = {"sim": float(sim.item()), "frags": list(self.frag_masses)}
        return self.state, reward, done, info

    # ---------- Helpers ---------
    def simulate_bins_from_frags(self) -> Tensor:
        if len(self.frag_masses) == 0:
            return torch.zeros(self.n_bins, device=self.device)
        peaks = torch.tensor([[m, 1.0] for m in self.frag_masses], device=self.device)
        return bin_spectrum(peaks, self.n_bins, self.mz_min, self.mz_max, intensity_norm="sum")

    def available_actions(self):
        """Return all valid actions from the current state."""
        return self.adapter.enumerate_applications(self.state)



######################## ---------- Backward (assembly) environment ----------


class BackwardMolEnv:
    """
    Backward RL environment for molecule assembly.
    Actions are adapter-defined keys (ints) that extend/modify the current graph.

    Reward: delta cosine(pred_bins, target_bins), where pred_bins is a fast
    proxy spectrum from the *accumulated* fragment masses the adapter returns.
    (You can make preview/apply return your fragmentation-derived masses.)

    API parity with ForwardFragEnv:
      - reset(seed) -> AssemblyState
      - step(action_key) -> (AssemblyState, reward: float, done: bool, info: dict)
      - preview_action_bins(action_keys) -> Tensor[1, A, n_bins]
    """
    def __init__(
        self,
        mod_engine: ModEngineAdapter,
        target_peaks: Tensor,    # [N,2] (mz, intensity)
        n_bins: int,
        mz_min: float,
        mz_max: float,
        max_steps: int = 30,
        device: str = "cpu",
        intensity_norm: str = "sum",
        entropy_penalty_invalid: float = 1.0,  # penalty if invalid action chosen
    ):
        self.adapter = mod_engine
        self.target_peaks = target_peaks.to(device)
        self.device = device

        self.n_bins = n_bins
        self.mz_min = mz_min
        self.mz_max = mz_max
        self.max_steps = max_steps
        self.intensity_norm = intensity_norm
        self.entropy_penalty_invalid = float(entropy_penalty_invalid)

        # Derived
        self.target_bins = bin_spectrum(
            self.target_peaks, n_bins, mz_min, mz_max, intensity_norm=self.intensity_norm
        ).to(device)

        # Episode variables
        self.state: Optional[DGState] = None
        self.pred_bins: Tensor = torch.zeros(self.n_bins, device=self.device)
        self.prev_sim: float = 0.0
        self.total_frags: List[float] = []  # accumulated fragment masses

    # ----------- Public API -----------
    def reset(self, dg: mod.DG, mol_graph: mod.Graph) -> DGState:
        """Start a new episode"""
        self.state = DGState(dg, mol_graph)
        self.pred_bins = torch.zeros(self.n_bins, device=self.device)
        self.prev_sim = 0.0
        self.total_frags = []
        return self.state

    def step(self, action_key: int) -> Tuple[DGState, float, bool, Dict[str, Any]]:
        """
        Apply chosen action. Returns updated state, reward, done, info.
        Reward = delta-cosine(pred, targ) using accumulated fragment masses.
        """
        assert self.state is not None, "Call reset() before step()."

        ok, new_frag_masses, next_node, smi = self.adapter.apply(action_key, self.state)
        info: Dict[str, Any] = dict(next_node or {})
        info["ok"] = bool(ok)

        if not ok:
            # End episode on invalid choice (or keep going — your choice).
            done = True
            reward = -self.entropy_penalty_invalid
            return self.state, reward, done, {**info, "invalid": True}

        if new_frag_masses:
            self.total_frags.extend(float(m) for m in new_frag_masses)

        # Compute reward
        sim = tanimoto_smiles_token(self.state.mol_graph.smiles, smi)
        reward = sim - float(self.prev_sim)
        self.prev_sim = sim

        # Termination
        done = len(self.adapter.enumerate_applications(self.state)) == 0
        info.update({"sim": sim, "n_frags": len(self.total_frags)})
        return self.state, reward, done, info

    # ----------- Training helpers -----------
    def preview_action_bins(self, action_keys: List[int]) -> Tensor:
        """
        Build [1, A, n_bins] tensor of per-action preview spectra.
        Uses adapter.preview_masses(action, state) for each action.
        """
        assert self.state is not None, "Call reset() before preview_action_bins()."
        if not action_keys:
            # Return an empty view with proper dims to avoid downstream special cases
            return torch.zeros(1, 0, self.n_bins, device=self.device)

        per_action_bins: List[Tensor] = []
        for key in action_keys:
            masses = self.adapter.preview_masses(key, self.state)
            bins = self._bins_from_masses(masses)  # [n_bins]
            per_action_bins.append(bins)

        a_bins = torch.stack(per_action_bins, dim=0).unsqueeze(0)  # [1, A, n_bins]
        return a_bins

    def available_actions(self):
        """Return all valid actions from the current state."""
        return self.adapter.enumerate_applications(self.state)

    # ----------- Internals -----------
    def _bins_from_masses(self, masses: List[float]) -> Tensor:
        """
        Fast helper: convert a list of fragment masses to a binned spectrum [n_bins].
        """
        if not masses:
            return torch.zeros(self.n_bins, device=self.device)
        peaks = torch.tensor([[m, 1.0] for m in masses], device=self.device, dtype=torch.float32)
        return bin_spectrum(peaks, self.n_bins, self.mz_min, self.mz_max, intensity_norm=self.intensity_norm)
