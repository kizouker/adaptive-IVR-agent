"""Menu map with current position (FN-REQ-IVR-005).

States are dialog steps (open question, example words, yes/no, ...),
edges are what moves the call on (an answer, a key press, silence).
Renders as ASCII (terminal, the `*` marks where we are), Mermaid,
or Graphviz DOT (real graphics: SVG/PNG, left to right, colored levels).
"""
import copy
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

ENCODING = "utf-8"
CURRENT_MARKER = "*"
CONNECTOR = "|"
INDENT = "  "
DOT_COMMAND = "dot"

SWEDISH_TITLE = "AF Agda - svenska kedjan"
ENGLISH_TITLE = "AF Agda - English branch (press 0)"

# One fill color per level, left to right: blue, amber, purple, teal, green.
LEVEL_COLORS = ["#BBDEFB", "#FFE0B2", "#E1BEE7", "#B2DFDB", "#C8E6C9"]
CURRENT_COLOR = "red"
CURRENT_PENWIDTH = 3


@dataclass
class State:
    """One dialog step the call can be in."""

    id: str
    label: str


STATUS_OBSERVED = "observed"
STATUS_INFERRED = "inferred"
STATUS_UNTESTED = "untested"


@dataclass
class Evidence:
    """What backs a map entry: status, counts, and source runs (FN-REQ-IVR-029)."""

    status: str = STATUS_UNTESTED
    tries: int = 0
    successes: int = 0
    sources: list[str] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        """Share of tries that led onward; 0.0 until the first try."""
        return self.successes / self.tries if self.tries else 0.0


@dataclass
class Edge:
    """One way the call moves from a state to the next."""

    source: str
    target: str
    label: str
    evidence: Evidence = field(default_factory=Evidence)


# AF Agda fallback chain, verified against calls 1, 2, 4, 5: open question,
# example alternatives, yes/no, transfer, then identification (BankID/Freja)
# before the queue. Failed ID still lands in the queue.
AF_AGDA_STATES = [
    State("open_question", "Beskriv vad du vill ha hjälp med?"),
    State("example_words", "Du kan till exempel säga... (alt 1, 2, 3)"),
    State("yes_no", "Har du fått ett rekommenderat brev? (ja/nej)"),
    State("transfer", "Kopplar dig direkt till kön."),
    State("identification", "Identifiering: BankID eller Freja?"),
    State("queue", "Du blir nu placerad i kö."),
]

AF_AGDA_EDGES = [
    Edge("open_question", "example_words", "no_match"),
    Edge("example_words", "yes_no", "no_match"),
    Edge("yes_no", "transfer", "ja/nej"),
    Edge("transfer", "identification", "kopplar"),
    Edge("identification", "queue", "legitimerad"),
]

NO_INPUT_EDGE_LABEL = "silence"

# English branch from call 5 part 4: pressing 0 skips all speech, then the
# key menus, SMS offer, identification and queue follow in order. Pressed
# digits are recorded but the path is the same; failed ID still queues.
ENGLISH_STATES = [
    State("english_menu", "English key menu (1, 2, 4)"),
    State("english_submenu", "Register? Press 1. Other? Press 2."),
    State("sms", "SMS with a link? Press 1."),
    State("identification", "Identify: mobile BankID or Freja?"),
    State("queue", "Placed in a queue for an officer."),
    State("officer", "Connecting you to an officer."),
]

ENGLISH_EDGES = [
    Edge("english_menu", "english_submenu", "silence"),
    Edge("english_submenu", "sms", "1/2/4/silence"),
    Edge("sms", "identification", "1/silence"),
    Edge("identification", "queue", "identified"),
    Edge("queue", "officer", "served"),
]

PRESS_ZERO_LABEL = "press 0"


