"""Builders from step logs (T-049): map + evidence derived, not hardcoded."""
from adaptive_ivr_agent.classify import classify, evidence_from_steps
from adaptive_ivr_agent.menu_map import MenuMap
from adaptive_ivr_agent.steps import Step

ROBOT = "robot"
CALLER = "caller"
STAFF = "staff"

WELCOME = "Välkommen till Arbetsförmedlingen."
OPEN = "Beskriv vad du vill ha hjälp med?"
NOMATCH = "Förlåt, jag uppfattade inte."


def sample_steps():
    return [
        Step(0, ROBOT, WELCOME),
        Step(1, CALLER, "eh..."),
        Step(2, ROBOT, OPEN),
        Step(3, CALLER, "aktivitetsrapport"),
        Step(4, ROBOT, NOMATCH),
    ]


def test_from_steps_builds_nodes_and_labeled_edges():
    shown = MenuMap.from_steps(sample_steps(), title="AF")
    assert [s.label for s in shown.states] == [WELCOME, OPEN, NOMATCH]
    assert [(e.source, e.target, e.label) for e in shown.edges] == [
        ("s1", "s2", "eh..."),
        ("s2", "s3", "aktivitetsrapport"),
    ]
    assert shown.current == "s1"
    assert shown.title == "AF"


def test_from_steps_reuses_nodes_and_marks_silence():
    steps = [Step(0, ROBOT, OPEN), Step(1, ROBOT, NOMATCH)]
    shown = MenuMap.from_steps(steps)
    assert [s.id for s in shown.states] == ["s1", "s2"]
    assert shown.edges[0].label == "silence"
    repeat = MenuMap.from_steps([Step(0, ROBOT, OPEN), Step(1, ROBOT, OPEN)])
    assert [s.id for s in repeat.states] == ["s1"]
    assert repeat.edges == []


def test_evidence_from_steps_finds_prompts_and_staff():
    steps = sample_steps() + [Step(5, STAFF, "Hur kan jag hjälpa dig?")]
    evidence = evidence_from_steps(steps)
    assert evidence.states_visited == [WELCOME, OPEN, NOMATCH]
    assert evidence.human_entered is True
    out = {v.axis: v.value for v in classify(evidence)}
    assert out["agents"] == "multi-agent"
    assert out["episodic"] == "sequential"
