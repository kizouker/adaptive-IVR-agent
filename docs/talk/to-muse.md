From claude-code (video) to muse (smooth-cosmic). Deadline 03:00 CET tonight.

Uncommitted in the shared tree (branch t2-195-cli-persist) — please review, put on a branch + PR; Rickard decides merge/push:
1. sh/talk.sh: CALL_LANG="${TALK_CALL_LANG:-sv}" (env override; --call still wins).
2. sh/holdmate.sh: export TALK_CALL_LANG="$MENU_LANG" after the remembered language, and again on the [7] language toggle.
   → Holdmate now runs fully in English when the menu is English (the video shows this).
   Tests: 247 pass, 1 fail test_menu.py::test_sound_labels_capitalized — fails identically without the change.
3. README.md line 11: video link → https://youtu.be/orxqS8rnxt0 (final submission video).

Also found (not fixed): record-call.sh lines 132/172 use `-ac 1` on BlackHole 16ch → averages 16 channels,
signal ~17 dB too quiet. Rickard has since switched to new devices (OUT_BH_MBP / IN_BH_MBP); scripts still
name IVR_Agent_Speakers / BlackHole 16ch and need updating.
Details: docs/talk/HANDOFF-claude.md.
