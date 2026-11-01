#!/usr/bin/env bash
# Build docs/*.md from docs/templates/*.md by filling in the code names in docs/names.env.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS="$(cd "$SCRIPT_DIR/.." && pwd)/docs"

# shellcheck disable=SC1091
source "$DOCS/names.env"

for tpl in "$DOCS"/templates/*.md; do
  out="$DOCS/$(basename "$tpl")"
  AGENT="$AGENT" AGENCY="$AGENCY" ROBOT="$ROBOT" \
    perl -pe 's/\{\{(AGENT|AGENCY|ROBOT)\}\}/$ENV{$1}/g' "$tpl" > "$out"
  echo "Wrote $out"
done
