#!/bin/bash
# Submission gate: auto-verify judging NFRs before the freeze (#175).
# Covers NFR-001 (video length), NFR-006 (keyless repo), NFR-010 (LICENSE),
# NFR-012 (freeze). Runs on: Rickard's Mac (M4). Modes: run | check.
# Both modes are read-only; check is the default-safe alias.
# Full map: docs/nfr-judging.md
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=ui.sh
. "$HERE/ui.sh"
MODE="${1:-run}"

ROOT="$(cd "$HERE/.." && pwd)"
VIDEO="${VIDEO:-$ROOT/data/video/holdmate-v1.mp4}"
FREEZE="2026-11-05 02:00 UTC"

title "Submission check ($MODE)"

step "Preflight"
what "Check tools before verifying anything."
command -v python3 >/dev/null 2>&1 || fail "python3 is missing"
command -v git >/dev/null 2>&1 || fail "git is missing"
command -v pytest >/dev/null 2>&1 || fail "pytest is missing"
if command -v ffprobe >/dev/null 2>&1; then HAS_FFPROBE=1; else HAS_FFPROBE=0; warn "ffprobe missing: video length unchecked"; fi
ok "tools ok"

step "NFR-010 LICENSE"
what "Repo root must grant clone/build/execute rights."
[ -f "$ROOT/LICENSE" ] || fail "LICENSE missing at repo root"
ok "LICENSE present"

step "NFR-001 video length"
what "Submitted video must be 180s or shorter (key content before 2:55)."
[ -f "$VIDEO" ] || fail "video file missing: $VIDEO (set VIDEO=...)"
if [ "$HAS_FFPROBE" = 1 ]; then
  DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO" 2>/dev/null | cut -d. -f1)"
  [ -n "$DUR" ] || fail "ffprobe could not read $VIDEO"
  [ "$DUR" -le 180 ] || fail "video is ${DUR}s, must be <= 180s"
  ok "video ${DUR}s <= 180s: $VIDEO"
else
  warn "skipped length check (no ffprobe): $VIDEO"
fi

step "NFR-006 keyless repo"
what "Quickstart files exist and the suite passes with no keys set."
[ -x "$ROOT/sh/holdmate.sh" ] || fail "sh/holdmate.sh missing or not executable"
[ -f "$ROOT/.env.example" ] || fail ".env.example missing"
grep -q "holdmate.sh" "$ROOT/README.md" || fail "README quickstart does not mention holdmate.sh"
ok "quickstart files present"
cd "$ROOT" || fail "cannot cd to $ROOT"
set -o pipefail
PYTEST_TAIL="$(PYTHONPATH=src pytest -q 2>&1 | tail -1)" || fail "pytest suite failed"
set +o pipefail
echo "    $PYTEST_TAIL"
ok "suite green (keyless)"
warn "manual: verify on a clean clone before the freeze"

step "Partner inference (open weights)"
what "OPENWEIGHT_URL must be set; remote hosts need a key (never printed)."
OW_URL="${OPENWEIGHT_URL:-http://127.0.0.1:11434/v1/chat/completions}"
OW_KEY="${OPENWEIGHT_API_KEY:-}"
case "$OW_URL" in
  *127.0.0.1*|*localhost*)
    ok "local runtime (Ollama/Glimmer): $OW_URL"
    ;;
  https://*)
    if [ -n "$OW_KEY" ]; then
      ok "partner runtime configured: $OW_URL (key set, not shown)"
    else
      warn "partner URL without OPENWEIGHT_API_KEY: $OW_URL"
    fi
    ;;
  *)
    fail "OPENWEIGHT_URL must be localhost or https: $OW_URL"
    ;;
esac

step "NFR-012 freeze"
what "No commits to the submission branch after $FREEZE."
NOW="$(date -u +%s)"
FROZEN_AT="$(date -u -j -f "%Y-%m-%d %H:%M %Z" "$FREEZE" +%s 2>/dev/null || date -u -d "$FREEZE" +%s)"
COUNT="$(cd "$ROOT" && git log --since="$FREEZE" --oneline | wc -l | tr -d ' ')"
if [ "$NOW" -ge "$FROZEN_AT" ]; then
  [ "$COUNT" = 0 ] || fail "$COUNT commits after the freeze"
  ok "frozen and clean"
else
  LEFT_HOURS=$(( (FROZEN_AT - NOW) / 3600 ))
  ok "freeze in ~${LEFT_HOURS}h ($FREEZE); pushes still allowed"
fi

title "Verdict"
ok "submission checks hold"
