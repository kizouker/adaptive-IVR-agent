How the 3-Stage Judging Workflow Operates
Submission Freeze: Wed, Nov 4 at 9:00 PM EST (Thu, Nov 5 at 02:00 UTC)
STAGE 1 · TRIAGE & FLAGGING
Nov 5–6
Pass/Fail Screening & Bonus Flagging
Every submission is screened pass/fail before entering rubric scoring:
Addresses Build for Your World or Push the Frontier
Meaningfully uses Meta Model API and/or Meta open-weight models at runtime
Public GitHub repository showing work built Oct 26 – Nov 4
Working, publicly accessible 3-minute demo video
Complies with Anti-Project rules (not a generic 1-prompt wrapper)
Critical Nuance: There are no opt-in checkboxes on the form for technical bonus prizes ($10k Open Weights, Best Agentic, Best Creative). Stage 1 screeners manually flag projects based on your video, top of README, and the “Use of Meta products” form field.
STAGE 2 · 10-POINT RUBRIC
Nov 6–8
Weighted Rubric & Partner Verification
Projects passing Stage 1 are scored on the Official Rules weights (overriding the “equally weighted” typo in the guide):
Impact (30% · 3.0 pts): Real-world utility, problem severity & post-hackathon viability
Use of Meta AI Tooling (25% · 2.5 pts): Creative, load-bearing multi-model or open-weight usage
Technical Depth (20% · 2.0 pts): Architecture, engineering quality & quantitative benchmarks
Demo Quality (25% · 2.5 pts): Clear 3-minute video + reproducible repo setup instructions
Partner Check: Infrastructure partners (Baseten, Modal, Fireworks) verify projects flagged for the $10k Open Weights bonus to confirm Muse Glimmer or Muse Spark Open is a load-bearing component.
STAGE 3 · LIVE FINALS
Mon, Nov 9 · 12:00 PM EST
Top 5 Indie & Top 5 Startup Broadcast
The Top 5 projects in the Indie track and Top 5 in the Startup track (10 finalists total) advance to the Closing Ceremony stream:
No live pitch or live Q&A required from finalists
Final Round Judges watch the submitted 3-minute demo videos live on stream
Ranked using the same 4-pillar rubric to crown track winners
Prizes stack: a project can win Main Track + multiple Bonus Prizes
Key Takeaway: Your submitted 3-minute video is the exact artifact played live for the Final Judges on November 9 — it must stand completely on its own.
2. Interactive 20-Point Pre-Submission Checklist
Click any item to mark it complete (5 items per pillar)
01
The 3-Minute Demo Video (25% + Finals)
0 / 5

Duration strictly ≤ 3:00 (aim for 2:50–2:55)
Hard Stop at 3:00
Organizers confirmed they will not disqualify a video that is a few seconds over, but they stop playback at the 3:00 mark. Never put your benchmarks, key results, or conclusion after 2:55.

Opening 1-line provenance in first 10 seconds
Disqualification Risk
Open your video (spoken + on-screen callout) with one clear sentence stating whether the project was built 100% from scratch during Oct 26–Nov 4 or what existed beforehand vs. what you built this week.

80%+ real product execution (not slides or IDE code)
Format
Record a live walkthrough of the working product rather than a slide presentation. You do not need to scroll through source code files on camera — the video just needs to match the code in your repo.

Live Meta model calls & roles visible on screen
Bonus Trigger
Show the end-to-end flow with live Meta model calls/telemetry visible, and explicitly show where and how each Meta model (Muse Spark, Muse Spark Open, Muse Glimmer, SAM 3.1, etc.) is used.

Public/Unlisted link + clear English audio & captions
Access
Host on YouTube (public or unlisted), Loom, or Vimeo with zero login wall. Human presenter/voiceover is preferred (English AI voiceover + burned-in captions are allowed). Speeding up long runs (e.g. 4x SPEED) is permitted.
02
GitHub Repository & Judge Reproducibility
0 / 5

