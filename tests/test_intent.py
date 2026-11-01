"""Intent normalizer chain: exact -> normalizer -> abstain (#145)."""
import io
import json
import urllib.request

import pytest

from adaptive_ivr_agent.intent import (
    HeuristicNormalizer,
    NotConfiguredError,
    SparkNormalizer,
    resolve,
)

VOCAB = ["handläggare", "skriva in mig", "aktivitetsrapport", "vab"]


def exact_respond(heard):
    clean = heard.strip().lower()
    if clean in VOCAB:
        return f"You said {clean}.", clean
    return "Not understood.", None


def test_exact_match_never_consults_normalizer():
    class Raising:
        def map(self, heard, vocab):
            raise AssertionError("consulted on exact hit")

    assert resolve("handläggare", exact_respond, Raising(), VOCAB) == (
        "handläggare", 1.0, "exact")


def test_heuristic_rescues_substring_and_punct():
    norm = HeuristicNormalizer()
    assert resolve("Jag ska bli kopplad till en handläggare.",
                   exact_respond, norm, VOCAB)[0] == "handläggare"
    assert resolve("Skriva in mig?", exact_respond, norm, VOCAB)[0] == "skriva in mig"


def test_heuristic_abstains_on_garbage_and_silence():
    norm = HeuristicNormalizer()
    for heard in ["...", "", "   ", "(silence)", "Tack för att du kom till."]:
        assert resolve(heard, exact_respond, norm, VOCAB)[0] is None


def test_ja_nej_exact_only():
    norm = HeuristicNormalizer()
    vocab = [*VOCAB, "ja", "nej"]
    assert norm.map("Ja.", vocab)[0] == "ja"
    assert norm.map("Jag vill säga ja till allt.", vocab)[0] is None
    assert norm.map("Nej tack.", vocab)[0] is None


def test_resolve_never_raises():
    def boom(heard):
        raise RuntimeError("ears down")

    class Down:
        def map(self, heard, vocab):
            raise RuntimeError("llm down")

    assert resolve("x", boom, Down(), VOCAB) == (None, 0.0, "abstain")


def test_spark_requires_config(monkeypatch):
    monkeypatch.delenv("SPARK_API_URL", raising=False)
    monkeypatch.delenv("SPARK_API_KEY", raising=False)
    with pytest.raises(NotConfiguredError):
        SparkNormalizer()
    with pytest.raises(NotConfiguredError):
        SparkNormalizer(endpoint="http://x.test/v1", api_key="k")


def test_spark_parses_and_validates(monkeypatch):
    norm = SparkNormalizer(endpoint="https://x.test/v1", api_key="k")
    body = json.dumps(
        {"choices": [{"message": {"content": '{"keyword": "vab", "confidence": 0.8}'}}]}
    ).encode()

    class FakeRes:
        def __enter__(self):
            return io.BytesIO(body)

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: FakeRes())
    assert norm.map("ont i magen, vab?", VOCAB) == ("vab", 0.8)


def test_spark_rejects_unknown_keyword_and_errors(monkeypatch):
    norm = SparkNormalizer(endpoint="https://x.test/v1", api_key="k")
    body = json.dumps(
        {"choices": [{"message": {"content": '{"keyword": "umlaut", "confidence": 9}'}}]}
    ).encode()

    class FakeRes:
        def __enter__(self):
            return io.BytesIO(body)

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: FakeRes())
    assert norm.map("x", VOCAB) == (None, 0.0)

    def boom(req, timeout):
        raise TimeoutError("slow")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    assert norm.map("handläggare sökes", VOCAB) == (None, 0.0)
    assert "handläggare" in norm._prompt("x", VOCAB)[0]["content"]
