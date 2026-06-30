"""Fragment set encoders for the machine-learning pipeline."""

from typing import List, Optional

import torch
from torch import nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data as GeometricData


class FragSetEncoderWrapper(nn.Module):
    """
    Fragment set encoder using PyTorch Geometric derivation trees with GNN.
    """

    def __init__(self, enc_mol: "EncMol", d_latent: int):
        super().__init__()
        self.enc_mol = enc_mol
        self.d_latent = d_latent
        self.gnn1 = GCNConv(d_latent + 1, 64)
        self.gnn2 = GCNConv(64, d_latent)
        self.global_pool = global_mean_pool

    def forward(self, deriv_tree_batch: Optional[List[Optional[GeometricData]]] = None) -> torch.Tensor:
        """
        Encode fragment set using the derivation-tree backend.

        Parameters
        ----------
        deriv_tree_batch : Optional[List[Optional[GeometricData]]]
            Per-sample derivation trees.

        Returns
        -------
        torch.Tensor
            Fragment embeddings [B, d_latent].
        """
        return self._forward_tree(deriv_tree_batch)

    def _forward_tree(self, deriv_tree_batch: Optional[List[Optional[GeometricData]]]) -> torch.Tensor:
        """Process derivation trees using GNN."""
        device = next(self.parameters()).device
        outs = []

        if deriv_tree_batch is None or len(deriv_tree_batch) == 0:
            return torch.zeros(1, self.d_latent, device=device)

        for tree in deriv_tree_batch:
            if tree is None or not hasattr(tree, "frag_graphs") or len(tree.frag_graphs) == 0:
                outs.append(torch.zeros(1, self.d_latent, device=device))
                continue

            frag_zs = self.enc_mol([fg for fg in tree.frag_graphs])

            if hasattr(tree, "masses") and tree.masses.numel() > 0:
                masses = tree.masses.to(device).unsqueeze(-1)
                x = torch.cat([frag_zs, masses], dim=-1)
            else:
                x = torch.cat([frag_zs, torch.zeros(frag_zs.size(0), 1, device=device)], dim=-1)

            edge_index = tree.edge_index.to(device).long()

            x1 = F.relu(self.gnn1(x, edge_index))
            x2 = self.gnn2(x1, edge_index)

            batch_idx = torch.zeros(x2.size(0), dtype=torch.long, device=device)
            pooled = self.global_pool(x2, batch_idx)
            outs.append(pooled)

        return torch.cat(outs, dim=0)


__all__ = ["FragSetEncoderWrapper"]
