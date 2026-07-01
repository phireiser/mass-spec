"""Dataset and preprocessing helpers for the machine-learning pipeline."""

from dataclasses import dataclass
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, Union
import random

import torch
from torch.utils.data import Dataset, DataLoader, Subset
from torch_geometric.data import Data as GeometricData

import mod

from src.machine_learning.featurizers import GraphFeaturizerMOD


@dataclass
class Sample:
    """Container for one dataset sample. So one molecule with its derivation graph"""
    graph_feat: GeometricData
    frag_bag: torch.Tensor
    true_spectrum: torch.Tensor
    smiles: str
    fragment_adjacency_fwd: torch.Tensor
    fragment_adjacency_bwd: torch.Tensor
    frag_graphs: Optional[List[GeometricData]] = None
    frag_adj_local: Optional[torch.Tensor] = None
    frag_masses: Optional[torch.Tensor] = None
    frag_deriv_tree_fwd: Optional[GeometricData] = None
    frag_deriv_tree_bwd: Optional[GeometricData] = None


def build_derivation_tree_from_collection(
    frag_graphs_list: List[GeometricData],
    frag_masses: torch.Tensor,
    derivation_graph: List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]],
    frag_smiles_to_idx: Dict[str, int],
) -> Optional[GeometricData]:
    if not frag_graphs_list or len(frag_graphs_list) == 0:
        return None

    n_frags = len(frag_graphs_list)
    edge_list = []
    for src_smi, _mass, targets, _rules in derivation_graph:
        src_idx = frag_smiles_to_idx.get(src_smi)
        if src_idx is None:
            continue
        for dst_smi_list in targets.values():
            for dst_smi in dst_smi_list:
                dst_idx = frag_smiles_to_idx.get(dst_smi)
                if dst_idx is not None:
                    edge_list.append([src_idx, dst_idx])

    if not edge_list:
        edge_index = torch.zeros((2, 0), dtype=torch.long)
    else:
        edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()

    if edge_index.numel() > 0:
        assert edge_index.max() < n_frags
        assert edge_index.min() >= 0

    tree_data = GeometricData(edge_index=edge_index)
    tree_data.frag_graphs = frag_graphs_list
    tree_data.masses = frag_masses
    return tree_data


def build_fragment_vocab(
    frag_coll: Dict[
        str,
        Tuple[
            List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]],
            List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]],
        ],
    ],
    existing_frag_to_id: Optional[Dict[str, int]] = None,
) -> Dict[str, int]:
    if existing_frag_to_id is not None:
        return existing_frag_to_id.copy()

    ctr = Counter()
    for _smile_of_mol, (fwd, bwd) in frag_coll.items():
        for item in fwd:
            ctr.update([item[0]])
        for item in bwd:
            ctr.update([item[0]])

    frag_to_id: Dict[str, int] = {}
    idx = 0
    for frag in ctr.keys():
        if frag not in frag_to_id:
            frag_to_id[frag] = idx
            idx += 1
    return frag_to_id


def frag_bag_from_list(
    frag_list: List[str],
    frag_to_id: Dict[str, int],
    fragment_vocab_size: int,
) -> torch.Tensor:
    bag = torch.zeros(fragment_vocab_size, dtype=torch.float32)
    for f in frag_list:
        idx = frag_to_id.get(f)
        if idx is not None:
            bag[idx] = 1.0
    return bag


def compute_bin_index(mz: float, mz_min: float, mz_max: float, bin_width: float) -> Optional[int]:
    if (mz < mz_min) or (mz >= mz_max):
        return None
    return int((mz - mz_min) / bin_width)


def bin_spectrum(
    peaks: List[Tuple[float, float]],
    mz_min: float,
    mz_max: float,
    bin_width: float,
    sqrt_and_l2: bool = True,
) -> torch.Tensor:
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


