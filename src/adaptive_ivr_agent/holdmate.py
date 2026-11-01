"""Holdmate calls by itself: BFS lessons against the practice robot (S2).

Rickard stays silent. For each persona, Holdmate systematically tries every
alternative utterance level by level (miss counts 0, 1, 2), runs each path to
transfer, identification, queue and handover, and lands what it learns in the
word table plus the menu map evidence. Headless and fast by default; --speak
says every turn aloud (Oskar calls, Alva answers).
"""

import argparse
import json
import subprocess
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from adaptive_ivr_agent.menu_map import (
    AF_AGDA_STATES,
    Edge,
    Evidence,
    MenuMap,
)
from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.robot import load_indexed_lines
from adaptive_ivr_agent.talk import AgdaCall

ENCODING = "utf-8"
CALLER_VOICE = "Oskar"
AGDA_VOICE = "Alva"
MAX_MISSES = 2
FIXED_PLACE = 3
PROBES = ["ja", "nej", "hej", "tack", ""]
SILENCE_LABEL = "(silence)"


def display(word: str) -> str:
    """Printable form; the empty probe is silence."""
    return word if word else SILENCE_LABEL


MISS_STATE = {0: "open_question", 1: "example_words", 2: "yes_no"}


class SimResult(NamedTuple):
    """One simulated call: the path tried and where it ended."""

    persona: str
    misses: int
    word: str
    path: list[str]
    matched: str | None
    transferred: bool
    served: bool


def build_agda(lines: dict[str, str], respond) -> AgdaCall:
    """Scripted Agda with the recorded lines; fixed queue place for lessons."""
    return AgdaCall(
        opening=f"{lines['L01'].split(' For English, press 0.')[0]} {lines['L02']}",
        examples=lines["L03"],
        yesno=lines["L22"],
        yesno_reprompt=lines["L41"],
        transfer=lines["L19"],
        identify_line=f"{lines['L43']} {lines['L09']}",
        identified_line=lines["L11"],
        served_line=lines["L30"],
        queue_line=lines["L13"],
        place_template=lines["L29"],
        respond=respond,
        queue_place=lambda: FIXED_PLACE,
    )


def run_call(agda: AgdaCall, word: str, misses: int) -> tuple[SimResult | None, list[str]]:
    """Say WORD at MISS_COUNT misses; on transfer run to handover.

    Returns the result (None never happens; kept simple) and the turns said.
    """
    turns = [f"YOU: {display(word)}"]
    answer = agda.reply_to(word, misses)
    turns.append(f"AGDA: {answer.reply}")
    transferred = answer.identify or answer.done
    served = False
    if answer.identify:
        entered = agda.after_identified(answer.misses)
        turns.append(f"AGDA: {entered.reply}")
        place = entered.queue_place or 0
        while place > 0:
            tick = agda.queue_tick(place, answer.misses)
            turns.append(f"AGDA: {tick.reply}")
            served = tick.done
            place = tick.queue_place or 0
    return (
        SimResult("", misses, word, [], answer.matched, transferred, served),
        turns,
    )


class Lesson:
    """BFS exploration for one persona; learning accumulates in knowledge."""

    def __init__(
        self,
        persona_id: str,
        candidates: list[str],
        agda: AgdaCall,
        knowledge: "Knowledge",
        max_misses: int = MAX_MISSES,
    ) -> None:
        self.persona_id = persona_id
        self.candidates = candidates
        self.agda = agda
        self.knowledge = knowledge
        self.max_misses = max_misses
        self.sims: list[SimResult] = []

    def run(self, speak: bool = False) -> dict:
        """Breadth-first: every word at misses 0, then 1, then 2."""
        queue: deque[tuple[int, list[str]]] = deque([(0, [])])
        visited: set[tuple[int, str]] = set()
        while queue:
            misses, path = queue.popleft()
            for word in self.candidates:
                if (misses, word) in visited:
                    continue
                visited.add((misses, word))
                result, turns = run_call(self.agda, word, misses)
                result = result._replace(persona=self.persona_id, path=[*path, word])
                self.sims.append(result)
                self.knowledge.observe(result)
                print(
                    f"  {display(word)} @{MISS_STATE[misses]} -> "
                    f"{'transfer' if result.transferred else 'miss'}",
                    flush=True,
                )
                if speak:
                    speak_turns(turns)
                if not result.transferred and misses < self.max_misses:
                    queue.append((misses + 1, [*path, word]))
        matched = sorted({s.word for s in self.sims if s.matched})
        return {
            "persona": self.persona_id,
            "sims": len(self.sims),
            "transfers": sum(1 for s in self.sims if s.transferred),
            "served": sum(1 for s in self.sims if s.served),
            "matched": matched,
        }


def speak_turns(turns: list[str]) -> None:
    """Say one call aloud; Ctrl-C stops after the current line."""
    for line in turns:
        voice = CALLER_VOICE if line.startswith("YOU:") else AGDA_VOICE
        print(line, flush=True)
        subprocess.run(["say", "-v", voice, line.split(": ", 1)[1]], check=True)


