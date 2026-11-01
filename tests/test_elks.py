"""46elks client prep: validation, billing math, mocked HTTP (#131)."""
import io
import json

import pytest

from adaptive_ivr_agent.elks import (
    ElksClient,
    NotConfiguredError,
    estimate_cost_sek,
    parse_hangup,
    valid_e164,
)


def test_requires_credentials(monkeypatch):
    monkeypatch.delenv("ELKS_USER", raising=False)
    monkeypatch.delenv("ELKS_PASS", raising=False)
    with pytest.raises(NotConfiguredError):
        ElksClient()


def test_validates_numbers():
    assert valid_e164("+46701234567")
    assert not valid_e164("0701234567")
    assert not valid_e164("")


def test_estimate_cost_sek():
    assert estimate_cost_sek(1) == 0.30
    assert estimate_cost_sek(10) == 3.00


def test_place_call_posts_expected_fields(monkeypatch):
    import urllib.request

    seen = {}

    class FakeRes:
        def __enter__(self):
            return io.BytesIO(b'{"id": "call-1", "state": "ongoing"}')

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout):
        seen["url"] = req.full_url
        seen["auth"] = req.headers.get("Authorization", "")
        seen["body"] = req.data.decode()
        return FakeRes()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    client = ElksClient(user="u", password="p")
    assert client.place_call("+46701111111", "+46702222222")["id"] == "call-1"
    assert seen["url"] == "https://api.46elks.com/a1/calls"
    assert seen["auth"].startswith("Basic ")
    assert "recordcall=true" in seen["body"].replace("%20", " ")
    with pytest.raises(ValueError):
        client.place_call("070", "+46702222222")


def test_parse_hangup_extracts_logged_fields():
    payload = {"id": "c", "from": "+1", "to": "+2", "created": "t",
               "state": "completed", "duration": "61", "extra": 1}
    assert parse_hangup(payload) == {
        "id": "c", "from": "+1", "to": "+2", "created": "t",
        "state": "completed", "duration": "61",
    }