Single self-contained public GitHub repository
Required
Must be a public GitHub repository (GitLab and private repos with judge invites are rejected). Keep everything needed to run the demo in one repo; if building on a startup backend, submit a clean standalone repo created during the hackathon window.

Step-by-step Quickstart + .env.example
Live URL Optional
A hosted live deployment is optional — what judges require is a runnable repository with clear setup instructions and a .env.example showing where to supply MODEL_API_KEY (never commit live API keys).

Keyless demo / recorded-trace replay mode included
High Judge Signal
Include a keyless replay mode, pre-recorded execution traces, or deterministic evaluation runner so judges without local GPUs or specific hardware can still verify your outputs immediately.

Zero third-party OAuth / login barriers on live demos
Zero Friction
Never require judges to authenticate with their own personal accounts (e.g., Google Calendar, Slack, GitHub OAuth) to test your app. Provide a one-click Guest / Demo Mode or pre-filled demo credentials in the README.

Quantitative benchmarks + open-sourced custom weights
20% Tech Depth
Organizers emphasized that benchmarks greatly strengthen your project (latency, accuracy, A/B comparisons). If your demo relies on fine-tuned LoRA adapters or custom weights, they must be published openly (e.g., Hugging Face Hub).
03
Bonus Prizes, Tracks & Team Rules
0 / 5

Explicitly call out Bonus Prizes in README & form
No Form Checkbox!
Because Stage 1 screeners manually flag projects for Best Build on Meta Open Weight Models ($10k), Best Agentic Use-Case, and Best Creative Build, state which bonus categories your project targets at the very top of your README and in the “Use of Meta products” submission field.

$10k Open Weight: Muse Glimmer / Muse Spark Open
$10,000 Prize
To qualify for the $10k Open Weight bonus, Muse Glimmer or Muse Spark Open (meta-models/muse-spark-open-1026) must run as a load-bearing stage (partner inference or self-hosted). Combining hosted Muse Spark 1.3 with Muse Spark Open does qualify; hosted SAM 3.1 alone does not.

Correct Track selected: Indie Developer vs. Startup
Legal Entity Rule
You choose your track on the submission form (regardless of your initial application). Startup Track requires an incorporated legal entity with the ability to employ people (EIN / Tax ID in the US; solo incorporated founders qualify). Unincorporated builders/teams must select Indie Developer.

$20k Most Viral on X: Link X video post in form
$20,000 Prize
Post your demo video on X before the Nov 4 deadline and paste the post URL into the submission form. Measured strictly by Likes + Reposts + Comments (views do not count; no specific hashtag required) through Sunday, Nov 8 at 11:59 PM EST.

All contributors are approved participants (max 4)
Strict Rule
Every person who contributes code or is listed on the team (up to 4 members) must be an individually accepted hackathon participant, and no participant may belong to more than one team or submit multiple projects.
04
Compliance, Licensing & Deadline Freeze
0 / 5

Respect Red Lines & differentiate from “1-Prompt Slop”
Eligibility
Hard red lines: Mental health/therapy advisors, patient-facing medical diagnosis/advice, and political/defense tools are strictly ineligible. For other domains (education, finance, sports, healthcare ops), organizers clarified the rule targets generic 1-prompt wrappers — explicitly state in paragraph 1 of your README how your system uses domain-specific depth, deterministic verification, or multi-model pipelines.

Include an open-source / source-available LICENSE file
Repo Hygiene
Add a clear LICENSE file (e.g., MIT or Apache-2.0) in the root of your repository so judges and partner verifiers have unambiguous permission to clone, build, and execute your submission.

Verify all 6 Cerebral Valley submission form fields
Portal Check
Confirm your form has: (1) Public GitHub URL, (2) 3-minute Video URL, (3) Track (Indie vs Startup), (4) Problem Statement (Build for Your World vs Push the Frontier), (5) Detailed “Use of Meta products” summary, and (6) X Post URL.

Submit draft early, then refine until Wed Nov 4, 9:00 PM EST
Strategy
Submitting early gives zero judging advantage (nothing is reviewed before the deadline), but submitting a draft early lets you verify your form links and edit freely right up until Wednesday, Nov 4 at 9:00 PM EST.

