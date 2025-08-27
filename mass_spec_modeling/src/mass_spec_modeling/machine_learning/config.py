"""configuration class for pytorch"""
class Cfg:
    """config class"""
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
