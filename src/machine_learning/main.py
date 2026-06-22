"""
Fragment-Aided Bidirectional Model
======================================================

The model learns two related mappings:
    * Molecule -> Spectrum  (forward prediction)
    * Spectrum -> Molecule  (inverse retrieval)


This will:
    1. Train the forward model (Phase A): molecule + fragment set -> spectrum.
    2. Train spectrum embeddings aligned with molecule embeddings (Phase B).
    3. Build a retrieval index.
    4. Demonstrate molecule->spectrum prediction and spectrum->molecule retrieval.
    5. Run evaluation demos.
    6. Save checkpoint to out/mini_frag_checkpoint.pt.

Outputs:
    * Console logs with per-epoch losses.
    * Retrieval demo showing top-K candidate SMILES.
    * Saved model checkpoint for later reuse or fine-tuning.
"""

import argparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Union, Any


from collections import Counter
from pathlib import Path
import numpy as np


import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, Subset, ConcatDataset
import matplotlib.pyplot as plt


from torch_geometric.nn import global_mean_pool
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data as GeometricData
from torch_geometric.data import Batch

# Optional FAISS for ANN retrieval
try:
    import faiss  # type: ignore
    _FAISS_AVAILABLE = True
except Exception:
    faiss = None
    _FAISS_AVAILABLE = False

# Optional Weights & Biases experiment tracking
try:
    import wandb  # type: ignore
    _WANDB_AVAILABLE = True
except Exception:
    wandb = None
    _WANDB_AVAILABLE = False

import mod
from src.machine_learning import utils_mod
from src.data_generation import utils
from src.project_paths import shared_path
from src.machine_learning.featurizers import GraphFeaturizerMOD
from src.machine_learning.models import DecSpecLatent, EncMol, EncSpec, TaskHeads
from src.machine_learning.data import Sample, RealDataset, collate, collate_vlex, build_curriculum_loader, train_test_split
from src.machine_learning.spectrum import make_parent_mass_mask_vec, make_parent_mass_mask_batch
from src.machine_learning.retrieval import IndexItem, LatentIndex, FaissLatentIndex, rerank_candidates, infer_mol_to_spec, infer_spec_to_mol
from src.machine_learning.evaluation import vec_to_peaks, demo_compare_spectrum, demo_retrieval_metrics, demo_ablate_adjacency, demo_noise_robustness, demo_visualize_reconstructions
from src.machine_learning.losses import cosine_loss, wasserstein_1d, info_nce, jaccard_binary
from src.machine_learning.fragments import FragSetEncoderVocabless, EncFragGraph, FragSetEncoderWrapper
from src.machine_learning.training import train_epoch_phase_a, train_epoch_phase_b
from src.machine_learning.demos import demo_heads_comparison, demo_fragment_perturbation


