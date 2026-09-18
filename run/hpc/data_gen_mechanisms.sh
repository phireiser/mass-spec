#!/bin/bash
# Convenience wrapper around run/hpc/data_gen.sh, submitting it configured
# for the mechanism-derived fragmentation rule library
# (src/data_generation/mechanisms) instead of the legacy hand-authored one
# (src/data_generation/rules) -- see main.py's --rule-source flag.
#
# Just sets the two env vars data_gen.sh already reads
# (MAIN_EXTRA_ARGS/PROCESSED_DIR_OVERRIDE) and submits it; no logic is
# duplicated. Dumps land in data/processed_mechanisms/{fwd,bwd} by default,
# so they never clobber the legacy-rule baseline in data/processed -- diff
# the two afterward.
#
# Usage:
#   bash run/hpc/data_gen_mechanisms.sh
#   DEFINITION_FILE=data/some_subset.csv bash run/hpc/data_gen_mechanisms.sh
#   PROCESSED_DIR_OVERRIDE=data/processed_mech_v2 bash run/hpc/data_gen_mechanisms.sh
#   MAIN_EXTRA_ARGS=--no-migration bash run/hpc/data_gen_mechanisms.sh   # combined with --rule-source
#
# To run an arm on a GENERALIZED library instead of the committed concrete one
# (run/setup/write_generated_rules.sh --context-radius N), name the file and a
# side output tree -- data_gen.sh bind-mounts it over the container's copy, so
# the committed generated_rules.py is left alone for everything else:
#   GENERATED_RULES_FILE=data/outputs/mech_libs/gen_r1h.py \
#     PROCESSED_DIR_OVERRIDE=data/processed_mech_r1h \
#     bash run/hpc/data_gen_mechanisms.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

# The bind target must exist inside the container even when GENERATED_RULES_FILE
# replaces its contents (apptainer cannot mount a file onto a missing path), so
# this check applies either way.
GENERATED_RULES="$REPO_ROOT/$SRC_DIR_REL/data_generation/mechanisms/generated_rules.py"
if [ ! -f "$GENERATED_RULES" ]; then
  echo "error: $GENERATED_RULES does not exist yet." >&2
  echo "Generate it first (inside the container, where mod is available):" >&2
  echo "    bash run/setup/write_generated_rules.sh" >&2
  exit 1
fi

# Forwarded to data_gen.sh, which resolves it against the repo root, checks it
# and turns it into the bind. Named here only so the error surfaces at submit
# time rather than in 172 array-task logs.
if [ -n "${GENERATED_RULES_FILE:-}" ]; then
  export GENERATED_RULES_FILE
fi

# Preserve any MAIN_EXTRA_ARGS the caller already set (e.g. --no-migration
# for a combined A/B arm) and append --rule-source on top of it.
export MAIN_EXTRA_ARGS="${MAIN_EXTRA_ARGS:-} --rule-source=mechanisms"
export PROCESSED_DIR_OVERRIDE="${PROCESSED_DIR_OVERRIDE:-data/processed_mechanisms}"

sbatch "$REPO_ROOT/run/hpc/data_gen.sh"