class RealDataset(Dataset):
    """Dataset that handles forward and backward derivation graphs."""

    def __init__(
        self,
        frag_coll: Dict[
            str,
            Tuple[
                List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]],
                List[Tuple[str, float, Dict[int, List[str]], Dict[int, List[str]]]],
            ],
        ],
        real_spectra_per_mol: List[List[Tuple[float, float]]],
        *,
        mz_min: float = 1.0,
        mz_max: float = 1000.0,
        bin_width: float = 1.0,
        frag_to_id: Optional[Dict[str, int]] = None,
        precompute: bool = True,
        graph_backend: str = "adjacency",
    ):
        self.real_spectra_per_mol = real_spectra_per_mol
        self.frag_coll = frag_coll
        self.graph_backend = graph_backend.lower()
        assert self.graph_backend in ("adjacency", "derivation_tree")

        self.mz_min = float(mz_min)
        self.mz_max = float(mz_max)
        self.bin_width = float(bin_width)
        self.spectrum_bins_size = int((self.mz_max - self.mz_min) / self.bin_width)

        assert len(frag_coll.keys()) == len(real_spectra_per_mol)

        if frag_to_id is None:
            self.frag_to_id = build_fragment_vocab(self.frag_coll)
        else:
            self.frag_to_id = build_fragment_vocab(self.frag_coll, existing_frag_to_id=frag_to_id)

        self.fragment_vocab_size = len(self.frag_to_id)
        self.graph_featurizer = GraphFeaturizerMOD()
        self._cache = None
        if precompute:
            self._precompute_all()
        self.complexities = self._compute_complexities()
        self.sorted_indices = sorted(range(len(self)), key=lambda i: self.complexities[i])
        self.parent_masses = self._compute_parent_masses()

    def _compute_parent_masses(self) -> List[float]:
        """Per-molecule parent exact mass (max fragment mass), for mass-bucketed
        batching. Read from the fragment collection so no extra mod parse is needed."""
        masses: List[float] = []
        for fwd, _bwd in self.frag_coll.values():
            masses.append(max((float(em) for (_s, em, _t, _r) in fwd), default=0.0))
        return masses

    def __len__(self) -> int:
        return len(self.frag_coll.keys())

    def __getitem__(self, idx: int):
        if self._cache is not None:
            graph_feats, bags, specs, adjs_fwd, adjs_bwd = self._cache[idx]
        else:
            mol = mod.Graph.fromSMILES(list(self.frag_coll.keys())[idx])
            graph_feats = self.graph_featurizer(mol)
            specs = self._make_spec(idx)
            bags = self._make_frag_bag(idx)
            adjs_fwd, adjs_bwd = self._make_frag_adj(idx)

        frag_smiles = self._frag_smiles_for_idx(idx)
        frag_graphs = []
        for smi in frag_smiles:
            try:
                frag_graphs.append(self.graph_featurizer(mod.Graph.fromSMILES(smi)))
            except Exception:
                print(f"Warning: mod could not parse fragment SMILES '{smi}'")

        frag_adj_local = self._local_adj_for_idx(idx)
        frag_masses = self._frag_masses_for_idx(idx)

        frag_deriv_tree_fwd = None
        frag_deriv_tree_bwd = None
        if self.graph_backend == "derivation_tree" and len(frag_graphs) > 0:
            frag_idx = {s: i for i, s in enumerate(frag_smiles)}
            fwd, bwd = list(self.frag_coll.values())[idx]
            frag_deriv_tree_fwd = build_derivation_tree_from_collection(frag_graphs, frag_masses, fwd, frag_idx)
            frag_deriv_tree_bwd = build_derivation_tree_from_collection(frag_graphs, frag_masses, bwd, frag_idx)

        return Sample(
            graph_feat=graph_feats,
            frag_bag=bags,
            true_spectrum=specs,
            fragment_adjacency_bwd=adjs_bwd,
            fragment_adjacency_fwd=adjs_fwd,
            smiles=list(self.frag_coll.keys())[idx],
            frag_graphs=frag_graphs,
            frag_adj_local=frag_adj_local,
            frag_masses=frag_masses,
            frag_deriv_tree_fwd=frag_deriv_tree_fwd,
            frag_deriv_tree_bwd=frag_deriv_tree_bwd,
        )

    def _make_frag_adj(self, idx: int) -> List[torch.Tensor]:
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

    def _make_frag_bag(self, idx: int) -> torch.Tensor:
        fwd_coll, _ = list(self.frag_coll.values())[idx]
        frag_smiles = [t[0] for t in fwd_coll]
        return frag_bag_from_list(frag_smiles, self.frag_to_id, self.fragment_vocab_size)

    def _make_spec(self, idx: int) -> torch.Tensor:
        return bin_spectrum(self.real_spectra_per_mol[idx], self.mz_min, self.mz_max, self.bin_width)

    def _frag_smiles_for_idx(self, idx: int) -> List[str]:
        fwd_coll, _ = list(self.frag_coll.values())[idx]
        return [t[0] for t in fwd_coll]

    def _frag_masses_for_idx(self, idx: int) -> torch.Tensor:
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

    def _local_adj_for_idx(self, idx: int) -> torch.Tensor:
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

    def _compute_complexities(self) -> List[int]:
        complexities: List[int] = []
        if self._cache is not None:
            for g, _b, _s, _af, _ab in self._cache:
                try:
                    complexities.append(int(g.x.size(0)))
                except Exception:
                    complexities.append(0)
        else:
            for smi in self.frag_coll.keys():
                try:
                    g = self.graph_featurizer(mod.Graph.fromSMILES(smi))
                    complexities.append(int(g.x.size(0)))
                except Exception:
                    complexities.append(0)
        return complexities


