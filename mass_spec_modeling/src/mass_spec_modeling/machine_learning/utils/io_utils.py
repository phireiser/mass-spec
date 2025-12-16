import pandas as pd


def read_mols_csv(path: str):
    """Read a CSV with molecule definitions (expects columns 'name' and 'smiles')."""
    df = pd.read_csv(path)
    return list(zip(df["name"], df["smiles"]))
