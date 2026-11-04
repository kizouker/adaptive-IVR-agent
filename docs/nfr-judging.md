# Holdmate — non-functional requirements from the judging workflow

Submission-driven quality requirements for the Meta Global AI Hackathon 2026.
Source of every number: `docs/judging-workflow.md` (organizers' 3-stage workflow,
10-point rubric, pre-submission checklist). Belongs to the Holdmate submission.

## ID line

`HOLDMATE-NFR-001` … `HOLDMATE-NFR-012`

## Coverage table (ISO/IEC 25010:2023 + constraints)

| Area | Status | Note |
|---|---|---|
| Functional suitability | covered | NFR-004, NFR-007 (Meta models load-bearing) |
| Performance efficiency | covered | NFR-006 (benchmarks incl. latency) |
| Compatibility | not relevant | — |
| Interaction capability | covered | NFR-003, NFR-005 (video clarity, captions) |
| Reliability | open | no night-shift target set; see Open questions |
| Security | covered | NFR-006 (no live keys, .env.example) |
| Maintainability | covered | NFR-006 (reproducible repo, tests) |
| Flexibility/portability | covered | NFR-006 (keyless replay, no GPU needed) |
| Safety | not relevant | — |
| Cost | open | see Open questions ($139 budget) |
| Law/GDPR | covered | NFR-009 (red lines), NFR-010 (LICENSE) |
| Operations | covered | NFR-011 (form fields), NFR-012 (freeze) |

## Priorities

1. Demo Quality (video is the finals artifact) — NFR-001…NFR-005.
2. Judge reproducibility (keyless repo) — NFR-006.
3. Bonus flagging (README header + open weights) — NFR-007, NFR-008.

Trade-off (from organizers): video + reproducibility before extra features.

## NFR-001 — Video duration

- Area: interaction capability. Touches: demo video.
- Measure: Scale = duration of submitted video in seconds. Meter = ffprobe on the
  submitted file. Must = ≤ 180. Goal = 170–175. Source = organizers.
- Scenario:
  ```gherkin
  Given the submitted demo video file
  When a judge plays it back
  Then playback of all key content finishes at or before 02:55
  ```

## NFR-002 — Provenance callout in first 10 seconds

- Area: interaction capability. Touches: demo video.
- Measure: Scale = seconds until the provenance sentence has been spoken AND shown.
  Meter = watch the video with a timer. Must = ≤ 10. Source = organizers.
- Text: repo predates the window (Sept 2026 audio experiments); all Holdmate
  agent/board/queue/app work built Oct 26 – Nov 4 (git history proves it).
- Scenario:
  ```gherkin
  Given the submitted demo video
  When the first 10 seconds play
  Then the viewer hears and sees the one-line provenance statement
  ```

## NFR-003 — Real product execution on screen

- Area: interaction capability. Touches: demo video.
- Measure: Scale = share of runtime showing the running product (not slides/IDE).
  Meter = timestamped shot list in docs/video-plan.md. Must = ≥ 80%. Source = organizers.
- Scenario:
  ```gherkin
  Given the video shot list
  When runtimes are summed by category
  Then live-product shots cover at least 144 of 180 seconds
  ```

## NFR-004 — Live Meta model calls visible

- Area: functional suitability. Touches: demo video, board telemetry.
- Measure: Scale = count of distinct Meta models shown live with their role on screen.
  Meter = shot list + board telemetry panel. Must = ≥ 1 (Muse Spark). Goal = 2
  (Spark + Spark Open/Glimmer). Source = organizers.
- Scenario:
  ```gherkin
  Given the running board with telemetry visible
  When an intent call uses a Meta model
  Then the video shows the call, the model name, and its role
  ```

## NFR-005 — Public link, English audio, captions

- Area: interaction capability. Touches: demo video.
- Measure: Scale = login walls between a judge and playback. Meter = open the URL
  in a logged-out browser. Must = 0. English voiceover + burned-in captions required.
  Source = organizers.
- Scenario:
  ```gherkin
  Given the submitted video URL in a logged-out browser
  When a judge opens it
  Then playback starts with English audio and captions, no login
  ```

## NFR-006 — Reproducible keyless repo

- Area: maintainability + flexibility + security. Touches: repo, quickstart.
- Measure: Scale = commands from clone to passing keyless demo. Meter = run on a
  clean checkout. Must = ≤ 3 commands, 0 API keys, 0 OAuth logins. Benchmarks
  (latency, accuracy, suite counts) published in README. Source = organizers.
