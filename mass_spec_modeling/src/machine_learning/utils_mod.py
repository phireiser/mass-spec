import ctypes
import os
import sys
import torch
from pprint import pprint

# --- Optional: MOD bootstrap (keep if you still need the local lib path) ---
# Move your previous two lines here so other modules can just `import mod` safely.
try:
    sys.setdlopenflags(sys.getdlopenflags() | ctypes.RTLD_GLOBAL)
    # Adjust/remove this path as needed for your environment:
    MOD_LIB = os.environ.get("MOD_LIB64", "/home/talax/xtof/local/Mod/lib64/")
    if os.path.isdir(MOD_LIB) and MOD_LIB not in sys.path:
        sys.path.append(MOD_LIB)
except Exception:
    pass

import mod  # PyMØD



def transform_hyperedge_index(hyperedge_index):
    if hyperedge_index.shape[1] == 0:  # empty hyperedge_index
        return hyperedge_index
    transition_points = (hyperedge_index[1][:-1] == 1) & (hyperedge_index[1][1:] == 0)
    edge_indices = torch.cumsum(torch.cat([torch.tensor([0]), transition_points]), dim=0)
    return torch.stack([hyperedge_index[0], edge_indices])


def inspect_hg(hg):
    print("\n=== HyperGraphData summary ===")
    print(f"x (vertex reps): \t\t {tuple(hg.x.shape)}")
    print(f"edge_index (incidence): \t {tuple(hg.edge_index.shape)}")
    print(f"edge_attr (edge reps): \t\t {tuple(hg.edge_attr.shape)}")
    if hasattr(hg, "edge_name"):
        print(f"# edge names: \t\t\t {len(hg.edge_name)}")
        print(f"# distinct edge names: \t\t {len(set(hg.edge_name))}")
        print("sample names (5):")
        pprint(list(set(hg.edge_name))[:5])
    if hg.edge_index.numel() > 0:
        ei = hg.edge_index
        n_show = min(ei.size(1), 10)
        pairs = [(int(ei[0,i]), int(ei[1,i])) for i in range(n_show)]
        print(f"first {n_show} incidence pairs (vertex_id, hyperedge_id): {pairs}")
    print("==============================\n")




def _safe_bond_type_key(e):
    """
    Return a stable string key for the edge's bond type.
    Never calls str() on Invalid to avoid mod.libpymod.LogicError.
    Falls back to stringLabel or 'INVALID'.
    """
    bt = getattr(e, "bondType", None)

    # If mod.BondType.Invalid exists and matches, treat as invalid
    BondType = getattr(mod, "BondType", None)
    if BondType is not None and hasattr(BondType, "Invalid") and bt == BondType.Invalid:
        return "BondType::Invalid"

    if bt is not None:
        try:
            return str(bt)  # e.g., "BondType::Single"
        except mod.libpymod.LogicError:
            pass

    # Fallbacks
    lbl = getattr(e, "stringLabel", None)
    return str(lbl) if lbl is not None else "INVALID"

BOND_ORDER = {
    "BondType::Single":   1.0,
    "BondType::Double":   2.0,
    "BondType::Triple":   3.0,
    "BondType::Aromatic": 1.5,   # conventional choiced
}

def _get_first_attr(obj, names):
    """Return the first non-None attribute from names, else None."""
    for n in names:
        if hasattr(obj, n):
            try:
                v = getattr(obj, n)
                if v is not None:
                    return v
            except Exception:
                pass
    return None