def collate_vlex(batch: List[Sample]):
    graph_feats = [b.graph_feat for b in batch]
    true_spectrum = torch.stack([b.true_spectrum for b in batch])
    smiles = [b.smiles for b in batch]
    frag_graphs = [b.frag_graphs or [] for b in batch]
    frag_adj_local = [b.frag_adj_local if b.frag_adj_local is not None else torch.zeros(0, 0) for b in batch]
    frag_masses = [b.frag_masses if b.frag_masses is not None else torch.zeros(0) for b in batch]
    frag_deriv_trees_fwd = [b.frag_deriv_tree_fwd for b in batch]
    frag_deriv_trees_bwd = [b.frag_deriv_tree_bwd for b in batch]
    return graph_feats, frag_graphs, frag_masses, true_spectrum, smiles, frag_adj_local, frag_deriv_trees_fwd, frag_deriv_trees_bwd


def build_curriculum_loader(dataset: RealDataset, batch_size: int, fraction: float, collate_fn) -> DataLoader:
    frac = float(max(0.0, min(1.0, fraction)))
    n = max(1, int(len(dataset) * frac))
    subset_idx = dataset.sorted_indices[:n]
    return DataLoader(Subset(dataset, subset_idx), batch_size=batch_size, shuffle=True, drop_last=False, collate_fn=collate_fn)


def build_hardneg_loader(dataset: RealDataset, batch_size: int, fraction: float, collate_fn) -> DataLoader:
    """Curriculum loader whose batches are near-isobaric.

    Takes the same easy-first curriculum fraction as :func:`build_curriculum_loader`,
    then sorts that fraction by parent mass and chunks it into contiguous batches, so
    the in-batch negatives seen by the InfoNCE / diversity / spectral-contrastive
    losses are the mass-nearest molecules. Mass can no longer separate a positive from
    its negatives, which forces the encoders and decoder onto structure rather than
    mass. Batch order is shuffled each call (main rebuilds the loader every epoch).
    """
    frac = float(max(0.0, min(1.0, fraction)))
    n = max(1, int(len(dataset) * frac))
    subset_idx = list(dataset.sorted_indices[:n])
    subset_idx.sort(key=lambda i: dataset.parent_masses[i])
    batches = [subset_idx[k:k + batch_size] for k in range(0, len(subset_idx), batch_size)]
    # fold a size-1 tail into the previous batch (InfoNCE needs >= 2 samples)
    if len(batches) >= 2 and len(batches[-1]) < 2:
        batches[-2].extend(batches.pop())
    random.shuffle(batches)
    return DataLoader(dataset, batch_sampler=batches, collate_fn=collate_fn)


def train_test_split(
    data: Union[List[Any], Dict[Any, Any]],
    test_size: float = 0.2,
    train_size: Optional[float] = None,
    shuffle: bool = True,
    random_state: Optional[int] = None,
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


__all__ = [
    "Sample",
    "RealDataset",
    "build_derivation_tree_from_collection",
    "build_fragment_vocab",
    "frag_bag_from_list",
    "compute_bin_index",
    "bin_spectrum",
    "collate_vlex",
    "build_curriculum_loader",
    "build_hardneg_loader",
    "train_test_split",
]
