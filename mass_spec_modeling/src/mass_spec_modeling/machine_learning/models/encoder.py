"""
Encoders
"""

from __future__ import annotations
import math
import torch
from torch import nn, Tensor
from torch_geometric.data import Data
from torch_geometric.nn import SAGPooling, global_mean_pool
from .layers import GraphGPSLayer, GINEBlock, graph_readout

class GraphEncoderTR(nn.Module):
    def __init__(self, cfg, rule_graph=False):
        super().__init__()
        self.cfg = cfg
        self.rule_graph = rule_graph
        self.in_linear = None                # lazy-init with correct in_features
        self.layer = GraphGPSLayer(cfg)
        self.pool = SAGPooling(cfg.dim_h, ratio=0.5)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.dim_h, cfg.dim_h*2),
            nn.GELU(), nn.Dropout(cfg.dropout),
            nn.Linear(cfg.dim_h*2, cfg.dim_h)
        )

    def forward(self, batch):
        # Create input projection on-the-fly to match feature count
        if self.in_linear is None:
            in_dim = int(batch.x.size(1))
            self.in_linear = nn.Linear(in_dim, self.cfg.dim_h).to(batch.x.device)

        batch.x = self.in_linear(batch.x.float())

        outputs = []
        for _ in range(self.cfg.num_layers):
            batch = self.layer(batch)
            outputs.append(batch.x)

        h = torch.stack(outputs).sum(0) if self.cfg.parallel_output else batch.x
        h = global_mean_pool(h, batch.batch)
        h = self.mlp(h)
        return h

# ----------------------- Reinforcement Learning -----------------------------------------

class GraphEncoderRL(nn.Module):
    """
    Simple GINE-based molecule graph encoder -> h_G
    Expects PyG Data with x (node), edge_index, edge_attr, and batch.
    """
    def __init__(
        self,
        node_dim: int = 32,
        edge_dim: int = 8,
        d_model: int = 256,
        n_layers: int = 4,
        dropout: float = 0.1
        ):
        super().__init__()
        self.in_proj = nn.Linear(node_dim, d_model)
        self.layers = nn.ModuleList([
            GINEBlock(d_model, d_model, edge_dim=edge_dim, dropout=dropout)
            for _ in range(n_layers)
        ])
        self.out_norm = nn.LayerNorm(d_model)

    def forward(self, data: Data) -> Tensor:
        x = data.x
        x = self.in_proj(x)
        for layer in self.layers:
            x = layer(x, data.edge_index, data.edge_attr)
        h = graph_readout(x, data.batch, method="mean")
        return self.out_norm(h)

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 4096):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: Tensor) -> Tensor:
        # x: [L,B,D]
        L = x.size(0)
        return x + self.pe[:L].unsqueeze(1)

class SpectrumEncoder(nn.Module):
    """
    Transformer over peak tokens: token=(mz, intensity, optional charge).
    Input: peaks [B, N, D_in] with D_in>=2 (mz,intensity)
    Output: h_S [B, d_model]
    """
    def __init__(
        self,
        d_in: int = 2,
        d_model: int = 256,
        n_layers: int = 4,
        n_heads: int = 8,
        dropout: float = 0.1
        ):
        super().__init__()
        self.in_proj = nn.Linear(d_in, d_model)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4*d_model,
            dropout=dropout,
            batch_first=True
            )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=n_layers)
        self.out = nn.LayerNorm(d_model)

    def forward(self, peaks: Tensor) -> Tensor:
        # peaks: [B,N,2]
        x = self.in_proj(peaks)
        x = self.encoder(x)              # [B,N,D]
        h = x.mean(dim=1)                # simple pooling
        return self.out(h)
