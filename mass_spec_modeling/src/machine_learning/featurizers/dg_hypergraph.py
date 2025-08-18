import torch
from torch_geometric.loader import DataLoader
from torch_geometric.data.hypergraph_data import HyperGraphData
from .graph import GraphFeaturizerMOD
from .rule import RuleFeaturizerMOD
import mod

class DGHypergraphFeaturizer:
    """
    Turns a locked mod.DG into HyperGraphData:
      - x: per-vertex graph embeddings (via your GraphEncoder)
      - edge_attr: per-hyperedge rule embeddings
      - edge_index: incidence matrix [2, M] with (vertex_id, hyperedge_id)
    """
    def __init__(self, cfg, graph_encoder_cls, rule_encoder_cls):
        self.cfg = cfg
        self.gf = GraphFeaturizerMOD()
        self.rf = RuleFeaturizerMOD(self.gf)
        self.graph_encoder = graph_encoder_cls(cfg, rule_graph=False)
        self.rule_encoder  = rule_encoder_cls(cfg, rule_graph=True)

    @staticmethod
    def _collect_graphs(dg: mod.DG):
        vtx_map = {}
        graphs = []
        for idx, v in enumerate(dg.vertices):
            g = v.graph
            vtx_map[g] = idx
            graphs.append(g)
        return vtx_map, graphs

    def _incidence_from_hyperedges(self, dg: mod.DG, vtx_map):
        rows, hyperedge_names = [], []
        h_idx = 0
        for e in dg.edges:
            # sources / targets are vertex handles with .graph
            for s in e.sources:
                rows.append([vtx_map[s.graph], h_idx])
            for t in e.targets:
                rows.append([vtx_map[t.graph], h_idx])

            try:
                rn = "+".join([r.name for r in e.rules]) if len(list(e.rules)) else "no_rule"
            except Exception:
                rn = "ruleset"
            hyperedge_names.append(rn)
            h_idx += 1

        edge_index = (torch.tensor(rows, dtype=torch.long).t().contiguous()
                      if rows else torch.empty((2, 0), dtype=torch.long))
        return edge_index, hyperedge_names, h_idx

    def __call__(self, dg: mod.DG) -> HyperGraphData:
        # 1) Per-vertex graphs → pyg Data list
        vtx_map, graphs = self._collect_graphs(dg)
        graph_datas = [self.gf(g) for g in graphs]

        # 2) Batch through your encoders to get fixed-dim reps
        mol_loader = DataLoader(graph_datas, batch_size=64, shuffle=False)
        mol_rep = torch.empty((0, self.cfg.dim_h))
        for batch in mol_loader:
            out = self.graph_encoder(batch)          # expect [B, dim_h]
            mol_rep = torch.cat([mol_rep, out], 0)

        # 3) Rules per hyperedge → pyg Data list (concat left|context|right)
        rule_datas = []
        for e in dg.edges:
            # Multiple rules per hyperedge: average their embeddings later
            r_datas = [self.rf(r) for r in e.rules]
            if not r_datas:
                # empty placeholder
                rule_datas.append(Data(x=torch.zeros((0,3), dtype=torch.long),
                                       edge_index=torch.empty((2,0), dtype=torch.long),
                                       edge_attr=torch.zeros((0,2), dtype=torch.long)))
            else:
                # Pack one by one; we’ll encode & mean-pool
                rule_datas.extend(r_datas)

        # Encode rules and mean-pool per hyperedge
        rule_loader = DataLoader(rule_datas, batch_size=64, shuffle=False)
        rule_emb_all = []
        for batch in rule_loader:
            out = self.rule_encoder(batch)           # [B, dim_h]
            rule_emb_all.append(out)
        rule_emb_all = torch.cat(rule_emb_all, 0) if rule_emb_all else torch.zeros((0, self.cfg.dim_h))

        # Re-group embeddings to hyperedges (assumes ordering matched above)
        # Count rules per hyperedge:
        rules_per_e = [max(1, len(list(e.rules))) for e in dg.edges]
        rule_rep = []
        pos = 0
        for k in rules_per_e:
            if k == 0:
                rule_rep.append(torch.zeros((1, self.cfg.dim_h)))
            else:
                rule_rep.append(rule_emb_all[pos:pos+k].mean(dim=0, keepdim=True))
                pos += k
        rule_rep = torch.cat(rule_rep, dim=0) if rule_rep else torch.zeros((0, self.cfg.dim_h))

        # 4) Hypergraph incidence
        edge_index, edge_names, num_hyperedges = self._incidence_from_hyperedges(dg, vtx_map)

        # 5) Assemble HyperGraphData
        hg = HyperGraphData(
            x=mol_rep,                  # [num_vertices, dim_h]
            edge_index=edge_index,      # [2, M] (vertex_id, hyperedge_id)
            edge_attr=rule_rep          # [num_hyperedges, dim_h]
        )
        hg.edge_name = edge_names      # optional convenience payload
        return hg
