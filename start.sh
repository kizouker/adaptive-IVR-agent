#!/bin/bash
# Simplest start: board server + open page + talk, in one command.
# Runs on: Rickard's Mac (M4). Modes: start (default) | check.
# Runs from anywhere; for sound/menu choices use sh/holdmate.sh instead.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "${1:-}" = "check" ] || [ "${1:-}" = "--check" ]; then
  exec "$HERE/sh/holdmate.sh" check
fi
if [ $# -gt 0 ]; then
  echo "usage: start.sh [check]" >&2
  exit 1
fi
[ -x "$HERE/sh/holdmate.sh" ] || { echo "missing: $HERE/sh/holdmate.sh" >&2; exit 1; }
exec "$HERE/sh/holdmate.sh" 1
