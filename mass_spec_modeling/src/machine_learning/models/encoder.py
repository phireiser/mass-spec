import torch
import torch.nn as nn
from torch_geometric.nn import SAGPooling, global_mean_pool
from .layers import GraphGPSLayer


class GraphEncoder(nn.Module):
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
