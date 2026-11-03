# Spark live eval 2026-11-03 (#204)

First real Muse Spark run against `https://api.meta.ai/v1/chat/completions`
with `MODEL_API_KEY` (key in local `.env`, never in Git).

Command: `PYTHONPATH=src python3 eval/llm_intent_eval.py --live`

## Result

- rescue: 3/3 (heuristic baseline: 2/3)
- abstain: 10/10 (one run 9/10: `jobbcoach → rusta och matcha`, defensible)
- exact: 3/3
- p95 latency: ~13–20 s per call (Spark reasoning; timeout default 30 s, SPARK_TIMEOUT overrides)
- temperature 0 for deterministic judging runs
- SAFETY OK

## Fixes on the way

1. Model `muse-spark` 404'd; Meta quickstart says `muse-spark-1.3` (#211).
2. 3 s timeout too short for live Spark; default now 20 s.
3. Added min-confidence 0.8 gate: low-confidence maps abstain to the ladder.
4. Prompt hardened: garbled/fragmentary utterances must return null.

## Provenance

`data/provenance.jsonl` now holds real `api.meta.ai` rows (38 at write time)
with non-zero `latency_ms` — evidence, not `x.test` stubs.
Committed sample (hashes only, no personal data):
`spark-live-provenance-2026-11-03.jsonl` in this folder.

## Full transcript

Archived run output: live header + per-utterance verdicts + summary
(rescue 3/3, abstain 10/10, exact 3/3, SAFETY OK).
