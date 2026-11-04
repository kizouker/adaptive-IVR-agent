"""Split-out menu modules: devices, music, and App i18n (R2)."""
import wave

from adaptive_ivr_agent import menu, menu_devices, menu_music


def test_i18n_defaults_to_english():
    assert menu.I18N("xx").lang == "en"
    assert menu.I18N().t("m_quit") == "Quit"


def test_i18n_toggle_flips_and_persists(tmp_path, monkeypatch):
    monkeypatch.setattr(menu, "LANG_FILE", tmp_path / ".menu-lang")
    strings = menu.I18N("en")
    strings.toggle()
    assert strings.lang == "sv"
    assert strings.t("m_quit") == "Avsluta"


def test_clamp_volume_bounds():
    assert menu_devices.clamp_volume(9.0) == 4.0
    assert menu_devices.clamp_volume(-1.0) == 0.1
    assert menu_devices.clamp_volume(1.26) == 1.3


def test_read_volume_missing_file_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(menu_devices, "VOLUME_FILE", tmp_path / "nope")
    assert menu_devices.read_volume() == 0.7


def test_read_input_name_missing_file_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(menu_devices, "INPUT_FILE", tmp_path / "nope")
    assert menu_devices.read_input_name() == ""


def test_system_devices_return_lists():
    assert isinstance(menu_devices.system_outputs(), list)
    assert isinstance(menu_devices.system_inputs(), list)


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


def test_menu_reexports_device_helpers():
    assert menu.read_volume is menu_devices.read_volume
    assert menu.system_outputs is menu_devices.system_outputs
    assert menu.menu_music_path is menu_music.menu_music_path


def test_read_personas_loads_roles():
    personas = menu.read_personas()
    assert personas and all(len(item) == 2 for item in personas)
