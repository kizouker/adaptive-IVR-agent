#!/usr/bin/env bash
# Check security basics: secrets, keys, dangerous patterns. Fails loudly.
# Part of T-051. CI runs this on every push. Full mapping: docs/security-review.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

fail() { echo "SECURITY FAIL: $1"; exit 1; }

git check-ignore -q .env || fail ".env is not ignored"

SELF="sh/check-security.sh"
keys=$(git grep -l "BEGIN .*PRIVATE KEY" -- . ":!$SELF" ':!*.md' || true)
[ -z "$keys" ] || fail "private key material tracked: $keys"

tokens=$(git grep -nE "(sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{8,}|xox[bap]-[A-Za-z0-9-]+)" -- . ":!$SELF" || true)
[ -z "$tokens" ] || fail "token-like strings tracked: $tokens"

dangerous=$(git grep -nE "\beval\(|\bexec\(|shell=True|dangerouslySetInnerHTML|os\.system" -- src ui/board/src || true)
[ -z "$dangerous" ] || fail "dangerous pattern: $dangerous"

echo "OK: security basics hold."
