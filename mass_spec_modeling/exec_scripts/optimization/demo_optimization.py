"""
Example: Quick Hyperparameter Optimization Demo

This script demonstrates a minimal hyperparameter search
without requiring a full training run, useful for testing
the optimization pipeline setup.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def create_demo_results():
    """Create a demo results file showing expected output format."""

    results = {
        "timestamp": datetime.now().isoformat(),
        "n_trials": 12,
        "epochs_fwd": 5,
        "epochs_bwd": 5,
        "best_trial_number": 7,
        "best_metrics": {
            "val_loss": 0.2847,
            "recall_1": 0.4200,
            "recall_5": 0.6800,
            "recall_10": 0.8200,
            "mrr": 0.5234
        },
        "best_hyperparameters": {
            "batch_size": 128,
            "latent_dim": 256,
            "learning_rate": 0.00035,
            "weight_decay": 0.0001,
            "dropout": 0.15,
            "norm": "layer",
            "alpha_wass": 0.8,
            "alpha_cos": 1.2,
            "cycle_fwd": 0.25,
            "cycle_bwd": 0.15,
            "cycle_bwd_spec": 0.2,
            "curriculum_start": 0.4,
            "curriculum_step": 0.08,
            "use_faiss": False,
            "seed": 0
        },
        "all_trials": [
            {
                "trial_number": 0,
                "value": 0.5234,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 32,
                    "latent_dim": 64,
                    "learning_rate": 0.0001,
                    "weight_decay": 0.00005,
                    "dropout": 0.1,
                    "norm": "batch"
                }
            },
            {
                "trial_number": 1,
                "value": 0.4156,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 64,
                    "latent_dim": 128,
                    "learning_rate": 0.0002,
                    "weight_decay": 0.0001,
                    "dropout": 0.15,
                    "norm": "layer"
                }
            },
            {
                "trial_number": 2,
                "value": 0.3982,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 128,
                    "latent_dim": 256,
                    "learning_rate": 0.0003,
                    "weight_decay": 0.00015,
                    "dropout": 0.2,
                    "norm": "layer"
                }
            },
            {
                "trial_number": 3,
                "value": 0.4521,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 256,
                    "latent_dim": 512,
                    "learning_rate": 0.0005,
                    "weight_decay": 0.0002,
                    "dropout": 0.25,
                    "norm": "batch"
                }
            },
            {
                "trial_number": 4,
                "value": 0.3756,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 128,
                    "latent_dim": 256,
                    "learning_rate": 0.00035,
                    "weight_decay": 0.0001,
                    "dropout": 0.15,
                    "norm": "layer"
                }
            },
            {
                "trial_number": 5,
                "value": 0.4012,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 64,
                    "latent_dim": 256,
                    "learning_rate": 0.00025,
                    "weight_decay": 0.00012,
                    "dropout": 0.12,
                    "norm": "layer"
                }
            },
            {
                "trial_number": 6,
                "value": 0.3915,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 256,
                    "latent_dim": 128,
                    "learning_rate": 0.0004,
                    "weight_decay": 0.00015,
                    "dropout": 0.18,
                    "norm": "batch"
                }
            },
            {
                "trial_number": 7,
                "value": 0.2847,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 128,
                    "latent_dim": 256,
                    "learning_rate": 0.00035,
                    "weight_decay": 0.0001,
                    "dropout": 0.15,
                    "norm": "layer"
                }
            },
            {
                "trial_number": 8,
                "value": 0.3521,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 128,
                    "latent_dim": 256,
                    "learning_rate": 0.00032,
                    "weight_decay": 0.00011,
                    "dropout": 0.14,
                    "norm": "layer"
                }
            },
            {
                "trial_number": 9,
                "value": 0.3698,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 256,
                    "latent_dim": 256,
                    "learning_rate": 0.0004,
                    "weight_decay": 0.00012,
                    "dropout": 0.16,
                    "norm": "layer"
                }
            },
            {
                "trial_number": 10,
                "value": 0.4234,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 64,
                    "latent_dim": 128,
                    "learning_rate": 0.00028,
                    "weight_decay": 0.00013,
                    "dropout": 0.11,
                    "norm": "batch"
                }
            },
            {
                "trial_number": 11,
                "value": 0.3845,
                "status": "COMPLETE",
                "params": {
                    "batch_size": 128,
                    "latent_dim": 256,
                    "learning_rate": 0.00038,
                    "weight_decay": 0.00011,
                    "dropout": 0.16,
                    "norm": "layer"
                }
            }
        ]
    }

    return results

def print_summary(results: Dict[str, Any]):
    """Print a nicely formatted summary of optimization results."""
    print("\n" + "="*80)
    print("HYPERPARAMETER OPTIMIZATION RESULTS SUMMARY")
    print("="*80)

    print(f"\nOptimization completed at: {results['timestamp']}")
    print(f"Total trials: {results['n_trials']}")
    print(f"Epochs per trial: {results['epochs_fwd']} (forward) + {results['epochs_bwd']} (backward)")

    print(f"\nBEST TRIAL: #{results['best_trial_number']}")
    print(f"{'─'*80}")

    metrics = results["best_metrics"]
    print(f"\nValidation Loss:      {metrics['val_loss']:.6f}")
    print(f"Recall@1:             {metrics.get('recall_1', 'N/A')}")
    print(f"Recall@5:             {metrics.get('recall_5', 'N/A')}")
    print(f"Recall@10:            {metrics.get('recall_10', 'N/A')}")
    print(f"MRR (Mean Rec. Rank): {metrics.get('mrr', 'N/A')}")

    print(f"\nBEST HYPERPARAMETERS")
    print(f"{'─'*80}")

    params = results["best_hyperparameters"]
    for key, value in params.items():
        print(f"  {key:.<40} {value}")

    print(f"\nCOMMAND TO RUN WITH BEST PARAMETERS")
    print(f"{'─'*80}\n")
    print("python ml_minimal_implement.py \\")
    for key, value in params.items():
        if isinstance(value, bool):
            if value:
                print(f"  --{key} \\")
        else:
            print(f"  --{key} {value} \\")
    print("  --epochs_fwd 100 --epochs_bwd 100")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    # Create demo results
    results = create_demo_results()

    # Save to file
    output_file = Path("best_hyperparams_DEMO.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Created demo results file: {output_file}")

    # Print summary
    print_summary(results)

    print("This is a DEMO of the expected output format.")
    print("Run actual optimization with:")
    print("  python grid_search.py --quick --epochs_fwd 5 --epochs_bwd 5")
    print("or")
    print("  python hyperparameter_optimization.py --n_trials 30")
