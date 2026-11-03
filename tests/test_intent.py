"""Intent normalizer chain: exact -> normalizer -> abstain (#145)."""
import io
import json
import urllib.request

import pytest

from adaptive_ivr_agent.intent import (
    HeuristicNormalizer,
    NotConfiguredError,
    OpenWeightNormalizer,
    SparkNormalizer,
    resolve,
    resolve_chain,
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


def test_spark_parses_and_validates(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENWEIGHT_LOG", str(tmp_path / "prov.jsonl"))
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


def test_spark_rejects_unknown_keyword_and_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENWEIGHT_LOG", str(tmp_path / "prov.jsonl"))
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


def test_spark_low_confidence_abstains(monkeypatch, tmp_path):
    log = tmp_path / "prov.jsonl"
    monkeypatch.setenv("OPENWEIGHT_LOG", str(log))
    norm = SparkNormalizer(endpoint="https://x.test/v1", api_key="k")
    body = json.dumps(
        {"choices": [{"message": {"content": '{"keyword": "vab", "confidence": 0.7}'}}]}
    ).encode()

    class FakeRes:
        def __enter__(self):
            return io.BytesIO(body)

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: FakeRes())
    assert norm.map("vabbb?", VOCAB) == (None, 0.0)
    row = json.loads(log.read_text(encoding="utf-8").strip())
    assert row["keyword"] is None  # gated map still leaves a trace


def test_spark_sends_reasoning_effort(monkeypatch, tmp_path):
    log = tmp_path / "prov.jsonl"
    monkeypatch.setenv("OPENWEIGHT_LOG", str(log))
    monkeypatch.delenv("SPARK_EFFORT", raising=False)
    monkeypatch.delenv("MODEL_API_EFFORT", raising=False)
    norm = SparkNormalizer(endpoint="https://x.test/v1", api_key="k")
    assert norm.effort == "medium"
    body = json.dumps(
        {"choices": [{"message": {"content": '{"keyword": "vab", "confidence": 1.0}'}}]}
    ).encode()
    seen = {}

    class FakeRes:
        def __enter__(self):
            return io.BytesIO(body)

        def __exit__(self, *a):
            return False

    def capture(req, timeout):
        seen.update(json.loads(req.data.decode("utf-8")))
        return FakeRes()

    monkeypatch.setattr(urllib.request, "urlopen", capture)
    assert norm.map("vab?", VOCAB) == ("vab", 1.0)
    assert seen["reasoning_effort"] == "medium"
    assert seen["temperature"] == 0
    monkeypatch.setenv("SPARK_EFFORT", "high")
    assert SparkNormalizer(endpoint="https://x.test/v1", api_key="k").effort == "high"


def test_openweight_localhost_needs_no_key(monkeypatch):
    monkeypatch.delenv("OPENWEIGHT_URL", raising=False)
    monkeypatch.delenv("OPENWEIGHT_API_KEY", raising=False)
    norm = OpenWeightNormalizer()
    assert norm.runtime == "openweight-local"
    assert norm.model == "meta-models/muse-spark-open-1026"


def test_openweight_partner_requires_https_and_key():
    with pytest.raises(NotConfiguredError):
        OpenWeightNormalizer(endpoint="http://partner.test/v1", api_key="k")
    with pytest.raises(NotConfiguredError):
        OpenWeightNormalizer(endpoint="https://partner.test/v1", api_key="")
    norm = OpenWeightNormalizer(endpoint="https://partner.test/v1", api_key="k")
    assert norm.runtime == "openweight-partner"


def test_openweight_logs_provenance(monkeypatch, tmp_path):
    log = tmp_path / "prov.jsonl"
    monkeypatch.setenv("OPENWEIGHT_LOG", str(log))
    norm = OpenWeightNormalizer(endpoint="http://127.0.0.1:11434/v1")
    body = json.dumps(
        {"choices": [{"message": {"content": '{"keyword": "vab", "confidence": 0.7}'}}]}
    ).encode()

    class FakeRes:
        def __enter__(self):
            return io.BytesIO(body)

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: FakeRes())
    assert norm.map("ont i magen, vab?", VOCAB) == ("vab", 0.7)
    row = json.loads(log.read_text(encoding="utf-8").strip())
    assert row["runtime"] == "openweight-local"
    assert row["keyword"] == "vab"
    assert row["confidence"] == 0.7
    assert len(row["prompt_sha256"]) == 16
    assert "latency_ms" in row


def test_spark_logs_provenance(monkeypatch, tmp_path):
    log = tmp_path / "prov.jsonl"
    monkeypatch.setenv("OPENWEIGHT_LOG", str(log))
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
    row = json.loads(log.read_text(encoding="utf-8").strip())
    assert row["runtime"] == "spark-hosted"
    assert row["model"] == "muse-spark-1.3"  # Meta quickstart default
    assert row["keyword"] == "vab"


def test_resolve_chain_names_stage():
    class First:
        def map(self, heard, vocab):
            return None, 0.0

    class Second:
        def map(self, heard, vocab):
            return "vab", 0.6

    assert resolve_chain("x", exact_respond, [("a", First()), ("b", Second())], VOCAB) == (
        "vab", 0.6, "b")
    assert resolve_chain("handläggare", exact_respond, [("b", Second())], VOCAB) == (
        "handläggare", 1.0, "exact")
