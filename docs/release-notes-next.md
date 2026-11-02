# v0.3.0 — device day (2026-11-02)

Merged to main via #147 (+ #142, #56). Tag: `v0.3.0`.

## Highlights

- iPhone + Watch LAN queue ticket (#146, #153, #100): SwiftUI apps poll the
  board over LAN with editable host, debug UI, and N/A states. YOUR TURN
  blink on a dedicated 0.6s timer + haptics on both (#162), iPhone beep with
  persisted mute toggle (#163), number-only first screen with queue detail
  moved to server → Details (#160), explore meter + Map screensaver rotating
  discovered vocabulary and the live call path (#164). Bundle IDs unified
  under com.kizouker.holdmate (#159). Install cheatsheet included.
- Queue demo countdown (#157): `sh/demo-queue.sh` counts 50 → 0 slowly so
  every screen follows live; Ctrl-C stops gracefully.
- Board: N/A queue placeholder, Playwright e2e (N/A → 42 → 0 with
  screenshots) + CI job, iPhone JSON contract tests (#158).
- Spark live wiring (#145, #129): intent ladder in the live loop; heuristic
  baseline rescue 2/3, abstain 10/10, exact 3/3, SAFETY OK.
- Docs + promo: README rewrite with numbered screenshots + block diagram,
  system overview with BankID flow (#155), 3-min video script + 10-shot
  production plan, Discord post.
- Also in the train: caller checklists (#143), 46elks client prep (#131),
  CLI round 2 mic/busy/survey (#138–#141), board wording/keypad/history (#56).
- Dropped: Python tkinter widget (#144, wontfix — system tkinter renders
  blank; queue lives on board + iPhone + Watch).

## Gates (merged tree @ main)

- `pytest -q`: 194 passed, 2 skipped.
- `npm --prefix ui/board run build`: pass.
- CI + CodeQL + e2e on #147: all green.
- Known red, do NOT merge: Dependabot #148/#149 (vite 8 bump fails build).
