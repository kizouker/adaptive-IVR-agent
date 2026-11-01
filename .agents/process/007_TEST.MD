In this chat you as an agent act as a Test specialist. 

# Test
Your goal is to verify that the requirements written in $PROJECTDIR/specs/requirements.md and in or in github $are testable and falsifiable.


How do we test each requirement. 

One pytest test per Gherkin scenario. The tests never call the real API (see `design/SAD.md`, section 8).



- Gherkin reference: https://cucumber.io/docs/gherkin/reference/
- INVEST (Bill Wake, 2003): https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
- ISTQB Foundation syllabus, ch. 4.5 (acceptance criteria, ATDD): https://www.istqb.org/certifications/certified-tester-foundation-level

## Dry-test mapping, built requirements (2026-11-01, T-053)

One pytest test per Gherkin scenario. Scenario IDs are the unique
`@REQ-SNN` tags in `features/` (all 57 tagged); test IDs are `file::test`
from `pytest --collect-only`. Unbuilt requirements are NOT mapped yet.

| Scenario ID | Scenario | Test |
|---|---|---|
| FN-003-S01 | One run creates a step file | `test_steps.py::test_one_run_creates_a_step_file` |
| FN-003-S02 | A logged call becomes steps | `test_steps.py::test_hand_logged_call_stores_as_steps` |
| FN-004-S01 | Keyword to outcome | `test_keywords.py::test_keyword_to_outcome` |
| FN-004-S02 | Outcome to words | `test_keywords.py::test_outcome_to_words` |
| FN-005-S01 | Star sits on the right step | `test_menu_map.py::test_marker_follows_moves` |
| FN-006-S01 | Three lines play | `test_robot.py::test_robot_plays_three_lines` |
| FN-006-S02 | Each line is saved as a step | `test_robot.py::test_each_line_is_saved_as_a_step` |
| FN-007-S01 | Known word or key moves on | `test_reactive.py::test_known_word_moves_on` |
| FN-007-S02 | Unknown input is not understood | `test_reactive.py::test_unknown_word_is_not_understood` |
| FN-007-S03 | Yes and no are accepted at confirm | `test_reactive.py::test_ja_and_nej_move_on_at_confirm` |
| FN-008-S01 | Table word for a wanted outcome | `test_caller.py::test_table_word_for_wanted_outcome` |
| FN-009-S01 | Map grows with every call | `test_explorer.py::test_map_grows_with_every_call` |
| FN-010-S01 | Queue reached, no loop | `test_route.py::test_route_to_queue_never_repeats` |
| FN-011-S01 | "Det är N samtal före dig" | `test_queue.py::test_det_ar_samtal_fore_dig` |
| FN-011-S02 | "anropare nummer N" | `test_queue.py::test_anropare_nummer` |
| FN-011-S03 | "Din plats är number" | `test_queue.py::test_din_plats_ar` |
| FN-012-S01 | Alert at number 2 | `test_alerter.py::test_alert_fires_at_number_two` |
| FN-013-S01 | Place known without listening | `test_queue.py::test_watch_tracks_latest_place_without_listening` |
| FN-029-S01 | Observation tagged with evidence | `test_menu_map.py::test_observation_tagged_with_evidence` |
| FN-029-S02 | Hypothesis revised on counter-evidence | `test_menu_map.py::test_observed_revised_on_counter_evidence` + `test_hypothesis_rejected_on_counter_evidence` |

Notes: FN-010 acceptance mentions "right place"/"name trap" outside its
single scenario — untestable as specified, needs a scenario.
(`test_loops_are_skipped_not_followed` is extra coverage, no scenario.)
FN-013 "shown" is implemented as queryable `.place`; board display is
future. Design-track T-work (classify, builders, live_view, architecture,
doorkeeper data) is covered by same-named test files, not by REQ scenarios.
