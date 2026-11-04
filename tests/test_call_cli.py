"""Tests for the holdmate-call CLI (#195).

Headless: the audio backend is mocked, so no real calls and no network.
State file is redirected to tmp_path; $CALL_NUMBER is scrubbed.
"""
from types import SimpleNamespace

import pytest

import adaptive_ivr_agent.call_cli as cli

E164 = "+46701234567"


@pytest.fixture(autouse=True)
def _isolated_state(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "STATE_PATH", str(tmp_path / "call.json"))
    monkeypatch.delenv("CALL_NUMBER", raising=False)


def _dial_args(**over):
    base = {"to": E164, "from_": None, "record": False,
            "transport": "local", "greeting": ""}
    base.update(over)
    return SimpleNamespace(**base)


def _seed_active_call():
    cli._save({"session_id": "s1", "transport": "local",
               "call_id": "c1", "to": E164, "call_state": "active"})


# ---------------------------------------------------------------- arg parsing

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
        return SimpleNamespace(session_id="s1")

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
                        lambda config: SimpleNamespace(session_id="s1"))
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
                        lambda config: SimpleNamespace(session_id="s1"))

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
        SimpleNamespace(session_id="s1"))
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
    assert "c1 ended" in capsys.readouterr().out