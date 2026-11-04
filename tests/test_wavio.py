"""Shared WAV writer (R3): params survive the round trip. Bit-identity of the
three call sites is covered by test_tones, test_audio and test_menu_app."""
import wave

from adaptive_ivr_agent.wavio import write_wav


def test_write_wav_roundtrip_params(tmp_path):
    target = tmp_path / "sub" / "dir" / "out.wav"
    frames = b"\x00\x01\x02\x03" * 100
    assert write_wav(target, frames, 44100) == str(target)
    with wave.open(str(target), "rb") as handle:
        assert (handle.getnchannels(), handle.getsampwidth(),
                handle.getframerate()) == (1, 2, 44100)
        assert handle.readframes(handle.getnframes()) == frames


def test_write_wav_empty_frames_kept(tmp_path):
    target = tmp_path / "empty.wav"
    write_wav(target, b"", 16000)
    with wave.open(str(target), "rb") as handle:
        assert handle.getframerate() == 16000
        assert handle.getnframes() == 0
