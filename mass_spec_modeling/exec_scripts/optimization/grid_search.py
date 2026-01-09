"""
Lightweight Hyperparameter Grid Search for ML Minimal Implementation
====================================================================

This script performs a quick grid search over key hyperparameters
without requiring Optuna. Useful for rapid experimentation.

Usage
-----
    python grid_search.py --quick  # Fast mode: 8 trials
    python grid_search.py          # Standard mode: more comprehensive
"""

import argparse
import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import itertools


def run_training(config: Dict[str, Any], epochs_fwd: int, epochs_bwd: int, device: str) -> Dict[str, float]:
    """Train with specific config and extract metrics. Returns metrics dict."""
    cmd = [
        "python3.10",
        str(Path(__file__).parent.parent / "ml_minimal_implement.py"),
        "--epochs_fwd", str(epochs_fwd),
        "--epochs_bwd", str(epochs_bwd),
        "--batch", str(config["batch_size"]),
        "--latent", str(config["latent_dim"]),
        "--lr", str(config["learning_rate"]),
        "--weight_decay", str(config["weight_decay"]),
        "--dropout", str(config["dropout"]),
        "--norm", config["norm"],
        "--alpha_wass", str(config["alpha_wass"]),
        "--alpha_cos", str(config["alpha_cos"]),
        "--cycle_fwd", str(config["cycle_fwd"]),
        "--device", device,
        "--seed", "0"
    ]

    print(f"\nTrying: batch={config['batch_size']}, latent={config['latent_dim']}, lr={config['learning_rate']}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        output = (result.stdout or "") + (result.stderr or "")

        # Extract final loss (simplified)
        loss_matches = re.findall(r'loss[:\s]+([0-9.]+)', output)
        if loss_matches:
            final_loss = float(loss_matches[-1])
        else:
            final_loss = 999.0

        status = "success" if result.returncode == 0 and final_loss != 999.0 else "failed"

        if status == "failed":
            # Print a short diagnostic to the console to help debugging
            print("  Warning: training run failed or no loss found. Return code:", result.returncode)
            if output:
                tail = "\n".join(output.strip().splitlines()[-15:])
                print("  ---- Begin training output tail ----")
                print(tail)
                print("  ---- End training output tail ----")

        return {"loss": final_loss, "status": status, "returncode": result.returncode}
    except Exception as e:
        print(f"  Error: {e}")
        return {"loss": 999.0, "status": "failed", "returncode": -1}


def quick_grid_search(epochs_fwd: int = 5, epochs_bwd: int = 5, device: str = "cuda"):
    """Quick grid search with minimal parameters."""

    configs = []

    # Quick search space
    batch_sizes = [64, 128]
    latent_dims = [64, 128]
    lrs = [1e-4, 5e-4]

    for batch, latent, lr in itertools.product(batch_sizes, latent_dims, lrs):
        configs.append({
            "batch_size": batch,
            "latent_dim": latent,
            "learning_rate": lr,
            "weight_decay": 1e-4,
            "dropout": 0.1,
            "norm": "layer",
            "alpha_wass": 0.5,
            "alpha_cos": 1.0,
            "cycle_fwd": 0.1,
        })

    return run_grid_search(configs, epochs_fwd, epochs_bwd, device)


def comprehensive_grid_search(epochs_fwd: int = 10, epochs_bwd: int = 10, device: str = "cuda"):
    """Comprehensive grid search over more parameters."""

    configs = []

    batch_sizes = [64, 128, 256]
    latent_dims = [64, 128, 256]
    lrs = [1e-5, 1e-4, 5e-4, 1e-3]
    norms = ["layer", "batch"]

    for batch, latent, lr, norm in itertools.product(batch_sizes, latent_dims, lrs, norms):
        configs.append({
            "batch_size": batch,
            "latent_dim": latent,
            "learning_rate": lr,
            "weight_decay": 1e-4,
            "dropout": 0.1,
            "norm": norm,
            "alpha_wass": 0.5,
            "alpha_cos": 1.0,
            "cycle_fwd": 0.1,
        })

    return run_grid_search(configs, epochs_fwd, epochs_bwd, device)


def run_grid_search(configs: List[Dict[str, Any]], epochs_fwd: int, epochs_bwd: int, device: str) -> Dict[str, Any]:
    """Execute grid search over provided configurations."""

    print(f"\n{'='*80}")
    print(f"GRID SEARCH: {len(configs)} configurations")
    print(f"Epochs: fwd={epochs_fwd}, bwd={epochs_bwd}")
    print(f"Device: {device}")
    print(f"{'='*80}\n")

    results = {
        "timestamp": datetime.now().isoformat(),
        "n_configs": len(configs),
        "epochs_fwd": epochs_fwd,
        "epochs_bwd": epochs_bwd,
        "trials": []
    }

    best_loss = float('inf')
    best_config = None

    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/{len(configs)}]", end=" ")

        metrics = run_training(config, epochs_fwd, epochs_bwd, device)

        trial_result = {
            "trial_id": i,
            "config": config,
            "metrics": metrics
        }
        results["trials"].append(trial_result)

        loss = metrics["loss"]
        print(f"loss={loss:.4f}")

        if loss < best_loss:
            best_loss = loss
            best_config = config

    results["best_loss"] = best_loss
    results["best_config"] = best_config

    # Save results
    output_file = Path("grid_search_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Print summary
    print(f"\n{'='*80}")
    print("GRID SEARCH COMPLETE")
    print(f"{'='*80}")
    print(f"Best Loss: {best_loss:.6f}")
    print(f"Best Configuration:")
    if best_config:
        for key, value in best_config.items():
            print(f"  {key}: {value}")
    print(f"\nResults saved to: {output_file.absolute()}")

    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Grid search for hyperparameters")
    p.add_argument("--quick", action="store_true", help="Run quick search (8 configs)")
    p.add_argument("--epochs_fwd", type=int, default=5, help="Forward phase epochs")
    p.add_argument("--epochs_bwd", type=int, default=5, help="Backward phase epochs")
    p.add_argument("--device", type=str, default="cuda")
    args = p.parse_args()

    if args.quick:
        quick_grid_search(args.epochs_fwd, args.epochs_bwd, args.device)
    else:
        comprehensive_grid_search(args.epochs_fwd, args.epochs_bwd, args.device)
