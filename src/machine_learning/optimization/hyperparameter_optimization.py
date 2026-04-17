"""
Hyperparameter Optimization for ML Minimal Implementation
==========================================================

This script performs automated hyperparameter optimization using Optuna

The optimization minimizes the validation loss while tracking retrieval
metrics (Recall@K, MRR) as secondary objectives.

Usage
-----
    $ python hyperparameter_optimization.py --n_trials 30 --epochs_fwd 20 --epochs_bwd 20

Best parameters will be saved to `best_hyperparams.json`.
"""

import argparse
import json
import sys
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List, Any
from datetime import datetime
import subprocess

try:
    import optuna
    from optuna.pruners import MedianPruner
    from optuna.samplers import TPESampler
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("Warning: Optuna not installed. Install with: pip install optuna")


def train_with_config(train: Path, config: Dict[str, Any], epochs_fwd: int, epochs_bwd: int, device: str = "cuda") -> Dict[str, float]:
    """
    Train the model with a specific hyperparameter configuration.
    Returns a dictionary with metrics (validation loss, recall@k, mrr).
    """
    # Build command to run the ml_minimal_implement.py with the given config
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

    print(f"\n{'='*80}")
    print(f"Training with config: {config}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*80}\n")

    try:
        # Run training and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

        # Parse output to extract validation metrics
        # Looking for patterns like "val_loss: 0.1234" in output
        output = (result.stdout or "") + (result.stderr or "")

        # Extract metrics from output
        metrics = _extract_metrics_from_output(output)

        if metrics is None:
            print("Warning: Could not extract metrics from output. Using high loss value.")
            metrics = {"val_loss": 1.0, "recall_1": 0.0, "mrr": 0.0}

        # If the subprocess failed, emit a short diagnostic to help debugging
        if result.returncode != 0:
            print(f"Training process exited with code {result.returncode}")
            tail = "\n".join(output.strip().splitlines()[-25:])
            if tail:
                print("---- Begin training output tail ----")
                print(tail)
                print("---- End training output tail ----")

        return metrics

    except subprocess.TimeoutExpired:
        print("Training timed out!")
        return {"val_loss": 1.0, "recall_1": 0.0, "mrr": 0.0}
    except Exception as e:
        print(f"Error during training: {e}")
        return {"val_loss": 1.0, "recall_1": 0.0, "mrr": 0.0}


def _extract_metrics_from_output(output: str) -> Dict[str, float]:
    """Extract validation metrics from training output."""
    import re

    metrics = {}

    # Try to find validation loss pattern
    val_loss_match = re.search(r'val[_\s]*loss[:\s]+([0-9.]+)', output, re.IGNORECASE)
    if val_loss_match:
        metrics["val_loss"] = float(val_loss_match.group(1))
    else:
        # Fallback: look for final loss values in output
        loss_matches = re.findall(r'loss[:\s]+([0-9.]+)', output)
        if loss_matches:
            metrics["val_loss"] = float(loss_matches[-1])  # Use last loss
        else:
            return None

    # Try to find retrieval metrics
    recall_match = re.search(r'R@1[:\s]+([0-9.]+)', output, re.IGNORECASE)
    if recall_match:
        metrics["recall_1"] = float(recall_match.group(1))

    mrr_match = re.search(r'MRR[:\s]+([0-9.]+)', output, re.IGNORECASE)
    if mrr_match:
        metrics["mrr"] = float(mrr_match.group(1))

    return metrics


