import torch
from torch_geometric.data import Data
import mod
from .graph import GraphFeaturizerMOD

class RuleFeaturizerMOD:
    """Encodes a mod.Rule by concatenating left/context/right graphs and tagging membership."""
    def __init__(self, graph_featurizer: GraphFeaturizerMOD):
        self.gf = graph_featurizer

    def _tag_nodes(self, data: Data, tag_vec):
        tag = torch.tensor([tag_vec] * data.num_nodes, dtype=torch.long)
        data.x = torch.cat([data.x, tag], dim=1) if data.num_nodes > 0 else torch.zeros((0, data.x.size(1)+3), dtype=torch.long)
        return data

    def __call__(self, r: mod.Rule) -> Data:
        # Proxies provide labelled-graph views
        L = self.gf(r.left)    # Rule.LeftGraph implements LabelledGraph
        C = self.gf(r.context) # Rule.ContextGraph
        R = self.gf(r.right)   # Rule.RightGraph

        L = self._tag_nodes(L, [1,0,0])
        C = self._tag_nodes(C, [0,1,0])
        R = self._tag_nodes(R, [0,0,1])

        # Offset and concat
        off_C = L.num_nodes
        off_R = L.num_nodes + C.num_nodes

        C.edge_index = C.edge_index + off_C
        R.edge_index = R.edge_index + off_R

        x = torch.cat([L.x, C.x, R.x], dim=0)
        edge_index = torch.cat([L.edge_index, C.edge_index, R.edge_index], dim=1)
        edge_attr  = torch.cat([L.edge_attr,  C.edge_attr,  R.edge_attr ], dim=0)

        return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)