@dataclass
class MenuMap:
    """A small dialog graph with a current position."""

    states: list[State] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    current: str = ""
    title: str = ""
    last_edge: tuple[str, str] | None = None

    @classmethod
    def af_agda(cls) -> "MenuMap":
        """The documented AF Agda fallback chain, starting at the open question."""
        return cls(
            states=copy.deepcopy(AF_AGDA_STATES),
            edges=copy.deepcopy(AF_AGDA_EDGES),
            current=AF_AGDA_STATES[0].id,
            title=SWEDISH_TITLE,
        )

    @classmethod
    def english_branch(cls) -> "MenuMap":
        """English key-menu branch (press 0), ending at an officer on silence."""
        return cls(
            states=copy.deepcopy(ENGLISH_STATES),
            edges=copy.deepcopy(ENGLISH_EDGES),
            current=ENGLISH_STATES[0].id,
            title=ENGLISH_TITLE,
        )

    @classmethod
    def from_steps(cls, steps: "list[Step]", title: str = "") -> "MenuMap":
        """Build the dialog graph from a step log instead of constants.

        Each robot prompt becomes a node (first-seen order); the caller turn
        between two prompts labels the edge. Repeats reuse the same node, so
        loops and reprompts show as edges, not new states.
        """
        from adaptive_ivr_agent.robot import ROBOT_SPEAKER

        states: list[State] = []
        by_text: dict[str, str] = {}
        edges: list[Edge] = []
        last_robot: str | None = None
        pending_caller = ""
        counter = 0
        for step in steps:
            if step.speaker == ROBOT_SPEAKER:
                if step.text not in by_text:
                    counter += 1
                    state_id = f"s{counter}"
                    by_text[step.text] = state_id
                    states.append(State(state_id, step.text))
                state_id = by_text[step.text]
                if last_robot is not None and last_robot != state_id:
                    edges.append(Edge(last_robot, state_id, pending_caller or "silence"))
                last_robot = state_id
                pending_caller = ""
            else:
                pending_caller = step.text
        current = states[0].id if states else ""
        return cls(states=states, edges=edges, current=current, title=title)

    def move_to(self, state_id: str) -> None:
        """Move the position marker; records the edge if one connects them."""
        if state_id not in {s.id for s in self.states}:
            raise ValueError(f"unknown state: {state_id}")
        if (self.current, state_id) in {(e.source, e.target) for e in self.edges}:
            self.last_edge = (self.current, state_id)
        self.current = state_id

    def position(self) -> int:
        """1-based position of the marker in state order."""
        return [s.id for s in self.states].index(self.current) + 1

    def _edge(self, source: str, target: str, label: str) -> Edge | None:
        found = [
            e
            for e in self.edges
            if (e.source, e.target, e.label) == (source, target, label)
        ]
        return found[0] if found else None

    def hypothesize(self, source: str, target: str, trigger: str) -> None:
        """Add an untested edge, unless the same labeled edge exists."""
        if self._edge(source, target, trigger) is None:
            edge = Edge(source, target, trigger)
            edge.evidence.status = STATUS_INFERRED
            self.edges.append(edge)

    def observe(
        self, source: str, target: str, trigger: str, origin: str, success: bool = True
    ) -> None:
        """Record one observed traversal; revise or reject on counter-evidence."""
        edge = self._edge(source, target, trigger)
        if edge is None:
            edge = Edge(source, target, trigger)
            self.edges.append(edge)
        proof = edge.evidence
        proof.tries += 1
        proof.sources.append(origin)
        if success:
            proof.successes += 1
            proof.status = STATUS_OBSERVED
        elif proof.status == STATUS_INFERRED:
            self.edges.remove(edge)
        else:
            proof.status = STATUS_INFERRED

    def render_ascii(self) -> str:
        """Vertical chain; the current state gets the `*` marker."""
        lines = []
        for index, state in enumerate(self.states):
            marker = CURRENT_MARKER if state.id == self.current else " "
            lines.append(f"{marker} {state.label}")
            if index < len(self.states) - 1:
                lines.append(f"{INDENT}{CONNECTOR}")
        return "\n".join(lines) + "\n"

    def render_mermaid(self) -> str:
        """Flowchart with the current state highlighted; renders on GitHub."""
        lines = ["flowchart TD"]
        for state in self.states:
            lines.append(f'    {state.id}["{state.label}"]')
        for edge in self.edges:
            lines.append(f"    {edge.source} -->|{edge.label}| {edge.target}")
        lines.append(f"    style {self.current} fill:#E1F5EE,stroke:#0F6E56")
        return "\n".join(lines) + "\n"

    def render_dot(self) -> str:
        """Graphviz DOT: left-to-right boxes, one color per level, header on top."""
        lines = [
            "digraph map {",
            '    rankdir=LR; label="' + self.title + '"; labelloc=top;',
            '    node [shape=box style="filled,rounded" fontname=Helvetica];',
        ]
        for index, state in enumerate(self.states):
            color = LEVEL_COLORS[index % len(LEVEL_COLORS)]
            extra = (
                f" color={CURRENT_COLOR} penwidth={CURRENT_PENWIDTH}"
                if state.id == self.current
                else ""
            )
            lines.append(
                f'    {state.id} [label="Nivå {index + 1}\\n{state.label}"'
                f" fillcolor=\"{color}\"{extra}];"
            )
        for edge in self.edges:
            walked = (edge.source, edge.target) == self.last_edge
            color = f" color={CURRENT_COLOR} penwidth=2" if walked else ""
            lines.append(
                f'    {edge.source} -> {edge.target} [label="{edge.label}"{color}];'
            )
        lines.append("}")
        return "\n".join(lines) + "\n"

    def render_image(self, path: str | Path, image_format: str = "svg") -> Path:
        """Render the map to SVG/PNG via Graphviz `dot` (real runs, never tests)."""
        if shutil.which(DOT_COMMAND) is None:
            raise RuntimeError(f"{DOT_COMMAND} is not available on this machine")
        target = Path(path)
        result = subprocess.run(
            [DOT_COMMAND, f"-T{image_format}"],
            input=self.render_dot().encode(ENCODING),
            capture_output=True,
            check=True,
        )
        target.write_bytes(result.stdout)
        return target
