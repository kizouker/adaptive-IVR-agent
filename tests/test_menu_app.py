"""Menu App i18n and re-exports (covers menu.py itself)."""
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


def test_menu_reexports_device_helpers():
    assert menu.read_volume is menu_devices.read_volume
    assert menu.system_outputs is menu_devices.system_outputs
    assert menu.menu_music_path is menu_music.menu_music_path


def test_read_personas_loads_roles():
    personas = menu.read_personas()
    assert personas and all(len(item) == 2 for item in personas)
