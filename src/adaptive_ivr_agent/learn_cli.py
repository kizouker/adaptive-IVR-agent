"""Interactive review driver for sh/learn-words.sh (thin glue over learn.review)."""

import json
import os
import sys
from collections.abc import Callable

from adaptive_ivr_agent.learn import known_words, pending_misses, read_misses, review

ENCODING = "utf-8"


def ask_factory(known: set[str]) -> Callable[[str], str | None]:
    """Prompt for one utterance. Returns a keyword, "" to skip, None to quit."""

    def ask(heard: str) -> str | None:
        print(f'\nHeard: "{heard}"')
        while True:
            try:
                answer = input("Keyword (Enter=skip, q=quit): ")
            except EOFError:
                return None
            word = answer.strip().lower()
            if word == "q":
                return None
            if word == "":
                return ""
            if word in known:
                return word
            try:
                again = input(f"'{word}' is not a known word. Use anyway? (y/n): ")
            except EOFError:
                return None
            if again.strip().lower() == "y":
                return word

    return ask


def main() -> int:
    """Review pending misses from env files; save approved aliases."""
    miss_file = os.environ["TALK_MISS_FILE"]
    learned_file = os.environ["TALK_LEARNED_FILE"]
    known = known_words(os.environ["TALK_PHRASEBOOKS"])
    with open(learned_file, encoding=ENCODING) as handle:
        learned = json.load(handle)
    pending = pending_misses(read_misses(miss_file), learned)
    learned.update(review(pending, ask_factory(known)))
    with open(learned_file, "w", encoding=ENCODING) as handle:
        json.dump(learned, handle, ensure_ascii=False, indent=2)
    print(f"Saved {len(learned)} reviewed utterance(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
