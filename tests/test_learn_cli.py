"""Interactive ask prompts for the review driver (input is injected)."""

from adaptive_ivr_agent.learn_cli import ask_factory


def test_ask_accepts_known_skip_and_quit(monkeypatch):
    ask = ask_factory({"vab"})
    monkeypatch.setattr("builtins.input", lambda prompt: "vab")
    assert ask("vabba") == "vab"
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert ask("vabba") == ""
    monkeypatch.setattr("builtins.input", lambda prompt: "q")
    assert ask("vabba") is None


def test_ask_confirms_unknown_word(monkeypatch):
    ask = ask_factory({"vab"})
    answers = iter(["vabb", "y"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    assert ask("vabba") == "vabb"


def test_ask_reprompts_on_no(monkeypatch):
    ask = ask_factory({"vab"})
    answers = iter(["vabb", "n", "vab"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    assert ask("vabba") == "vab"
