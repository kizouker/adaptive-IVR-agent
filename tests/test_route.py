"""Loop-free routes to a target state (FN-REQ-IVR-010)."""
from adaptive_ivr_agent.menu_map import Edge, MenuMap, State
from adaptive_ivr_agent.route import find_route


def test_route_to_queue_never_repeats():
    route = find_route(MenuMap.af_roksolana(), "queue")
    assert route == ["open_question", "example_words", "yes_no", "transfer", "identification", "queue"]
    assert len(route) == len(set(route))


def test_loops_are_skipped_not_followed():
    shown = MenuMap(
        states=[State("a", "A"), State("b", "B"), State("c", "C")],
        edges=[
            Edge("a", "b", "go"),
            Edge("b", "a", "back"),
            Edge("b", "c", "onward"),
        ],
        current="a",
    )
    assert find_route(shown, "c") == ["a", "b", "c"]


def test_unreachable_target_gives_none():
    shown = MenuMap.af_roksolana()
    assert find_route(shown, "atlantis") is None
