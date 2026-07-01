"""Fragment set encoders for the machine-learning pipeline."""

from typing import List, Optional, Tuple, Union

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

    def forward(
        self,
        deriv_tree_batch: Optional[List[Optional[GeometricData]]] = None,
        return_nodes: bool = False,
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, List[torch.Tensor], List[torch.Tensor]]]:
        """
        Encode fragment set using the derivation-tree backend.

        Parameters
        ----------
        deriv_tree_batch : Optional[List[Optional[GeometricData]]]
            Per-sample derivation trees.
        return_nodes : bool
            If True, also return the per-fragment (pre-pool) node embeddings and
            their normalized masses, so a fragment-grounded decoder can predict an
            intensity per fragment. The three returns are aligned per sample.

        Returns
        -------
        torch.Tensor
            Pooled fragment embeddings [B, d_latent].
        (torch.Tensor, list[torch.Tensor], list[torch.Tensor])
            When ``return_nodes`` is True: pooled [B, d_latent], a length-B list of
            per-fragment node embeddings [n_i, d_latent], and a length-B list of
            per-fragment normalized masses [n_i] (empty tensors for absent trees).
        """
        return self._forward_tree(deriv_tree_batch, return_nodes=return_nodes)

    def _forward_tree(
        self,
        deriv_tree_batch: Optional[List[Optional[GeometricData]]],
        return_nodes: bool = False,
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, List[torch.Tensor], List[torch.Tensor]]]:
        """Process derivation trees using GNN."""
        device = next(self.parameters()).device
        outs: List[torch.Tensor] = []
        node_embs: List[torch.Tensor] = []
        node_masses: List[torch.Tensor] = []

        if deriv_tree_batch is None or len(deriv_tree_batch) == 0:
            pooled = torch.zeros(1, self.d_latent, device=device)
            if return_nodes:
                return pooled, [torch.zeros(0, self.d_latent, device=device)], [torch.zeros(0, device=device)]
            return pooled

        for tree in deriv_tree_batch:
            if tree is None or not hasattr(tree, "frag_graphs") or len(tree.frag_graphs) == 0:
                outs.append(torch.zeros(1, self.d_latent, device=device))
                node_embs.append(torch.zeros(0, self.d_latent, device=device))
                node_masses.append(torch.zeros(0, device=device))
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
            node_embs.append(x2)
            node_masses.append(x[:, -1])  # normalized mass channel, per fragment

        pooled_all = torch.cat(outs, dim=0)
        if return_nodes:
            return pooled_all, node_embs, node_masses
        return pooled_all


__all__ = ["FragSetEncoderWrapper"]
