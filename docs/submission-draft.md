# Submission draft — Cerebral Valley portal (copy-paste, then refine until freeze)

Freeze: Wed Nov 4 9:00 PM EST = Thu Nov 5 03:00 CET. Strategy: submit this
draft early to verify links, edit freely until the freeze (NFR-011, NFR-012).

## 1. Public GitHub URL

https://github.com/kizouker/adaptive-IVR-agent

## 2. 3-minute Video URL

TBD — upload to YouTube (public or unlisted) Nov 3, paste link here.
Rules: ≤ 3:00 (all key content before 2:55), provenance line in first 10s,
80%+ live product, Meta calls visible, English audio + captions (NFR-001…005).
Shot plan: docs/video-plan.md.

## 3. Track

Indie Developer (solo, unincorporated — confirm at submit time).

## 4. Problem Statement

Build for Your World (citizens vs. government phone robots).

## 5. Use of Meta products (detailed)

- Muse Spark (api.meta.ai, hosted): opt-in live intent normalization mapping
  noisy caller utterances onto the closed IVR vocabulary, plus the A/B eval
  harness (eval/llm_intent_eval.py --live). Set MODEL_API_KEY; sim runs keyless.
- Muse Spark Open (meta-models/muse-spark-open-1026): wired as a load-bearing
  intent stage (OpenWeightNormalizer, #171) — Ollama-local default, partner
  inference via env. Live verification + metrics before the freeze.
- Every model call writes a JSONL provenance row (model, runtime, latency).
- Planned before freeze: Meta speech-to-text for the robot voice (vs macOS say).

## 6. X Post URL

TBD — post video on X before Nov 4, paste URL here. Scored on
Likes + Reposts + Comments through Nov 8 (views excluded). See #174.

## Pre-submit checklist

- [ ] Video uploaded, logged-out playback works, captions burned in
- [ ] README top header matches fields 3–5
- [ ] Keyless quickstart verified on clean clone (NFR-006)
- [ ] X post live, URL in form
- [ ] After freeze: zero pushes to submission branch (NFR-012)
