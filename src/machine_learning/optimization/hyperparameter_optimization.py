"""
Hyperparameter Optimization for ML Minimal Implementation
==========================================================

This script performs automated hyperparameter optimization using Optuna.

The optimization *maximizes* the mass-controlled learned MRR within a +/-5 Da
mass window (raw retrieval metrics reduce to parent-mass filtering per the
forward-collapse audit, so mass-controlled MRR is the only target that rewards
learned chemistry). Raw MRR and R@1 are tracked as secondaries, not optimized.

Each trial runs main.py in a subprocess and reads its single ``OPTUNA_OBJECTIVE``
line. A trial that times out or crashes before emitting that line is pruned, so
the sampler never models an unfinished run as a real (poor) result.

Usage
-----
    $ python hyperparameter_optimization.py --n_trials 20 --epochs_fwd 500 --epochs_bwd 500

Best parameters will be saved to `best_hyperparams.json`.
"""

import argparse
import json
import os
import sys
import torch
import numpy as np
import yaml
from pathlib import Path
from typing import Dict, Tuple, List, Any
from datetime import datetime
import subprocess

from src.project_paths import shared_path

# Optuna search-space keys -> main.py argument names, so the emitted YAML is
# directly consumable by `main.py --hparams` with no renaming step.
_ARG_NAME_MAP = {
    "batch_size": "batch",
    "latent_dim": "latent",
    "learning_rate": "lr",
}


def _hparams_for_main(best_config: Dict[str, Any]) -> Dict[str, Any]:
    """Rename Optuna param keys to main.py argument names for the YAML."""
    return {_ARG_NAME_MAP.get(k, k): v for k, v in best_config.items()}

try:
    import optuna
    from optuna.pruners import MedianPruner
    from optuna.samplers import TPESampler
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("Warning: Optuna not installed. Install with: pip install optuna")


def train_with_config(train: Path, config: Dict[str, Any], epochs_fwd: int, epochs_bwd: int, device: str = "cuda", use_wandb: bool = False, timeout: int = 3600) -> Dict[str, float]:
    """
    Train the model with a specific hyperparameter configuration.

    Returns the metrics dict parsed from main.py's ``OPTUNA_OBJECTIVE`` line
    (mass-controlled MRR + tracked secondaries). If the trial times out or fails
    before it emits that line, the trial is pruned (``optuna.TrialPruned``) so the
    sampler does not model an unfinished run as a real, poor result.
    """
    # Build command to run the main training script with the given config
    cmd = [
        "python",
        str(train),
        "--epochs_fwd", str(epochs_fwd),
        "--epochs_bwd", str(epochs_bwd),
        "--batch", str(config["batch_size"]),
        "--latent", str(config["latent_dim"]),
        "--lr", str(config["learning_rate"]),
        "--weight_decay", str(config["weight_decay"]),
        "--dropout", str(config["dropout"]),
        "--norm", str(config["norm"]),
        "--alpha_wass", str(config["alpha_wass"]),
        "--alpha_cos", str(config["alpha_cos"]),
        "--cycle_fwd", str(config["cycle_fwd"]),
        "--cycle_bwd", str(config["cycle_bwd"]),
        "--cycle_bwd_spec", str(config["cycle_bwd_spec"]),
        "--curriculum_start", str(config["curriculum_start"]),
        "--curriculum_step", str(config["curriculum_step"]),
        "--device", device,
        "--seed", str(config.get("seed", 0))
    ]

    if config.get("use_faiss", False):
        cmd.append("--use_faiss")

    # Each trial trains in its own subprocess, so each becomes its own wandb run.
    # WANDB_RUN_GROUP (set by the launch script) ties them into one sweep view.
    if use_wandb:
        cmd.append("--wandb")

    print(f"\n{'='*80}")
    print(f"Training with config: {config}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*80}\n")

    try:
        # Run training and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"Training timed out after {timeout}s -> pruning trial")
        raise optuna.TrialPruned()
    except Exception as e:
        print(f"Error launching training: {e} -> pruning trial")
        raise optuna.TrialPruned()

    output = (result.stdout or "") + (result.stderr or "")
    metrics = _extract_metrics_from_output(output)

    # If the subprocess failed, emit a short diagnostic to help debugging
    if result.returncode != 0:
        print(f"Training process exited with code {result.returncode}")
        tail = "\n".join(output.strip().splitlines()[-25:])
        if tail:
            print("---- Begin training output tail ----")
            print(tail)
            print("---- End training output tail ----")

    if metrics is None:
        print("Warning: no OPTUNA_OBJECTIVE line in output (training did not reach "
              "evaluation) -> pruning trial")
        raise optuna.TrialPruned()

    return metrics


