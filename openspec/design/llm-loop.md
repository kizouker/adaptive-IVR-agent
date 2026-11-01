# LLM in the loop (design for #129)

Today: exact normalized match (`ReactiveRobot.respond` + `with_aliases`);
`classify.py` is post-call environment classification, not intent.
Goal: rescue noisy STT onto the closed 31-word vocab or abstain.

## Placement (chosen: A, miss normalizer)

- A. Miss normalizer (tonight's PoC): exact -> alias -> normalizer ->
  miss ladder. `src/adaptive_ivr_agent/intent.py`, eval
  `eval/llm_intent_eval.py`. Not wired into the live path yet.
- B. Next-answer policy (later): LLM picks answers; needs offline eval
  first, latency budget TBD.
- C. Lesson mining (later): LLM clusters misses into alias proposals.

## Baseline (heuristic, Nov 2)

`eval/llm_intent_eval.py`: rescue 2/3, abstain 10/10, exact 3/3,
SAFETY OK (p95 0.0ms). Known gaps for the LLM: conjugations
("skriver in mig"), confusable pairs (aktivitetsstöd/aktivitetsrapport
guarded by cutoff 0.75 + adversarial case).

## Rules

- Closed set: output must be a vocab word or null; ja/nej exact-only.
- Fail open: any LLM error/timeout abstains to the ladder.
- Latency budget ~3s; cost tracked per call (cap Monday).
- No live wiring until the eval beats the heuristic on rescues with
  zero adversarial violations.

## Monday

1. Key + endpoint into `.env` (`SPARK_API_URL`, `SPARK_API_KEY`).
2. Run eval with `SparkNormalizer`, compare against baseline.
3. Decide wiring + budget; keep keyword fallback forever.
