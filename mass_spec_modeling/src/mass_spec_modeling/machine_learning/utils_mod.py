""""
inspect py-torch gemoetric tensors
"""

from pprint import pprint
import pandas as pd


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
