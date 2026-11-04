"""Chiptune music synthesis (mirrors menu_music.py)."""
import wave

from adaptive_ivr_agent import menu_music


def test_note_freq_concert_pitch():
    assert menu_music._note_freq("A4") == 440.0


def test_render_menu_music_valid_wav(tmp_path):
    target = tmp_path / "music.wav"
    assert menu_music.render_menu_music(target) == str(target)
    with wave.open(str(target), "rb") as handle:
        assert (handle.getnchannels(), handle.getsampwidth(),
                handle.getframerate()) == (1, 2, menu_music.MUSIC_RATE)
        assert handle.getnframes() > 0


def test_menu_music_path_prefers_override(tmp_path, monkeypatch):
    override = tmp_path / "theme.wav"
    override.write_bytes(b"RIFF----")
    monkeypatch.setattr(menu_music, "MUSIC_OVERRIDE", override)
    assert menu_music.menu_music_path() == str(override)
