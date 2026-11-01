"""Explorer tries words and the map grows (FN-REQ-IVR-009)."""
from adaptive_ivr_agent.explorer import ONWARD_STATE, TOPIC_STATE, Explorer
from adaptive_ivr_agent.reactive import ReactiveRobot


def make_explorer():
    robot = ReactiveRobot({"aktivitetsrapport": "report", "program": "program"})
    return Explorer(["aktivitetsrapport", "program", "blalajka"], robot)


def test_map_grows_with_every_call():
    explorer = make_explorer()
    assert len(explorer.shown.edges) == 0
    first = explorer.run("run-1")
    assert (first["word"], first["matched"]) == ("aktivitetsrapport", True)
    assert len(explorer.shown.edges) == 1
    explorer.run("run-2")
    explorer.run("run-3")
    assert len(explorer.shown.edges) == 3


def test_matched_words_move_on_unknown_stay():
    explorer = make_explorer()
    explorer.run("run-1")
    explorer.run("run-2")
    explorer.run("run-3")
    targets = {(e.label, e.target) for e in explorer.shown.edges}
    assert targets == {
        ("aktivitetsrapport", ONWARD_STATE),
        ("program", ONWARD_STATE),
        ("blalajka", TOPIC_STATE),
    }


def test_exhausted_vocab_returns_none():
    explorer = Explorer(["hej"], ReactiveRobot({}))
    assert explorer.run("run-1")["matched"] is False
    assert explorer.run("run-2") is None
