"""Queue number parsing (FN-REQ-IVR-011): three spec phrasings + observed AF lines."""
from adaptive_ivr_agent.queue import find_place


def test_det_ar_samtal_fore_dig():
    assert find_place("Det är 38 samtal före dig") == 38


def test_anropare_nummer():
    assert find_place("anropare nummer 12") == 12


def test_din_plats_ar():
    assert find_place("Din plats är: 47") == 47


def test_af_swedish_queue_line():
    assert find_place("Du har plats 1 i kön") == 1


def test_af_english_queue_line():
    assert find_place("You are number 8 in the queue") == 8


def test_no_number_gives_none():
    assert find_place("Välkommen till Arbetsförmedlingen.") is None
