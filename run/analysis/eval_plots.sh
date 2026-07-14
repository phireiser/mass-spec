#!/bin/bash
set -euo pipefail

# Regenerate the cosine/MRR and Recall@k evaluation figures from the metrics CSVs
# and copy them into the report's shared figure directory.

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/src/paths.env"

FIGURES_DIR_REL="thesis/shared/figures"

# Full-gallery ablation figures (diagnostics): cosine/MRR bars + Recall@k.
apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
"$SIF" \
  python "$C_SRC/plot/eval_from_metrics_csv.py" \
    --summary-csv "$C_OUTPUTS/metrics/metrics_main.csv" \
    --per-query-csv "$C_OUTPUTS/metrics/metrics_per_query.csv" \
    --output-dir "$C_OUTPUTS/plots" \
    --with-ci \
    --with-significance

# Headline figure: mass-controlled learned-vs-chance retrieval (held-out test split).
apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
"$SIF" \
  python "$C_SRC/plot/plot_mass_controlled.py" \
    --csv "$C_OUTPUTS/metrics/mass_controlled.csv" \
    --split test \
    --output-dir "$C_OUTPUTS/plots"

# Publish the figures into the report tree. The report embeds the PDF
# (\includegraphics)
for stem in cosine_mrr recall_at_k mass_controlled_mrr; do
  cp "$REPO_ROOT/$OUTPUTS_DIR_REL/plots/$stem.pdf" "$REPO_ROOT/$FIGURES_DIR_REL/$stem.pdf"
done

echo "Copied cosine_mrr, recall_at_k and mass_controlled_mrr to $FIGURES_DIR_REL/"
