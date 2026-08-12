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
import sys
from typing import List, Optional, Dict, Tuple


from pathlib import Path


import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, ConcatDataset


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
from src.machine_learning.models import DecSpecFragment, EncMol, EncSpec, TaskHeads
from src.machine_learning.data import RealDataset, collate_vlex, build_hardneg_loader, train_test_split
from src.machine_learning.retrieval import LatentIndex, FaissLatentIndex, infer_mol_to_spec, infer_spec_to_mol
from src.machine_learning.evaluation import demo_compare_spectrum, demo_retrieval_metrics, mass_controlled_retrieval_metrics, demo_noise_robustness, demo_visualize_reconstructions
from src.machine_learning.fragments import FragSetEncoderWrapper
from src.machine_learning.training import train_epoch_phase_a, train_epoch_phase_b
from src.machine_learning.checkpoint import load_checkpoint, save_checkpoint


# Hyperparameters that may be supplied via a sweep YAML (--hparams). Epochs,
# paths, device and tracking flags are deliberately excluded: those are per-run
# training concerns, not tuned model hyperparameters.
_HPARAMS_OVERRIDABLE = {
    "batch", "latent", "lr", "weight_decay", "dropout", "norm",
    "alpha_wass", "alpha_cos", "cycle_fwd", "cycle_bwd", "cycle_bwd_spec",
    "curriculum_start", "curriculum_step", "use_faiss", "seed",
}


