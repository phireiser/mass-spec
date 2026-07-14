#!/usr/bin/env python3
from __future__ import annotations

"""
Create two evaluation plots from the generated metrics CSVs.

Inputs
------
1. Summary CSV (required), e.g. outputs/metrics/metrics_main.csv
   Expected columns:
   - model
   - cosine_similarity
   - recall_at_1 ... recall_at_20
   - mrr

2. Per-query CSV (optional, recommended for confidence intervals), e.g. outputs/metrics/metrics_per_query.csv
   Expected columns:
   - query_id
   - query_smiles
   - model
   - cosine
   - rank
   - rr
   - hit_at_1 ... hit_at_20

Outputs (each written as both .pdf and .svg; the report embeds the PDF)
-------
1. cosine_mrr.pdf / .svg
   Grouped bar chart for:
   - Cosine similarity
   - MRR

2. recall_at_k.pdf / .svg
   Line plot of Recall@k for k = 1..20

If --with-ci is used and a per-query CSV is provided, bootstrap 95% confidence
intervals are added:
- error bars on the cosine/MRR bar chart
- shaded confidence bands on the Recall@k plot

If --with-significance is used and a per-query CSV is provided, pairwise
significance brackets are added on the cosine/MRR bar chart with numeric
p-value labels for all model pairs (shown separately for cosine and MRR).

Example
-------
python run/plot/eval_from_metrics_csv.py \
    --summary-csv outputs/metrics/metrics_main.csv \
    --per-query-csv outputs/metrics/metrics_per_query.csv \
    --output-dir outputs/plots/ \
    --with-ci \
    --with-significance
"""

import argparse
import csv
import itertools
import random
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

MAX_K = 20

# The report includes figures as PDF (\includegraphics); LISC has no Inkscape,
# so the svg package cannot convert at build time. We emit PDF as the figure the
# thesis embeds and keep an SVG alongside for quick previewing.
FIGURE_FORMATS = (".pdf", ".svg")