class Knowledge:
    """Word table + map evidence, merged across runs and saved as JSON."""

    def __init__(self) -> None:
        self.words: dict[str, dict] = {}
        self.lessons: list[dict] = []
        self.shown = MenuMap.af_agda()

    def observe(self, result: SimResult) -> None:
        """Record one sim in the word table and on the map."""
        entry = self.words.setdefault(
            result.word, {"tries": 0, "transfers": 0, "keywords": {}}
        )
        entry["tries"] += 1
        if result.transferred:
            entry["transfers"] += 1
        if result.matched:
            keywords = entry["keywords"]
            keywords[result.matched] = keywords.get(result.matched, 0) + 1
        origin = f"lesson:{result.persona}"
        source = MISS_STATE[result.misses]
        label = display(result.word)
        if result.transferred:
            self.shown.observe(source, "transfer", label, origin, success=True)
            self.shown.observe("transfer", "identification", "kopplar", origin)
            self.shown.observe("identification", "queue", "legitimerad", origin)
            for _ in range(FIXED_PLACE - 1):
                self.shown.observe("queue", "queue", "tick", origin)
            self.shown.observe("queue", "officer", "served", origin)
        else:
            # A reprompt at yes/no loops back to yes/no (misses keep counting).
            target = MISS_STATE.get(result.misses + 1, "yes_no")
            self.shown.observe(source, target, label, origin, success=False)

    def add_lesson(self, summary: dict) -> None:
        """Append one persona summary with a timestamp."""
        self.lessons.append(
            {**summary, "ts": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        )

    def to_json(self) -> dict:
        """Serializable word table, map evidence and lesson history."""
        return {
            "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "words": self.words,
            "map": {
                "states": [{"id": s.id, "label": s.label} for s in self.shown.states],
                "edges": [
                    {
                        "source": e.source,
                        "target": e.target,
                        "label": e.label,
                        "tries": e.evidence.tries,
                        "successes": e.evidence.successes,
                        "status": e.evidence.status,
                    }
                    for e in self.shown.edges
                ],
            },
            "lessons": self.lessons,
        }

    def save(self, path: str | Path) -> None:
        """Write the merged knowledge file."""
        target = Path(path)
        target.write_text(
            json.dumps(self.to_json(), ensure_ascii=False, indent=2), encoding=ENCODING
        )

    @classmethod
    def load(cls, path: str | Path) -> "Knowledge":
        """Reload merged knowledge; missing file starts empty."""
        known = cls()
        raw_path = Path(path)
        if not raw_path.exists():
            return known
        raw = json.loads(raw_path.read_text(encoding=ENCODING))
        known.words = raw.get("words", {})
        known.lessons = raw.get("lessons", [])
        for saved in raw.get("map", {}).get("edges", []):
            edge = known.shown._edge(saved["source"], saved["target"], saved["label"])
            if edge is None:
                edge = Edge(saved["source"], saved["target"], saved["label"])
                known.shown.edges.append(edge)
            edge.evidence = Evidence(
                status=saved.get("status", "untested"),
                tries=saved.get("tries", 0),
                successes=saved.get("successes", 0),
            )
        return known


def load_personas(phrasebooks: str | Path) -> list[dict]:
    """Roles from the phrasebook file."""
    raw = json.loads(Path(phrasebooks).read_text(encoding=ENCODING))
    return raw["roles"]


def lesson_log(path: str | Path, result: SimResult) -> None:
    """Append one sim record (Holdmate's training history)."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "persona": result.persona,
        "misses": result.misses,
        "word": display(result.word),
        "matched": result.matched,
        "transferred": result.transferred,
        "served": result.served,
    }
    with open(path, "a", encoding=ENCODING) as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    """Run BFS lessons for one or all personas; save knowledge."""
    parser = argparse.ArgumentParser(description="Holdmate calls Agda by itself (BFS).")
    parser.add_argument("--phrasebooks", required=True)
    parser.add_argument("--lines", required=True)
    parser.add_argument("--knowledge", required=True)
    parser.add_argument("--lessons", required=True)
    parser.add_argument("--as", dest="persona", default="")
    parser.add_argument("--depth", type=int, default=MAX_MISSES)
    parser.add_argument("--speak", action="store_true")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args(argv)

    if args.depth < 0 or args.depth > MAX_MISSES:
        parser.error(f"--depth must be 0..{MAX_MISSES}")
    lines = load_indexed_lines(args.lines)
    ears = ReactiveRobot.from_phrasebooks(args.phrasebooks)
    agda = build_agda(lines, ears.respond)
    personas = load_personas(args.phrasebooks)
    if args.persona:
        personas = [r for r in personas if r["id"] == args.persona]
        if not personas:
            print(f"unknown persona: {args.persona}", file=sys.stderr)
            return 1
    knowledge = Knowledge() if args.fresh else Knowledge.load(args.knowledge)
    planned = [
        (role, list(dict.fromkeys([*role["vocabulary"], *PROBES])))
        for role in personas
    ]
    total = sum(len(candidates) * (args.depth + 1) for _, candidates in planned)
    print(f"plan: {len(planned)} lessons, up to {total} sims (depth 0..{args.depth})")
    try:
        for index, (role, candidates) in enumerate(planned, 1):
            print(f"lesson {index}/{len(planned)}: {role['id']} ({len(candidates)} words)")
            lesson = Lesson(role["id"], candidates, agda, knowledge,
                            max_misses=args.depth)
            summary = lesson.run(speak=args.speak)
            for sim in lesson.sims:
                lesson_log(args.lessons, sim)
            knowledge.add_lesson(summary)
            print(
                f"{role['id']}: {summary['sims']} sims, "
                f"{summary['transfers']} transfers, {summary['served']} served, "
                f"matched {len(summary['matched'])} words: "
                f"{', '.join(summary['matched']) or '-'}"
            )
    except KeyboardInterrupt:
        print("stopped early; saving what was learned so far")
    knowledge.save(args.knowledge)
    print(f"knowledge: {args.knowledge}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
