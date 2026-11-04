#!/usr/bin/env python3
"""Intent eval PoC: rescue rate, abstain precision, no-regression (#145).

Runs resolve() over hand-labeled misses (real talk-misses rows), adversarial
must-abstain cases, and exact-vocab no-regression cases. Prints metrics;
exits nonzero on safety violations (wrong keyword on adversarial, or an
exact match resolving differently). Rescue rate is reported, not gated:
this run establishes the heuristic baseline for Monday's Spark compare.
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from adaptive_ivr_agent.intent import (  # noqa: E402
    HeuristicNormalizer,
    NotConfiguredError,
    OpenWeightNormalizer,
    SparkNormalizer,
    resolve,
)
from adaptive_ivr_agent.reactive import ReactiveRobot  # noqa: E402

PHRASEBOOKS = ROOT / "data" / "role-phrasebooks.json"

# (heard, expected keyword or None, adversarial?)
CASES = [
    # Real miss rows -> rescue (substring/exact-after-punct-strip).
    ("Jag ska bli kopplad till en handläggare.", "handläggare", False),
    ("Aktivitt skriver in mig i ett jobb.", "skriva in mig", False),
    ("Vilket yrke passar mig?", "vilket yrke passar mig", False),
    # Real miss rows -> abstain (not in closed vocab / garbage).
    ("Tack för att du kom till.", None, False),
    ("Välkomna!", None, False),
    ("Kan man få jobbcoach?", None, False),
    ("Trapport eller söka arbete?", None, False),
    ("Vi ställer en fråga om det som man startar företag.", None, False),
    # Adversarial: must abstain, never mis-transfer.
    ("Aktivitetsstöd.", None, True),  # benefit, not aktivitetsrapport
    ("eller aktivitetsstörd.", None, True),
    ("påanmäla", None, True),  # misheard topic, not "skriv in dig"
    ("Ja.", None, True),  # ladder owns ja/nej; ja not in vocab
    ("Häs hjälp med att söka arbete.", None, True),  # phrase not in vocab
    # Exact vocab -> exact source, normalizer never consulted.
    ("aktivitetsrapport", "aktivitetsrapport", False),
    ("vab", "vab", False),
    ("handläggare", "handläggare", False),
]


def main() -> int:
    ears = ReactiveRobot.from_phrasebooks(str(PHRASEBOOKS))
    vocab = sorted({w for r in ears.roles for w in r.get("vocabulary", [])}) \
        if hasattr(ears, "roles") else []
    if not vocab:
        import json
        raw = json.loads(PHRASEBOOKS.read_text(encoding="utf-8"))
        vocab = sorted({w for r in raw["roles"] for w in r["vocabulary"]})
    if "--live" in sys.argv[1:]:
        if "--debug" in sys.argv[1:]:
            import os

            os.environ["SPARK_DEBUG"] = "1"
        args = sys.argv[1:]
        if "--effort" in args:
            import os

            os.environ["SPARK_EFFORT"] = args[args.index("--effort") + 1]
        try:
            normalizer = SparkNormalizer(stage="eval")
        except NotConfiguredError as err:
            print(f"live needs configuration: {err}")
            return 2
        print(f"live: model={normalizer.model} effort={normalizer.effort} "
              f"endpoint={normalizer.endpoint} (max {len(CASES)} calls)")
    elif "--openweight" in sys.argv[1:]:
        try:
            normalizer = OpenWeightNormalizer(stage="eval")
        except NotConfiguredError as err:
            print(f"openweight needs configuration: {err}")
            return 2
        print(f"openweight: model={normalizer.model} runtime={normalizer.runtime} "
              f"endpoint={normalizer.endpoint} (max {len(CASES)} calls)")
    else:
        normalizer = HeuristicNormalizer()
    rescue_ok = rescue_n = abstain_ok = abstain_n = exact_ok = exact_n = 0
    adversarial_fail = []
    latencies = []
    for heard, expected, adversarial in CASES:
        t0 = time.perf_counter()
        keyword, conf, source = resolve(heard, ears.respond, normalizer, vocab)
        latencies.append((time.perf_counter() - t0) * 1000)
        mark = "ok" if keyword == expected else "MISS"
        if expected is None:
            abstain_n += 1
            abstain_ok += keyword is None
            if adversarial and keyword is not None:
                adversarial_fail.append((heard, keyword))
        elif source == "exact":
            exact_n += 1
            exact_ok += keyword == expected
        else:
            rescue_n += 1
            rescue_ok += keyword == expected
        print(f"[{mark}] {heard[:50]!r:54} -> {keyword!r} ({source})")
    latencies.sort()
    p95 = latencies[max(0, int(len(latencies) * 0.95) - 1)]
    print(f"rescue: {rescue_ok}/{rescue_n} abstain: {abstain_ok}/{abstain_n} "
          f"exact: {exact_ok}/{exact_n} p95: {p95:.1f}ms")
    if adversarial_fail or exact_ok != exact_n:
        print(f"SAFETY FAIL: adversarial={adversarial_fail} exact={exact_ok}/{exact_n}")
        return 1
    print("SAFETY OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
