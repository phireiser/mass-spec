import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.utils import to_dense_batch
from torch_geometric.nn import GENConv, GINEConv
from .convolution import DirectedHGConv

class GraphGPSLayer(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.dim_h = cfg.dim_h

        # width of edge_attr coming from your featurizer: bond_type -> 1
        self.bond_attr_dim = getattr(cfg, "bond_attr_dim", 1)

        # NEW: edge feature encoder to match GENConv’s requirement
        self.edge_encoder = nn.Sequential(
            nn.Linear(self.bond_attr_dim, self.dim_h),
            nn.GELU(),
            nn.Dropout(getattr(cfg, "dropout", 0.0)),
            nn.Linear(self.dim_h, self.dim_h),
        )

        self.dim_h = cfg.dim_h
        self.num_heads = cfg.num_heads
        self.attn_dropout = cfg.attn_dropout
        self.layer_norm = cfg.layer_norm
        self.batch_norm = cfg.batch_norm

        # self.edge_emb = nn.Linear(bond_attr_dim, atom_attr_dim)
        # Local message-passing model.
        if cfg.local_gnn_type == 'None':
            self.local_model = None
        elif cfg.local_gnn_type == 'GENConv':
            self.local_model = GENConv(cfg.dim_h, cfg.dim_h)
        elif cfg.local_gnn_type == 'GINE':
            self.local_model = GINEConv(nn.Sequential(nn.Linear(cfg.dim_h, cfg.dim_h), nn.GELU(),nn.Linear(cfg.dim_h,cfg.dim_h)),edge_dim=cfg.bond_attr_dim)

        # Global attention transformer-style model.
        if cfg.global_model_type == 'None':
            self.self_attn = None
        elif cfg.global_model_type == 'Transformer':
            self.self_attn = torch.nn.MultiheadAttention(cfg.dim_h, cfg.num_heads, dropout=self.attn_dropout, batch_first=True)

        if self.layer_norm and self.batch_norm:
            raise ValueError("Cannot apply two types of normalization together")

        # Normalization for MPNN and Self-Attention representations.
        if self.layer_norm:
            self.norm1_local = nn.LayerNorm(cfg.dim_h)
            self.norm1_attn = nn.LayerNorm(cfg.dim_h)
        if self.batch_norm:
            self.norm1_local = nn.BatchNorm1d(cfg.dim_h)
            self.norm1_attn = nn.BatchNorm1d(cfg.dim_h)

        self.dropout_local = nn.Dropout(cfg.dropout)
        self.dropout_attn = nn.Dropout(cfg.dropout)

        # Feed Forward block.
        self.activation = F.gelu
        self.ff_linear1 = nn.Linear(cfg.dim_h, cfg.dim_h * 2)
        self.ff_linear2 = nn.Linear(cfg.dim_h * 2, cfg.dim_h)
        if self.layer_norm:
            self.norm2 = nn.LayerNorm(cfg.dim_h)
        if self.batch_norm:
            self.norm2 = nn.BatchNorm1d(cfg.dim_h)
        self.ff_dropout1 = nn.Dropout(cfg.dropout)
        self.ff_dropout2 = nn.Dropout(cfg.dropout)

    def forward(self, batch):
        h = batch.x.float()
        h_in = h

        h_out_list = []

        # Local GNN:
        if self.local_model is not None:
            # Build edge features for GENConv
            if hasattr(batch, "edge_attr") and batch.edge_attr is not None and batch.edge_attr.numel():
                ea = batch.edge_attr
                if ea.dim() == 1:
                    ea = ea.view(-1, 1)
                # sanity check: width matches encoder
                if ea.size(-1) != self.edge_encoder[0].in_features:
                    raise RuntimeError(
                        f"edge_attr has width {ea.size(-1)} but edge_encoder expects "
                        f"{self.edge_encoder[0].in_features}. Set cfg.edge_attr_dim accordingly."
                    )
                eattr = self.edge_encoder(ea.float())   # (E, edge_attr_dim) -> (E, dim_h)
            else:
                eattr = None

            # pass to GENConv (or your local model)
            h_local = self.local_model(h, batch.edge_index, edge_attr=eattr).float()

            h_local = self.dropout_local(h_local)
            h_local = h_in + h_local
            if self.layer_norm: h_local = self.norm1_local(h_local)
            if self.batch_norm: h_local = self.norm1_local(h_local)
            h_out_list.append(h_local)

        # Global self-attention (pack per graph)
        if self.self_attn is not None:
            H, mask = to_dense_batch(h_in, batch.batch)        # [B, S, D], [B, S]
            H_attn = self.self_attn(H, H, H, need_weights=False)[0]  # [B, S, D]
            # Unpack back to [N, D] using mask order:
            h_attn = H_attn[mask]
            h_attn = self.dropout_attn(h_attn)
            h_attn = h_in + h_attn
            if self.layer_norm: h_attn = self.norm1_attn(h_attn)
            if self.batch_norm: h_attn = self.norm1_attn(h_attn)
            h_out_list.append(h_attn)

        h = sum(h_out_list) if len(h_out_list) > 1 else h_out_list[0]
        h = h + self._ff_block(h)
        if self.layer_norm: h = self.norm2(h)
        if self.batch_norm: h = self.norm2(h)

        batch.x = h
        return batch

    def _sa_block(self, x, mask):
        """Self-attention block."""
        x = self.self_attn(x, x, x, attn_mask=mask, need_weights=False)[0]
        return x

    def _ff_block(self, x):
        """Feed Forward block."""
        x = self.ff_dropout1(self.activation(self.ff_linear1(x)))
        return self.ff_dropout2(self.ff_linear2(x))


class HyperGraphLayer(nn.Module):
    def __init__(self, cfg):
        super().__init__()


        self.dim_h = cfg.dim_h
        self.num_heads = cfg.num_heads
        self.attn_dropout = cfg.attn_dropout
        self.layer_norm = cfg.layer_norm
        self.batch_norm = cfg.batch_norm
        # self.lin = nn.Linear(cfg.dim_h * cfg.hg_attn_heads, cfg.dim_h)
        # self.hypergraph_conv = HypergraphConv(cfg.dim_h, cfg.dim_h, use_attention=True)
        self.hypergraph_conv = DirectedHGConv(cfg)
        self.attn = nn.MultiheadAttention(cfg.dim_h, cfg.num_heads, dropout=self.attn_dropout, batch_first=True)

        self.mlp = nn.Sequential(
            nn.Linear(cfg.dim_h, cfg.dim_h*2),
            nn.GELU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.dim_h*2, cfg.dim_h),
            nn.GELU(),
            nn.Dropout(cfg.dropout)
        )

        self.layer_norm_local = nn.LayerNorm(cfg.dim_h)
        self.layer_norm_attn = nn.LayerNorm(cfg.dim_h)
        self.layer_norm = nn.LayerNorm(cfg.dim_h)

    def transform_hyperedge_index(hyperedge_index):
        """
        transforms from boundary-marked sequence
        ->
        explicit (cumsum) hyperedge indices.
        """

        if hyperedge_index.shape[1] == 0:  # empty hyperedge_index
            return hyperedge_index
        transition_points = (hyperedge_index[1][:-1] == 1) & (hyperedge_index[1][1:] == 0)
        edge_indices = torch.cumsum(torch.cat([torch.tensor([0]), transition_points]), dim=0)
        return torch.stack([hyperedge_index[0], edge_indices])

    def forward(self, hypergraph):
        h = hypergraph.x
        h_in = h


        hyperedge_index = transform_hyperedge_index(hypergraph.edge_index)
        # print(f"hyperedge_index after transform: {hyperedge_index}")
        hyperedge_head_tail = hypergraph.edge_index[1]
        h_local = self.hypergraph_conv(h,hyperedge_index,hyperedge_head_tail , hypergraph.edge_attr, hypergraph.batch)
        # h_local = self.hypergraph_conv(h, hypergraph.edge_index, hyperedge_attr = x_j)
        # print(f"hypergraph layer h_local shape after hypergraph conv: {h_local.shape}")
        h_local = h_local + h_in
        h_local = self.layer_norm_local(h_local)
        h_attn = self.attn(h, h, h, need_weights=False)[0]
        # print(f"hypergraph layer h_attn shape after attn: {h_attn.shape}")
        h_attn = h_attn + h_in
        h_attn = self.layer_norm_attn(h_attn)

        h= h_local + h_attn
        h = h + self.mlp(h)
        h = self.layer_norm(h)
        # print(f"hypergraph layer output x shape : {h.shape}")
        hypergraph.x = h
        return hypergraph