def save_figure(fig, output_path: Path) -> None:
    """Write ``fig`` to ``output_path`` once per :data:`FIGURE_FORMATS` suffix."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for ext in FIGURE_FORMATS:
        fig.savefig(output_path.with_suffix(ext), dpi=300, bbox_inches="tight")


def load_summary_csv(csv_path: Path) -> dict[str, dict[str, float]]:
    required = {"model", "cosine_similarity", "mrr"}
    required.update({f"recall_at_{k}" for k in range(1, MAX_K + 1)})

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Summary CSV file has no header row.")

        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Summary CSV is missing required columns: {', '.join(sorted(missing))}")

        data: dict[str, dict[str, float]] = {}
        for row in reader:
            model = row["model"].strip()
            if not model:
                raise ValueError("Encountered empty model name in summary CSV.")

            model_data = {
                "Cosine similarity": float(row["cosine_similarity"]),
                "MRR": float(row["mrr"]),
            }
            for k in range(1, MAX_K + 1):
                model_data[f"Recall@{k}"] = float(row[f"recall_at_{k}"])

            data[model] = model_data

    if not data:
        raise ValueError("Summary CSV contained no data rows.")

    return data


def load_per_query_csv(csv_path: Path) -> list[dict]:
    required = {"query_id", "query_smiles", "model", "cosine", "rank", "rr"}
    required.update({f"hit_at_{k}" for k in range(1, MAX_K + 1)})

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Per-query CSV file has no header row.")

        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Per-query CSV is missing required columns: {', '.join(sorted(missing))}")

        rows = []
        for row in reader:
            rank_raw = row["rank"].strip()
            parsed = {
                "query_id": row["query_id"].strip(),
                "query_smiles": row["query_smiles"].strip(),
                "model": row["model"].strip(),
                "cosine": float(row["cosine"]),
                "rank": None if rank_raw == "" else int(rank_raw),
                "rr": float(row["rr"]),
            }
            for k in range(1, MAX_K + 1):
                parsed[f"hit_at_{k}"] = int(row[f"hit_at_{k}"])
            rows.append(parsed)

    if not rows:
        raise ValueError("Per-query CSV contained no data rows.")

    return rows


def group_by_model(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["model"], []).append(row)
    return grouped


def bootstrap_mean_ci(values: list[float], n_boot: int = 5000, seed: int = 0) -> tuple[float, float, float]:
    rng = random.Random(seed)
    n = len(values)
    if n == 0:
        raise ValueError("Cannot bootstrap empty values.")
    if n == 1:
        v = float(values[0])
        return v, v, v

    means = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)

    means_arr = np.array(means, dtype=float)
    estimate = float(sum(values) / n)
    ci_low = float(np.quantile(means_arr, 0.025))
    ci_high = float(np.quantile(means_arr, 0.975))
    return estimate, ci_low, ci_high


def compute_summary_ci(
    grouped: dict[str, list[dict]], n_boot: int = 5000, seed: int = 0
) -> dict[str, dict[str, tuple[float, float, float]]]:
    out: dict[str, dict[str, tuple[float, float, float]]] = {}
    for i, (model, rows) in enumerate(grouped.items()):
        cosine_vals = [r["cosine"] for r in rows]
        rr_vals = [r["rr"] for r in rows]
        out[model] = {
            "Cosine similarity": bootstrap_mean_ci(cosine_vals, n_boot=n_boot, seed=seed + i),
            "MRR": bootstrap_mean_ci(rr_vals, n_boot=n_boot, seed=seed + 1000 + i),
        }
    return out


def compute_recall_curve_ci(
    grouped: dict[str, list[dict]], n_boot: int = 5000, seed: int = 0
) -> dict[str, dict[int, tuple[float, float, float]]]:
    rng = random.Random(seed)
    out: dict[str, dict[int, tuple[float, float, float]]] = {}

    for model, rows in grouped.items():
        n = len(rows)
        out[model] = {}
        for k in range(1, MAX_K + 1):
            base_vals = [float(r[f"hit_at_{k}"]) for r in rows]
            estimate = float(sum(base_vals) / n)

            boot_means = []
            for _ in range(n_boot):
                sample = [base_vals[rng.randrange(n)] for _ in range(n)]
                boot_means.append(sum(sample) / n)

            boot_arr = np.array(boot_means, dtype=float)
            ci_low = float(np.quantile(boot_arr, 0.025))
            ci_high = float(np.quantile(boot_arr, 0.975))
            out[model][k] = (estimate, ci_low, ci_high)

    return out


def _paired_randomization_p_value(
    values_a: list[float], values_b: list[float], n_perm: int = 10000, seed: int = 0
) -> float:
    if len(values_a) != len(values_b):
        raise ValueError("Paired significance test requires equal-length samples.")
    if not values_a:
        raise ValueError("Paired significance test requires non-empty samples.")

    diffs = np.array(values_a, dtype=float) - np.array(values_b, dtype=float)
    observed = float(abs(np.mean(diffs)))

    if np.allclose(diffs, 0.0):
        return 1.0

    rng = np.random.default_rng(seed)
    count = 0

    for _ in range(n_perm):
        signs = rng.choice(np.array([-1.0, 1.0]), size=len(diffs), replace=True)
        perm_stat = float(abs(np.mean(diffs * signs)))
        if perm_stat >= observed:
            count += 1

    return float((count + 1) / (n_perm + 1))


def _unpaired_permutation_p_value(
    values_a: list[float], values_b: list[float], n_perm: int = 10000, seed: int = 0
) -> float:
    if not values_a or not values_b:
        return float("nan")

    a = np.array(values_a, dtype=float)
    b = np.array(values_b, dtype=float)
    observed = float(abs(np.mean(a) - np.mean(b)))

    pooled = np.concatenate([a, b])
    n_a = len(a)
    rng = np.random.default_rng(seed)
    count = 0

    for _ in range(n_perm):
        shuffled = pooled[rng.permutation(len(pooled))]
        stat = float(abs(np.mean(shuffled[:n_a]) - np.mean(shuffled[n_a:])))
        if stat >= observed:
            count += 1

    return float((count + 1) / (n_perm + 1))


def compute_pairwise_significance(
    grouped: dict[str, list[dict]],
    models: list[str],
    n_perm: int = 10000,
    seed: int = 0,
) -> dict[str, dict[tuple[str, str], float]]:
    model_query_values: dict[str, dict[str, dict[str, float]]] = {}
    for model, rows in grouped.items():
        model_query_values[model] = {
            row["query_id"]: {
                "Cosine similarity": float(row["cosine"]),
                "MRR": float(row["rr"]),
            }
            for row in rows
        }

    out: dict[str, dict[tuple[str, str], float]] = {
        "Cosine similarity": {},
        "MRR": {},
    }
    for i, (model_a, model_b) in enumerate(itertools.combinations(models, 2)):
        rows_a = grouped.get(model_a, [])
        rows_b = grouped.get(model_b, [])

        common_query_ids = sorted(
            set(model_query_values.get(model_a, {}).keys())
            & set(model_query_values.get(model_b, {}).keys())
        )

        for metric in ["Cosine similarity", "MRR"]:
            if common_query_ids:
                vals_a = [model_query_values[model_a][qid][metric] for qid in common_query_ids]
                vals_b = [model_query_values[model_b][qid][metric] for qid in common_query_ids]
                p_val = _paired_randomization_p_value(
                    vals_a,
                    vals_b,
                    n_perm=n_perm,
                    seed=seed + i,
                )
            else:
                if metric == "Cosine similarity":
                    vals_a = [float(r["cosine"]) for r in rows_a]
                    vals_b = [float(r["cosine"]) for r in rows_b]
                else:
                    vals_a = [float(r["rr"]) for r in rows_a]
                    vals_b = [float(r["rr"]) for r in rows_b]
                p_val = _unpaired_permutation_p_value(
                    vals_a,
                    vals_b,
                    n_perm=n_perm,
                    seed=seed + i,
                )
            out[metric][(model_a, model_b)] = p_val

    return out


def _format_p_value_label(p_val: float) -> str:
    # Use fixed format for moderate values and scientific notation for tiny p-values.
    if np.isnan(p_val):
        return "p=n/a"
    if p_val >= 1e-3:
        return f"p={p_val:.3f}"
    return f"p={p_val:.2e}"


def _draw_significance_brackets(
    ax: plt.Axes,
    metric_x_positions: dict[str, dict[str, float]],
    metric_bar_tops: dict[str, dict[str, float]],
    significance: dict[str, dict[tuple[str, str], float]],
) -> float:
    """
    Draw pairwise significance brackets above the bars for each metric.

    Returns the highest y-coordinate any bracket/label reached, so the caller
    can set the axis y-limit with enough headroom.
    """
    base_step = 0.03
    hook_height = 0.01
    label_pad = 0.02  # space above the hook for the p-value label
    overall_ceiling = 0.0

    for metric, pairs in significance.items():
        x_pos = metric_x_positions.get(metric, {})
        y_top = metric_bar_tops.get(metric, {})
        if not x_pos or not y_top:
            continue

        # Per-bar running "ceiling" so later, wider brackets stack above
        # earlier ones that sit between their endpoints.
        current_ceiling = dict(y_top)

        # Draw narrowest spans first so shorter brackets end up beneath wider ones.
        for (model_a, model_b), p_val in sorted(
            pairs.items(),
            key=lambda kv: abs(x_pos[kv[0][0]] - x_pos[kv[0][1]]),
        ):
            label = _format_p_value_label(p_val)

            x1 = x_pos[model_a]
            x2 = x_pos[model_b]
            if x1 > x2:
                x1, x2 = x2, x1

            # Every bar the bracket would visually span — not just the two endpoints.
            spanned = [m for m, xp in x_pos.items() if x1 <= xp <= x2]
            y = max(current_ceiling[m] for m in spanned) + base_step

            ax.plot(
                [x1, x1, x2, x2],
                [y, y + hook_height, y + hook_height, y],
                color="black",
                linewidth=1.0,
            )
            ax.text(
                (x1 + x2) / 2,
                y + hook_height + 0.003,
                label,
                ha="center",
                va="bottom",
                fontsize=9,
            )

            new_ceiling = y + hook_height + label_pad
            for m in spanned:
                current_ceiling[m] = max(current_ceiling[m], new_ceiling)
            overall_ceiling = max(overall_ceiling, new_ceiling)

    return overall_ceiling


def plot_cosine_mrr(
    summary: dict[str, dict[str, float]],
    output_path: Path,
    ci_data: dict[str, dict[str, tuple[float, float, float]]] | None = None,
    significance: dict[str, dict[tuple[str, str], float]] | None = None,
    title: str = "Cosine Similarity and MRR Across Model Variants",
) -> None:
    models = list(summary.keys())
    metrics = ["Cosine similarity", "MRR"]

    values = np.array([[summary[m][metric] for metric in metrics] for m in models])

    x = np.arange(len(metrics))
    n_models = len(models)
    width = 0.8 / n_models

    fig, ax = plt.subplots(figsize=(8, 6))
    metric_x_positions: dict[str, dict[str, float]] = {metric: {} for metric in metrics}
    metric_bar_tops: dict[str, dict[str, float]] = {metric: {} for metric in metrics}

    for i, model in enumerate(models):
        offset = (i - (n_models - 1) / 2) * width
        y = values[i]

        if ci_data is not None and model in ci_data:
            lower_err = []
            upper_err = []
            for metric in metrics:
                est, ci_low, ci_high = ci_data[model][metric]
                lower_err.append(max(0.0, est - ci_low))
                upper_err.append(max(0.0, ci_high - est))
            yerr = np.array([lower_err, upper_err])
        else:
            yerr = None

        bars = ax.bar(
            x + offset,
            y,
            width,
            label=model,
            yerr=yerr,
            capsize=4 if yerr is not None else 0,
        )

        for j, metric in enumerate(metrics):
            metric_x_positions[metric][model] = float(x[j] + offset)
            upper = float(y[j])
            if yerr is not None:
                upper += float(yerr[1, j])
            metric_bar_tops[metric][model] = upper

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.0)
    ax.set_title(title)
    ax.legend(frameon=True)
    ax.grid(axis="y", alpha=0.3)

    if significance is not None:
        top_reached = _draw_significance_brackets(
            ax=ax,
            metric_x_positions=metric_x_positions,
            metric_bar_tops=metric_bar_tops,
            significance=significance,
        )
        # Headroom for the topmost label.
        ax.set_ylim(0, max(1.0, top_reached + 0.04))

    fig.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def plot_recall_curve(
    summary: dict[str, dict[str, float]],
    output_path: Path,
    ci_data: dict[str, dict[int, tuple[float, float, float]]] | None = None,
    title: str = "Recall@k for k = 1..20",
) -> None:
    ks = np.arange(1, MAX_K + 1)

    fig, ax = plt.subplots(figsize=(10, 6))

    for model, model_metrics in summary.items():
        recalls = [model_metrics[f"Recall@{k}"] for k in ks]
        ax.plot(ks, recalls, marker="o", label=model)

        if ci_data is not None and model in ci_data:
            lows = [ci_data[model][k][1] for k in ks]
            highs = [ci_data[model][k][2] for k in ks]
            ax.fill_between(ks, lows, highs, alpha=0.15)

    ax.set_xlabel("k")
    ax.set_ylabel("Recall@k")
    ax.set_xticks(ks)
    ax.set_ylim(0, 1.0)
    ax.set_title(title)
    ax.legend(frameon=True)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create cosine/MRR and Recall@k plots from summary/per-query evaluation CSVs."
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("../../outputs/metrics/metrics_main.csv"),
        help="Path to summary metrics CSV.",
    )
    parser.add_argument(
        "--per-query-csv",
        type=Path,
        default=Path("../../outputs/metrics/metrics_per_query.csv"),
        help="Optional path to per-query metrics CSV. Required for confidence intervals.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../../outputs/plots"),
        help="Directory for output plots.",
    )
    parser.add_argument(
        "--with-ci",
        action="store_true",
        help="Bootstrap 95%% confidence intervals from the per-query CSV.",
    )
    parser.add_argument(
        "--with-significance",
        action="store_true",
        help="Add pairwise significance brackets with p-values to cosine/MRR bars.",
    )
    parser.add_argument(
        "--bootstrap-samples",
        type=int,
        default=5000,
        help="Number of bootstrap samples if --with-ci is enabled.",
    )
    parser.add_argument(
        "--significance-permutations",
        type=int,
        default=10000,
        help="Number of randomization permutations if --with-significance is enabled.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed for bootstrap confidence intervals.",
    )

    args = parser.parse_args()

    summary = load_summary_csv(args.summary_csv)

    summary_ci = None
    recall_ci = None
    significance = None

    if args.with_ci or args.with_significance:
        if args.per_query_csv is None:
            raise ValueError("--with-ci/--with-significance require --per-query-csv")
        per_query_rows = load_per_query_csv(args.per_query_csv)
        grouped = group_by_model(per_query_rows)

    if args.with_ci:
        summary_ci = compute_summary_ci(
            grouped, n_boot=args.bootstrap_samples, seed=args.seed
        )
        recall_ci = compute_recall_curve_ci(
            grouped, n_boot=args.bootstrap_samples, seed=args.seed
        )

    if args.with_significance:
        significance = compute_pairwise_significance(
            grouped,
            models=list(summary.keys()),
            n_perm=args.significance_permutations,
            seed=args.seed,
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    cosine_path = args.output_dir / "cosine_mrr.pdf"
    recall_path = args.output_dir / "recall_at_k.pdf"
    plot_cosine_mrr(
        summary=summary,
        output_path=cosine_path,
        ci_data=summary_ci,
        significance=significance,
    )
    plot_recall_curve(
        summary=summary,
        output_path=recall_path,
        ci_data=recall_ci,
    )

    for base in (cosine_path, recall_path):
        for ext in FIGURE_FORMATS:
            print(f"Saved: {base.with_suffix(ext).resolve()}")


if __name__ == "__main__":
    main()