def main():
    """
    Entry point for training and demonstrating the Mini-FRAG model.

    Steps
    -----
    1. Build dataset.
    2. Train forward & fragment models (Phase A).
    3. Train spectrum alignment (Phase B).
    4. Build latent retrieval index.
    5. Demonstrate molecule -> spectrum and spectrum -> molecule examples.
    6. Save model checkpoint.
    """
    p = argparse.ArgumentParser()
    p.add_argument("--epochs_fwd", type=int, default=1000, help="Phase A epochs (mol+frag -> spec)")
    p.add_argument("--epochs_bwd", type=int, default=1000, help="Phase B epochs (align spec latent)")
    p.add_argument("--batch", type=int, default=128)
    p.add_argument("--latent", type=int, default=128)
    p.add_argument("--lr", type=float, default=2e-4, help="Learning rate for the optimizer")
    p.add_argument("--weight_decay", type=float, default=1e-4, help="Weight decay for optimizers")
    p.add_argument("--dropout", type=float, default=0.1, help="Dropout rate for MLP blocks")
    p.add_argument("--norm", type=str, default="layer", choices=["layer", "batch", "none"], help="Normalization layer type")
    p.add_argument("--alpha_wass", type=float, default=0.5, help="Weight for Wasserstein spectrum loss")
    p.add_argument("--alpha_cos", type=float, default=1.0, help="Weight for cosine spectrum loss")
    p.add_argument("--cycle_fwd", type=float, default=0.1, help="Cycle-consistency weight (mol->spec->latent alignment)")
    p.add_argument("--cycle_bwd", type=float, default=0.1, help="Cycle-consistency weight (spec->spec_hat->spec_latent alignment)")
    p.add_argument("--cycle_bwd_spec", type=float, default=0.1, help="Cycle-consistency weight (spec->mol latent alignment)")
    p.add_argument("--curriculum_start", type=float, default=0.3, help="Starting fraction of easy molecules")
    p.add_argument("--curriculum_step", type=float, default=0.05, help="Per-epoch fraction increment")
    p.add_argument("--use_faiss", action="store_true", help="Use FAISS index for retrieval if available")
    p.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--seed", type=int, default=0)
    # Retrieval and diversity parameters (now actively used in training)
    p.add_argument("--alpha_retrieval", type=float, default=1.0, help="Weight for within-batch retrieval ranking loss (Phase B)")
    p.add_argument("--alpha_diversity", type=float, default=0.1, help="Weight for spectrum diversity loss (Phase A)")
    p.add_argument("--contrastive_temp", type=float, default=0.07, help="Temperature for info_nce contrastive loss (Phase B)")
    p.add_argument("--skip_reranking", action="store_true", help="Skip forward-model reranking during retrieval evaluation (faster, tests embedding quality)")
    # paths and data options
    p.add_argument("--mol_def_path", type=str, default=shared_path("DATA_DIR_REL", "compounds.csv"), help="Path to CSV file with molecule definitions (name, SMILES)")
    p.add_argument("--spectra_dir", type=str, default=shared_path("NIST_SPECTRA_DIR_REL"), help="Directory containing .jdx spectrum files named by molecule name")
    p.add_argument("--load_path", type=str, default=shared_path("PROCESSED_DIR_REL"), help="Directory containing derivation trees")
    p.add_argument("--output_dir", type=str, default=shared_path("CHECKPOINT_DIR_REL"), help="Directory to save checkpoints and outputs")
    p.add_argument("--wandb", action="store_true", help="Log this run to Weights & Biases (respects WANDB_* env vars, e.g. WANDB_MODE=offline)")
    args = p.parse_args()

    # Experiment tracking. Project/group/mode/run-dir all come from WANDB_* env vars
    # set by the SLURM launch script; on HPC compute nodes use WANDB_MODE=offline and
    # `wandb sync` from a login node afterward.
    use_wandb = args.wandb and _WANDB_AVAILABLE
    if args.wandb and not _WANDB_AVAILABLE:
        print("Warning: --wandb passed but the wandb package is not installed; skipping tracking.")
    if use_wandb:
        wandb.init(config=vars(args))

    torch.manual_seed(args.seed)
    device = torch.device(args.device)
    print(f"Using device={device}")

    mols_definitions = utils_mod.read_mols_csv(Path(args.mol_def_path))
    frag_coll: Dict[
        str,
        Tuple[
            List[  # forward
                Tuple[
                    str, # frag_smiles
                    float, # exact mass
                    Dict[int, List[str]], # targets
                    Dict[int, List[str]]  # rules
                    ]
                ],
            List[   # backward
                Tuple[
                    str, # frag_smiles
                    float, # exact mass
                    Dict[int, List[str]], # targets
                    Dict[int, List[str]]  # rules
                    ]
                ]
        ]
    ] = {}
    real_spectra_by_smiles: Dict[str, List[Tuple[float, float]]] = {}
    mol_order: List[str] = []

    for name, smi in mols_definitions:
        if (Path(args.load_path) / "fwd" / f"{name}.dmp").exists() \
        and (Path(args.load_path) / "bwd" / f"{name}.dmp").exists():
            mol = mod.Graph.fromSMILES(smi, name=name)


            fwd_dg = utils.load_derivation_graph(name, path=Path(args.load_path) / "fwd")
            bwd_dg = utils.load_derivation_graph(name, path=Path(args.load_path) / "bwd")

            fwd_coll = []
            for graph_term in fwd_dg.graphDatabase: # when loading DG len(createdGraphs)=0
                graph = utils.graph_from_term(graph_term)
                if graph.isMolecule:
                    dg_v = fwd_dg.findVertex(graph_term)
                    targets = dict()
                    rules = dict()
                    for edge in dg_v.outEdges:
                        targets[edge.id] = [utils.graph_from_term(t.graph).smiles for t in edge.targets]
                        rules[edge.id] = [rule for rule in edge.rules]
                    fwd_coll.append((graph.smiles, graph.exactMass, targets, rules))



            bwd_coll = []
            for graph_term in bwd_dg.graphDatabase: # when loading DG len(createdGraphs)=0
                graph = utils.graph_from_term(graph_term)
                if graph.isMolecule:
                    dg_v = bwd_dg.findVertex(graph_term)
                    try:
                        targets = dict()
                        rules = dict()
                        for edge in dg_v.outEdges:
                            targets[edge.id] = [utils.graph_from_term(t.graph).smiles for t in edge.targets]
                            rules[edge.id] = [rule for rule in edge.rules]
                        bwd_coll.append((graph.smiles, graph.exactMass, targets, rules))
                    except mod.libpymod.LogicError:
                        #bwd_coll.append((graph.smiles, dict(), dict()))
                        print("empty edges for ", graph.smiles)

            frag_coll[smi] = (fwd_coll, bwd_coll)
            real_spectra_by_smiles[smi] = utils.get_spectra_from_local_jdx(name, folder=Path(args.spectra_dir))
            mol_order.append(smi)

    # Align fragments and spectra by SMILES to avoid length mismatches from skipped files or overwrites
    aligned_smiles = [s for s in mol_order if s in frag_coll and s in real_spectra_by_smiles]
    dropped_frag = set(frag_coll.keys()) - set(aligned_smiles)
    dropped_spec = set(real_spectra_by_smiles.keys()) - set(aligned_smiles)
    if dropped_frag or dropped_spec:
        print(f"Warning: dropping {len(dropped_frag)} frag-only and {len(dropped_spec)} spec-only entries to align datasets")
    frag_coll = {s: frag_coll[s] for s in aligned_smiles}
    real_spectra_per_mol: List[List[Tuple[float, float]]] = [real_spectra_by_smiles[s] for s in aligned_smiles]
    print(f"Loaded {len(aligned_smiles)} molecules with paired fragments and spectra (from {len(mols_definitions)} definitions)")

    train_spect, test_spect = train_test_split(
        data= real_spectra_per_mol,
        test_size=0.2,
        random_state=42,
        shuffle=False
        )
    train_frags, test_frags = train_test_split(
        data = frag_coll,
        test_size=0.2,
        random_state=42,
        shuffle=False
    )

    train_spect, vali_spect = train_test_split(
        train_spect,
        test_size=.3,
        random_state=42,
        shuffle=False
    )
    train_frags, vali_frags = train_test_split(
        train_frags,
        test_size=0.3,
        random_state=42,
        shuffle=False
    )

    # Build dataset
    train_ds = RealDataset(
        train_frags, train_spect,
        precompute=True,
        graph_backend="derivation_tree"
        )

    vali_ds = RealDataset(
        vali_frags, vali_spect,
        frag_to_id=train_ds.frag_to_id,  # ensure consistent fragment vocab across splits
        precompute=True,
        graph_backend="derivation_tree"
        )

    test_ds = RealDataset(
        test_frags, test_spect,
        frag_to_id=train_ds.frag_to_id,
        precompute=True,
        graph_backend="derivation_tree"
        )

    # Use dataset to configure the model:
    spectrum_bins_size = train_ds.spectrum_bins_size


    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=False, drop_last=False, collate_fn=collate_vlex)
    val_loader   = DataLoader(vali_ds, batch_size=args.batch, shuffle=False, collate_fn=collate_vlex)
    test_loader  = DataLoader(test_ds, batch_size=args.batch, shuffle=False, collate_fn=collate_vlex)

    # Models
    enc_mol  = EncMol(args.latent).to(device)
    frag_set_enc = FragSetEncoderWrapper(enc_mol, d_latent=args.latent).to(device)
    enc_spec = EncSpec(spectrum_bins_size, args.latent, dropout=args.dropout, norm=args.norm).to(device)
    dec_spec = DecSpecLatent(d_in=args.latent, spectrum_bins_size=spectrum_bins_size, dropout=args.dropout, norm=args.norm).to(device)
    # Task heads (shared trunk projections)
    heads = TaskHeads(d_latent=args.latent, d_task=args.latent).to(device)
    # expose for helper functions (script-level convenience)
    globals()['heads'] = heads

    # Optimizers (separate per phase keeps it simple)
    opt_a = torch.optim.Adam(list(frag_set_enc.parameters()) +
                             list(dec_spec.parameters()) +
                             list(heads.parameters()), lr=args.lr, weight_decay=args.weight_decay)
    opt_b = torch.optim.Adam(list(enc_mol.parameters()) +
                             list(enc_spec.parameters()) +
                             list(dec_spec.parameters()) +
                             list(heads.parameters()), lr=args.lr, weight_decay=args.weight_decay)

    # ----------------- Phase A -----------------
    print("== Phase A: train forward (vocab-agnostic) ==")
    for epoch in range(1, args.epochs_fwd + 1):
        frac = min(1.0, args.curriculum_start + (epoch - 1) * args.curriculum_step)
        cur_loader = build_curriculum_loader(train_ds, batch_size=args.batch, fraction=frac, collate_fn=collate_vlex)
        loss = train_epoch_phase_a(
            cur_loader, device, enc_mol, enc_spec, frag_set_enc, heads, dec_spec, opt_a,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1,
            alpha_cosine=args.alpha_cos, alpha_wass=args.alpha_wass, lam_cycle=args.cycle_fwd,
            alpha_diversity=args.alpha_diversity
        )
        print(f"[A] epoch {epoch:02d} loss {loss:.4f} | frac {frac:.2f}")
        if use_wandb:
            wandb.log({"phaseA/loss": loss, "phaseA/frac": frac, "epoch": epoch})

    # ----------------- Phase B -----------------
    print("== Phase B: align spec latent + spectrum recon (vocab-agnostic) ==")
    for epoch in range(1, args.epochs_bwd + 1):
        frac = min(1.0, args.curriculum_start + (epoch - 1) * args.curriculum_step)
        cur_loader = build_curriculum_loader(train_ds, batch_size=args.batch, fraction=frac, collate_fn=collate_vlex)
        loss = train_epoch_phase_b(
            cur_loader, device, enc_spec, enc_mol, heads, dec_spec, opt_b,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1,
            alpha_cosine=args.alpha_cos, alpha_wass=args.alpha_wass, lam_cycle=args.cycle_bwd, lam_cycle_spec=args.cycle_bwd_spec,
            contrastive_temp=args.contrastive_temp, alpha_retrieval=args.alpha_retrieval
        )
        print(f"[B] epoch {epoch:02d} loss {loss:.4f} | frac {frac:.2f}")
        if use_wandb:
            # offset epoch so Phase B continues the same x-axis after Phase A
            wandb.log({"phaseB/loss": loss, "phaseB/frac": frac, "epoch": args.epochs_fwd + epoch})

    # ----------------- Build retrieval index -----------------
    # CRITICAL: Build index on TRAIN+VAL so evaluation sets have ground truth molecules
    print("== Building retrieval index on TRAIN+VAL sets ==")
    if args.use_faiss and _FAISS_AVAILABLE:
        index = FaissLatentIndex(d=args.latent)
    else:
        index = LatentIndex(d=args.latent)
    index_dataset = ConcatDataset([train_ds, vali_ds])
    index.build(index_dataset, device, enc_mol)


    # ----------------- Demo: Structure - > Spectrum -----------------
    batch_data = next(iter(test_loader))
    if len(batch_data) == 8:
        graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, deriv_trees_fwd, deriv_trees_bwd = batch_data
    else:
        graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local = batch_data
        deriv_trees_fwd = [None] * len(smiles)

    i = 0
    spec_hat = infer_mol_to_spec(
        graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], device,
        enc_mol, frag_set_enc, dec_spec, heads,
        smiles=smiles[i], mz_min=test_ds.mz_min, mz_max=test_ds.mz_max, bin_width=test_ds.bin_width,
        frag_deriv_tree=deriv_trees_fwd[i]
    )
    cos_sim = F.cosine_similarity(
        F.normalize(spec_hat, dim=-1).unsqueeze(0),
        F.normalize(spec[i], dim=-1).unsqueeze(0),
        dim=-1
    ).item()
    print(f"Mol->Spec for {smiles[i]} | cosine={cos_sim:.3f}")

    # ----------------- Demo: Compare to ground truth spectrum -----------------
    print("== Demo: Compare predicted vs ground truth (TEST sample) ==")
    _ = demo_compare_spectrum(
        graph_feats[i], frag_graphs[i], frag_masses[i], adj_local[i], spec[i], device,
        enc_mol, frag_set_enc, dec_spec, heads,
        mz_min=test_ds.mz_min, bin_width=test_ds.bin_width, smiles=smiles[i], mz_max=test_ds.mz_max, top_k=10
    )

    # ----------------- Demo: Spectrum - > Structure -----------------
    print("== Demo: Spec -> Mol retrieval + re-ranking on the same VAL sample ==")
    ranked = infer_spec_to_mol(spec[i], index, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec,
                               mz_min=test_ds.mz_min, mz_max=test_ds.mz_max, bin_width=test_ds.bin_width, topk=10)
    print("Top-5 candidates:")
    print(f"{'SMILES':>40s} | {'Score':>8s}")
    print("-" * 50)
    for s, sc in ranked[:5]:
        print(f"{s:>40s} | {sc:8.3f}")

    # ----------------- Demo: Retrieval metrics on VAL/TEST -----------------
    print("== Retrieval metrics (VAL) ==")
    val_metrics = demo_retrieval_metrics(index, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, topk_list=(1,5,10), max_batches=5, skip_reranking=args.skip_reranking)
    print(val_metrics)
    print("== Retrieval metrics (TEST) ==")
    test_metrics = demo_retrieval_metrics(index, test_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, topk_list=(1,5,10), max_batches=5, skip_reranking=args.skip_reranking)
    print(test_metrics)
    if use_wandb:
        # flatten nested metric dicts into "val/..."/"test/..." scalars for the wandb UI
        wandb.log({f"val/{k}": v for k, v in val_metrics.items()})
        wandb.log({f"test/{k}": v for k, v in test_metrics.items()})
    # ----------------- Demo: Fragment graph ablation -----------------
    print("== Graph ablation on one VAL sample ==")
    ablation = demo_ablate_adjacency(graph_feats[i], frag_graphs[i], adj_local[i], frag_masses[i], spec[i],
                                     smiles[i], test_ds.mz_min, test_ds.mz_max, test_ds.bin_width,
                                     device, enc_mol, frag_set_enc, dec_spec, heads)
    print(ablation)

    # ----------------- Demo: Spectrum noise robustness -----------------
    print("== Spectrum noise robustness (VAL subset) ==")
    noise_res = demo_noise_robustness(index, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5)
    print(noise_res)

    # ----------------- Demo: Visualization of reconstructions -----------------
    print("== Visualization: saving recon plots for a few VAL samples ==")
    _ = demo_visualize_reconstructions(graph_feats, frag_graphs, frag_masses, spec, smiles, adj_local, device, enc_mol, frag_set_enc, dec_spec, heads, n_samples=3)

    # save checkpoint
    ckpt = {
        "enc_mol": enc_mol.state_dict(),
        "frag_set_enc": frag_set_enc.state_dict(),
        "enc_spec": enc_spec.state_dict(),
        "dec_spec": dec_spec.state_dict(),
        "heads": heads.state_dict(),
        "args": vars(args),
    }
    torch.save(ckpt, args.output_dir / "ml_checkpoint.pt")
    print(f"Saved checkpoint to {args.output_dir / 'ml_checkpoint.pt'}")

    if use_wandb:
        artifact = wandb.Artifact("ml_checkpoint", type="model")
        artifact.add_file(str(args.output_dir / "ml_checkpoint.pt"))
        wandb.log_artifact(artifact)
        wandb.finish()

if __name__ == "__main__":
    main()
