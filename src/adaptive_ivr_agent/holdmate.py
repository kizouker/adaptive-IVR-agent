"""Holdmate calls by itself: BFS lessons against the practice robot (S2).

Rickard stays silent. For each persona, Holdmate systematically tries every
alternative utterance level by level (miss counts 0, 1, 2), runs each path to
transfer, identification, queue and handover, and lands what it learns in the
word table plus the menu map evidence. Headless and fast by default; --speak
says every turn aloud (Oskar calls, Alva answers).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from adaptive_ivr_agent.intent import SparkFallback, maybe_spark_normalizer
from adaptive_ivr_agent.live_view import (
    SPECIAL_PROBES,
    LiveCall,
    build_coverage,
    build_live_board,
    line_translations,
    translate_robot,
)
from adaptive_ivr_agent.menu_map import (
    AF_ROKSOLANA_STATES,
    Edge,
    Evidence,
    MenuMap,
)
from adaptive_ivr_agent.reactive import ReactiveRobot
from adaptive_ivr_agent.robot import load_indexed_lines
from adaptive_ivr_agent.talk import RoksolanaCall

ENCODING = "utf-8"
CALLER_VOICE = "Oskar"
ROKSOLANA_VOICE = "Alva"
MAX_MISSES = 2
FIXED_PLACE = 3
PROBES = list(SPECIAL_PROBES)
SILENCE_LABEL = "(silence)"


def display(word: str) -> str:
    """Printable form; the empty probe is silence."""
    return word if word else SILENCE_LABEL


def _colors() -> bool:
    """ANSI colors when a human watches: a tty, or forced for the pager."""
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty() or os.environ.get("HOLDEMATE_COLOR") == "1"


def _paint(code: str, text: str) -> str:
    if not _colors():
        return text
    return f"\x1b[{code}m{text}\x1b[0m"


def bold(text: str) -> str:
    """Bold on a terminal, plain in tests and files."""
    return _paint("1", text)


def italic(text: str) -> str:
    """Italics on a terminal, plain in tests and files."""
    return _paint("3", text)


def green(text: str) -> str:
    """Green on a terminal, plain in tests and files."""
    return _paint("32", text)


def red(text: str) -> str:
    """Red on a terminal, plain in tests and files."""
    return _paint("31", text)


def dim(text: str) -> str:
    """Dim on a terminal, plain in tests and files."""
    return _paint("2", text)


def wintitle(text: str) -> None:
    """Terminal window title follows the lessons (silent without a tty)."""
    try:
        with open("/dev/tty", "w", encoding=ENCODING) as tty:
            tty.write(f"\x1b]0;Holdmate: {text}\x07")
    except OSError:
        pass


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
    exchanges: tuple = ()


class Exchange(NamedTuple):
    """One board turn inside a sim: who said what, and the state after."""

    caller: str
    robot: str
    matched: bool
    state: str
    queue_place: int | None = None
    spark: dict | None = None


#: Recorded English line set for English lessons (#238): welcome menu,
#: sub-menu, SMS offer, identification, queue, place number and handover.
ENGLISH_LESSON_LINE_IDS = ("L17", "L18", "L31", "L32", "L35", "L36", "L37")


def build_roksolana(lines: dict[str, str], respond, busy: bool = False,
                    lang: str = "sv") -> RoksolanaCall:
    """Scripted Roksolana with the recorded lines; fixed queue place for lessons.

    lang="en" speaks the recorded English line set (welcome menu, sub-menu,
    SMS offer, identification, queue, handover) and takes yes/no answers;
    Swedish stays the default. There is no recorded English busy-day line,
    so English lessons open with the English menu either way.
    """
    if lang == "en":
        return RoksolanaCall(
            opening=lines["L17"],
            examples=lines["L18"],
            yesno=lines["L31"],
            yesno_reprompt=lines["L31"],
            transfer=lines["L37"],
            identify_line=lines["L32"],
            identified_line=lines["L38"],
            failed_line=lines["L34"],
            served_line=lines["L37"],
            queue_line=lines["L35"],
            place_template=lines["L36"],
            respond=respond,
            queue_place=lambda: FIXED_PLACE,
            survey_line=lines["L15"],
            survey_done=lines["L16"],
            english_menu=lines["L17"],
            yesno_words=("yes", "no"),
        )
    welcome = lines["L44"] if busy else lines["L01"]
    opening = welcome if busy else f"{welcome} {lines['L02']}"
    return RoksolanaCall(
        opening=opening,
        examples=lines["L03"],
        yesno=lines["L22"],
        yesno_reprompt=lines["L41"],
        transfer=lines["L19"],
        identify_line=f"{lines['L43']} {lines['L09']}",
        identified_line=lines["L11"],
        failed_line=lines["L12"],
        served_line=lines["L30"],
        queue_line=lines["L13"],
        place_template=lines["L29"],
        respond=respond,
        queue_place=lambda: FIXED_PLACE,
        survey_line=lines["L15"],
        survey_done=lines["L16"],
        english_menu=lines["L17"],
    )


def run_call(
    roksolana: RoksolanaCall, word: str, misses: int, spark_fallback=None
) -> tuple[SimResult, list[str], list[Exchange]]:
    """Say WORD at MISS_COUNT misses; on transfer run to handover.

    Returns the result, the turns said, and board exchanges with states.
    SPARK_FALLBACK (a SparkFallback, #205) donates its last rescue to the
    first exchange so the board can badge it; None keeps the sim keyless.
    """
    turns = [f"YOU: {display(word)}"]
    answer = roksolana.reply_to(word, misses)
    turns.append(f"ROKSOLANA: {answer.reply}")
    transferred = answer.identify or answer.done
    first_state = "transfer" if transferred else MISS_STATE.get(answer.misses, "yes_no")
    spark = spark_fallback.last if spark_fallback is not None else None
    exchanges = [
        Exchange(display(word), answer.reply, answer.matched is not None,
                 first_state, spark=spark)
    ]
    served = False
    if answer.identify:
        entered = roksolana.after_identified(answer.misses)
        turns.append(f"ROKSOLANA: {entered.reply}")
        exchanges.append(Exchange("", entered.reply, False, "queue", entered.queue_place))
        place = entered.queue_place or 0
        while place > 0:
            tick = roksolana.queue_tick(place, answer.misses)
            turns.append(f"ROKSOLANA: {tick.reply}")
            exchanges.append(Exchange("", tick.reply, False, "queue", tick.queue_place))
            served = tick.done
            place = tick.queue_place or 0
        if served:
            survey = roksolana.after_served(answer.misses)
            turns.append(f"ROKSOLANA: {survey.reply}")
            exchanges.append(Exchange("1", survey.reply, False, "survey"))
    return (
        SimResult("", misses, word, [], answer.matched, transferred, served,
                  tuple(exchanges)),
        turns,
        exchanges,
    )


class Lesson:
    """BFS exploration for one persona; learning accumulates in knowledge."""

    def __init__(
        self,
        persona_id: str,
        candidates: list[str],
        roksolana: RoksolanaCall,
        knowledge: "Knowledge",
        max_misses: int = MAX_MISSES,
        spark_fallback=None,
    ) -> None:
        self.persona_id = persona_id
        self.candidates = candidates
        self.roksolana = roksolana
        self.knowledge = knowledge
        self.max_misses = max_misses
        self.spark_fallback = spark_fallback
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
                result, turns, _ = run_call(self.roksolana, word, misses,
                                            self.spark_fallback)
                result = result._replace(persona=self.persona_id, path=[*path, word])
                self.sims.append(result)
                self.knowledge.observe(result)
                mark = green("✓") if result.transferred else red("✗")
                state = MISS_STATE[misses].replace("_", " ")
                outcome = "transfer" if result.transferred else "miss"
                said = italic(display(word))
                print(f"  {mark} {said} → {bold(outcome)} {dim(f'({state})')}",
                      flush=True)
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


def _wrap_width() -> int:
    """Dialogue width: the terminal when watched, 100 in pipes and files."""
    try:
        if sys.stdout.isatty():
            return shutil.get_terminal_size().columns
    except OSError:
        pass
    return 100


def _dialogue(tag_painted: str, tag_plain: str, said: str, width: int) -> str:
    """One wrapped dialogue turn; paint stays out of the width math."""
    lead = f"    {tag_plain} "
    rows = textwrap.wrap(said, width=width - len(lead)) or [""]
    first = f"    {tag_painted} {rows[0]}"
    rest = [" " * len(lead) + cont for cont in rows[1:]]
    return "\n".join([first, *rest])


def speak_turns(turns: list[str]) -> None:
    """Say one call aloud; Ctrl-C stops at once instead of trailing off."""
    width = _wrap_width()
    for line in turns:
        said = line.split(": ", 1)[1]
        if line.startswith("YOU:"):
            print(_dialogue(bold("You:"), "You:", said, width))
            voice = CALLER_VOICE
        else:
            print(_dialogue(dim("Roksolana:"), "Roksolana:", said, width))
            voice = ROKSOLANA_VOICE
        proc = subprocess.Popen(["say", "-v", voice, said])
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            raise
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, "say")
    print()


class Knowledge:
    """Word table + map evidence, merged across runs and saved as JSON."""

    def __init__(self) -> None:
        self.words: dict[str, dict] = {}
        self.lessons: list[dict] = []
        self.shown = MenuMap.af_roksolana()

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
                edge = Edge(saved["source"], saved["target"], saved["label"],
                            saved.get("label_en", ""))
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


def lesson_call(role: dict, lesson: Lesson, translations: dict) -> LiveCall:
    """One lesson as a board call: every sim exchange becomes a turn."""
    call = LiveCall(
        persona=role["id"],
        label=role["label"],
        errand=role["errand"],
        errand_en=role.get("errand_en"),
        robot_name="AF Roksolana (lesson)",
    )
    for sim in lesson.sims:
        for exchange in sim.exchanges:
            call.add_turn(exchange.caller, exchange.robot, exchange.matched,
                          exchange.state,
                          robot_en=translate_robot(exchange.robot, translations),
                          queue_place=exchange.queue_place,
                          spark=exchange.spark)
    return call


def write_lesson_board(path: str | Path, calls: list[LiveCall],
                       knowledge: "Knowledge", roles: list) -> None:
    """Board state: lesson calls plus run log, word table and coverage."""
    board = build_live_board(calls)
    board["lessons"] = knowledge.lessons
    board["words"] = {
        word: {"tries": entry["tries"], "transfers": entry["transfers"]}
        for word, entry in knowledge.words.items()
    }
    board["coverage"] = build_coverage(roles, knowledge.words)
    Path(path).write_text(json.dumps(board, ensure_ascii=False), encoding=ENCODING)


def main(argv: list[str] | None = None) -> int:
    """Run BFS lessons for one or all personas; save knowledge."""
    parser = argparse.ArgumentParser(description="Holdmate calls Roksolana by itself (BFS).")
    parser.add_argument("--phrasebooks", required=True)
    parser.add_argument("--lines", required=True)
    parser.add_argument("--knowledge", required=True)
    parser.add_argument("--lessons", required=True)
    parser.add_argument("--as", dest="persona", default="")
    parser.add_argument("--depth", type=int, default=MAX_MISSES)
    parser.add_argument("--lang", default="sv", choices=("sv", "en"),
                        help="lesson language: sv (default) or en "
                             "(recorded English lines + English vocab, #238)")
    parser.add_argument("--speak", action="store_true")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--board-out", default="")
    parser.add_argument("--spark", action="store_true",
                        help="rescue word-step misses with one Muse Spark call (#205)")
    args = parser.parse_args(argv)

    if args.depth < 0 or args.depth > MAX_MISSES:
        parser.error(f"--depth must be 0..{MAX_MISSES}")
    lines = load_indexed_lines(args.lines, lang=args.lang)
    translations = line_translations(args.lines)
    ears = ReactiveRobot.from_phrasebooks(args.phrasebooks, lang=args.lang)
    all_roles = load_personas(args.phrasebooks)

    def lesson_vocab(role: dict) -> list[str]:
        """Persona words in the lesson language (English falls back to Swedish)."""
        if args.lang == "en":
            return list(role.get("vocabulary_en") or role["vocabulary"])
        return list(role["vocabulary"])

    spark_fallback = None
    if args.spark:
        vocab = list(dict.fromkeys(
            word for role in all_roles for word in lesson_vocab(role)))
        normalizer = maybe_spark_normalizer(True)
        if normalizer is None:
            print("spark: no key, fallback skipped (keyless run)")
        else:
            spark_fallback = SparkFallback(ears.respond, normalizer, vocab)
    roksolana = build_roksolana(lines, spark_fallback.respond if spark_fallback else ears.respond,
                                lang=args.lang)
    personas = all_roles
    if args.persona:
        personas = [r for r in all_roles if r["id"] == args.persona]
        if not personas:
            print(f"unknown persona: {args.persona}", file=sys.stderr)
            return 1
    knowledge = Knowledge() if args.fresh else Knowledge.load(args.knowledge)
    planned = [
        (role, list(dict.fromkeys([*lesson_vocab(role), *PROBES])))
        for role in personas
    ]
    total = sum(len(candidates) * (args.depth + 1) for _, candidates in planned)
    print(bold(f"plan: {len(planned)} lessons, up to {total} sims (depth 0..{args.depth})"))
    live_calls: list[LiveCall] = []
    try:
        for index, (role, candidates) in enumerate(planned, 1):
            print(bold(f"lesson {index}/{len(planned)}: {role['id']} ({len(candidates)} words)"))
            wintitle(f"lesson {index}/{len(planned)}: {role['id']}")
            lesson = Lesson(role["id"], candidates, roksolana, knowledge,
                            max_misses=args.depth, spark_fallback=spark_fallback)
            summary = lesson.run(speak=args.speak)
            for sim in lesson.sims:
                lesson_log(args.lessons, sim)
            knowledge.add_lesson(summary)
            words = ", ".join(summary["matched"]) or "-"
            print(
                f"{bold(role['id'])}: {summary['sims']} sims, "
                f"{summary['transfers']} transfers, {summary['served']} served, "
                f"matched {len(summary['matched'])} words: {italic(words)}"
            )
            if args.board_out:
                live_calls.append(lesson_call(role, lesson, translations))
                coverage_roles = all_roles
                if args.lang == "en":
                    coverage_roles = [
                        {**r, "vocabulary": lesson_vocab(r)} for r in all_roles
                    ]
                write_lesson_board(args.board_out, live_calls, knowledge, coverage_roles)
    except KeyboardInterrupt:
        print("stopped early; saving what was learned so far")
    except BrokenPipeError:
        pass  # pager quit early; save below what was learned so far
    knowledge.save(args.knowledge)
    try:
        print(f"knowledge: {args.knowledge}")
    except BrokenPipeError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
