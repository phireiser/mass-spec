""""
inspect py-torch gemoetric tensors
"""

from pprint import pprint
from typing import List, Tuple
import pandas as pd
import torch
import mod
from .target_peaks import clean_spectra, make_peaks_tensor


def inspect_hg(hg):
    """display statistics of the torch Data"""
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
    print(hg)                   # the summary
    print(hg.x)                 # node features
    print(hg.edge_index)        # incidence matrix
    print(hg.edge_attr)         # edge (hyperedge) features
    print(hg.edge_name)         # names/IDs of hyperedges

    print("==============================\n")
    # --- Node features ---
    df_nodes = pd.DataFrame(hg.x.numpy())
    df_nodes.index.name = "node_id"
    print("=== Nodes ===")
    print(df_nodes.head())

    # --- Edge (hyperedge) features ---
    df_edges = pd.DataFrame(hg.edge_attr.numpy())
    df_edges.index.name = "edge_id"
    print("\n=== Edges ===")
    print(df_edges.head())

    # --- Edge incidence (which nodes belong to which edge) ---
    src, dst = hg.edge_index.numpy()
    df_incidence = pd.DataFrame({"node_id": src, "edge_id": dst})
    print("\n=== Incidence (node edge mapping) ===")
    print(df_incidence.head())

    # --- Hyperedge names if available ---
    if hasattr(hg, "edge_name"):
        df_edges["name"] = hg.edge_name
        print("\n=== Edges with names ===")
        print(df_edges.head())


def spectra_to_tensor(cleaned: List[Tuple[float, float]]) -> torch.Tensor:
    """
    Convert cleaned spectra into a 2D torch tensor.

    Parameters
    ----------
    cleaned : List[Tuple[float, float]]
        List of (m/z, intensity) pairs.

    Returns
    -------
    torch.Tensor
        shape (N, 2), dtype float32
    """
    if not cleaned:
        return torch.empty((0, 2), dtype=torch.float32)

    tensor = torch.tensor(cleaned, dtype=torch.float32)
    return tensor


def build_fragment_catalog(all_frag_lists, ppm_merge=5.0) -> torch.Tensor:
    # all_frag_lists: List[List[float]]
    flat = []
    for frags in all_frag_lists:
        for m in frags:
            if isinstance(m, torch.Tensor):
                if m.ndim == 0:
                    flat.append(float(m.item()))
                else:
                    flat.extend(float(x) for x in m.reshape(-1).tolist())
            else:
                flat.append(float(m))
    if not flat:
        return torch.empty(0, dtype=torch.float32)

    masses = torch.tensor(flat, dtype=torch.float64)
    masses, _ = torch.sort(masses)

    keep = [0]
    for i in range(1, masses.numel()):
        m_prev = masses[keep[-1]]
        ppm = (masses[i] - m_prev).abs() / max(float(m_prev), 1e-9) * 1e6
        if ppm > ppm_merge:
            keep.append(i)
    catalog = masses[keep].to(torch.float32)
    return catalog

def frags_to_mask(frag_masses, catalog, ppm_tol=10.0):
    """
    frag_masses: 1D tensor [F]
    catalog: 1D tensor [K]
    returns: 1D tensor [K] with {0,1}
    """
    if len(frag_masses) == 0 or len(catalog) == 0:
        return torch.zeros(len(catalog), dtype=torch.float32)
    # pairwise ppm distances
    fm = frag_masses.view(-1, 1)           # [F,1]
    cm = catalog.view(1, -1)               # [1,K]
    ppm = (fm - cm).abs() / cm.clamp(min=1e-6) * 1e6  # [F,K]
    hits = (ppm <= ppm_tol).any(dim=0)     # [K]
    return hits.float()

# Optional: intensity-weighted targets instead of {0,1}
def frags_to_soft_mask(frag_mz_int, catalog, ppm_tol=10.0, p=1.0):
    """
    frag_mz_int: tensor [F,2] (mz,intensity)
    returns: [K] in [0,1], normalized; p controls sharpness (1 linear, 2 quadratic)
    """
    if frag_mz_int.numel() == 0 or len(catalog) == 0:
        return torch.zeros(len(catalog), dtype=torch.float32)
    fm = frag_mz_int[:, 0].view(-1, 1)     # [F,1]
    fi = frag_mz_int[:, 1].view(-1, 1)     # [F,1]
    cm = catalog.view(1, -1)               # [1,K]
    ppm = (fm - cm).abs() / cm.clamp(min=1e-6) * 1e6
    w = (ppm <= ppm_tol).float() * (fi ** p)   # assign intensity to matched catalog bins
    v = w.sum(dim=0)                            # [K]
    if v.sum() > 0:
        v = v / v.sum()
    return v.to(torch.float32)

