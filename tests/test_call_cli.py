"""Tests for the holdmate-call CLI (#195, T2 persistence).

Headless: the audio backend is mocked, so no real calls and no network.
State file is redirected to tmp_path; $CALL_NUMBER is scrubbed.
Each cmd_* call followed by clearing audio._SESSIONS simulates a fresh
CLI process: state must survive via the state file alone.
"""
import argparse
import wave
from types import SimpleNamespace

import pytest

import adaptive_ivr_agent.call_cli as cli
from adaptive_ivr_agent import audio
from adaptive_ivr_agent import call_cli


E164 = "+46701234567"


@pytest.fixture(autouse=True)
def _isolated_state_and_audio(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "STATE_PATH", str(tmp_path / "call.json"))
    monkeypatch.setattr(audio, "OUT_DIR", tmp_path / "audio")
    monkeypatch.delenv("CALL_NUMBER", raising=False)
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


def _dial_args(**over):
    base = {"to": E164, "from_": None, "record": False,
            "transport": "local", "greeting": ""}
    base.update(over)
    return SimpleNamespace(**base)


def _seed_active_call():
    cli._save({"session_id": "s1", "transport": "local",
               "call_id": "c1", "to": E164, "call_state": "active"})


def _fake_session(to=E164):
    """Minimal open_session stand-in shaped like a real Session."""
    call = SimpleNamespace(call_id="c1", to_e164=to, state="active",
                           reason=None, seq_out=0, seq_in=0,
                           started=0.0, inbox=[], rec=None)
    return SimpleNamespace(session_id="s1", transport="local",
                           calls={"c1": call})


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


# ---------------------------------------------------------------- arg parsing (main #195)

def test_parser_dial_defaults():
    args = cli.build_parser().parse_args(["dial", "--to", E164])
    assert args.cmd == "dial"
    assert args.transport == "local"
    assert args.record is False
    assert args.greeting == ""
    assert args.func is cli.cmd_dial


@pytest.mark.parametrize("transport", ["local", "blackhole", "elks"])
def test_parser_dial_transport_choices(transport):
    args = cli.build_parser().parse_args(
        ["dial", "--to", E164, "--transport", transport])
    assert args.transport == transport


def test_parser_rejects_unknown_transport():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(
            ["dial", "--to", E164, "--transport", "pigeon"])


def test_parser_requires_subcommand():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args([])


def test_parser_say_requires_text():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["say"])
    args = cli.build_parser().parse_args(["say", "--text", "hej"])
    assert args.text == "hej"
    assert args.func is cli.cmd_say


def test_parser_wires_all_commands():
    cases = {"status": [], "hangup": [], "rec-stop": [],
             "listen": [], "dtmf": ["--digits", "1"],
             "rec-start": [], "dial": ["--to", E164]}
    funcs = {"status": cli.cmd_status, "hangup": cli.cmd_hangup,
             "rec-stop": cli.cmd_rec_stop, "listen": cli.cmd_listen,
             "dtmf": cli.cmd_dtmf, "rec-start": cli.cmd_rec_start,
             "dial": cli.cmd_dial}
    for cmd, extra in cases.items():
        args = cli.build_parser().parse_args([cmd, *extra])
        assert args.func is funcs[cmd], cmd


# ---------------------------------------------------------------- dial

def test_dial_mocks_backend_and_persists_state(monkeypatch):
    seen = {}

    def fake_open(config):
        seen["config"] = config
        return _fake_session()

    def fake_dial(session_id, to, record=False, greeting=""):
        seen.update(session_id=session_id, to=to,
                    record=record, greeting=greeting)
        return {"call_id": "c1", "state": "active"}

    monkeypatch.setattr(cli.audio, "open_session", fake_open)
    monkeypatch.setattr(cli.audio, "dial", fake_dial)
    out = cli.cmd_dial(_dial_args())
    assert out == f"call c1 to {E164}: active"
    assert seen["config"] == {"transport": "local"}
    assert seen["to"] == E164
    assert cli._load()["call_id"] == "c1"


def test_dial_falls_back_to_call_number_env(monkeypatch):
    monkeypatch.setenv("CALL_NUMBER", E164)
    monkeypatch.setattr(cli.audio, "open_session",
                        lambda config: _fake_session())
    monkeypatch.setattr(cli.audio, "dial",
                        lambda *a, **k: {"call_id": "c1", "state": "active"})
    out = cli.cmd_dial(_dial_args(to=None))
    assert E164 in out


def test_dial_requires_to_or_call_number():
    assert cli.cmd_dial(_dial_args(to=None)) == \
        "--to or $CALL_NUMBER is required"


def test_dial_greeting_passthrough(monkeypatch):
    seen = {}
    monkeypatch.setattr(cli.audio, "open_session",
                        lambda config: _fake_session())

    def fake_dial(session_id, to, record=False, greeting=""):
        seen["greeting"] = greeting
        return {"call_id": "c1", "state": "dialing"}

    monkeypatch.setattr(cli.audio, "dial", fake_dial)
    cli.cmd_dial(_dial_args(transport="elks", greeting="Hej!"))
    assert seen["greeting"] == "Hej!"


def test_dial_elks_transport_reaches_backend(monkeypatch):
    seen = {}
    monkeypatch.setattr(
        cli.audio, "open_session",
        lambda config: seen.update(config=config) or
        _fake_session())
    monkeypatch.setattr(cli.audio, "dial",
                        lambda *a, **k: {"call_id": "c1", "state": "dialing"})
    out = cli.cmd_dial(_dial_args(transport="elks"))
    assert "dialing" in out
    assert seen["config"] == {"transport": "elks"}


# ---------------------------------------------------------------- status

def test_status_shows_call_and_health(monkeypatch):
    _seed_active_call()
    monkeypatch.setattr(cli.audio, "call_status",
                        lambda s, c: {"state": "active"})
    monkeypatch.setattr(cli.audio, "audio_health",
                        lambda s: {"tts_engine": "synth"})
    monkeypatch.setattr(cli.audio, "rec_status",
                        lambda s, c: {"recording": False})
    out = cli.cmd_status(SimpleNamespace())
    assert "c1" in out and E164 in out
    assert "active" in out and "transport=local" in out
    assert "tts=synth" in out and "rec=False" in out


def test_status_without_call_errors():
    assert cli.cmd_status(SimpleNamespace()) == \
        "no active call (dial first)"


def test_status_corrupt_state_errors(tmp_path):
    path = tmp_path / "call.json"
    path.write_text("not-json{{{", encoding="utf-8")
    assert cli.cmd_status(SimpleNamespace()) == \
        "no active call (dial first)"


# ---------------------------------------------------------------- hangup

def test_hangup_ends_call_and_clears_state(monkeypatch):
    _seed_active_call()
    monkeypatch.setattr(cli.audio, "hangup",
                        lambda s, c: {"call_id": "c1", "duration_s": 12.5})
    out = cli.cmd_hangup(SimpleNamespace())
    assert out == "call c1 ended after 12.5s"
    assert cli._load() == {}


def test_hangup_without_call_errors():
    assert cli.cmd_hangup(SimpleNamespace()) == \
        "no active call (dial first)"


def test_say_without_call_errors():
    assert cli.cmd_say(SimpleNamespace(text="hej", voice=None)) == \
        "no active call (dial first)"


# ---------------------------------------------------------------- main

def test_main_prints_and_returns_zero(monkeypatch, capsys):
    _seed_active_call()
    monkeypatch.setattr(cli.audio, "hangup",
                        lambda s, c: {"call_id": "c1", "duration_s": 1.0})
    assert cli.main(["hangup"]) == 0