- Scenario:
  ```gherkin
  Given a clean clone without any API keys
  When a judge runs the README quickstart
  Then the sim demo and eval replay pass with no login wall
  ```

## NFR-007 — Meta models load-bearing, bonus callout in README

- Area: functional suitability. Touches: intent pipeline, README.
- Measure: Scale = Meta model stages on the runtime path + README header present.
  Meter = code trace (MODEL_API_KEY path) + README top section. Must = Spark wired
  at runtime and bonus targets stated at top of README. Goal = Spark Open/Glimmer
  as a second load-bearing stage (partner or self-hosted). Source = organizers.
- Scenario:
  ```gherkin
  Given the README top section and the intent pipeline
  When a Stage 1 screener reads the header and traces MODEL_API_KEY
  Then bonus targets are stated and a Meta model sits on the runtime path
  ```

## NFR-008 — Track, team, viral post

- Area: constraints. Touches: submission form.
- Measure: Scale = form-field completeness. Meter = checklist against the portal.
  Must = Indie Developer track (unincorporated solo), ≤ 4 approved contributors,
  X post URL in form before Nov 4. Source = organizers.
- Scenario:
  ```gherkin
  Given the Cerebral Valley submission form
  When Rickard reviews it before the freeze
  Then track, team, and X URL fields are filled and correct
  ```

## NFR-009 — Red lines respected

- Area: law. Touches: README paragraph 1, agent scope.
- Measure: Scale = binary. Meter = read README §1. Must = states domain depth
  (scripted-sim training, deterministic eval, multi-stage pipeline), no medical/
  therapy/political/defense use. Source = organizers.
- Scenario:
  ```gherkin
  Given README paragraph 1
  When a screener reads it
  Then the system is distinguishable from a generic 1-prompt wrapper
  ```

## NFR-010 — LICENSE file

- Area: law. Touches: repo root.
- Measure: Scale = binary. Meter = file exists at root. Must = MIT (done).
  Source = organizers.
- Scenario:
  ```gherkin
  Given a fresh clone
  When a judge lists the repo root
  Then a LICENSE file grants clone/build/execute rights
  ```

## NFR-011 — All 6 form fields verified

- Area: operations. Touches: submission form.
- Measure: Scale = fields confirmed. Meter = portal checklist (repo URL, video URL,
  track, problem statement, "Use of Meta products", X URL). Must = 6/6. Source = organizers.
- Scenario:
  ```gherkin
  Given the draft submission
  When Rickard opens it before the freeze
  Then all 6 fields hold valid values
  ```

## NFR-012 — Deadline freeze respected

- Area: operations. Touches: git history.
- Measure: Scale = commits to the submission branch after the freeze. Meter =
  `git log --since="2026-11-05 02:00 UTC"`. Must = 0. Freeze: Wed Nov 4 9:00 PM EST
  (Thu Nov 5 02:00 UTC / 03:00 CET). Source = organizers.
- Scenario:
  ```gherkin
  Given the submission branch after the freeze
  When judges inspect the commit state
  Then no commit is newer than the freeze timestamp
  ```

## Constraints

- Freeze: no pushes to the submission branch after Nov 5 02:00 UTC.
- Single public GitHub repo; no GitLab, no private-with-invite.
- Custom weights (if any) must be published openly (e.g. Hugging Face Hub).
- One team per participant; max 4 members, all individually accepted.

## Out of scope

- Live hosted deployment: optional per organizers; keyless repo is what counts.
- $20k Viral on X tactics: Rickard's call, not an engineering requirement.

## Open questions

- Reliability target (uptime/error budget for the board)? → Rickard/PM.
- Cost ceiling for API spend before the deadline ($139 left)? → Rickard.
- Final track confirm: Indie Developer? → Rickard (needed at submit time).
- $10k Open Weights: attempt Spark Open/Glimmer load-bearing, or skip? → Rickard.

## Notes

- How to test: NFR-001 ffprobe; NFR-002/003/005 shot-list review; NFR-004
  telemetry screenshot; NFR-006 clean-checkout run; NFR-007 code trace + README
  read; NFR-008/011 portal checklist; NFR-010/012 file + git checks.
- Suggestion: add `sh/submission-check.sh` that verifies NFR-001, NFR-006,
  NFR-010, NFR-012 automatically before the freeze.
- Suggestion (provenance): log every Meta/local model call as JSONL
  (model id, runtime, prompt hash, latency) so benchmarks and the "Use of Meta
  products" field write themselves.