def get_out_edges_by_vertex_id(dg: mod.DG, v_id: int):
    """
    returns the ids of the hyperedges
    for a certain hyper vertex idenitfied by its mod id
    """
    return [e.id for e in next(v.outEdges for v in dg.vertices if v.id == v_id)]

def get_rule_ids_by_edge_id(dg: mod.DG, eid: int):
    """
    gets the mod ids of the rules
    of a specific edge identified by its mod id
    """
    edge = next(e for e in dg.edges if e.id == eid)
    return [r.id for r in edge.rules]

def get_fragment_ids_by_edge_id(dg: mod.DG, eid: int):
    """
    gets the mod ids of the edges
    of a specific edge identified by its mod id
    """
    edge = next(e for e in dg.edges if e.id == eid)
    return [t.id for t in edge.targets]

def read_mols_csv(path: str):
    """read csv with name and smiles molecuel definitions"""
    df = pd.read_csv(path)  # expects columns "name" and "smiles"
    mols_definitions = list(zip(df["name"], df["smiles"]))
    return mols_definitions


@torch.no_grad()
def peaks_to_mask_batch(
    peaks_batch,
    catalog_mz: torch.Tensor,
    ppm_merge: float = 5.0,
) -> torch.Tensor:
    """
    peaks_batch: List of per-sample peaks. Each item can be:
      - List[Tuple[mz, inten]]  (preferred)
      - List[mz]                (mz only)
      - Tensor[F, 2]            (mz,inten)
      - Tensor[F] or Tensor[F,1](mz only)
      - None or empty
    catalog_mz: Tensor[K] (sorted, on any device/dtype)
    returns: Tensor[B, K] float mask on same device as catalog_mz
    """
    device = catalog_mz.device
    K = int(catalog_mz.numel())
    B = len(peaks_batch)
    mask = torch.zeros((B, K), dtype=torch.float32, device=device)

    cat_dtype = catalog_mz.dtype  # ensure searchsorted dtypes match

    def is_empty(x) -> bool:
        if x is None:
            return True
        if isinstance(x, (list, tuple)):
            return len(x) == 0
        if torch.is_tensor(x):
            return x.numel() == 0
        return False

    for b, pairs in enumerate(peaks_batch):
        if is_empty(pairs):
            continue

        # Normalize to a 1D tensor of m/z values (on device, same dtype as catalog)
        if isinstance(pairs, (list, tuple)):
            # list of (mz, inten) OR list of mz
            if len(pairs) > 0 and isinstance(pairs[0], (list, tuple)) and len(pairs[0]) >= 1:
                mzs = [float(p[0]) for p in pairs]  # ignore intensity
            else:
                mzs = [float(p) for p in pairs]
            frags = torch.tensor(mzs, dtype=cat_dtype, device=device)
        elif torch.is_tensor(pairs):
            t = pairs.to(device)
            if t.ndim == 1:
                frags = t.to(dtype=cat_dtype)
            elif t.ndim == 2:
                # [F, 2] (mz,inten) or [F,1]
                frags = t[:, 0].to(dtype=cat_dtype)
            else:
                # Unexpected rank; skip
                continue
        else:
            # Unknown type; skip
            continue

        if frags.numel() == 0:
            continue

        # PPM window per fragment
        frags = frags.contiguous()
        tol = (ppm_merge * 1e-6) * frags
        left  = torch.searchsorted(catalog_mz, frags - tol)
        right = torch.searchsorted(catalog_mz, frags + tol, right=True)

        # For each fragment, mark the nearest catalog bin inside the window
        for i in range(frags.numel()):
            l = int(left[i])
            r = int(right[i])
            if l >= r:
                continue
            seg = catalog_mz[l:r]
            k = l + int(torch.argmin((seg - frags[i]).abs()))
            mask[b, k] = 1.0

    return mask

def clean_spectra_tensor(spectra, *, device=None, dtype=torch.float32):
    cleaned = clean_spectra(spectra)                 # List[(mz,intensity)]
    return make_peaks_tensor(cleaned, device=device, dtype=dtype, normalize="max")
