"""Policy def"""

import torch
from torch import nn

class ActionAwarePolicy(nn.Module):
    """
    Inputs:
      pred:  [B, n_bins]   current predicted spectrum bins
      targ:  [B, n_bins]   target spectrum bins
      depth: scalar or [B] (optional, if use_depth=True)
      a_bins:[B, A, n_bins] simulated bins *if* each action were taken
    Outputs:
      logits: [B, A]       per-action scores
      value:  [B, 1]       state-value
    """
    def __init__(self, n_bins: int, hidden: int = 64, use_depth: bool = False):
        super().__init__()
        self.n_bins = n_bins
        self.use_depth = use_depth

        ctx_in = 2 * n_bins + (1 if use_depth else 0)
        self.ctx_mlp = nn.Sequential(
            nn.Linear(ctx_in, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.value_head = nn.Linear(hidden, 1)

        # Per-action scoring head: concat action’s simulated bins with global context
        self.act_head = nn.Sequential(
            nn.Linear(n_bins + hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, pred: torch.Tensor, targ: torch.Tensor, depth, a_bins: torch.Tensor):
        # Ensure batch dims
        if pred.dim() == 1: pred = pred.unsqueeze(0)
        if targ.dim() == 1: targ = targ.unsqueeze(0)

        B, A, N = a_bins.shape
        assert N == self.n_bins, f"a_bins n_bins={N} != expected {self.n_bins}"

        if self.use_depth:
            # depth can be python int/float or tensor
            d = torch.as_tensor(depth, device=pred.device, dtype=pred.dtype)
            if d.dim() == 0: d = d.view(1)
            if d.numel() == 1 and B > 1: d = d.expand(B)
            d = d.view(B, 1)
            ctx_in = torch.cat([pred, targ, d], dim=1)  # [B, 2*n_bins+1]
        else:
            ctx_in = torch.cat([pred, targ], dim=1)     # [B, 2*n_bins]

        ctx = self.ctx_mlp(ctx_in)                      # [B, H]
        value = self.value_head(ctx)                    # [B, 1]

        # Repeat context across actions and score each action with its bins
        ctx_rep = ctx.unsqueeze(1).expand(-1, A, -1)    # [B, A, H]
        joint = torch.cat([a_bins, ctx_rep], dim=2)     # [B, A, n_bins+H]
        logits = self.act_head(joint).squeeze(-1)       # [B, A]

        return logits, value
