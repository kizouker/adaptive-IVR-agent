#!/bin/bash
# Teach Agda the words it failed to hear.
# Runs on: Rickard's Mac (M4). Modes: apply (default) | check.
# Reads data/talk-misses.jsonl, asks what each miss meant (keyword, Enter to
# skip, q to quit), saves to data/learned-words.json. Next call loads them.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"
MODE="apply"
for arg in "$@"; do
  case "$arg" in
    check|--check) MODE="check" ;;
    *) fail "Unknown argument: $arg (use: check)" ;;
  esac
done

MISS_FILE="$ROOT/data/talk-misses.jsonl"
LEARNED_FILE="$ROOT/data/learned-words.json"
PHRASEBOOKS="$ROOT/data/role-phrasebooks.json"
pending=0
aliases=0

counts() {
  # Prints "pending=<n> aliases=<n>" for the current files.
  TALK_MISS_FILE="$MISS_FILE" TALK_LEARNED_FILE="$LEARNED_FILE" \
    PYTHONPATH="$ROOT/src" python3 - <<'EOF'
import json
import os
from adaptive_ivr_agent.learn import pending_misses, read_misses

learned_path = os.environ["TALK_LEARNED_FILE"]
learned = json.load(open(learned_path, encoding="utf-8")) if os.path.exists(learned_path) else {}
pending = pending_misses(read_misses(os.environ["TALK_MISS_FILE"]), learned)
print(f"pending={len(pending)} aliases={sum(1 for v in learned.values() if v)}")
EOF
}

title "Teach Agda your words ($MODE)"

step "Preflight"
what "Check tools and files before asking anything."
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
ok "tools: python3"
[ -f "$PHRASEBOOKS" ] || fail "Phrasebooks not found: $PHRASEBOOKS"
ok "phrasebooks: $PHRASEBOOKS"
if [ -f "$MISS_FILE" ]; then
  ok "misses: $MISS_FILE"
else
  info "no misses yet ($MISS_FILE missing) — talk to Agda first"
fi
if [ ! -f "$LEARNED_FILE" ]; then
  if [ "$MODE" = "check" ]; then
    info "no learned words yet ($LEARNED_FILE missing)"
  else
    echo '{}' > "$LEARNED_FILE" || fail "Could not create $LEARNED_FILE"
    [ -f "$LEARNED_FILE" ] || fail "Learned-words file missing after create: $LEARNED_FILE"
    ok "created: $LEARNED_FILE"
  fi
else
  ok "learned words: $LEARNED_FILE"
fi

if [ "$MODE" = "check" ]; then
  eval "$(counts)" || fail "Could not read the learning files"
  info "$pending utterance(s) waiting for review, $aliases alias(es) learned"
  title "Check only: nothing changed"
  exit 0
fi

eval "$(counts)" || fail "Could not read the learning files"
if [ "$pending" = "0" ]; then
  ok "nothing new to review ($aliases aliases learned)"
  exit 0
fi

step "Review"
what "Ask what each of the $pending missed utterance(s) meant."
TALK_MISS_FILE="$MISS_FILE" TALK_LEARNED_FILE="$LEARNED_FILE" TALK_PHRASEBOOKS="$PHRASEBOOKS" \
  PYTHONPATH="$ROOT/src" python3 -m adaptive_ivr_agent.learn_cli \
  || fail "Review failed"

step "Verify"
what "Read the learned words back."
eval "$(counts)" || fail "Could not read $LEARNED_FILE after saving"
ok "$aliases alias(es) learned, $pending utterance(s) still waiting"

title "Done — the next call loads the new words"