def _apply_hparams_yaml(args, path):
    """Overlay hyperparameters from a sweep YAML onto ``args``.

    Precedence: argparse defaults < YAML < explicit CLI flags. Only known
    hyperparameter names are honored; a flag the user passed explicitly on the
    command line always wins over the YAML. Returns the dict actually applied.
    """
    import yaml
    explicit = {t[2:].split("=", 1)[0] for t in sys.argv[1:] if t.startswith("--")}
    with open(path) as fh:
        doc = yaml.safe_load(fh) or {}
    hp = doc.get("hyperparameters", doc)  # tolerate nested or flat mapping
    applied = {}
    for k, v in hp.items():
        if k in _HPARAMS_OVERRIDABLE and k not in explicit:
            setattr(args, k, v)
            applied[k] = v
    return applied


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
    p.add_argument("--alpha_spec_con", type=float, default=1.0, help="Weight for spectral contrastive loss (Phase A): spec_hat_i vs true_j over mass-bucketed negatives")
    p.add_argument("--contrastive_temp", type=float, default=0.07, help="Temperature for info_nce contrastive loss (Phase B)")
    p.add_argument("--skip_reranking", action="store_true", help="Skip forward-model reranking during retrieval evaluation (faster, tests embedding quality)")
    # paths and data options
    p.add_argument("--mol_def_path", type=str, default=shared_path("DATA_DIR_REL", "compounds.csv"), help="Path to CSV file with molecule definitions (name, SMILES)")
    p.add_argument("--spectra_dir", type=str, default=shared_path("PARQUET_DIR_REL"), help="Directory containing the NIST spectra Parquet store (spectra.parquet/index.parquet)")
    p.add_argument("--load_path", type=str, default=shared_path("PROCESSED_DIR_REL"), help="Directory containing derivation trees")
    p.add_argument("--output_dir", type=str, default=shared_path("CHECKPOINT_DIR_REL"), help="Directory to save checkpoints and outputs")
    p.add_argument("--wandb", action="store_true", help="Log this run to Weights & Biases (respects WANDB_* env vars, e.g. WANDB_MODE=offline)")
    p.add_argument("--hparams", type=str, default=None,
                   help="YAML of tuned hyperparameters (from the Optuna sweep) to load as defaults. "
                        "Explicit CLI flags override it; epochs/paths/device are never taken from it.")
    p.add_argument("--eval_only", action="store_true",
                   help="Skip both training phases and evaluate a saved checkpoint instead. "
                        "Model-shape hyperparameters are taken from the checkpoint.")
    p.add_argument("--resume", type=str, default=None,
                   help="Checkpoint to evaluate with --eval_only (default: <output_dir>/ml_checkpoint.pt).")
    args = p.parse_args()
    # --output_dir arrives as a str when passed on the CLI (e.g. from the HPC
    # launcher); normalize to Path so downstream "/" joins work.
    args.output_dir = Path(args.output_dir)

    # Overlay tuned hyperparameters from a sweep YAML, if given. Done before
    # wandb.init and seeding so the resolved config is what gets logged and used.
    if args.hparams:
        applied = _apply_hparams_yaml(args, args.hparams)
        print(f"Loaded {len(applied)} hyperparameters from {args.hparams}: {applied}")

    # Evaluate a saved run instead of training one. The modules must be built with
    # the geometry they were trained with, so the shape-defining hyperparameters
    # come from the checkpoint's own saved args rather than from the CLI defaults.
    # Zeroing the epoch counts turns both training loops into no-ops.
    resume_path: Optional[Path] = None
    if args.eval_only:
        resume_path = Path(args.resume) if args.resume else args.output_dir / "ml_checkpoint.pt"
        saved_args = torch.load(resume_path, map_location="cpu", weights_only=False).get("args", {})
        for key in ("latent", "dropout", "norm"):
            if key in saved_args and getattr(args, key) != saved_args[key]:
                print(f"--eval_only: {key}={saved_args[key]} from checkpoint (CLI had {getattr(args, key)})")
                setattr(args, key, saved_args[key])
        args.epochs_fwd = 0
        args.epochs_bwd = 0

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

    # Derivation dumps are named by CAS registry number -- the store's primary
    # key and the single identifier data-gen writes (`--name-by-cas`). Dumps
    # written before that rename still carry the human name from compounds.csv,
    # so try CAS first and fall back, the same order as the analysis tools use
    # (see feasibility/run_ceiling.py::_dump_stems).
    fwd_dir = Path(args.load_path) / "fwd"
    bwd_dir = Path(args.load_path) / "bwd"

    def _dump_stem(name: str, smiles: str) -> Optional[str]:
        cas = utils.get_cas_by_smiles(smiles, Path(args.spectra_dir))
        for stem in (cas, name):
            if stem and (fwd_dir / f"{stem}.dmp").exists():
                return str(stem)
        return None

    n_by_cas = 0
    for name, smi in mols_definitions:
        stem = _dump_stem(name, smi)
        if stem is not None:
            n_by_cas += (stem != name)
            mol = mod.Graph.fromSMILES(smi, name=name)


            fwd_dg = utils.load_derivation_graph(stem, path=fwd_dir)

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



            # The backward dump is optional: the backward pass is opt-in in data-gen
            # (--run-backward) and its collection is unused by the model. Load it only
            # if present; otherwise use an empty backward collection so the molecule is
            # NOT dropped for lacking a bwd dump.
            bwd_coll = []
            bwd_dmp = bwd_dir / f"{stem}.dmp"
            if bwd_dmp.exists():
                bwd_dg = utils.load_derivation_graph(stem, path=bwd_dir)
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
            real_spectra_by_smiles[smi] = utils.get_spectra_by_smiles(smi, Path(args.spectra_dir))
            mol_order.append(smi)

    # Align fragments and spectra by SMILES to avoid length mismatches from skipped files or overwrites
    aligned_smiles = [s for s in mol_order if s in frag_coll and s in real_spectra_by_smiles]
    dropped_frag = set(frag_coll.keys()) - set(aligned_smiles)
    dropped_spec = set(real_spectra_by_smiles.keys()) - set(aligned_smiles)
    if dropped_frag or dropped_spec:
        print(f"Warning: dropping {len(dropped_frag)} frag-only and {len(dropped_spec)} spec-only entries to align datasets")
    frag_coll = {s: frag_coll[s] for s in aligned_smiles}
    real_spectra_per_mol: List[List[Tuple[float, float]]] = [real_spectra_by_smiles[s] for s in aligned_smiles]
    print(f"Loaded {len(aligned_smiles)} molecules with paired fragments and spectra (from {len(mols_definitions)} definitions; {n_by_cas} dumps resolved by CAS)")

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


    val_loader   = DataLoader(vali_ds, batch_size=args.batch, shuffle=False, collate_fn=collate_vlex)
    test_loader  = DataLoader(test_ds, batch_size=args.batch, shuffle=False, collate_fn=collate_vlex)

    # Models
    enc_mol  = EncMol(args.latent).to(device)
    frag_set_enc = FragSetEncoderWrapper(enc_mol, d_latent=args.latent).to(device)
    enc_spec = EncSpec(spectrum_bins_size, args.latent, dropout=args.dropout, norm=args.norm).to(device)
    dec_spec = DecSpecFragment(
        d_node=args.latent, d_cond=args.latent, spectrum_bins_size=spectrum_bins_size,
        mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width,
        dropout=args.dropout,
    ).to(device)
    # Task heads (shared trunk projections)
    heads = TaskHeads(d_latent=args.latent, d_task=args.latent).to(device)
    # expose for helper functions (script-level convenience)
    globals()['heads'] = heads

    # --eval_only: restore the trained weights in place. enc_mol rides along inside
    # frag_set_enc (see checkpoint.py), and the modules stay in their default train()
    # mode, which is the mode they were in at the end of a training run -- so the
    # evaluation below sees the same configuration it would after training.
    if args.eval_only:
        load_checkpoint(
            resume_path,
            frag_set_enc=frag_set_enc,
            enc_spec=enc_spec,
            dec_spec=dec_spec,
            heads=heads,
            map_location=device,
        )
        print(f"Loaded checkpoint {resume_path} -- skipping both training phases")

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
        cur_loader = build_hardneg_loader(train_ds, batch_size=args.batch, fraction=frac, collate_fn=collate_vlex)
        loss = train_epoch_phase_a(
            cur_loader, device, enc_mol, enc_spec, frag_set_enc, heads, dec_spec, opt_a,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1,
            alpha_cosine=args.alpha_cos, alpha_wass=args.alpha_wass, lam_cycle=args.cycle_fwd,
            alpha_diversity=args.alpha_diversity, alpha_spec_con=args.alpha_spec_con,
            contrastive_temp=args.contrastive_temp
        )
        print(f"[A] epoch {epoch:02d} loss {loss:.4f} | frac {frac:.2f}")
        if use_wandb:
            wandb.log({"phaseA/loss": loss, "phaseA/frac": frac, "epoch": epoch})

    # ----------------- Phase B -----------------
    print("== Phase B: align spec latent + spectrum recon (vocab-agnostic) ==")
    for epoch in range(1, args.epochs_bwd + 1):
        frac = min(1.0, args.curriculum_start + (epoch - 1) * args.curriculum_step)
        cur_loader = build_hardneg_loader(train_ds, batch_size=args.batch, fraction=frac, collate_fn=collate_vlex)
        loss = train_epoch_phase_b(
            cur_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, opt_b,
            mz_min=train_ds.mz_min, mz_max=train_ds.mz_max, bin_width=train_ds.bin_width, beta_forbidden=0.1,
            alpha_cosine=args.alpha_cos, alpha_wass=args.alpha_wass, lam_cycle=args.cycle_bwd, lam_cycle_spec=args.cycle_bwd_spec,
            contrastive_temp=args.contrastive_temp, alpha_retrieval=args.alpha_retrieval
        )
        print(f"[B] epoch {epoch:02d} loss {loss:.4f} | frac {frac:.2f}")
        if use_wandb:
            # offset epoch so Phase B continues the same x-axis after Phase A
            wandb.log({"phaseB/loss": loss, "phaseB/frac": frac, "epoch": args.epochs_fwd + epoch})

    # Persist the trained model immediately, before any (fragile) eval/demo step.
    # The mass-controlled TEST scorecard builds a TRAIN+VAL+TEST index and has
    # crashed there before; saving here means such a crash costs the scorecard,
    # not the whole training run.
    if not args.eval_only:
        ckpt_path = args.output_dir / "ml_checkpoint.pt"
        save_checkpoint(
            ckpt_path,
            frag_set_enc=frag_set_enc,
            enc_spec=enc_spec,
            dec_spec=dec_spec,
            heads=heads,
            args=vars(args),
        )
        print(f"Saved checkpoint to {ckpt_path}")

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
        graph_feats, _frag_graphs, _frag_masses, spec, smiles, _adj_local, deriv_trees_fwd, _ = batch_data
    else:
        graph_feats, _frag_graphs, _frag_masses, spec, smiles, _adj_local = batch_data
        deriv_trees_fwd = [None] * len(smiles)

    i = 0
    spec_hat = infer_mol_to_spec(
        graph_feats[i],
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
        graph_feats[i], spec[i],
        enc_mol, frag_set_enc, dec_spec, heads,
        mz_min=test_ds.mz_min, bin_width=test_ds.bin_width, smiles=smiles[i], mz_max=test_ds.mz_max, top_k=10,
        frag_deriv_tree=deriv_trees_fwd[i]
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

    # ----------------- Mass-controlled retrieval scorecard (headline) -----------------
    # Learned retrieval only counts if it beats the mass-only baseline; see the
    # forward-collapse audit for why mass must be the bar, not an unmeasured confound.
    mass_by_smiles = {}
    for ds in (train_ds, vali_ds):
        for smi, m in zip(list(ds.frag_coll.keys()), ds.parent_masses):
            mass_by_smiles[smi] = m
    print("== Mass-controlled retrieval (VAL) ==")
    val_massctl = mass_controlled_retrieval_metrics(
        index, val_loader, device, enc_spec, enc_mol, heads, mass_by_smiles,
        mz_min=vali_ds.mz_min, mz_max=vali_ds.mz_max, bin_width=vali_ds.bin_width,
        topk_list=(1, 5, 10, 20), windows=(5.0, 20.0),
    )
    # Held-out TEST scorecard. Trial selection used VAL, so VAL's delta is
    # optimistic; TEST was never seen by the sweep -> an unbiased "beyond mass"
    # check. Retrieval needs the true molecule in the gallery, so build a
    # TRAIN+VAL+TEST library (closed-library retrieval, the structure-elucidation
    # setting). The VAL scorecard above keeps its TRAIN+VAL gallery unchanged so
    # the sweep objective it feeds stays comparable across runs.
    print("== Mass-controlled retrieval (TEST, held out) ==")
    if args.use_faiss and _FAISS_AVAILABLE:
        index_test = FaissLatentIndex(d=args.latent)
    else:
        index_test = LatentIndex(d=args.latent)
    index_test.build(ConcatDataset([train_ds, vali_ds, test_ds]), device, enc_mol)
    mass_by_smiles_test = dict(mass_by_smiles)
    for smi, m in zip(list(test_ds.frag_coll.keys()), test_ds.parent_masses):
        mass_by_smiles_test[smi] = m
    test_massctl = mass_controlled_retrieval_metrics(
        index_test, test_loader, device, enc_spec, enc_mol, heads, mass_by_smiles_test,
        mz_min=test_ds.mz_min, mz_max=test_ds.mz_max, bin_width=test_ds.bin_width,
        topk_list=(1, 5, 10, 20), windows=(5.0, 20.0),
    )
    print(
        "TEST_MASSCTL "
        f"massctl_mrr_w5={test_massctl.get('window5.0/learned_MRR', 0.0):.6f} "
        f"massctl_delta_w5={test_massctl.get('window5.0/delta_MRR', 0.0):.6f}"
    )
    # Single source of truth for the sweep objective + tracked secondaries, used
    # for both the parseable line below and the wandb "objective/*" namespace so
    # the two can never drift. Mass-controlled learned MRR is the headline: raw
    # MRR collapses to parent-mass filtering (forward-collapse audit), so the
    # sweep maximizes retrieval *within* a +/-5 Da window; the rest are tracked.
    objective_metrics = {
        "massctl_mrr_w5": val_massctl.get("window5.0/learned_MRR", 0.0),
        "massctl_delta_w5": val_massctl.get("window5.0/delta_MRR", 0.0),
        "mrr": val_metrics.get("MRR", 0.0),
        "r1": val_metrics.get("R@1", 0.0),
    }
    # Machine-parseable objective line parsed by
    # optimization/hyperparameter_optimization.py.
    print("OPTUNA_OBJECTIVE " + " ".join(f"{k}={v:.6f}" for k, v in objective_metrics.items()))
    if use_wandb:
        # flatten nested metric dicts into "val/..."/"test/..." scalars for the wandb UI
        wandb.log({f"val/{k}": v for k, v in val_metrics.items()})
        wandb.log({f"test/{k}": v for k, v in test_metrics.items()})
        wandb.log({f"val_massctl/{k}": v for k, v in val_massctl.items()})
        wandb.log({f"test_massctl/{k}": v for k, v in test_massctl.items()})
        # Explicit objective namespace: "objective/massctl_mrr_w5" is exactly what
        # Optuna maximizes, so the wandb sweep view and the study agree at a glance.
        wandb.log({f"objective/{k}": v for k, v in objective_metrics.items()})

    # Plots go beside the checkpoints, under data/outputs/plots.
    plots_dir = args.output_dir.parent / "plots"

    # ----------------- Demo: Spectrum noise robustness -----------------
    print("== Spectrum noise robustness (VAL subset) ==")
    noise_res = demo_noise_robustness(index, val_loader, device, enc_spec, enc_mol, frag_set_enc, heads, dec_spec, noise_levels=(0.0, 0.05, 0.1, 0.2), topk_list=(1,5,10), max_batches=5, out_dir=plots_dir)
    print(noise_res)

    # ----------------- Demo: Visualization of reconstructions -----------------
    print("== Visualization: saving recon plots for a few VAL samples ==")
    _ = demo_visualize_reconstructions(graph_feats, spec, smiles, enc_mol, frag_set_enc, dec_spec, heads, n_samples=3, deriv_trees=deriv_trees_fwd, out_dir=plots_dir)

    # Checkpoint was already saved right after training (above), so a crash in the
    # eval/demo section cannot lose the trained weights. Upload it as a wandb
    # artifact here, once the run is otherwise complete.
    if use_wandb:
        artifact = wandb.Artifact("ml_checkpoint", type="model")
        artifact.add_file(str(ckpt_path))
        wandb.log_artifact(artifact)
        wandb.finish()

if __name__ == "__main__":
    main()
