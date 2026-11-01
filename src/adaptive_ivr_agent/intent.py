"""Intent normalizer PoC: exact -> alias -> normalizer -> miss ladder (#145).

Placement A from the LLM design: on keyword miss, map noisy STT onto the
closed persona vocab or abstain. HeuristicNormalizer is the offline
baseline; SparkNormalizer calls Muse Spark when configured (Monday key).
Never raises into the call path: any failure abstains to the ladder.
"""
from __future__ import annotations

import difflib
import json
import os
import urllib.parse
import urllib.request

from adaptive_ivr_agent.talk import normalize

SILENCE = "(silence)"
EXACT_ONLY = ("ja", "nej")


class Normalizer:
    """Maps one heard utterance onto vocab; (None, 0.0) abstains."""

    def map(self, heard: str, vocab: list[str]) -> tuple[str | None, float]:
        raise NotImplementedError


class HeuristicNormalizer(Normalizer):
    """Offline baseline: exact, substring, then fuzzy close match."""

    # 0.75 keeps "Aktivitetsstöd." from misfiring to "aktivitetsrapport"
    # (eval adversarial); conjugations like "skriver in mig" stay misses
    # for the LLM to rescue on Monday.
    def __init__(self, cutoff: float = 0.75) -> None:
        self.cutoff = cutoff

    def map(self, heard: str, vocab: list[str]) -> tuple[str | None, float]:
        clean = normalize(heard).strip(" .!?…,:;\"'")
        if not clean or clean == SILENCE:
            return None, 0.0
        lowered = {v.lower(): v for v in vocab}
        if clean in EXACT_ONLY:
            hit = lowered.get(clean)
            return (hit, 1.0) if hit else (None, 0.0)
        if clean in lowered:
            return lowered[clean], 1.0
        for word in sorted(lowered, key=len, reverse=True):
            if len(word) >= 5 and word not in EXACT_ONLY and word in clean:
                return lowered[word], 0.9
        pool = [w for w in lowered if w not in EXACT_ONLY]
        best = difflib.get_close_matches(clean, pool, n=1, cutoff=self.cutoff)
        if not best:
            return None, 0.0
        score = difflib.SequenceMatcher(None, clean, best[0]).ratio()
        return lowered[best[0]], round(score, 3)


SPARK_SYSTEM = (
    "You map one Swedish IVR caller utterance to exactly one keyword "
    "from the list, or null if unclear. Output JSON "
    '{"keyword": str|null, "confidence": 0-1} and nothing else. '
    "Never invent keywords. Map ja/nej only for exactly that word."
)


class NotConfiguredError(RuntimeError):
    """No Spark endpoint/key (Monday brings both)."""


class SparkNormalizer(Normalizer):
    """Muse Spark via an OpenAI-chat-compatible endpoint (hackathon
    partners speak this shape). Any error abstains to the ladder."""

    def __init__(
        self,
        endpoint: str = "",
        api_key: str = "",
        model: str = "muse-spark",
        timeout: int = 3,
    ) -> None:
        self.endpoint = endpoint or os.environ.get("SPARK_API_URL", "")
        self.api_key = api_key or os.environ.get("SPARK_API_KEY", "")
        if not self.endpoint or not self.api_key:
            raise NotConfiguredError("set SPARK_API_URL + SPARK_API_KEY")
        if urllib.parse.urlparse(self.endpoint).scheme != "https":
            raise NotConfiguredError("SPARK_API_URL must be https")
        self.model = model
        self.timeout = timeout

    def _prompt(self, heard: str, vocab: list[str]) -> list[dict]:
        return [
            {"role": "system", "content": f"{SPARK_SYSTEM} Keywords: {vocab}"},
            {"role": "user", "content": normalize(heard)},
        ]

    def map(self, heard: str, vocab: list[str]) -> tuple[str | None, float]:
        clean = normalize(heard)
        if not clean or clean == SILENCE:
            return None, 0.0
        body = json.dumps(
            {"model": self.model, "messages": self._prompt(heard, vocab)}
        ).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            # nosec B310: endpoint scheme validated https in __init__
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                payload = json.load(res)
            content = payload["choices"][0]["message"]["content"]
            verdict = json.loads(content)
        except Exception:
            return None, 0.0
        keyword = verdict.get("keyword")
        if keyword not in vocab:
            return None, 0.0
        try:
            conf = float(verdict.get("confidence", 0.0))
        except (TypeError, ValueError):
            conf = 0.0
        return keyword, min(1.0, max(0.0, conf))


def resolve(heard: str, respond, normalizer: Normalizer, vocab: list[str]):
    """Chain exact match -> normalizer -> abstain. Returns (keyword, conf, source)."""
    try:
        _, matched = respond(heard)
    except Exception:
        matched = None
    if matched is not None:
        return matched, 1.0, "exact"
    clean = normalize(heard)
    if not clean or clean == SILENCE:
        return None, 0.0, "abstain"
    try:
        keyword, conf = normalizer.map(heard, vocab)
    except Exception:
        return None, 0.0, "abstain"
    if keyword is None:
        return None, 0.0, "abstain"
    return keyword, conf, "normalizer"
