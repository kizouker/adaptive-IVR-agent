"""Tests for holdmate-call CLI persistence across processes (T2).

Each cmd_* call followed by clearing audio._SESSIONS simulates a fresh
CLI process: state must survive via the state file alone.
"""
import argparse
import wave

import pytest

from adaptive_ivr_agent import audio
from adaptive_ivr_agent import call_cli


E164 = "+46701234567"


@pytest.fixture(autouse=True)
def _isolated_state_and_audio(tmp_path, monkeypatch):
    import adaptive_ivr_agent.audio as mod

    monkeypatch.setattr(call_cli, "STATE_PATH", str(tmp_path / "call.json"))
    monkeypatch.setattr(mod, "OUT_DIR", tmp_path / "audio")
    audio._SESSIONS.clear()
    yield
    audio._SESSIONS.clear()


def _fresh_process():
    audio._SESSIONS.clear()


def _args(**kwargs):
    defaults = {"to": E164, "transport": "local", "record": False,
                "text": "hej", "voice": None, "seconds": 2,
                "digits": "0", "mode": "both"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_dial_then_status_and_hangup():
    assert "active" in call_cli.cmd_dial(_args())
    _fresh_process()
    assert "active" in call_cli.cmd_status(_args())
    _fresh_process()
    assert "ended after" in call_cli.cmd_hangup(_args())
    assert "no active call" in call_cli.cmd_status(_args())


def test_say_then_listen_hears_frames():
    call_cli.cmd_dial(_args())
    _fresh_process()
    said = call_cli.cmd_say(_args(text="hej hej"))
    assert "bytes" in said
    _fresh_process()
    heard = call_cli.cmd_listen(_args())
    assert "heard 0 frames" not in heard


def test_rec_start_say_rec_stop_writes_wavs(tmp_path):
    call_cli.cmd_dial(_args())
    _fresh_process()
    assert "recording" in call_cli.cmd_rec_start(_args())
    _fresh_process()
    call_cli.cmd_say(_args(text="ett tva tre"))
    _fresh_process()
    saved = call_cli.cmd_rec_stop(_args())
    assert "saved" in saved
    wavs = sorted((tmp_path / "audio").glob("*.wav"))
    assert len(wavs) == 3
    for wav in wavs:
        with wave.open(str(wav), "rb") as handle:
            assert handle.getnframes() > 0
            assert handle.getframerate() == 16000


def test_dial_needs_number(monkeypatch):
    monkeypatch.delenv("CALL_NUMBER", raising=False)
    assert "required" in call_cli.cmd_dial(_args(to=None))
