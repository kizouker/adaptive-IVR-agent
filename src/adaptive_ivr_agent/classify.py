"""Post-call environment classification on the AIMA ch.2 axes (T-048).

After each call, Holdmate judges the line it just spoke to from observed
evidence only. The logic is deliberately asymmetric: one surprise proves
partial/stochastic/unknown, while a clean run only suggests the converse
("so far"). Verdicts get stronger as more calls accumulate.
"""
from dataclasses import dataclass, field


@dataclass
class CallEvidence:
    """What one call showed, distilled from its step log."""

    states_visited: list[str] = field(default_factory=list)
    surprises: list[str] = field(default_factory=list)
    same_input_different_result: bool = False
    silence_reprompted: bool = False
    queue_moved_unprompted: bool = False
    human_entered: bool = False
    known_branches_unexplored: bool = False


@dataclass
class Verdict:
    """One axis judgement plus the observation behind it."""

    axis: str
    value: str
    reason: str


ROBOT_SPEAKER = "robot"
CALLER_SPEAKER = "caller"


def evidence_from_steps(steps: "list[Step]") -> CallEvidence:
    """Derive what a step log proves on its own.

    Covers visited states (robot prompts in order) and human detection (any
    speaker outside robot/caller). Surprises, silence handling and queue
    movement still need interpretation (T-048 demo distills them by hand).
    """
    prompts = [s.text for s in steps if s.speaker == ROBOT_SPEAKER]
    human = any(s.speaker not in (ROBOT_SPEAKER, CALLER_SPEAKER) for s in steps)
    return CallEvidence(states_visited=prompts, human_entered=human)


def classify(evidence: CallEvidence) -> list[Verdict]:
    """Judge a line on all seven ch.2 axes from one call's evidence."""
    multi_step = len(evidence.states_visited) > 1
    surprised = bool(evidence.surprises)
    return [
        Verdict(
            "observable",
            "partially observable" if surprised else "fully observable so far",
            f"surprises: {evidence.surprises}" if surprised else "every prompt matched the map",
        ),
        Verdict(
            "deterministic",
            "stochastic" if evidence.same_input_different_result else "deterministic so far",
            "same input gave different results"
            if evidence.same_input_different_result
            else "same inputs gave same results",
        ),
        Verdict(
            "episodic",
            "sequential" if multi_step else "episodic",
            f"{len(evidence.states_visited)} steps, position mattered"
            if multi_step
            else "single step, nothing carried over",
        ),
        Verdict(
            "static",
            "dynamic"
            if evidence.queue_moved_unprompted
            else ("semidynamic" if evidence.silence_reprompted else "static so far"),
            "queue moved without our action"
            if evidence.queue_moved_unprompted
            else ("silence was reprompted, waiting costs score"
                  if evidence.silence_reprompted
                  else "nothing changed while we waited"),
        ),
        Verdict(
            "discrete",
            "discrete",
            "finite prompts, words and keys; audio discretised by STT",
        ),
        Verdict(
            "agents",
            "multi-agent" if evidence.human_entered else "single-agent",
            "a human entered at handover" if evidence.human_entered else "only the robot acted",
        ),
        Verdict(
            "known",
            "unknown"
            if surprised or evidence.known_branches_unexplored
            else "known so far",
            "unmapped behaviour or branches remain"
            if surprised or evidence.known_branches_unexplored
            else "nothing outside the prior map seen",
        ),
    ]
