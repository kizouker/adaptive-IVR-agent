"""Menu map with position (FN-REQ-IVR-005): the * sits on the right step."""
import pytest

from adaptive_ivr_agent.menu_map import (
    CURRENT_MARKER,
    LEVEL_COLORS,
    Edge,
    MenuMap,
    State,
)


def test_marker_starts_on_open_question():
    assert MenuMap.af_roksolana().position() == 1
    first = MenuMap.af_roksolana().render_ascii().splitlines()[0]
    assert first.startswith(CURRENT_MARKER)


def test_marker_follows_moves():
    shown = MenuMap.af_roksolana()
    shown.move_to("example_words")
    assert shown.position() == 2
    shown.move_to("yes_no")
    assert shown.position() == 3
    marked = [line for line in shown.render_ascii().splitlines() if line.startswith(CURRENT_MARKER)]
    assert len(marked) == 1
    assert "rekommenderat brev" in marked[0]


def test_unknown_state_is_rejected():
    with pytest.raises(ValueError):
        MenuMap.af_roksolana().move_to("atlantis")


def test_english_branch_walks_to_officer_on_silence():
    shown = MenuMap.english_branch()
    assert [s.id for s in shown.states] == [
        "english_menu",
        "english_submenu",
        "sms",
        "identification",
        "queue",
        "officer",
    ]
    assert shown.position() == 1
    shown.move_to("english_submenu")
    assert shown.position() == 2
    shown.move_to("sms")
    shown.move_to("identification")
    shown.move_to("queue")
    shown.move_to("officer")
    assert shown.position() == 6
    marked = [line for line in shown.render_ascii().splitlines() if line.startswith(CURRENT_MARKER)]
    assert len(marked) == 1
    assert "officer" in marked[0].lower()


def test_dot_has_levels_colors_and_current():
    shown = MenuMap.af_roksolana()
    shown.move_to("example_words")
    dot = shown.render_dot()
    assert "rankdir=LR" in dot
    assert "AF Roksolana - svenska kedjan" in dot
    assert "Nivå 1" in dot and "Nivå 2" in dot
    assert "#FFE0B2" in dot
    assert "example_words" in dot and "color=red" in dot
    assert "no_match" in dot


def test_dot_english_branch():
    shown = MenuMap.english_branch()
    dot = shown.render_dot()
    assert "English branch" in dot
    assert "english_menu" in dot and "silence" in dot


def test_walked_edge_is_red_in_dot():
    shown = MenuMap.af_roksolana()
    shown.move_to("example_words")
    dot = shown.render_dot()
    assert 'open_question -> example_words [label="no_match" color=red penwidth=2];' in dot


def test_observation_tagged_with_evidence():
    shown = MenuMap.af_roksolana()
    shown.observe("open_question", "example_words", "no_match", origin="run-1", success=True)
    edge = [e for e in shown.edges if (e.source, e.target) == ("open_question", "example_words")][0]
    assert edge.evidence.status == "observed"
    assert edge.evidence.sources == ["run-1"]
    assert edge.evidence.tries == 1


def test_hypothesis_rejected_on_counter_evidence():
    shown = MenuMap.af_roksolana()
    shown.hypothesize("example_words", "queue", "shortcut?")
    shown.observe("example_words", "queue", "shortcut?", origin="run-2", success=False)
    assert all((e.source, e.target) != ("example_words", "queue") for e in shown.edges)


def test_observed_revised_on_counter_evidence():
    shown = MenuMap.af_roksolana()
    shown.observe("open_question", "example_words", "no_match", origin="run-1", success=True)
    shown.observe("open_question", "example_words", "no_match", origin="run-2", success=False)
    edge = [e for e in shown.edges if (e.source, e.target) == ("open_question", "example_words")][0]
    assert edge.evidence.status == "inferred"
    assert (edge.evidence.tries, edge.evidence.successes) == (2, 1)
    assert edge.evidence.confidence == 0.5


