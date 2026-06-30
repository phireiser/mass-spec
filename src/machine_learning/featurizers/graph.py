"""
Featurizer for MOD Molecule Graphs
"""

import torch
from torch_geometric.data import Data

import mod
from src.data_generation.utils.term_transfers import (
    atomic_number,
    encode_vertex_label,
    graph_from_term,
)


BOND_STRENGTH = {
    mod.BondType.Single:   1.0,
    mod.BondType.Double:   2.0,
    mod.BondType.Triple:   3.0,
    mod.BondType.Aromatic: 1.5,   # conventional choice
}


class GraphFeaturizerMOD:
    """
    Convert a mod.Graph to torch_geometric.Data:
      - x[i] = [atom_id, charge, radical]  (dtype: long)
      - edge_attr[k] = [bond_type_float]    (shape [E, 1], dtype: float32)
      - edge_index in COO (undirected by doubling)
    """

    def _vertex_feat(self, v: mod.Graph.Vertex):
        # Parse from the raw stringLabel so biradicals survive: mod's v.radical
        # is a bool (caps at 1) and int(v.atomId) raises for non-concrete atoms
        # like 'C..', which would otherwise drop both atom id and radical count.
        symbol, c, r = encode_vertex_label(getattr(v, "stringLabel", ""))
        a = atomic_number(symbol)
        return [a, c, r]

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

        # Node features
        x_rows = [self._vertex_feat(v) for v in vtx]
        if x_rows:
            x = torch.tensor(x_rows, dtype=torch.long)
        else:
            x = torch.zeros((0, 3), dtype=torch.long)

        # Edges and attributes
        edges, eattrs = [], []
        for e in g.edges:
            k_src = key_of(e.source)
            k_tgt = key_of(e.target)
            try:
                u = idx_of[k_src]
                v = idx_of[k_tgt]
            except KeyError as ex:
                raise RuntimeError(f"Edge {e!r} references unknown vertex "
                    "(src={k_src!r}, tgt={k_tgt!r})") from ex

            f = self._edge_feat(e)

            edges.append([u, v])
            eattrs.append(f)

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
