"""Spectrum -> Fingerprint predictor"""

from __future__ import annotations
from torch import nn
from torch import Tensor

class BackwardPredictorBins(nn.Module):
    """
    Input:  binned spectrum [B, n_bins] (normalized)
    Output: fragment logits [B, K] (multi-label over fragment catalog masses)
    """
    def __init__(self, n_bins: int, out_dim: int, d: int = 1024, dropout: float = 0.1):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(n_bins, d),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d, d),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.head = nn.Linear(d, out_dim)  # logits over K fragments

    def forward(self, binned: Tensor) -> Tensor:
        h = self.mlp(binned)
        return self.head(h)  # [B, K] logits