class CrossAttention(nn.Module):
    def __init__(self, state_dim, rule_dim, output_dim):
        super().__init__()
        self.query = nn.Linear(rule_dim, output_dim)
        self.key = nn.Linear(state_dim, output_dim)
        self.value = nn.Linear(state_dim, output_dim)

    def forward(self, state, rule):
        # Reshape representations if necessary
        # rule = rule.view(rule.size(0), rule.size(1), -1)
        # state = state.view(state.size(0), state.size(1), -1)

        # Compute query, key, and value
        # print(f"rule shape in cross attention: {rule.shape}")
        # print(f"state shape in cross attention: {state.shape}")
        query = self.query(rule).unsqueeze(1)  # Add singleton dimension for batch
        # print(f"query shape in cross attention: {query.shape}")
        key = self.key(state).unsqueeze(0).transpose(-2, -1)   # Transpose key
        # print(f"key shape in cross attention: {key.shape}")
        value = self.value(state).unsqueeze(1)  # Add singleton dimension for batch
        # print(f"value shape in cross attention: {value.shape}")

        # Compute cross-attention scores
        attention_scores = torch.bmm(query, key) / (query.size(-1) ** 0.5)
        attention_weights = torch.softmax(attention_scores, dim=-1)
        # print(f"attention_weights shape in cross attention: {attention_weights.shape}")
        # Apply attention to value
        attended_representation = torch.bmm(attention_weights, value)
        # print(f"attended_representation shape in cross attention: {attended_representation.shape}")
        # Combine representations
        combined_representation = rule + attended_representation.squeeze(1)
        # print(f"combined_representation shape in cross attention: {combined_representation.shape}")

        return combined_representation
