import torch
from torch_geometric.data import Data

import mod
from ..utils_mod import _get_first_attr, _safe_bond_type_key, BOND_ORDER



class LabelVocab:
    """
    Small helper: dynamic vocab for string/enum labels
    """
    def __init__(self, add_misc=True):
        self._map = {}
        self._frozen = False
        if add_misc:
            self._map["<UNK>"] = 0

    def __len__(self): return len(self._map)
    def freeze(self): self._frozen = True
    def idx(self, key):
        if key in self._map: return self._map[key]
        if self._frozen: return self._map.get("<UNK>", 0)
        self._map[key] = len(self._map)
        return self._map[key]


class GraphFeaturizerMOD:
    """
    Convert a mod.Graph to torch_geometric.Data:
      - x[i] = [v_label_id, charge, degree]
      - edge_attr[k] = [e_label_id, bond_type_id]
      - edge_index in COO (undirected by doubling)
    Vocabularies are learned on the fly from encountered labels.
    """
    def __init__(self):
        self.v_label_vocab = LabelVocab()
        self.e_label_vocab = LabelVocab()
        self.bond_type_vocab = LabelVocab()

    def _vertex_feat(self, v):
        # Try several common label fields; many rule/context vertices lack stringLabel
        raw_lbl = _get_first_attr(v, ("stringLabel", "label", "atomLabel", "symbol", "element", "name"))
        v_lbl = self.v_label_vocab.idx(str(raw_lbl) if raw_lbl is not None else "<UNK>")

        # charge (optional on many graphs)
        try:
            chg = int(getattr(v, "charge", 0) or 0)
        except Exception:
            chg = 0

        # degree (some vertex types don’t expose it; keep 0 fallback)
        deg = getattr(v, "degree", None)
        if deg is None:
            deg = getattr(v, "deg", None)
        if deg is None and hasattr(v, "inDegree") and hasattr(v, "outDegree"):
            try:
                deg = int(v.inDegree + v.outDegree)
            except Exception:
                deg = 0
        if deg is None:
            deg = 0

        return [v_lbl, chg, int(deg)]


    def _edge_feat(self, e):
        e_raw = _get_first_attr(e, ("stringLabel", "label", "type", "name"))
        e_lbl = self.e_label_vocab.idx(str(e_raw) if e_raw is not None else "<UNK>")
        bt_key = _safe_bond_type_key(e)
        bt = self.bond_type_vocab.idx(bt_key)
        order = float(BOND_ORDER.get(bt_key, 0.0))  # numeric bond order
        return [e_lbl, bt], order


    def __call__(self, g: mod.Graph) -> Data:
        vtx = list(g.vertices)
        idx_of = {v: i for i, v in enumerate(vtx)}

        x_rows = [self._vertex_feat(v) for v in vtx]
        x = torch.tensor(x_rows, dtype=torch.long) if x_rows else torch.zeros((0, 3), dtype=torch.long)

        edges, eattrs, eweights = [], [], []
        for e in g.edges:
            u = idx_of[e.source]; v = idx_of[e.target]
            f, w = self._edge_feat(e)
            edges.append([u, v]); eattrs.append(f); eweights.append(w)
            edges.append([v, u]); eattrs.append(f); eweights.append(w)

        edge_index = (torch.tensor(edges, dtype=torch.long).t().contiguous()
                    if edges else torch.empty((2, 0), dtype=torch.long))
        edge_attr = (torch.tensor(eattrs, dtype=torch.long)
                    if eattrs else torch.zeros((0, 2), dtype=torch.long))
        edge_weight = (torch.tensor(eweights, dtype=torch.float32)
                    if eweights else torch.zeros((0,), dtype=torch.float32))

        return Data(x=x, edge_index=edge_index, edge_attr=edge_attr, edge_weight=edge_weight)