Zero commits or pushes after Wed Nov 4, 9:00 PM EST
Hard Freeze
Once the deadline passes (Wed Nov 4, 21:00 EST / Thu Nov 5, 02:00 UTC), stop pushing to the submission branch — judges verify the exact commit state at the deadline.
3. Recommended 3:00 Video Pacing Blueprint
Proportional 180-second allocation for Stage 1 screening, Stage 2 rubric & Stage 3 live finals
0:00 Start
0:15 Live Demo (45% of runtime)
1:35 Meta AI Stack (22%)
2:15 Benchmarks (17%)
2:55 Stop (3:00 Cutoff)
0:00 – 0:15
15s
Hook & Provenance
1-sentence problem statement + mandatory 1-line provenance callout stating what was built from scratch during Oct 26–Nov 4.
0:15 – 1:35
80s
Live Product Walkthrough
Jump straight into the running product (no slide deck). Show a real end-to-end user workflow with live Meta model calls visible on screen.
1:35 – 2:15
40s
Meta AI Architecture
Show how Meta models work together under the hood (e.g. Muse Spark + Muse Spark Open / Muse Glimmer / SAM 3.1) to trigger Stage 1 bonus prize flagging.
2:15 – 2:45
30s
Benchmarks & Proof
Show quantitative evaluation metrics (accuracy, latency, A/B model comparison, test suite, 1-command reproducibility).
2:45 – 2:55
10s
Summary & Clean Stop
Final summary card with repo URL, Meta models used, and headline metrics — finishing cleanly at 2:55 before the 3:00 cutoff.
4. Copy-Paste README Provenance Header & Bonus Prize Guide
Help Stage 1 screeners & Stage 2 judges verify your project in 10 seconds
1. Top of README.md
2. Portal “Use of Meta products” Field
Copy Snippet
## Meta Global AI Hackathon 2026 — Submission Overview

- **Track & Problem Statement**: Indie Developer (or Startup) · Push the Frontier (or Build for Your World)
- **Hackathon Provenance (Oct 26 – Nov 4, 2026)**: Built 100% from scratch during the hackathon window.
- **Meta AI Runtime Models**:
  - `Muse Spark 1.3` (`api.meta.ai`) — Primary reasoning, tool-use & orchestration
  - `Muse Spark Open` / `Muse Glimmer` — Load-bearing open-weight inference stage
  - `SAM 3.1` / `Muse Wonder` / `Muse Voice` — Multimodal perception / synthesis
- **Bonus Prize Categories Targeted**:
  - Best Build on Meta Open Weight Models ($10k) · Best Agentic Use-Case · Best Creative Build
- **3-Minute Demo Video**: https://youtu.be/YOUR_VIDEO_ID
- **Quickstart & Keyless Replay**: Run `cp .env.example .env` with `MODEL_API_KEY`, or `npm run demo:replay`.
How Bonus Prizes Are Flagged & Verified
Prizes Stack!
Best Build on Meta Open Weight Models
$10,000
How to qualify: Use Muse Glimmer or Muse Spark Open (meta-models/muse-spark-open-1026) as a load-bearing runtime stage (partner inference or local GPU). Manually flagged in Stage 1 & verified by Baseten / Modal / Fireworks.
Best Agentic Use-Case & Best Creative Build
Bonus
How to qualify: No form checkbox — Stage 1 screeners flag contenders based on multi-step tool/agent autonomy or creative multimodal synthesis shown in your 3-minute video and README header.
Most Viral Project on X
$20,000
How to qualify: Post your demo video on X before Nov 4 and paste the X URL in the submission form. Ranked by Likes + Reposts + Comments (views excluded) through Sun, Nov 8 at 11:59 PM EST.
Community Vote Winner
$10,000
How to qualify: Opens on the Cerebral Valley project gallery after the Nov 4 deadline (1 vote per verified account; winner announced Mon, Nov 16).
