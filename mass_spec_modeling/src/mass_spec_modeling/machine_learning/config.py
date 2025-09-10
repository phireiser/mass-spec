"""configuration class for pytorch"""

from __future__ import annotations
from dataclasses import dataclass, field


class Cfg:
    """model config class"""
    def __init__(self,
                 dim_h=128,
                 num_layers=2,
                 parallel_output=False,
                 dropout=0.1,
                 # local/global blocks
                 local_gnn_type='GENConv',          # choices: 'None' | 'GENConv' | 'GINE'
                 global_model_type='Transformer',   # choices: 'None' | 'Transformer'
                 num_heads=4,
                 attn_dropout=0.0,
                 layer_norm=True,
                 batch_norm=False,
                 # feature dims
                 bond_attr_dim=1,                   # we encode bond_type
                 # hypergraph conv heads (if you use DirectedHGConv)
                 num_edge_heads=4,
                 num_node_heads=4):
        self.dim_h = dim_h
        self.num_layers = num_layers
        self.parallel_output = parallel_output
        self.dropout = dropout
        self.local_gnn_type = local_gnn_type
        self.global_model_type = global_model_type
        self.num_heads = num_heads
        self.attn_dropout = attn_dropout
        self.layer_norm = layer_norm
        self.batch_norm = batch_norm
        self.bond_attr_dim = bond_attr_dim
        self.num_edge_heads = num_edge_heads
        self.num_node_heads = num_node_heads

# ----------------------- Reinforcement Learning -----------------------------------------

@dataclass
class DataConfig:
    n_bins: int = 20000          # spectrum bins (e.g., 0..2000 m/z with 0.1 Da)
    mz_min: float = 0.0
    mz_max: float = 2000.0
    bin_size: float = 0.1        # (mz_max - mz_min) / n_bins must equal this
    ppm_tol: float = 10.0
    intensity_norm: str = "sum"  # "sum" or "max"

@dataclass
class ModelConfig:
    d_model: int = 256
    gnn_layers: int = 4
    spec_layers: int = 4
    spec_heads: int = 8
    dropout: float = 0.1
    fragment_catalog_size: int = 4096  # K in the outline

@dataclass
class TrainConfig:
    lr: float = 1e-3
    weight_decay: float = 1e-5
    epochs: int = 20
    batch_size: int = 16
    grad_clip: float = 1.0
    device: str = "cuda"

@dataclass
class RLConfig:
    gamma: float = 0.99
    entropy_coef: float = 0.01
    value_coef: float = 0.5
    lr: float = 3e-4
    rollout_len: int = 5
    max_steps: int = 200000
    log_interval: int = 1000
    device: str = "cuda"
    max_depth: int = 6   # max rule applications per episode

@dataclass
class FullConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    rl: RLConfig = field(default_factory=RLConfig)
