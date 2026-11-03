"""Intent normalizer PoC: exact -> alias -> normalizer -> miss ladder (#145).

Placement A from the LLM design: on keyword miss, map noisy STT onto the
closed persona vocab or abstain. HeuristicNormalizer is the offline
baseline; SparkNormalizer calls Muse Spark when configured (Monday key).
Never raises into the call path: any failure abstains to the ladder.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import sys
import time
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
    "Never invent keywords. Map ja/nej only for exactly that word. "
    "Return null for garbled or fragmentary utterances even when a "
    "keyword looks close; only map when the keyword or a clear "
    "paraphrase is present."
)


class NotConfiguredError(RuntimeError):
    """No Spark endpoint/key (set MODEL_API_KEY, like the helloworld)."""


DEFAULT_SPARK_URL = "https://api.meta.ai/v1/chat/completions"


class SparkNormalizer(Normalizer):
    """Muse Spark via an OpenAI-chat-compatible endpoint (hackathon
    partners speak this shape). Any error abstains to the ladder."""

    def __init__(
        self,
        endpoint: str = "",
        api_key: str = "",
        model: str = "",
        timeout: int = 20,
    ) -> None:
        self.endpoint = (
            endpoint
            or os.environ.get("SPARK_API_URL", "")
            or os.environ.get("MODEL_API_URL", "")
            or DEFAULT_SPARK_URL
        )
        self.api_key = (
            api_key
            or os.environ.get("SPARK_API_KEY", "")
            or os.environ.get("MODEL_API_KEY", "")
        )
        if not self.api_key:
            raise NotConfiguredError("set MODEL_API_KEY (or SPARK_API_KEY)")
        if urllib.parse.urlparse(self.endpoint).scheme != "https":
            raise NotConfiguredError("Spark endpoint must be https")
        self.model = (
            model
            or os.environ.get("SPARK_MODEL", "")
            or os.environ.get("MODEL_API_MODEL", "")
            or "muse-spark-1.3"  # Meta quickstart default 2026-11
        )
        self.timeout = timeout

    def _prompt(self, heard: str, vocab: list[str]) -> list[dict]:
        return [
            {"role": "system", "content": f"{SPARK_SYSTEM} Keywords: {vocab}"},
            {"role": "user", "content": normalize(heard)},
        ]

    def _provenance(self, heard: str, vocab: list[str], keyword, conf, ms: float) -> None:
        prompt = json.dumps(self._prompt(heard, vocab), ensure_ascii=False)
        log_provenance(
            {
                "model": self.model,
                "runtime": "spark-hosted",
                "endpoint": self.endpoint,
                "latency_ms": round(ms, 1),
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                "heard_sha256": hashlib.sha256(heard.encode()).hexdigest()[:16],
                "keyword": keyword,
                "confidence": conf,
            }
        )

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
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:  # nosec B310: https validated
                payload = json.load(res)
            content = payload["choices"][0]["message"]["content"]
            verdict = json.loads(content)
        except Exception as err:
            if os.environ.get("SPARK_DEBUG"):
                print(f"[spark-debug] request failed: {type(err).__name__}: {err}",
                      file=sys.stderr)
            return None, 0.0
        ms = (time.perf_counter() - t0) * 1000
        keyword = verdict.get("keyword")
        if keyword not in vocab:
            if os.environ.get("SPARK_DEBUG"):
                print(f"[spark-debug] out-of-vocab: {keyword!r} conf={verdict.get('confidence')}",
                      file=sys.stderr)
            self._provenance(heard, vocab, None, 0.0, ms)
            return None, 0.0
        try:
            conf = float(verdict.get("confidence", 0.0))
        except (TypeError, ValueError):
            conf = 0.0
        conf = min(1.0, max(0.0, conf))
        if conf < 0.8:  # low-confidence Spark maps abstain to the ladder
            self._provenance(heard, vocab, None, conf, ms)
            return None, 0.0
        self._provenance(heard, vocab, keyword, conf, ms)
        return keyword, conf


DEFAULT_OPENWEIGHT_URL = "http://127.0.0.1:11434/v1/chat/completions"
DEFAULT_OPENWEIGHT_MODEL = "meta-models/muse-spark-open-1026"
LOCALHOSTS = ("127.0.0.1", "localhost", "::1")


def log_provenance(event: dict) -> None:
    """Best-effort JSONL provenance row. Never raises."""
    try:
        path = os.environ.get("OPENWEIGHT_LOG", "data/provenance.jsonl")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


class OpenWeightNormalizer(Normalizer):
    """Muse Spark Open / Glimmer as a load-bearing intent stage (#171).

    Any OpenAI-chat-compatible endpoint: Ollama locally (default, no key)
    or a partner endpoint (Baseten/Modal/Fireworks) via OPENWEIGHT_URL +
    OPENWEIGHT_API_KEY. Same closed-vocab contract as Spark; every call
    appends a provenance row. Any error abstains to the ladder.
    """

    def __init__(
        self,
        endpoint: str = "",
        api_key: str | None = None,
        model: str = "",
        timeout: int = 30,
    ) -> None:
        self.endpoint = (
            endpoint
            or os.environ.get("OPENWEIGHT_URL", "")
            or DEFAULT_OPENWEIGHT_URL
        )
        host = urllib.parse.urlparse(self.endpoint).hostname or ""
        self.runtime = (
            "openweight-local" if host in LOCALHOSTS else "openweight-partner"
        )
        key = (
            api_key
            if api_key is not None
            else os.environ.get("OPENWEIGHT_API_KEY", "")
        )
        scheme = urllib.parse.urlparse(self.endpoint).scheme
        if self.runtime == "openweight-local":
            if scheme not in ("http", "https"):
                raise NotConfiguredError("OpenWeight local endpoint must be http(s)")
        else:
            if scheme != "https":
                raise NotConfiguredError("OpenWeight partner endpoint must be https")
            if not key:
                raise NotConfiguredError("set OPENWEIGHT_API_KEY for partner endpoint")
        self.api_key = key
        self.model = (
            model
            or os.environ.get("OPENWEIGHT_MODEL", "")
            or DEFAULT_OPENWEIGHT_MODEL
        )
        self.timeout = timeout

    def _prompt(self, heard: str, vocab: list[str]) -> list[dict]:
        return [
            {"role": "system", "content": f"{SPARK_SYSTEM} Keywords: {vocab}"},
            {"role": "user", "content": normalize(heard)},
        ]

    def _provenance(self, heard: str, vocab: list[str], keyword, conf, ms: float) -> None:
        prompt = json.dumps(self._prompt(heard, vocab), ensure_ascii=False)
        log_provenance(
            {
                "model": self.model,
                "runtime": self.runtime,
                "endpoint": self.endpoint,
                "latency_ms": round(ms, 1),
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()[:16],
                "heard_sha256": hashlib.sha256(heard.encode()).hexdigest()[:16],
                "keyword": keyword,
                "confidence": conf,
            }
        )

    def map(self, heard: str, vocab: list[str]) -> tuple[str | None, float]:
        clean = normalize(heard)
        if not clean or clean == SILENCE:
            return None, 0.0
        body = json.dumps(
            {"model": self.model, "messages": self._prompt(heard, vocab)}
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(self.endpoint, data=body, headers=headers)
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:  # nosec B310: scheme validated
                payload = json.load(res)
            content = payload["choices"][0]["message"]["content"]
            verdict = json.loads(content)
        except Exception as err:
            if os.environ.get("SPARK_DEBUG"):
                print(f"[openweight-debug] request failed: {type(err).__name__}: {err}",
                      file=sys.stderr)
            return None, 0.0
        ms = (time.perf_counter() - t0) * 1000
        keyword = verdict.get("keyword")
        if keyword not in vocab:
            self._provenance(heard, vocab, None, 0.0, ms)
            return None, 0.0
        try:
            conf = float(verdict.get("confidence", 0.0))
        except (TypeError, ValueError):
            conf = 0.0
        conf = min(1.0, max(0.0, conf))
        self._provenance(heard, vocab, keyword, conf, ms)
        return keyword, conf


def resolve_chain(heard: str, respond, normalizers, vocab: list[str]):
    """Chain exact match -> each (name, normalizer) -> abstain.

    Returns (keyword, conf, source) where source names the stage that hit.
    """
    try:
        _, matched = respond(heard)
    except Exception:
        matched = None
    if matched is not None:
        return matched, 1.0, "exact"
    clean = normalize(heard)
    if not clean or clean == SILENCE:
        return None, 0.0, "abstain"
    for name, normalizer in normalizers:
        try:
            keyword, conf = normalizer.map(heard, vocab)
        except Exception:
            continue
        if keyword is not None:
            return keyword, conf, name
    return None, 0.0, "abstain"


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
