"""Post-call classification (T-048): surprises prove, clean runs suggest."""
from adaptive_ivr_agent.classify import CallEvidence, classify


def verdicts(evidence):
    return {v.axis: v.value for v in classify(evidence)}


def test_af_like_call_is_partial_stochastic_unknown():
    out = verdicts(
        CallEvidence(
            states_visited=["open_question", "example_words", "yes_no"],
            surprises=["misheard topic", "no_match"],
            same_input_different_result=True,
            silence_reprompted=True,
            known_branches_unexplored=True,
        )
    )
    assert out["observable"] == "partially observable"
    assert out["deterministic"] == "stochastic"
    assert out["episodic"] == "sequential"
    assert out["static"] == "semidynamic"
    assert out["known"] == "unknown"


def test_clean_dtmf_call_suggests_but_never_proves():
    out = verdicts(CallEvidence(states_visited=["menu", "submenu", "queue"]))
    assert out["observable"] == "fully observable so far"
    assert out["deterministic"] == "deterministic so far"
    assert out["static"] == "static so far"
    assert out["known"] == "known so far"


def test_queue_movement_means_dynamic_and_human_means_multi():
    out = verdicts(
        CallEvidence(
            states_visited=["queue"],
            queue_moved_unprompted=True,
            human_entered=True,
        )
    )
    assert out["static"] == "dynamic"
    assert out["agents"] == "multi-agent"


def test_every_verdict_carries_a_reason():
    for verdict in classify(CallEvidence(states_visited=["menu"])):
        assert verdict.reason.strip()
    assert [v.axis for v in classify(CallEvidence())] == [
        "observable",
        "deterministic",
        "episodic",
        "static",
        "discrete",
        "agents",
        "known",
    ]
