"""Live call board rendering (T-045): template + bilingual data, no browser."""
import json
import re
from pathlib import Path

import pytest

from adaptive_ivr_agent.live_view import (
    STATE_NAMES,
    LiveCall,
    build_board,
    build_call,
    build_live_board,
    render_live_page,
    vtt_timestamp,
    write_captions,
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


def test_officer_turn_carries_own_speaker():
    call = LiveCall()
    call.add_turn("", "Welcome, officer here.", False, "officer",
                  speaker="Officer (Daniel)")
    assert call.turns[-1]["speaker"] == "Officer (Daniel)"
    plain = LiveCall()
    plain.add_turn("", "Hi.", False, "open_question")
    assert "speaker" not in plain.turns[-1]


def test_live_call_can_switch_map_and_voice():
    call = LiveCall(map_name="english", robot_name="AF Agda (Samantha)")
    call.add_turn("(pressed 0)", "Welcome to Arbetsförmedlingen.", True, "english_menu")
    shot = call.snapshot()
    assert shot["map"] == "english"
    assert shot["robot_name"] == "AF Agda (Samantha)"
    assert shot["position"] == "english_menu"
    board = build_live_board([call])
    assert board["calls"][0]["map"] == "english"
    assert board["maps"]["english"]["states"][-1]["en"] == "Officer"


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
    assert call["errand_en"] == "Register as a job seeker"
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


def test_live_call_accumulates_turns_and_tracks_position():
    call = LiveCall()
    assert call.position == "open_question"
    call.add_turn("vabba", "reply one", False, "example_words")
    call.add_turn("vab", "reply two", True, "transfer")
    snapshot = call.snapshot()
    assert snapshot["persona"] == "live-caller"
    assert snapshot["position"] == "transfer"
    assert [t["state"] for t in snapshot["turns"]] == ["example_words", "transfer"]
    assert snapshot["turns"][0]["state_name"]["sv"] == "Exempelord"


def test_live_call_carries_audio_only_when_given():
    call = LiveCall()
    call.add_turn("vab", "reply", True, "transfer",
                 caller_audio="audio/r1-you.wav", robot_audio="audio/r1-agda.mp3")
    call.add_turn("nej", "reply", False, "yes_no")
    first, second = call.snapshot()["turns"]
    assert (first["caller_audio"], first["robot_audio"]) == ("audio/r1-you.wav", "audio/r1-agda.mp3")
    assert "caller_audio" not in second and "robot_audio" not in second


def test_live_board_matches_board_shape():
    call = LiveCall()
    call.add_turn("vab", "reply", True, "transfer")
    state = build_live_board([call])
    assert set(state) == {"generated", "maps", "calls"}
    assert set(state["maps"]) == {"swedish", "english"}
    assert state["calls"][0]["label"] == "You (live)"
    assert re.fullmatch(r"\d{2}:\d{2}:\d{2}", state["generated"])


def test_vtt_timestamps_cover_minutes_and_hours():
    assert vtt_timestamp(0) == "00:00:00.000"
    assert vtt_timestamp(2.5) == "00:00:02.500"
    assert vtt_timestamp(61.234) == "00:01:01.234"
    assert vtt_timestamp(3661.5) == "01:01:01.500"


def test_captions_file_is_valid_vtt(tmp_path):
    path = tmp_path / "r1-you.vtt"
    write_captions(path, "  vabba ", 3.2)
    assert path.read_text(encoding="utf-8") == "WEBVTT\n\n00:00.000 --> 00:00:03.200\nvabba\n"


def test_opening_turn_is_robot_only():
    call = LiveCall()
    call.add_turn("", "welcome, what is it?", False, "open_question",
                 robot_audio="audio/r0-agda.mp3", robot_captions="audio/r0-agda.vtt")
    turn = call.snapshot()["turns"][0]
    assert turn["caller"] == ""
    assert turn["robot_audio"] == "audio/r0-agda.mp3"
    assert "caller_audio" not in turn


def test_queue_turn_carries_place_number():
    call = LiveCall()
    call.add_turn("vab", "reply", True, "queue", queue_place=3)
    turn = call.snapshot()["turns"][0]
    assert turn["queue_place"] == 3
    assert call.position == "queue"


def test_queue_turn_carries_start_total_for_progress():
    call = LiveCall()
    call.add_turn("", "reply", False, "queue", queue_place=7, queue_total=30)
    turn = call.snapshot()["turns"][0]
    assert (turn["queue_place"], turn["queue_total"]) == (7, 30)


def test_map_blob_ships_edges_for_option_lists():
    state = build_board([("ny-arbetslos", 1)], PHRASEBOOKS)
    edges = state["maps"]["swedish"]["edges"]
    assert {"source": "yes_no", "target": "transfer", "label": "ja/nej"} in edges
    assert all(set(edge) == {"source", "target", "label"} for edge in edges)


def test_live_call_carries_captions_and_speaker_names():
    call = LiveCall()
    call.add_turn("vab", "reply", True, "transfer",
                 caller_audio="audio/r1-you.wav", robot_audio="audio/r1-agda.mp3",
                 caller_captions="audio/r1-you.vtt", robot_captions="audio/r1-agda.vtt")
    snapshot = call.snapshot()
    assert (snapshot["caller_name"], snapshot["robot_name"]) == ("You", "AF Agda (Alva)")
    turn = snapshot["turns"][0]
    assert (turn["caller_captions"], turn["robot_captions"]) == ("audio/r1-you.vtt", "audio/r1-agda.vtt")
