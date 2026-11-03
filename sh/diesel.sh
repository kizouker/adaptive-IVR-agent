#!/bin/bash
# Diesel walks across your terminal (#189). Pure ASCII, no dependencies.
# Runs on: Rickard's Mac (M4). Run: ./sh/diesel.sh [steps, default 40]
set -u
STEPS="${1:-40}"

frame() { # $1 = x offset, $2 = bob (0/1)
  _pad="$(printf '%*s' "$1" '')"
  _up=""; [ "$2" = 1 ] && _up=" "
  printf '%s%s/\_/\\\n' "$_pad" "$_up"
  printf '%s%s( o.o )\n' "$_pad" "$_up"
  printf '%s%s > ^ <\n' "$_pad" "$_up"
}

i=0
while [ "$i" -lt "$STEPS" ]; do
  clear
  frame "$((i % 50))" "$((i % 2))"
  i=$((i + 1))
  sleep 0.15
done
clear
echo "Diesel supervised this session."
