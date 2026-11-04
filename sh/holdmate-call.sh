#!/bin/bash
# Holdmate calls Roksolana by itself: BFS lessons per persona, headless and fast.
# Runs on: Rickard's Mac (M4). Modes: run (default) | check.
# Flags: --as <persona> (one lesson), --all (every persona, default),
#   --depth 0..2 (miss levels, default 2), --lang sv|en (lesson language,
#   default sv), --speak (Oskar calls, Alva answers),
#   --fresh (reset knowledge first), --spark (Muse Spark rescues word-step
#   misses; keyless runs skip it). Learning lands in data/holdmate-knowledge.json
# (word table + map evidence) and data/holdmate-lessons.jsonl (sim history).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
ROOT="$(cd "$HERE/.." && pwd)"

MODE="run"
PERSONA=""
DEPTH="2"
LANG="sv"
SPEAK=0
FRESH=0
SPARK=0
while [ $# -gt 0 ]; do
  case "$1" in
    check|--check) MODE="check" ;;
    --all) PERSONA="" ;;
    --as)
      PERSONA="${2:-}"
      [ -n "$PERSONA" ] || fail "--as needs a persona id (see data/role-phrasebooks.json)"
      shift
      ;;
    --depth)
      DEPTH="${2:-}"
      case "$DEPTH" in
        0|1|2) ;;
        *) fail "--depth must be 0, 1 or 2" ;;
      esac
      shift
      ;;
    --speak) SPEAK=1 ;;
    --fresh) FRESH=1 ;;
    --spark) SPARK=1 ;;
    --lang)
      LANG="${2:-}"
      case "$LANG" in
        sv|en) ;;
        *) fail "--lang must be sv or en" ;;
      esac
      shift
      ;;
    *) fail "Unknown argument: $1 (use: check, --all, --as <id>, --depth N, --lang sv|en, --speak, --fresh, --spark)" ;;
  esac
  shift
done

PHRASEBOOKS="$ROOT/data/role-phrasebooks.json"
LINES="$ROOT/data/doorkeeper-lines.json"
KNOWLEDGE="$ROOT/data/holdmate-knowledge.json"
LESSONS="$ROOT/data/holdmate-lessons.jsonl"
BOARD="$ROOT/ui/board/public/board-state.json"

title "Holdmate calls by itself ($MODE)"

step "Preflight"
what "Check python, phrasebooks and recorded lines before running lessons."
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
ok "tool: python3"
[ -f "$PHRASEBOOKS" ] || fail "Phrasebooks not found: $PHRASEBOOKS"
ok "phrasebooks: ${PHRASEBOOKS#$ROOT/}"
[ -f "$LINES" ] || fail "Recorded lines not found: $LINES"
ok "recorded lines: ${LINES#$ROOT/}"
if [ "$SPEAK" = 1 ]; then
  command -v say >/dev/null 2>&1 || fail "say is missing (macOS only)"
  ok "speech: Oskar calls, Alva answers"
fi
if [ -n "$PERSONA" ]; then
  PYTHONPATH="$ROOT/src" python3 - "$PERSONA" "$PHRASEBOOKS" <<'EOF' \
    || fail "Unknown persona '$PERSONA'"
import json
import sys
roles = json.load(open(sys.argv[2], encoding="utf-8"))["roles"]
sys.exit(0 if any(r["id"] == sys.argv[1] for r in roles) else 1)
EOF
  ok "persona: $PERSONA"
else
  info "personas: all 8 roles"
fi
info "depth: $DEPTH miss levels"
info "language: $LANG"

[ "$MODE" = "check" ] && { title "Check only: nothing changed"; exit 0; }

step "Run lessons"
what "Breadth-first over every alternative; every sim runs to handover."
ARGS="--phrasebooks $PHRASEBOOKS --lines $LINES --knowledge $KNOWLEDGE --lessons $LESSONS --depth $DEPTH --lang $LANG --board-out $BOARD"
[ -n "$PERSONA" ] && ARGS="$ARGS --as $PERSONA"
[ "$SPEAK" = 1 ] && ARGS="$ARGS --speak"
[ "$FRESH" = 1 ] && ARGS="$ARGS --fresh"
[ "$SPARK" = 1 ] && ARGS="$ARGS --spark"
DISPLAY="holdmate lessons --depth $DEPTH --lang $LANG"
[ -n "$PERSONA" ] && DISPLAY="$DISPLAY --as $PERSONA"
[ "$SPEAK" = 1 ] && DISPLAY="$DISPLAY --speak"
[ "$FRESH" = 1 ] && DISPLAY="$DISPLAY --fresh"
[ "$SPARK" = 1 ] && DISPLAY="$DISPLAY --spark"
run "$DISPLAY"
# shellcheck disable=SC2086
PYTHONPATH="$ROOT/src" python3 -m adaptive_ivr_agent.holdmate $ARGS \
  || fail "Lessons failed"
[ -s "$KNOWLEDGE" ] || fail "Knowledge missing: $KNOWLEDGE"
ok "knowledge: ${KNOWLEDGE#$ROOT/}"
[ -s "$LESSONS" ] || fail "Lesson history missing: $LESSONS"
ok "history: ${LESSONS#$ROOT/}"
if [ -s "$BOARD" ]; then
  python3 "$ROOT/sh/bake-board.py" --board "$BOARD" --lines "$LINES"
  ok "board: ${BOARD#$ROOT/}"
else
  warn "board file missing: $BOARD (display only)"
fi

step "Learned table"
what "Show which words transfer and which miss, per the saved knowledge."
PYTHONPATH="$ROOT/src" python3 - "$KNOWLEDGE" <<'EOF'
import json
import sys
known = json.load(open(sys.argv[1], encoding="utf-8"))
words = known["words"]
shown = {w: (w if w else "(silence)") for w in words}
moved = sorted(shown[w] for w, e in words.items() if e["transfers"] == e["tries"] and e["tries"])
mixed = sorted(shown[w] for w, e in words.items() if 0 < e["transfers"] < e["tries"])
stuck = sorted(shown[w] for w, e in words.items() if e["transfers"] == 0 and e["tries"])
print(f"words learned: {len(words)}")
print(f"always transfer ({len(moved)}): {', '.join(moved) or '-'}")
print(f"sometimes miss ({len(mixed)}): {', '.join(mixed) or '-'}")
print(f"never transfer ({len(stuck)}): {', '.join(stuck) or '-'}")
print(f"lessons saved: {len(known['lessons'])}")
EOF

title "Done — Holdmate learned without Rickard saying a word"
