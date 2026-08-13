#!/bin/bash
set -euo pipefail

# Regenerate the cosine/MRR and Recall@k evaluation figures from the metrics CSVs
# and copy them into the report's shared figure directory.

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a


# Full-gallery ablation figures (diagnostics): cosine/MRR bars + Recall@k.
apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --env PYTHONPATH="$C_APP" \
"$REPO_ROOT/$SIF_REL" \
  python "$C_SRC/plot/eval_from_metrics_csv.py" \
    --summary-csv "$C_METRICS/metrics_main.csv" \
    --per-query-csv "$C_METRICS/metrics_per_query.csv" \
    --output-dir "$C_PLOTS" \
    --with-ci \
    --with-significance

# Headline figure: mass-controlled learned-vs-chance retrieval (held-out test split).
apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --env PYTHONPATH="$C_APP" \
"$REPO_ROOT/$SIF_REL" \
  python "$C_SRC/plot/plot_mass_controlled.py" \
    --csv "$C_METRICS/mass_controlled.csv" \
    --split test \
    --output-dir "$C_PLOTS"

# Publish the figures into the report tree. The report embeds the PDF
# (\includegraphics)
for stem in cosine_mrr recall_at_k mass_controlled_mrr; do
  cp "$REPO_ROOT/$PLOTS_DIR_REL/$stem.pdf" "$REPO_ROOT/$FIGURES_DIR_REL/$stem.pdf"
done

echo "Copied cosine_mrr, recall_at_k and mass_controlled_mrr to $FIGURES_DIR_REL/"
