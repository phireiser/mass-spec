"""
Parse and format best hyperparameters from optimization results.

Usage:
    python format_best_params.py [--input best_hyperparams.json] [--output params.yaml]
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any
import yaml


def format_best_params(results_file: Path, output_file: Path = None, format: str = "json"):
    """Extract and format best parameters from optimization results."""

    # Load results
    with open(results_file) as f:
        results = json.load(f)

    best_params = results.get("best_hyperparameters", {})
    best_metrics = results.get("best_metrics", {})

    if not best_params:
        print("Error: No best hyperparameters found in results file.")
        return False

    # Format output
    output_data = {
        "metadata": {
            "timestamp": results.get("timestamp"),
            "optimization_trials": results.get("n_trials"),
            "epochs_forward": results.get("epochs_fwd"),
            "epochs_backward": results.get("epochs_bwd"),
            "best_trial": results.get("best_trial_number"),
        },
        "best_metrics": best_metrics,
        "hyperparameters": best_params,
    }

    # Save in requested format
    if output_file is None:
        output_file = Path("best_params") / f"best_hyperparams.{format}"

    output_file.parent.mkdir(parents=True, exist_ok=True)

    if format == "json":
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)

    elif format == "yaml":
        with open(output_file, "w") as f:
            yaml.dump(output_data, f, default_flow_style=False)

    elif format == "txt":
        with open(output_file, "w") as f:
            f.write("BEST HYPERPARAMETERS FOR ML MINIMAL IMPLEMENTATION\n")
            f.write("=" * 60 + "\n\n")

            f.write("OPTIMIZATION METADATA\n")
            f.write("-" * 60 + "\n")
            for key, value in output_data["metadata"].items():
                f.write(f"  {key}: {value}\n")

            f.write("\nBEST METRICS\n")
            f.write("-" * 60 + "\n")
            for key, value in best_metrics.items():
                f.write(f"  {key}: {value}\n")

            f.write("\nHYPERPARAMETERS\n")
            f.write("-" * 60 + "\n")
            for key, value in best_params.items():
                f.write(f"  {key}: {value}\n")

            f.write("\nCOMMAND LINE ARGUMENTS\n")
            f.write("-" * 60 + "\n")
            f.write("Run training with these parameters using:\n\n")
            f.write("python ml_minimal_implement.py \\\n")
            for key, value in best_params.items():
                arg_name = key.replace("_", "_")
                if isinstance(value, bool):
                    if value:
                        f.write(f"  --{arg_name} \\\n")
                else:
                    f.write(f"  --{arg_name} {value} \\\n")

    elif format == "sh":
        with open(output_file, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Best hyperparameters script\n")
            f.write(f"# Generated from optimization with {output_data['metadata']['optimization_trials']} trials\n\n")
            f.write("python ml_minimal_implement.py \\\n")
            for key, value in best_params.items():
                arg_name = key.replace("_", "_")
                if isinstance(value, bool):
                    if value:
                        f.write(f"  --{arg_name} \\\n")
                else:
                    f.write(f"  --{arg_name} {value} \\\n")
            f.write("  \"$@\"\n")

        # Make executable
        output_file.chmod(0o755)

    print(f"Best hyperparameters saved to: {output_file.absolute()}")
    print(f"\nBest Metrics:")
    for key, value in best_metrics.items():
        print(f"  {key}: {value}")
    print(f"\nBest Hyperparameters:")
    for key, value in best_params.items():
        print(f"  {key}: {value}")

    return True


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Format best hyperparameters from optimization")
    p.add_argument("--input", type=Path, default=Path("best_hyperparams.json"),
                   help="Input results file from optimization")
    p.add_argument("--output", type=Path, help="Output file (auto-determined if not specified)")
    p.add_argument("--format", choices=["json", "yaml", "txt", "sh"], default="json",
                   help="Output format")
    args = p.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        exit(1)

    format_best_params(args.input, args.output, args.format)
