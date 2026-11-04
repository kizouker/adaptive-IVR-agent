"""Tests for the audio duplex core (T1) + BlackHole transport (T3).

Headless: local transport loopback, synth TTS fallback, mocked devices.
Hardware (tel: dial, BlackHole capture) is verified on Rickard's Mac.
"""
import time
import wave
from pathlib import Path

import pytest

from adaptive_ivr_agent.audio import (
    BLACKHOLE_DEVICE,
    FRAME_BYTES,
    AudioConfigError,
    DeviceBusyError,
    DeviceNotFoundError,
    UnknownSessionError,
    audio_health,
    call_status,
    close_session,
    dial,
    hangup,
    open_session,
    poll_inbound,
    push_outbound,
    rec_start,
    rec_status,
    rec_stop,
    say_text,
    send_dtmf,
    transcribe_inbound,
)

E164 = "+46701234567"


@pytest.fixture(autouse=True)
def _isolated_out_dir(tmp_path, monkeypatch):
    import adaptive_ivr_agent.audio as mod

    monkeypatch.setattr(mod, "OUT_DIR", tmp_path / "audio")


@pytest.fixture
def session():
    owner = open_session({"transport": "local"})
    yield owner
    close_session(owner.session_id)


@pytest.fixture
def call(session):
    info = dial(session.session_id, E164)
    return session.session_id, info["call_id"]


def test_dial_loopback_goes_active(call):
    session_id, call_id = call
    assert call_status(session_id, call_id)["state"] == "active"


def test_dial_rejects_non_e164(session):
    with pytest.raises(ValueError):
        dial(session.session_id, "123")


def test_say_text_echoes_on_loopback_fast(call):
    session_id, call_id = call
    started = time.time()
    result = say_text(session_id, call_id, "hej")
    assert result["bytes_sent"] > 0
    frames = poll_inbound(session_id, call_id)
    assert frames, "loopback must echo outbound audio"
    assert all(len(frame.pcm) == FRAME_BYTES for frame in frames)
    assert time.time() - started < 2.0


def test_rec_produces_playable_wavs(call, tmp_path):
    session_id, call_id = call
    rec = rec_start(session_id, call_id, path=str(tmp_path / "clip"))
    assert rec_status(session_id, call_id)["recording"] is True
    say_text(session_id, call_id, "recording check one two")
    out = rec_stop(session_id, rec["rec_id"])
    for key in ("path_mix", "path_in", "path_out"):
        assert Path(out[key]).exists()
        with wave.open(out[key], "rb") as handle:
            assert handle.getnframes() > 0
            assert handle.getframerate() == 16000


def test_rec_twice_is_busy(call):
    session_id, call_id = call
    first = rec_start(session_id, call_id)
    with pytest.raises(DeviceBusyError):
        rec_start(session_id, call_id)
    rec_stop(session_id, first["rec_id"])


def test_hangup_record_and_idempotent_second(call):
    session_id, call_id = call
    first = hangup(session_id, call_id)
    assert first["state"] == "ended"
    assert first["duration_s"] >= 0.0
    second = hangup(session_id, call_id)
    assert second["state"] == "ended"


def test_send_dtmf_zero_produces_frames(call):
    session_id, call_id = call
    send_dtmf(session_id, call_id, "0")
    frames = poll_inbound(session_id, call_id)
    assert len(frames) >= 2  # tone + gap


def test_send_dtmf_rejects_letters(call):
    session_id, call_id = call
    with pytest.raises(ValueError):
        send_dtmf(session_id, call_id, "abc")


def test_transcribe_stub_is_honest_silence(call):
    session_id, call_id = call
    result = transcribe_inbound(session_id, call_id)
    assert result == {"text": "(silence)", "confidence": 0.0,
                      "source": "stub"}


def test_unknown_session_raises():
    with pytest.raises(UnknownSessionError):
        audio_health("nope")


def test_unknown_transport_rejected():
    with pytest.raises(AudioConfigError):
        open_session({"transport": "pigeon"})


def test_health_shape_local(session):
    health = audio_health(session.session_id)
    assert health["transport_ok"] is True
    assert health["tts_ok"] is True
    assert health["stt_ok"] is False  # T5 pending, stub only