def test_evidence_does_not_leak_between_maps():
    first, second = MenuMap.af_roksolana(), MenuMap.af_roksolana()
    first.observe("open_question", "example_words", "no_match", origin="run-1", success=True)
    edge = [e for e in second.edges if (e.source, e.target) == ("open_question", "example_words")][0]
    assert edge.evidence.status == "untested"
    assert (edge.evidence.tries, edge.evidence.successes) == (0, 0)


def test_mermaid_highlights_current_state():
    shown = MenuMap.af_roksolana()
    shown.move_to("transfer")
    text = shown.render_mermaid()
    assert "flowchart TD" in text
    assert "style transfer" in text
    assert "no_match" in text


def test_full_walk_ends_at_officer_position_eight():
    shown = MenuMap.af_roksolana()
    for state_id in ("example_words", "yes_no", "transfer", "identification", "queue"):
        shown.move_to(state_id)
    assert shown.position() == 6
    assert shown.current == "queue"
    shown.move_to("officer")
    assert shown.position() == 8
    assert shown.last_edge == ("queue", "officer")
    marked = [line for line in shown.render_ascii().splitlines() if line.startswith(CURRENT_MARKER)]
    assert marked == ["* En handläggare svarar."]


def test_jump_without_edge_keeps_last_edge_unset():
    shown = MenuMap.af_roksolana()
    assert shown.last_edge is None
    shown.move_to("transfer")
    assert shown.current == "transfer"
    assert shown.last_edge is None
    assert "color=red penwidth=2" not in shown.render_dot()


def test_walked_move_records_last_edge():
    shown = MenuMap.af_roksolana()
    shown.move_to("example_words")
    assert shown.last_edge == ("open_question", "example_words")
    shown.move_to("yes_no")
    assert shown.last_edge == ("example_words", "yes_no")


def test_ascii_shape_connectors_and_trailing_newline():
    text = MenuMap.af_roksolana().render_ascii()
    assert text.endswith("\n") and not text.endswith("\n\n")
    lines = text.splitlines()
    assert len(lines) == 2 * len(MenuMap.af_roksolana().states) - 1
    assert [line for line in lines if line.strip() == "|"] != []
    assert all(line.startswith("  |") for line in lines[1::2])
    assert text.splitlines()[0] == "* Beskriv vad du vill ha hjälp med?"


def test_mermaid_edges_and_node_labels():
    text = MenuMap.english_branch().render_mermaid()
    assert 'english_menu["English key menu (1, 2, 4)"]' in text
    assert "english_menu -->|silence| english_submenu" in text
    assert "english_submenu -->|1/2/4/silence| sms" in text
    assert "sms -->|1/silence| identification" in text
    assert "identification -->|identified| queue" in text
    assert "queue -->|served| officer" in text
    assert "style english_menu" in text


def test_dot_level_colors_cycle_after_five_states():
    states = [State(f"s{i}", f"step {i}") for i in range(6)]
    shown = MenuMap(states=states, edges=[], current="s0", title="cycle")
    dot = shown.render_dot()
    assert dot.count(f'fillcolor="{LEVEL_COLORS[0]}"') == 2
    assert "Nivå 6" in dot


def test_dot_fresh_map_has_no_walked_edge():
    dot = MenuMap.english_branch().render_dot()
    assert "color=red penwidth=2" not in dot
    assert "color=red penwidth=3" in dot


def test_move_error_names_the_unknown_state():
    with pytest.raises(ValueError, match="atlantis"):
        MenuMap.af_roksolana().move_to("atlantis")


def test_custom_edge_renders_in_all_formats():
    shown = MenuMap(
        states=[State("a", "Alpha"), State("b", "Beta")],
        edges=[Edge("a", "b", "press 1")],
        current="a",
        title="tiny",
    )
    assert shown.position() == 1
    assert "* Alpha" in shown.render_ascii()
    assert "a -->|press 1| b" in shown.render_mermaid()
    assert 'a -> b [label="press 1"];' in shown.render_dot()
