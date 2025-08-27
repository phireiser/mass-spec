"""
Featurizer for MOD Rule Graphs
"""
from typing import Iterable, Optional, Union
import torch
from torch_geometric.data import Data
import mod

class RuleIDIndexer:
    def __init__(self,
                 known: Optional[Union[int, Iterable[int]]] = None,
                 freeze: bool = True,
                 use_unk: bool = False):
        self.id2idx = {}
        self.freeze = freeze
        self.unk_idx = 0 if use_unk else None
        if use_unk:
            self.id2idx["<UNK>"] = 0
        if known is not None:
            for rid in self._iter_ids(known):
                if rid not in self.id2idx:
                    self.id2idx[rid] = len(self.id2idx)

    def __len__(self):
        return sum(1 for k in self.id2idx.keys() if k != "<UNK>")

    def _iter_ids(self, items: Union[int, Iterable[int]]):
        if isinstance(items, mod.Rule):
            yield int(items.id); return
        if isinstance(items, int):
            yield int(items); return
        seen = set()
        for x in items:
            rid = int(x.id) if isinstance(x, mod.Rule) else int(x)
            if rid not in seen:
                seen.add(rid)
                yield rid

    def __call__(self, r_or_id: int) -> torch.Tensor:
        rid = int(r_or_id.id) if isinstance(r_or_id, mod.Rule) else int(r_or_id)
        if rid not in self.id2idx:
            if self.unk_idx is not None:
                return torch.tensor([self.unk_idx], dtype=torch.long)
            if self.freeze:
                raise KeyError(f"Unknown rule id {rid} and indexer is frozen.")
            self.id2idx[rid] = len(self.id2idx)
        return torch.tensor([self.id2idx[rid]], dtype=torch.long)


class RuleFeaturizerMOD:
    """
    Returns a 1-node PyG Data:
      - x: [[idx]]  (Long or Float)  shape [1,1]
      - edge_index: empty (2 x 0)
    """
    def __init__(
        self,
        indexer: RuleIDIndexer = RuleIDIndexer(freeze=True, use_unk=True),
        as_float: bool = False
        ):
        # Guard: don’t allow passing the class itself
        if isinstance(indexer, type):
            raise TypeError(
                "Pass an *instance* of RuleIDIndexer, e.g. RuleIDIndexer(known=..., freeze=True), "
                "not the class RuleIDIndexer."
            )
        self.indexer = indexer
        self.as_float = as_float

    def __call__(self, r: mod.Rule) -> Data:
        idx = self.indexer(r)  # tensor([idx])
        if not isinstance(idx, torch.Tensor):
            raise TypeError(f"Indexer must return a torch.Tensor, got {type(idx).__name__}.")
        x = idx.view(1, 1)
        if self.as_float:
            x = x.float()
        edge_index = torch.empty((2, 0), dtype=torch.long)
        return Data(x=x, edge_index=edge_index)