def objective(runpath: Path, trial: "optuna.Trial", epochs_fwd: int, epochs_bwd: int, device: str) -> float:
    """
    Optuna objective function: defines the hyperparameter search space
    and returns the value to minimize (validation loss).
    """
    # Define hyperparameter search space
    config = {
        "batch_size": trial.suggest_categorical("batch_size", [32, 64, 128, 256]),
        "latent_dim": trial.suggest_categorical("latent_dim", [64, 128, 256, 512]),
        "learning_rate": trial.suggest_loguniform("learning_rate", 1e-5, 1e-2),
        "weight_decay": trial.suggest_loguniform("weight_decay", 1e-6, 1e-3),
        "dropout": trial.suggest_uniform("dropout", 0.0, 0.5),
        "norm": trial.suggest_categorical("norm", ["layer", "batch", "none"]),
        "alpha_wass": trial.suggest_uniform("alpha_wass", 0.1, 2.0),
        "alpha_cos": trial.suggest_uniform("alpha_cos", 0.1, 2.0),
        "cycle_fwd": trial.suggest_uniform("cycle_fwd", 0.01, 1.0),
        "cycle_bwd": trial.suggest_uniform("cycle_bwd", 0.01, 1.0),
        "cycle_bwd_spec": trial.suggest_uniform("cycle_bwd_spec", 0.01, 1.0),
        "curriculum_start": trial.suggest_uniform("curriculum_start", 0.1, 0.9),
        "curriculum_step": trial.suggest_uniform("curriculum_step", 0.01, 0.2),
        "use_faiss": trial.suggest_categorical("use_faiss", [True, False]),
        "seed": 0
    }

    # Train with this config
    metrics = train_with_config(runpath, config, epochs_fwd, epochs_bwd, device)

    # Return primary metric to minimize (validation loss)
    val_loss = metrics.get("val_loss", 1.0)

    # Report secondary metrics (for tracking, not optimization)
    trial.set_user_attr("recall_1", metrics.get("recall_1", 0.0))
    trial.set_user_attr("mrr", metrics.get("mrr", 0.0))
    trial.set_user_attr("config", config)

    return val_loss


def run_optimization(runpath: Path, n_trials: int, epochs_fwd: int, epochs_bwd: int, device: str = "cuda"):
    """Run hyperparameter optimization."""

    print(f"\nStarting hyperparameter optimization with {n_trials} trials...")
    print(f"Epochs (forward): {epochs_fwd}, Epochs (backward): {epochs_bwd}")
    print(f"Device: {device}\n")

    # Create study
    sampler = TPESampler(seed=0)
    pruner = MedianPruner(n_startup_trials=2, n_warmup_steps=0)

    study = optuna.create_study(
        direction="minimize",  # Minimize validation loss
        sampler=sampler,
        pruner=pruner
    )

    # Run optimization
    study.optimize(
        lambda trial: objective(runpath, trial, epochs_fwd, epochs_bwd, device),
        n_trials=n_trials,
        n_jobs=1,  # Sequential execution (GPU cannot parallelize)
        show_progress_bar=True
    )

    # Extract best trial
    best_trial = study.best_trial
    best_config = best_trial.user_attrs.get("config", {})
    best_metrics = {
        "val_loss": best_trial.value,
        "recall_1": best_trial.user_attrs.get("recall_1", 0.0),
        "mrr": best_trial.user_attrs.get("mrr", 0.0),
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

    # Save to JSON
    output_file = args.output_dir / "best_hyperparams.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'='*80}")
    print("OPTIMIZATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nBest Trial: #{best_trial.number}")
    print(f"Best Validation Loss: {best_metrics['val_loss']:.6f}")
    print(f"Best Recall@1: {best_metrics['recall_1']:.4f}")
    print(f"Best MRR: {best_metrics['mrr']:.4f}")
    print(f"\nBest Hyperparameters:")
    for key, value in best_config.items():
        print(f"  {key}: {value}")

    print(f"\nFull results saved to: {output_file.absolute()}")

    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Hyperparameter optimization for ML minimal implementation")
    p.add_argument("--train_script", type=Path, default=Path("src/machine_learning/main.py"), help="Path to the training script")
    p.add_argument("--output_dir", type=Path, default=Path("outputs/best_params"), help="Directory to save optimization results")
    p.add_argument("--n_trials", type=int, default=20, help="Number of optimization trials")
    p.add_argument("--epochs_fwd", type=int, default=10, help="Forward phase epochs (per trial)")
    p.add_argument("--epochs_bwd", type=int, default=10, help="Backward phase epochs (per trial)")
    p.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = p.parse_args()

    run_optimization(
        runpath=args.train_script,
        n_trials=args.n_trials,
        epochs_fwd=args.epochs_fwd,
        epochs_bwd=args.epochs_bwd,
        device=args.device
    )