def _extract_metrics_from_output(output: str) -> Dict[str, float]:
    """Parse the single ``OPTUNA_OBJECTIVE`` line emitted by main.py.

    Expected form::

        OPTUNA_OBJECTIVE massctl_mrr_w5=0.1234 massctl_delta_w5=0.0100 mrr=0.2000 r1=0.1000

    Returns a dict of the ``key=float`` tokens, or ``None`` if the line is absent
    (which the caller treats as an unusable trial).
    """
    import re

    m = re.search(r'OPTUNA_OBJECTIVE\s+(.*)', output)
    if not m:
        return None

    metrics = {}
    for tok in m.group(1).split():
        key, sep, val = tok.partition("=")
        if not sep:
            continue
        try:
            metrics[key] = float(val)
        except ValueError:
            continue

    return metrics or None


def objective(
        runpath: Path,
        trial: "optuna.Trial",
        epochs_fwd: int,
        epochs_bwd: int,
        device: str,
        use_wandb: bool = False,
        timeout: int = 3600
        ) -> float:
    """
    Optuna objective: defines the search space and returns the value to
    *maximize* -- the mass-controlled learned MRR within +/-5 Da. Raw retrieval
    metrics reduce to parent-mass filtering (forward-collapse audit), so the
    mass-controlled score is the only target that rewards learned chemistry.
    """
    # Define hyperparameter search space
    config = {
        "batch_size": trial.suggest_categorical("batch_size", [32, 64, 128, 256]),
        "latent_dim": trial.suggest_categorical("latent_dim", [64, 128, 256, 512]),
        "learning_rate": trial.suggest_float("learning_rate", 1e-5, 1e-2, log=True),
        "weight_decay": trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True),
        "dropout": trial.suggest_float("dropout", 0.0, 0.5),
        "norm": trial.suggest_categorical("norm", ["layer", "batch", "none"]),
        "alpha_wass": trial.suggest_float("alpha_wass", 0.1, 2.0),
        "alpha_cos": trial.suggest_float("alpha_cos", 0.1, 2.0),
        "cycle_fwd": trial.suggest_float("cycle_fwd", 0.01, 1.0),
        "cycle_bwd": trial.suggest_float("cycle_bwd", 0.01, 1.0),
        "cycle_bwd_spec": trial.suggest_float("cycle_bwd_spec", 0.01, 1.0),
        "curriculum_start": trial.suggest_float("curriculum_start", 0.1, 0.9),
        "curriculum_step": trial.suggest_float("curriculum_step", 0.01, 0.2),
        "use_faiss": trial.suggest_categorical("use_faiss", [True, False]),
        "seed": 0
    }

    # Name this trial's wandb run so it is identifiable within the sweep group.
    # The subprocess inherits os.environ, so setting it here propagates to main.py.
    if use_wandb:
        os.environ["WANDB_NAME"] = f"trial-{trial.number}"

    # Train with this config (raises optuna.TrialPruned on timeout/failure)
    metrics = train_with_config(runpath, config, epochs_fwd, epochs_bwd, device, use_wandb=use_wandb, timeout=timeout)

    # Primary metric to maximize: mass-controlled learned MRR within +/-5 Da
    objective_value = metrics.get("massctl_mrr_w5", 0.0)

    # Report secondary metrics (for tracking, not optimization)
    trial.set_user_attr("massctl_delta_w5", metrics.get("massctl_delta_w5", 0.0))
    trial.set_user_attr("mrr", metrics.get("mrr", 0.0))
    trial.set_user_attr("r1", metrics.get("r1", 0.0))
    trial.set_user_attr("config", config)

    return objective_value


