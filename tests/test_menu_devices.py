"""Audio device helpers (mirrors menu_devices.py)."""
from adaptive_ivr_agent import menu_devices


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
