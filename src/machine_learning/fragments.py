"""Fragment set encoders for the machine-learning pipeline."""

from typing import List, Optional

import torch
from torch import nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data as GeometricData


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
            nn.Linear(d_latent, d_latent // 2),
            nn.Tanh(),
            nn.Linear(d_latent // 2, 1),
        )

    def _encode_fragments(self, frags: List[GeometricData]) -> torch.Tensor:
        if len(frags) == 0:
            d = self.enc_mol.gnn2.out_channels
            return torch.zeros(1, d, device=next(self.parameters()).device)
        return self.enc_mol(frags)

    def forward(
        self,
        frag_graphs_batch: List[List[GeometricData]],
        adj_batch: Optional[List[torch.Tensor]] = None,
        mass_batch: Optional[List[torch.Tensor]] = None,
    ) -> torch.Tensor:
        device = next(self.parameters()).device
        outs: List[torch.Tensor] = []
        for i, frags in enumerate(frag_graphs_batch):
            z_i = self._encode_fragments(frags).to(device)
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
            a = torch.softmax(self.att(z_i).squeeze(-1), dim=-1)
            z = (a.unsqueeze(-1) * z_i).sum(0, keepdim=True)
            outs.append(z)
        return torch.cat(outs, dim=0)


class EncFragGraph(nn.Module):
    """
    Graph-aware fragment encoder.
    frag_bag: [B, V] with V fragments as nodes.
    adjacency: [B, V, V] (preferred) or [V, V] (will be expanded).
    """

    def __init__(self, fragment_vocab_size, d_latent=128, d_h=256, R=None, mass_vocab: Optional[torch.Tensor] = None):
        super().__init__()
        self.fragment_vocab_size = fragment_vocab_size
        self.lin0 = nn.Linear(2, d_h)
        self.lin1 = nn.Linear(d_h, d_latent)
        self.rule_emb = nn.Embedding(R, d_h) if R is not None else None
        if mass_vocab is not None:
            mass_vocab = mass_vocab.detach().clone().float()
            if mass_vocab.dim() != 1 or mass_vocab.numel() != fragment_vocab_size:
                raise ValueError("mass_vocab must be a 1D tensor of length fragment_vocab_size")
            self.register_buffer("mass_vocab", mass_vocab)
        else:
            self.register_buffer("mass_vocab", None)

    def aggregate(
        self: "EncFragGraph",
        x: torch.Tensor,
        edges: Optional[torch.Tensor] = None,
        adjacency: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Aggregate fragment features using adjacency or edge list.
        """
        if adjacency is not None:
            if adjacency.dim() == 2:
                adjacency = adjacency.unsqueeze(0)
            B, V, H = x.shape
            if adjacency.size(0) == 1:
                adjacency = adjacency.expand(B, V, V)
            I = torch.eye(V, device=x.device).unsqueeze(0).expand(B, V, V)
            A = adjacency + I
            return torch.bmm(A, x)

        elif edges is not None:
            for (src, dst, b, *rest) in edges:
                rule_bias = self.rule_emb(rest[0]) if (self.rule_emb and rest) else 0.0
                x[b, dst] = x[b, dst] + x[b, src] + rule_bias
            return x

        raise ValueError("Either adjacency or edges must be provided for aggregation.")

    def forward(self, frag_bag, edges=None, adjacency=None, mass: Optional[torch.Tensor] = None):
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

        x_in = torch.stack([frag_bag, m], dim=-1)
        x0 = torch.tanh(self.lin0(x_in))
        x_aggr = self.aggregate(x0, edges=edges, adjacency=adjacency)
        z_nodes = self.lin1(x_aggr)
        return z_nodes.mean(dim=1)


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
        frag_graphs_batch: List[List[GeometricData]],
        adj_batch: Optional[List[torch.Tensor]] = None,
        mass_batch: Optional[List[torch.Tensor]] = None,
        deriv_tree_batch: Optional[List[Optional[GeometricData]]] = None,
    ) -> torch.Tensor:
        """
        Encode fragment set using derivation tree backend.

        Parameters
        ----------
        frag_graphs_batch : List[List[GeometricData]]
            Per-sample lists of fragment graphs.
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


__all__ = ["FragSetEncoderVocabless", "EncFragGraph", "FragSetEncoderWrapper"]
