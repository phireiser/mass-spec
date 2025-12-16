"""Reinforcement Learning Training"""
from pathlib import Path
import torch
import mod


from mass_spec_modeling.machine_learning.datasets import SpectraDataset
from mass_spec_modeling.machine_learning.train_supervised import (
    train_forward_supervised, normalize_feature_dims, train_backward_supervised)
from mass_spec_modeling.machine_learning.rl.envs import ForwardFragEnv, BackwardMolEnv
from mass_spec_modeling.machine_learning.rl.train_reinforce import (
    reinforce_forward_env, reinforce_backward_env)
from mass_spec_modeling.machine_learning.rl.policy import ActionAwarePolicy
from mass_spec_modeling.machine_learning.rl.mod_engine_adapter import ModEngineAdapter
from mass_spec_modeling.machine_learning.config import FullConfig, Cfg
from mass_spec_modeling.machine_learning.featurizers.dg_hypergraph import GraphFeaturizerMOD
from mass_spec_modeling.machine_learning import utils_mod


from mass_spec_modeling.mod_fragmentation import utils


MOL_DEF_PATH = "~/Nextcloud/studium/computationalScience/thesis/mol/" \
            + "mass_spec_modeling/exec_scripts/ms_data/compounds.csv"
LOAD_PATH = Path("~/Nextcloud/studium/computationalScience/thesis/mol/dump/")
ROOT_NODE_ID = 0

cfg = Cfg()
fcfg = FullConfig()

device = "cuda" if torch.cuda.is_available() and fcfg.train.device == "cuda" else "cpu"


mols_definitions = utils_mod.read_mols_csv(MOL_DEF_PATH)
# testing dataset
mols_definitions = [
        ("aniline", "C1=CC=C(C=C1)N"),
        ("benzoic_acid", "C1=CC=C(C=C1)C(=O)O"),
        ("benzene", "C1=CC=CC=C1"),
    ]


######################################## Prepare Data Set

mol_graphs, peaks_list, frags_per_sample = [], [], []


# Forward
for name, smi in mols_definitions:
    mol = mod.Graph.fromSMILES(smi, name=name)
    dg = utils.load_derivation_graph(mol.name, path=LOAD_PATH / "fwd")

    # featurize graph -> PyG Data
#   hg = dg_featurizer(dg)
#   mol_graphs.append(hg.mol_rep)
#   mol_graph_enc = GraphEncoderRL()
    featurizer =  GraphFeaturizerMOD()
    data = featurizer(mol)
    mol_graphs.append(data)

    # spectrum from DG (list of (mz,int))
    pairs_with_rules = utils.get_spectra_from_mod_derivation_graph(dg)
    pairs = [(p[0], p[1]) for p in pairs_with_rules]
    peaks = torch.tensor(pairs, dtype=torch.float32)
    peaks_list.append(peaks)

    # fragments for mask = just masses
    frags_per_sample.append([m for (m, _I) in pairs])

# Build fragment catalog and masks ONCE
catalog = utils_mod.build_fragment_catalog(frags_per_sample, ppm_merge=5.0)
frag_masks = [
    utils_mod.frags_to_mask(torch.tensor(masses, dtype=torch.float32), catalog, ppm_tol=5.0)
    for masses in frags_per_sample
]

# Dataset (supervised pretrain)
dataset = SpectraDataset(
    mol_graphs=mol_graphs,
    peaks_list=peaks_list,
    n_bins=fcfg.data.n_bins,
    mz_min=fcfg.data.mz_min,
    mz_max=fcfg.data.mz_max,
    intensity_norm=fcfg.data.intensity_norm,
    frag_catalog_masks=frag_masks,
)

######################################## Do real RL training

node_dim, edge_dim = normalize_feature_dims(mol_graphs)

# Supervised forward model (G -> S) pretrain
forward_model = train_forward_supervised(
    dataset=dataset,
    node_dim=node_dim,
    edge_dim=edge_dim,
    cfg=fcfg,
)

backward_model, catalog_mz = train_backward_supervised(
    dataset=dataset,        # your SpectraDataset
    catalog_mz=None,        # or pass a prebuilt catalog tensor [K]
    ppm_merge=5.0,
    epochs=10,
    batch_size=32,
    device=device,
)

fragmenter_adapter = ModEngineAdapter()

# Use the last loaded DG and mol from the loop
sample_last_name, last_smi = mols_definitions[-1]
sample_last_mol = mod.Graph.fromSMILES(last_smi, name=sample_last_name)
sample_last_dg_fwd, _ = utils.load_derivation_graph(sample_last_mol.name, path=LOAD_PATH / "fwd" )
sample_last_dg_bwd, _ = utils.load_derivation_graph(sample_last_mol.name, path=LOAD_PATH / "bwd" )

# Get/clean a target spectrum for RL (e.g., PubChem)
pubchem = utils.get_spectra_from_pubchem(smiles=sample_last_mol.smiles)
target_peaks_tensor = utils_mod.clean_spectra_tensor(pubchem, device=device)

assembler_adapter = ModEngineAdapter()

policy = ActionAwarePolicy(n_bins=fcfg.data.n_bins).to(device)
opt = torch.optim.Adam(policy.parameters(), lr=fcfg.rl.lr)

env_fwd = ForwardFragEnv(
    mod_engine=fragmenter_adapter,
    featurizer=None, #dg_featurizer
    target_peaks=target_peaks_tensor,  # [N,2]
    n_bins=fcfg.data.n_bins,
    mz_min=fcfg.data.mz_min,
    mz_max=fcfg.data.mz_max,
    ppm_tol=fcfg.data.ppm_tol,
    max_depth=fcfg.rl.max_depth,
    device=device,
)
env_fwd.reset(dg=sample_last_dg_fwd, mol_graph=sample_last_mol)


reinforce_forward_env(
    env_fwd, fragmenter_adapter, policy, opt,
    gamma=fcfg.rl.gamma,
    episodes=1000,
    device=device
)


env_bwd = BackwardMolEnv(
    mod_engine=assembler_adapter,
    target_peaks=target_peaks_tensor,   # [N,2]
    n_bins=env_fwd.n_bins,
    mz_min=env_fwd.mz_min,
    mz_max=env_fwd.mz_max,
    max_steps=30,
    device=device
)
env_bwd.reset(dg=sample_last_dg_bwd, mol_graph=sample_last_mol)

reinforce_backward_env(
    env_bwd, assembler_adapter, policy, opt,
    gamma=fcfg.rl.gamma,
    episodes=1000,
    device=device
)
