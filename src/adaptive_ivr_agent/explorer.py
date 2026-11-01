"""Explorer: tries words on the practice robot, fills the map (FN-REQ-IVR-009)."""
from adaptive_ivr_agent.menu_map import MenuMap, State
from adaptive_ivr_agent.reactive import ReactiveRobot

TOPIC_STATE = "topic"
ONWARD_STATE = "moved_on"


class Explorer:
    """One call per run: tries the next untried word, records the outcome.

    Matched words become edges toward onward; misses become tried-here loops.
    Evidence on every edge says which run proved it.
    """

    def __init__(self, words: list[str], robot: ReactiveRobot) -> None:
        self._words = list(words)
        self._tried: set[str] = set()
        self._robot = robot
        self.shown = MenuMap(
            states=[State(TOPIC_STATE, "Topic step"), State(ONWARD_STATE, "Moved on")],
            current=TOPIC_STATE,
        )

    def run(self, origin: str) -> dict | None:
        """Try the next word; return the observation, None when exhausted."""
        remaining = [w for w in self._words if w not in self._tried]
        if not remaining:
            return None
        word = remaining[0]
        self._tried.add(word)
        reply, matched = self._robot.respond(word)
        ok = matched is not None
        target = ONWARD_STATE if ok else TOPIC_STATE
        self.shown.observe(TOPIC_STATE, target, word, origin=origin, success=ok)
        return {"word": word, "matched": ok, "reply": reply}
