"""DTMF connecting beeps: valid WAV, right length, real tone (#70)."""
import struct
import wave

import pytest

from adaptive_ivr_agent.tones import (
    BEEP_SECONDS,
    BEEPS,
    GAP_SECONDS,
    SAMPLE_RATE,
    dtmf_samples,
    write_beeps,
)


def test_beeps_write_valid_mono_wav(tmp_path):
    target = tmp_path / "beeps.wav"
    write_beeps(target)
    with wave.open(str(target), "rb") as handle:
        assert handle.getnchannels() == 1
        assert handle.getsampwidth() == 2
        assert handle.getframerate() == SAMPLE_RATE
        expected = int(SAMPLE_RATE * BEEPS * (BEEP_SECONDS + GAP_SECONDS))
        assert handle.getnframes() == expected
        raw = handle.readframes(handle.getnframes())
    peak = max(abs(s) for s in struct.unpack(f"<{len(raw) // 2}h", raw))
    assert peak > 1000


def test_unknown_key_is_rejected():
    with pytest.raises(ValueError, match="DTMF"):
        dtmf_samples("Z", 0.1)


def test_each_pad_key_mixes_two_tones():
    one = dtmf_samples("1", 0.05)
    nine = dtmf_samples("9", 0.05)
    assert one != nine
    assert any(s > 0.1 for s in one) and any(s < -0.1 for s in one)
