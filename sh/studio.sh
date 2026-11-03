#!/bin/bash
# shellcheck shell=bash
# Studio prompt for video recording (#132). SOURCE it, don't execute:
#   source sh/studio.sh
# Sets a short prompt for this shell only. New shells are unaffected.
if (return 0 2>/dev/null); then
  PS1='holdmate$ '
  echo "Studio prompt on. Checklist: fullscreen, Cmd-+ twice, dock hidden, Do Not Disturb, mouse out of frame."
else
  echo "Run: source sh/studio.sh (sourcing required to change your prompt)"
  exit 1
fi
