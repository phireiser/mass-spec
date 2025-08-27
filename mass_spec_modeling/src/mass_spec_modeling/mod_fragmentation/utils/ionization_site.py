from rdkit import Chem
from rdkit.Chem import Draw
from pkasolver.pkasolver import pKaSolver
from rdkit.Chem import Draw

def predict_ionization_sites(smiles, ph=7.4):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    # Initialize solver (uses light model by default)
    solver = pKaSolver()

    # Generate protonation states and predict pKa values
    results = solver.predict_pka(mol)

    # Filter for sites near the desired pH
    ionizable_atoms = []
    for atom_idx, pka in results.items():
        if abs(pka - ph) <= 3:
            ionizable_atoms.append((atom_idx, pka))

    return ionizable_atoms, mol



def draw_ionization(mol, atom_indices):
    d2d = Draw.MolDraw2DCairo(300, 300)
    opts = d2d.drawOptions()
    highlight = {idx: (1.0, 0.0, 0.0) for idx in atom_indices}  # red
    Draw.rdMolDraw2D.PrepareAndDrawMolecule(
        d2d,
        mol,
        highlightAtoms=atom_indices,
        highlightAtomColors=highlight
    )
    d2d.FinishDrawing()
    d2d.WriteDrawingText("ionization_sites.png")
    print("Saved visualization to ionization_sites.png")


if __name__ == "__main__":
    smiles = "CC(=O)O"  # Acetic acid as example
    sites, mol = predict_ionization_sites(smiles)
    draw_ionization(mol, [idx for idx, _ in sites])

    print("Ionization Sites (atom index, predicted pKa):")
    for idx, pka in sites:
        atom = mol.GetAtomWithIdx(idx)
        print(f"  Atom {idx} ({atom.GetSymbol()}): pKa ~ {pka:.2f}")