def run_optimization(
        runpath: Path,
        n_trials: int,
        epochs_fwd: int,
        epochs_bwd: int,
        device: str = "cuda",
        use_wandb: bool = False,
        timeout: int = 3600
        ) -> Dict[str, Any]:
    """Run hyperparameter optimization."""

    print(f"\nStarting hyperparameter optimization with {n_trials} trials...")
    print(f"Epochs (forward): {epochs_fwd}, Epochs (backward): {epochs_bwd}")
    print(f"Per-trial timeout: {timeout}s")
    print(f"Device: {device}\n")

    # Create study
    sampler = TPESampler(seed=0)
    pruner = MedianPruner(n_startup_trials=2, n_warmup_steps=0)

    study = optuna.create_study(
        direction="maximize",  # Maximize mass-controlled learned MRR (+/-5 Da)
        sampler=sampler,
        pruner=pruner
    )

    # Run optimization
    study.optimize(
        lambda trial: objective(runpath, trial, epochs_fwd, epochs_bwd, device, use_wandb=use_wandb, timeout=timeout),
        n_trials=n_trials,
        n_jobs=1,  # Sequential execution (GPU cannot parallelize)
        show_progress_bar=True
    )

    # A trial that timed out / crashed is pruned, so it never becomes "best".
    # If nothing completed, there is no best trial to report -- surface that
    # clearly rather than raising deep inside optuna.
    completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
    if not completed:
        print("\nNo trials completed successfully (all pruned or failed).")
        print("Likely the per-trial timeout is too short for the chosen epoch count.")
        return {}

    # Extract best trial
    best_trial = study.best_trial
    best_config = best_trial.user_attrs.get("config", {})
    best_metrics = {
        "massctl_mrr_w5": best_trial.value,
        "massctl_delta_w5": best_trial.user_attrs.get("massctl_delta_w5", 0.0),
        "mrr": best_trial.user_attrs.get("mrr", 0.0),
        "r1": best_trial.user_attrs.get("r1", 0.0),
    }

    # Prepare output
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_trials": n_trials,
        "epochs_fwd": epochs_fwd,
        "epochs_bwd": epochs_bwd,
        "best_trial_number": best_trial.number,
        "best_metrics": best_metrics,
        "best_hyperparameters": best_config,
        "all_trials": []
    }

    # Add all trials to output
    for trial in study.trials:
        trial_info = {
            "trial_number": trial.number,
            "value": trial.value,
            "status": str(trial.state),
            "params": trial.params,
            "user_attrs": trial.user_attrs
        }
        output["all_trials"].append(trial_info)

    # Timestamped, non-clobbering artifacts (consumed by run/hpc/ml_train.sh).
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    # 1) Full dated record (same schema as before, timestamped filename).
    json_file = output_dir / f"best_params_{stamp}.json"
    with open(json_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    # 2) Hyperparameter YAML in main.py arg names, loaded via `main.py --hparams`.
    #    Epochs are intentionally excluded: they are an HPO ranking budget, not a
    #    training budget -- ml_train.sh sets the real epoch count separately.
    yaml_doc = {
        "metadata": {
            "source_json": json_file.name,
            "timestamp": output["timestamp"],
            "best_trial": best_trial.number,
            "n_trials": n_trials,
            "sweep_epochs_fwd": epochs_fwd,
            "sweep_epochs_bwd": epochs_bwd,
            "best_metrics": best_metrics,
        },
        "hyperparameters": _hparams_for_main(best_config),
    }
    yaml_dated = output_dir / f"best_hyperparams_{stamp}.yaml"
    yaml_latest = output_dir / "best_hyperparams_latest.yaml"
    for yf in (yaml_dated, yaml_latest):
        with open(yf, "w") as f:
            yaml.safe_dump(yaml_doc, f, default_flow_style=False, sort_keys=False)

    print(f"\n{'='*80}")
    print("OPTIMIZATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nBest Trial: #{best_trial.number}")
    print(f"Best mass-controlled MRR (+/-5 Da): {best_metrics['massctl_mrr_w5']:.6f}")
    print(f"  delta vs chance (+/-5 Da):       {best_metrics['massctl_delta_w5']:+.6f}")
    print(f"  raw MRR: {best_metrics['mrr']:.4f}   R@1: {best_metrics['r1']:.4f}")
    print(f"\nBest Hyperparameters:")
    for key, value in best_config.items():
        print(f"  {key}: {value}")

    print(f"\nFull results saved to:        {json_file.absolute()}")
    print(f"Hyperparameter YAML:          {yaml_dated.absolute()}")
    print(f"Latest (used by ml_train.sh): {yaml_latest.absolute()}")

    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Hyperparameter optimization for ML minimal implementation")
    p.add_argument("--train_script", type=Path, default=shared_path("SRC_DIR_REL", "machine_learning", "main.py"), help="Path to the training script")
    p.add_argument("--output_dir", type=Path, default=shared_path("BEST_PARAMS_DIR_REL"), help="Directory to save optimization results")
    p.add_argument("--n_trials", type=int, default=20, help="Number of optimization trials")
    p.add_argument("--epochs_fwd", type=int, default=500, help="Forward phase epochs (per trial)")
    p.add_argument("--epochs_bwd", type=int, default=500, help="Backward phase epochs (per trial)")
    p.add_argument("--trial_timeout", type=int, default=int(os.environ.get("TRIAL_TIMEOUT", "3600")),
                   help="Per-trial subprocess timeout in seconds; a trial that exceeds it is pruned (env: TRIAL_TIMEOUT)")
    p.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--wandb", action="store_true", help="Log each trial to Weights & Biases as its own run (respects WANDB_* env vars)")
    args = p.parse_args()

    run_optimization(
        runpath=args.train_script,
        n_trials=args.n_trials,
        epochs_fwd=args.epochs_fwd,
        epochs_bwd=args.epochs_bwd,
        device=args.device,
        use_wandb=args.wandb,
        timeout=args.trial_timeout
    )
