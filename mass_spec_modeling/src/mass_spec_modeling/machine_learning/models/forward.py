from __future__ import annotations
from torch import nn, Tensor
from .encoder import GraphEncoderRL

class ForwardPredictor(nn.Module):
    """
    Graph → Spectrum bins (+ fragment catalog multi-label)
    """
    def __init__(self, node_dim: int, edge_dim: int, d_model: int, n_layers: int, n_bins: int, frag_catalog_size: int, dropout: float = 0.1):
        super().__init__()
        self.genc = GraphEncoderRL(node_dim=node_dim, edge_dim=edge_dim, d_model=d_model, n_layers=n_layers, dropout=dropout)
        self.head_bins = nn.Sequential(
            nn.Linear(d_model, 4*d_model), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(4*d_model, n_bins)
        )
        self.head_frags = nn.Linear(d_model, frag_catalog_size)

    def forward(self, pyg_batch) -> tuple[Tensor, Tensor]:
        h = self.genc(pyg_batch)              # [B, d]
        s_bins = self.head_bins(h)            # [B, n_bins]
        frag_logits = self.head_frags(h)      # [B, K]
        return s_bins, frag_logits
