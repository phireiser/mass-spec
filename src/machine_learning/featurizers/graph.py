"""
Featurizer for MOD Molecule Graphs
"""

import torch
from torch_geometric.data import Data

import mod
from src.data_generation.utils.term_transfers import (
    encode_vertex_label,
    graph_from_term,
)


BOND_STRENGTH = {
    mod.BondType.Single:   1.0,
    mod.BondType.Double:   2.0,
    mod.BondType.Triple:   3.0,
    mod.BondType.Aromatic: 1.5,   # conventional choice
}

# Fixed element vocabulary so the node-feature width is constant across all
# graphs (required for batching). Anything outside falls into the "other" slot.
ELEMENT_VOCAB = ("C", "H", "O", "N", "S", "P", "F", "Cl", "Br", "I", "Si", "B")
_ELEMENT_INDEX = {sym: i for i, sym in enumerate(ELEMENT_VOCAB)}
# Node feature layout: one-hot(element)+other, then
# [charge, radical, degree, aromatic, incident_bond_order].
ATOM_FEATURE_DIM = len(ELEMENT_VOCAB) + 1 + 5


class GraphFeaturizerMOD:
    """
    Convert a mod.Graph to torch_geometric.Data:
      - x[i] = one-hot(element)+other, then [charge, radical, degree, aromatic,
        incident_bond_order]  (dtype: float32, width ``ATOM_FEATURE_DIM``)
      - edge_attr[k] = [bond_order_float]   (shape [E, 1], dtype: float32)
      - edge_index in COO, undirected (each bond emitted in both directions)

    The connectivity-derived channels (degree, aromatic flag, summed bond order)
    are what let the encoder separate constitutional isomers instead of collapsing
    to composition/mass; plain atom identity alone cannot.
    """

    def _vertex_label(self, v: mod.Graph.Vertex):
        # Parse from the raw stringLabel so biradicals survive: mod's v.radical
        # is a bool (caps at 1) and int(v.atomId) raises for non-concrete atoms
        # like 'C..', which would otherwise drop both atom id and radical count.
        symbol, c, r = encode_vertex_label(getattr(v, "stringLabel", ""))
        return symbol, float(c), float(r)

    def _edge_feat(self, e: mod.Graph.Edge):
        # Map bondType -> float with clear error on unknown types
        try:
            return float(BOND_STRENGTH[e.bondType])
        except KeyError as ex:
            raise KeyError(f"Unknown bondType {e.bondType!r} for edge {e!r}") from ex

    @staticmethod
    def _maybe_term_graph(g: mod.Graph) -> mod.Graph:
        # Heuristic: if the first vertex looks like a term 'a(...)', convert.
        # Works only when graph has at least one vertex and stringLabel exists.
        vlist = list(g.vertices)
        if vlist:
            lbl = getattr(vlist[0], "stringLabel", "")
            if isinstance(lbl, str) and lbl.startswith("a("):
                return graph_from_term(g)
        return g


    def __call__(
        self, g: mod.Graph,
        device: torch.device | str | None = None
        ) -> Data:
        # Convert term graphs if needed
        g = self._maybe_term_graph(g)

        # Prefer a stable vertex order if an id is available
        try:
            vtx = sorted(g.vertices, key=lambda v: getattr(v, "id"))
        except AttributeError:
            vtx = list(g.vertices)

        # Choose a stable key for dicts even if Vertex is unhashable
        def key_of(vertex):
            try:
                hash(vertex)
                return vertex
            except TypeError:
                # fall back to intrinsic id if present; else, last resort: repr
                return getattr(vertex, "id", repr(vertex))

        idx_of = {key_of(v): i for i, v in enumerate(vtx)}
        n = len(vtx)

        # Per-vertex atom labels (symbol, charge, radical)
        labels = [self._vertex_label(v) for v in vtx]

        # Connectivity-derived accumulators + undirected edge lists
        degree = [0.0] * n
        bond_order = [0.0] * n
        aromatic = [0.0] * n
        edges, eattrs = [], []
        for e in g.edges:
            k_src = key_of(e.source)
            k_tgt = key_of(e.target)
            try:
                u = idx_of[k_src]
                v = idx_of[k_tgt]
            except KeyError as ex:
                raise RuntimeError(f"Edge {e!r} references unknown vertex "
                    f"(src={k_src!r}, tgt={k_tgt!r})") from ex

            f = self._edge_feat(e)
            degree[u] += 1.0; degree[v] += 1.0
            bond_order[u] += f; bond_order[v] += f
            if e.bondType == mod.BondType.Aromatic:
                aromatic[u] = 1.0; aromatic[v] = 1.0

            # emit both directions so message passing is undirected
            edges.append([u, v]); eattrs.append(f)
            edges.append([v, u]); eattrs.append(f)

        # Assemble wide float node features: one-hot(element)+other, then
        # [charge, radical, degree, aromatic, incident_bond_order].
        x_rows = []
        for i, (symbol, c, r) in enumerate(labels):
            onehot = [0.0] * (len(ELEMENT_VOCAB) + 1)
            onehot[_ELEMENT_INDEX.get(symbol, len(ELEMENT_VOCAB))] = 1.0
            x_rows.append(onehot + [c, r, degree[i], aromatic[i], bond_order[i]])
        if x_rows:
            x = torch.tensor(x_rows, dtype=torch.float32)
        else:
            x = torch.zeros((0, ATOM_FEATURE_DIM), dtype=torch.float32)

        edge_index = (
            torch.tensor(edges, dtype=torch.long).t().contiguous()
            if edges else torch.empty((2, 0), dtype=torch.long)
        )

        # Normalize edge_attr to [E, 1] float32
        if eattrs:
            edge_attr = torch.as_tensor(eattrs, dtype=torch.float32).reshape(-1, 1)
        else:
            edge_attr = torch.zeros((0, 1), dtype=torch.float32)

        data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)

        if device is not None:
            data = data.to(device)
        return data