def test_blackhole_missing_device_helpful(monkeypatch):
    import adaptive_ivr_agent.audio as mod

    monkeypatch.setattr(mod, "_device_present", lambda name: False)
    monkeypatch.setattr(mod.shutil, "which", lambda name: "/usr/bin/" + name)
    owner = open_session({"transport": "blackhole"})
    monkeypatch.setattr(mod, "_blackhole_dial", lambda number: None)
    info = dial(owner.session_id, E164)
    with pytest.raises(DeviceNotFoundError, match="BlackHole"):
        poll_inbound(owner.session_id, info["call_id"])
    close_session(owner.session_id)


def test_blackhole_reports_no_device_in_health(monkeypatch):
    import adaptive_ivr_agent.audio as mod

    monkeypatch.setattr(mod, "_device_present", lambda name: False)
    owner = open_session({"transport": "blackhole"})
    assert audio_health(owner.session_id)["transport_ok"] is False
    close_session(owner.session_id)


# ------------------------------------------------- 46elks transport (T4)


@pytest.fixture()
def _elks_env(monkeypatch):
    import adaptive_ivr_agent.audio as mod

    monkeypatch.setenv("ELKS_API_USER", "user")
    monkeypatch.setenv("ELKS_API_PASS", "pass")
    monkeypatch.setenv("ELKS_FROM", "+46707654321")
    monkeypatch.setenv("ELKS_MAX_MINUTES", "10")
    monkeypatch.setattr(mod, "_ELKS_BILLED_MIN", 0)
    mod._ELKS_LIVE.clear()
    return mod


def _fake_client(monkeypatch, mod, calls):
    class FakeClient:
        def place_call(self, **kwargs):
            calls.append(kwargs)
            return {"id": "elks-1"}

    monkeypatch.setattr(mod, "ElksClient", FakeClient)


def test_elks_dial_sends_voice_start(_elks_env, monkeypatch):
    mod = _elks_env
    calls = []
    _fake_client(monkeypatch, mod, calls)
    owner = open_session({"transport": "elks"})
    info = dial(owner.session_id, E164, greeting="hej hej")
    assert info["state"] == "dialing"  # no answer signal without webhook
    assert info["elks_id"] == "elks-1"
    assert calls[0]["voice_start"] == "hej hej"
    assert calls[0]["recordcall"] == "true"
    close_session(owner.session_id)


def test_elks_single_call_guard(_elks_env, monkeypatch):
    mod = _elks_env
    _fake_client(monkeypatch, mod, [])
    owner = open_session({"transport": "elks"})
    dial(owner.session_id, E164)
    with pytest.raises(DeviceBusyError, match="one 46elks call"):
        dial(owner.session_id, E164)
    close_session(owner.session_id)


def test_elks_budget_guard(_elks_env, monkeypatch):
    mod = _elks_env
    _fake_client(monkeypatch, mod, [])
    monkeypatch.setattr(mod, "_ELKS_BILLED_MIN", 10)
    owner = open_session({"transport": "elks"})
    with pytest.raises(DeviceBusyError, match="budget spent"):
        dial(owner.session_id, E164)
    close_session(owner.session_id)


def test_elks_hangup_bills_started_minute(_elks_env, monkeypatch):
    import adaptive_ivr_agent.audio as mod

    _fake_client(monkeypatch, mod, [])
    owner = open_session({"transport": "elks"})
    info = dial(owner.session_id, E164)
    out = hangup(owner.session_id, info["call_id"])
    assert out["billed_min"] == 1
    assert mod._ELKS_BILLED_MIN == 1
    close_session(owner.session_id)


def test_elks_midcall_is_loud_not_silent(_elks_env, monkeypatch):
    import adaptive_ivr_agent.audio as mod

    _fake_client(monkeypatch, mod, [])
    owner = open_session({"transport": "elks"})
    info = dial(owner.session_id, E164)
    with pytest.raises(mod.TransportError, match="#203"):
        say_text(owner.session_id, info["call_id"], "hej")
    with pytest.raises(mod.TransportError, match="#203"):
        poll_inbound(owner.session_id, info["call_id"])
    close_session(owner.session_id)


def test_elks_health_needs_creds_and_from(_elks_env, monkeypatch):
    owner = open_session({"transport": "elks"})
    assert audio_health(owner.session_id)["transport_ok"] is True
    monkeypatch.delenv("ELKS_FROM")
    assert audio_health(owner.session_id)["transport_ok"] is False
    close_session(owner.session_id)


def test_blackhole_device_is_input_record_aggregate():
    assert BLACKHOLE_DEVICE == "IVR_Input_Record"
