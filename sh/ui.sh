#!/bin/bash
# Shared output helpers for the scripts in this folder. Source it: . "$HERE/ui.sh"
# Colours are on when a terminal is attached (even if output goes through a pipe,
# like the PC alias: 2>&1 | tee /dev/tty | pbcopy). NO_COLOR=1 turns them off.
if { [ -t 1 ] || [ -t 2 ] || { : >/dev/tty; } 2>/dev/null; } && [ -z "${NO_COLOR:-}" ]; then
  B=$'\e[1m'; D=$'\e[2m'; R=$'\e[31m'; G=$'\e[32m'; Y=$'\e[33m'; C=$'\e[36m'; X=$'\e[0m'
else
  B=""; D=""; R=""; G=""; Y=""; C=""; X=""
fi
STEP_N=0
title() { printf '\n%s%s== %s ==%s\n' "$B" "$C" "$*" "$X"; }
step()  { STEP_N=$((STEP_N + 1)); printf '\n%s%s[%s] %s%s\n' "$B" "$C" "$STEP_N" "$*" "$X"; }
what()  { printf '    %sWhat:%s %s\n' "$D" "$X" "$*"; }
run()   { printf '    %s$ %s%s\n' "$D" "$*" "$X"; }
ok()    { printf '    %s%s✔ OK:%s %s\n' "$B" "$G" "$X" "$*"; }
warn()  { printf '    %s%s⚠ WARN:%s %s\n' "$B" "$Y" "$X" "$*"; }
fail()  { printf '    %s%s✘ FAIL:%s %s\n' "$B" "$R" "$X" "$*"; exit 1; }
info()  { printf '    %s%s%s\n' "$D" "$*" "$X"; }
