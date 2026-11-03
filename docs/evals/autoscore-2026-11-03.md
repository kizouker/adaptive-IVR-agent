# Autoscore eval 2026-11-03 (portal robot, unofficial heuristic)

Total: 7.2 / 10. Project #135.

## 1. Impact & Alignment — 2.5 / 3.0

- Base hackathon repo +1.0
- Domain alignment +0.3
- Eval & benchmark proof +0.3
- Docker packaging +0.4
- Multi-module scope (>10 files) +0.2
- Detailed problem docs (>5 KB) +0.3

## 2. Meta AI Tooling — 1.3 / 2.5

- Base +0.5
- Muse Spark integration +0.3
- Open-weights / fine-tuning +0.5

## 3. Technical Depth — 2.0 / 2.0 (capped)

- Base +0.3
- 50+ window commits (146) +0.6
- Automated test suite +0.3
- Modular src/ architecture +0.3
- Agent / eval harness +1.2 (sic)
- Automated CI workflow +0.2
- PR review workflow (9 PRs) +0.2
- Pillar cap max 2.0

## 4. Demo Completeness — 1.4 / 2.5

- Base +0.4
- Reproducible setup guide +0.4
- Live web deployment +0.4
- Visual docs & diagrams (>6 KB) +0.2

## Reconciliation vs brain/eval.md (my estimate ~5.5–6)

- Impact: robot 2.5 vs my 2.0 — Docker + docs pay more than I thought.
- Meta: robot 1.3 vs my 1.0 — close; +1.2 still available (verify open weights live).
- Tech: robot 2.0 (capped) vs my 1.3 — commits/PRs/CI count hard; pillar maxed, stop investing here.
- Demo: robot 1.4 vs my 1.3 — close; +1.1 available (final video).

Biggest levers confirmed: Baseten verify (+Meta) + final video (+Demo).

## Robot rows vs our submission-check (gap map)

| Robot row (pts) | Our check | Verdict |
|---|---|---|
| Docker packaging (+0.4) | board-docker test exists, not in gate | GAP: call it from gate |
| Eval & benchmark proof (+0.3) | pytest green only, no numbers | GAP: assert benchmark file |
| Problem docs >5KB | not checked | GAP: size assert on README |
| Spark integration (+0.3) | partner config only, no live call | GAP: optional live probe |
| Open-weights (+0.5) | partner config only | GAP: provenance rows exist? |
| Test suite (+0.3) | pytest in gate | OK |
| CI workflow (+0.2) | not checked | GAP: gh run list last = green? |
| Commits/PRs (+0.8) | n/a (history, not state) | SKIP |
| Setup guide (+0.4) | quickstart files asserted | OK |
| Live web (+0.4) | not checked | GAP: curl Pages + Azure fqdn |
| Video (+0.4 base) | ffprobe ≤180s | OK |
| LICENSE | asserted | OK (not scored, required) |
| Freeze | asserted | OK (not scored, required) |
