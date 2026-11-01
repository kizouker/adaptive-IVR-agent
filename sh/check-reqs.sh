#!/usr/bin/env bash
# Verify REQ ID coverage: every requirement in openspec/specs must appear
# as a tag in features/ and as a ticket heading in openspec/tickets.md.
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0
# IDs never contain whitespace, so word splitting is safe and intended here.
# shellcheck disable=SC2013
for id in $(grep -rhoE '(FN|NF)-REQ-IVR-[0-9]+' openspec/specs --include=spec.md | sort -u); do
  grep -rlq "@$id" features/ || { echo "MISSING feature tag: $id"; fail=1; }
  grep -q "^### $id " openspec/tickets.md || { echo "MISSING ticket: $id"; fail=1; }
done

if [ "$fail" -eq 0 ]; then echo "OK: all REQ IDs have feature tags and tickets."; fi
exit "$fail"
