"""Live call board rendering (T-045): template + bilingual data, no browser."""
import json
import re
from pathlib import Path

import pytest

from adaptive_ivr_agent.live_view import (
    STATE_NAMES,
    build_board,
    build_call,
    render_live_page,
)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "ui" / "call-board-template.html"
PHRASEBOOKS = ROOT / "data" / "role-phrasebooks.json"


def test_board_has_bilingual_states_and_turns():
    state = build_board([("ny-arbetslos", 2)], PHRASEBOOKS)
    assert state["maps"]["swedish"]["states"][0]["en"] == "Open question"
    call = state["calls"][0]
    assert call["errand"] and len(call["turns"]) == 2
    assert call["turns"][0]["matched"] is True
    assert call["turns"][0]["state_name"]["sv"]


def test_rendered_page_carries_data_and_toggle():
    page = render_live_page(build_board([("sjukskriven", 1)], PHRASEBOOKS), TEMPLATE)
    assert "__STATE_JSON__" not in page
    assert "Sick-listed job seeker" in page
    assert "sjukpenning" in page or "anmäl sjukfrånvaro" in page
    assert 'id="btn-sv"' in page and 'id="btn-en"' in page
    assert "Ja/nej-fråga" in page


def test_every_map_state_has_both_languages():
    from adaptive_ivr_agent.menu_map import MenuMap

    for shown in (MenuMap.af_agda(), MenuMap.english_branch()):
        for state in shown.states:
            assert set(STATE_NAMES[state.id]) == {"sv", "en"}


def test_missing_placeholder_is_rejected(tmp_path):
    bad = tmp_path / "bad.html"
    bad.write_text("<html></html>", encoding="utf-8")
    with pytest.raises(ValueError):
        render_live_page({"calls": []}, bad)


def test_build_call_carries_persona_fields_and_states():
    call = build_call("ny-arbetslos", 2, PHRASEBOOKS)
    assert call["persona"] == "ny-arbetslos"
    assert call["label"] == "Newly unemployed job seeker"
    assert call["errand"] == "Skriva in mig som arbetssökande"
    assert call["map"] == "swedish"
    assert call["position"] == "example_words"
    assert [t["state"] for t in call["turns"]] == ["open_question", "example_words"]
    assert call["turns"][0]["caller"] == "skriva in mig"
    assert all(t["matched"] for t in call["turns"])


def test_unknown_persona_id_is_rejected():
    with pytest.raises(StopIteration):
        build_call("no-such-persona", 1, PHRASEBOOKS)


def test_zero_turns_stays_on_open_question():
    call = build_call("sjukskriven", 0, PHRASEBOOKS)
    assert call["turns"] == []
    assert call["position"] == "open_question"


def test_turns_are_capped_by_walk_and_vocabulary():
    call = build_call("ny-arbetslos", 10, PHRASEBOOKS)
    assert len(call["turns"]) == 3
    assert call["position"] == "yes_no"


def test_board_timestamp_format_and_both_maps():
    state = build_board([("sjukskriven", 1)], PHRASEBOOKS)
    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", state["generated"])
    assert set(state["maps"]) == {"swedish", "english"}
    assert state["maps"]["english"]["states"][-1]["en"] == "Officer"
    assert state["maps"]["swedish"]["title"] == "AF Agda - svenska kedjan"


def test_board_supports_many_calls_and_none():
    state = build_board([("ny-arbetslos", 1), ("sjukskriven", 2)], PHRASEBOOKS)
    assert [c["persona"] for c in state["calls"]] == ["ny-arbetslos", "sjukskriven"]
    assert [len(c["turns"]) for c in state["calls"]] == [1, 2]
    assert build_board([], PHRASEBOOKS)["calls"] == []


def test_rendered_page_embeds_parseable_state(tmp_path):
    template = tmp_path / "page.html"
    template.write_text('{"board": __STATE_JSON__}', encoding="utf-8")
    state = build_board([("ny-arbetslos", 1)], PHRASEBOOKS)
    page = render_live_page(state, template)
    assert json.loads(page)["board"]["calls"][0]["persona"] == "ny-arbetslos"
    assert "Skriva in mig som arbetssökande" in page  # raw utf-8, not \u-escaped
