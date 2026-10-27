#!/usr/bin/env bash
# Double-click in Finder: opens Terminal and checks the whole sound chain.
cd "$(dirname "$0")"
./sh/record-call.sh --check
