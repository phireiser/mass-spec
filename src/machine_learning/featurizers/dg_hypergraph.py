"""
mod Derivation Graph
conversion to
py-Geometric Data
"""

import torch
from torch_geometric.loader import DataLoader
from torch_geometric.data.hypergraph_data import HyperGraphData
from torch_geometric.data import Data
import mod

from .graph import GraphFeaturizerMOD
from .rule import RuleFeaturizerMOD


class DGHypergraphFeaturizer:
    """
    Turns a locked mod.DG into HyperGraphData:
      - x: per-vertex graph embeddings (via your GraphEncoder)
      - edge_attr: per-hyperedge rule embeddings
      - edge_index: incidence matrix [2, M] with (vertex_id, hyperedge_id)
    """

    mol_rep = None
    edge_index = None
    rule_rep = None
    edge_names = None

    def __init__(
        self,
        cfg,
        graph_encoder_cls,
        rule_encoder_cls,
        *,
        batch_size_graph: int | None = None,
        batch_size_rule: int | None = None,
        eval_mode: bool = True,
        device: torch.device | str | None = None,
    ):

        self.cfg = cfg
        self.gf = GraphFeaturizerMOD()
        self.rf = RuleFeaturizerMOD()

        # Encoders
        self.graph_encoder = graph_encoder_cls(cfg, rule_graph=False)
        self.rule_encoder = rule_encoder_cls(cfg, rule_graph=True)

        # Options
        self.batch_size_graph = batch_size_graph or getattr(cfg, "batch_mol", 64)
        self.batch_size_rule = batch_size_rule or getattr(cfg, "batch_rule", 64)
        self.eval_mode = eval_mode

        # Device
        if device is not None:
            self.device = torch.device(device)
        else:
            try:
                self.device = next(self.graph_encoder.parameters()).device
            except StopIteration:
                self.device = torch.device("cpu")

        # Move & eval
        self.graph_encoder.to(self.device)
        self.rule_encoder.to(self.device)
        if self.eval_mode:
            self.graph_encoder.eval()
            self.rule_encoder.eval()

    # ----------------------------- helpers ---------------------------------

    @staticmethod
    def _graph_id(g) -> int:
        """Stable key for mapping graphs to vertex indices."""
        return getattr(g, "id", id(g))

    def _collect_graphs(self, dg: mod.DG):
        """Map each vertex's graph to a contiguous vertex index; return ordered graph list."""
        vtx_map: dict[int, int] = {}
        graphs: list = []
        for idx, v in enumerate(dg.vertices):
            g = v.graph
            vtx_map[self._graph_id(g)] = idx
            graphs.append(g)
        return vtx_map, graphs

    @staticmethod
    def _validate_graph_datas(graph_datas: list[Data]):
        for i, d in enumerate(graph_datas):
            if d.edge_attr.dim() != 2 or d.edge_attr.size(1) != 1:
                raise RuntimeError(f"graph edge_attr shape mismatch at i={i}: {tuple(d.edge_attr.shape)}")
            if d.x.dim() != 2 or d.x.size(1) != 3:
                raise RuntimeError(f"graph x shape mismatch at i={i}: {tuple(d.x.shape)}")

    def _encode_graphs(self, graph_datas: list[Data]) -> torch.Tensor:
        """Encode per-vertex graphs -> [num_vertices, dim_h]."""
        if not graph_datas:
            return torch.empty((0, self.cfg.dim_h), device=self.device)
        chunks: list[torch.Tensor] = []
        loader = DataLoader(graph_datas, batch_size=self.batch_size_graph, shuffle=False)
        for batch in loader:
            batch = batch.to(self.device)
            out = self.graph_encoder(batch)  # [B, dim_h]
            if out.dim() != 2 or out.size(1) != self.cfg.dim_h:
                raise RuntimeError(f"graph_encoder output shape {tuple(out.shape)} != (*, {self.cfg.dim_h})")
            chunks.append(out)
        return torch.cat(chunks, dim=0)

    def _rule_placeholder(self) -> Data:
        """Empty rule graph acceptable by the rule encoder (no reference to RuleFeaturizerMOD)."""
        # If your rule encoder expects different shapes/dtypes, adapt here.
        return Data(
            x=torch.zeros((0, 3), dtype=torch.long),
            edge_index=torch.empty((2, 0), dtype=torch.long),
            edge_attr=torch.zeros((0, 1), dtype=torch.float32),
        )

    @staticmethod
    def _materialize_edges(dg: mod.DG):
        """Return a concrete list of edges; safe for multiple passes."""
        return list(dg.edges)

    def _prepare_rules(self, edges: list) -> tuple[list[Data], list[int]]:
        """Turn edge rules into featurizer inputs and keep counts per hyperedge."""
        rule_datas: list[Data] = []
        rules_per_edge: list[int] = []
        for e in edges:
            rules = list(e.rules)
            n = len(rules)
            rules_per_edge.append(max(1, n))
            if n:
                rule_datas.extend(self.rf(r) for r in rules)
            else:
                rule_datas.append(self._rule_placeholder())
        return rule_datas, rules_per_edge

    def _encode_rules(self, rule_datas: list[Data]) -> torch.Tensor:
        """Encode rule graphs -> [num_rules_total, dim_h]."""
        if not rule_datas:
            return torch.empty((0, self.cfg.dim_h), device=self.device)
        chunks: list[torch.Tensor] = []
        loader = DataLoader(rule_datas, batch_size=self.batch_size_rule, shuffle=False)
        for batch in loader:
            batch = batch.to(self.device)
            out = self.rule_encoder(batch)  # [B, dim_h]
            if out.dim() != 2 or out.size(1) != self.cfg.dim_h:
                raise RuntimeError(f"rule_encoder output shape {tuple(out.shape)} != (*, {self.cfg.dim_h})")
            chunks.append(out)
        return torch.cat(chunks, dim=0)

    def _pool_rules(
        self,
        rule_emb_all: torch.Tensor,
        rules_per_edge: list[int]
        ) -> torch.Tensor:
        """Mean-pool rule embeddings per hyperedge -> [num_hyperedges, dim_h]."""
        if not rules_per_edge:
            return torch.empty((0, self.cfg.dim_h), device=self.device)
        rep_chunks: list[torch.Tensor] = []
        pos = 0
        for k in rules_per_edge:
            rep_chunks.append(rule_emb_all[pos:pos + k].mean(dim=0, keepdim=True))
            pos += k
        return torch.cat(rep_chunks, dim=0)

    def _incidence_from_hyperedges(self, dg: mod.DG, vtx_map: dict[int, int]):
        """Incidence pairs (node_idx, hyperedge_idx), names, and count."""
        rows: list[list[int]] = []
        names: list[str] = []
        for h_idx, e in enumerate(dg.edges):
            for s in e.sources:
                rows.append([vtx_map[self._graph_id(s.graph)], h_idx])
            for t in e.targets:
                rows.append([vtx_map[self._graph_id(t.graph)], h_idx])
            rules = list(e.rules)
            rn = "+".join(getattr(r, "name", "rule") for r in rules) if rules else "no_rule"
            names.append(rn)
        edge_index = (
            torch.tensor(rows, dtype=torch.long).t().contiguous()
            if rows else torch.empty((2, 0), dtype=torch.long)
        )
        return edge_index, names, len(names)

    def _assemble(
        self,
        mol_rep: torch.Tensor,
        edge_index: torch.Tensor,
        rule_rep: torch.Tensor,
        edge_names: list[str]
        ) -> HyperGraphData:
        """Create the HyperGraphData and align devices."""
        if rule_rep.size(0) != len(edge_names):
            raise RuntimeError(
                f"rule_rep rows ({rule_rep.size(0)}) != num_hyperedges ({len(edge_names)}). "
                "Ordering or counting of rules/hyperedges likely mismatched."
            )
        hg = HyperGraphData(
            x=mol_rep,                 # [num_vertices, dim_h]
            edge_index=edge_index.to(self.device),  # incidence
            edge_attr=rule_rep,        # [num_hyperedges, dim_h]
        )
        hg.edge_name = edge_names
        hg.mol_rep = mol_rep  # Explicitly add mol_rep to the HyperGraphData object
        return hg

    # ------------------------------- main -----------------------------------

    @torch.no_grad()
    def __call__(self, dg: mod.DG) -> HyperGraphData:
        """
        Convert a mod.DG into a HyperGraphData with:
          - x: [num_vertices, dim_h]   (molecular graph embeddings)
          - edge_index: [2, M]         (incidence: vertex_id, hyperedge_id)
          - edge_attr: [num_hyperedges, dim_h] (rule embeddings per hyperedge)
        """

        # Per-vertex graph featurization & encoding
        vtx_map, graphs = self._collect_graphs(dg)
        graph_datas = [self.gf(g) for g in graphs]
        self._validate_graph_datas(graph_datas)
        self.mol_rep = self._encode_graphs(graph_datas)

        # Per-hyperedge rule featurization & encoding
        edges_list = self._materialize_edges(dg)
        rule_datas, rules_per_edge = self._prepare_rules(edges_list)
        rule_emb_all = self._encode_rules(rule_datas)
        self.rule_rep = self._pool_rules(rule_emb_all, rules_per_edge)

        # Incidence and packaging
        self.edge_index, self.edge_names, _ = self._incidence_from_hyperedges(dg, vtx_map)
        return self._assemble(
            self.mol_rep,
            self.edge_index,
            self.rule_rep,
            self.edge_names
            )
