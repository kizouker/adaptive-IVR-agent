"""Holdmate audio module: duplex calls via program or CLI (#194, #196).

Contract (from duplex design): 16 kHz mono 16-bit PCM, 20 ms frames
(640 bytes), seq + ts_ms. Agent sees text + events, never bytes.

T1 ships: session lifecycle, dial/hangup/status, say_text/push_outbound
OUT, poll_inbound IN (loopback echo on local), rec_start/stop (mix +
split wavs), send_dtmf synth, audio_health. Transports: local
(headless-tested) and blackhole (tel: + BlackHole device; hardware
verify left for Rickard's Mac). Streaming STT/TTS adapters are T5.
"""

from __future__ import annotations

import math
import os
import shutil
import struct
import subprocess
import time
import uuid
import wave
from dataclasses import dataclass, field
from pathlib import Path

from .elks import ElksClient, valid_e164
from .tones import DTMF_FREQS

SAMPLE_RATE = 16000
FRAME_MS = 20
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000
FRAME_BYTES = FRAME_SAMPLES * 2
SILENCE = "(silence)"
BLACKHOLE_DEVICE = "IVR_Input_Record"

OUT_DIR = Path("data/audio")


class AudioError(RuntimeError):
    pass


class AudioConfigError(AudioError):
    pass


class DeviceNotFoundError(AudioError):
    pass


class DeviceBusyError(AudioError):
    pass


class UnknownSessionError(AudioError):
    pass


class UnknownCallError(AudioError):
    pass


class TransportError(AudioError):
    pass


class TTSError(AudioError):
    pass


@dataclass
class Frame:
    seq: int
    ts_ms: int
    pcm: bytes


@dataclass
class _Call:
    call_id: str
    to_e164: str
    state: str = "dialing"
    reason: str | None = None
    seq_out: int = 0
    seq_in: int = 0
    inbox: list = field(default_factory=list)
    rec: dict | None = None
    started: float = field(default_factory=time.time)


@dataclass
class Session:
    session_id: str
    transport: str
    tts: str = "say"
    stt: str = "stub"
    voice: str = "Oskar"
    lang: str = "sv-SE"
    calls: dict = field(default_factory=dict)
    spool: str | None = None  # CLI loopback file (cross-process echo)


_SESSIONS: dict[str, Session] = {}


def _run(cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _need(session_id: str) -> Session:
    try:
        return _SESSIONS[session_id]
    except KeyError:
        raise UnknownSessionError(session_id) from None


def _need_call(session: Session, call_id: str) -> _Call:
    try:
        return session.calls[call_id]
    except KeyError:
        raise UnknownCallError(call_id) from None


# ---------------------------------------------------------------- session

_ELKS_BILLED_MIN = 0  # started minutes billed by 46elks this process
_ELKS_LIVE: set[str] = set()  # elks call_ids currently up (max 1: cost guard)

ELKS_NO_MIDCALL = ("46elks REST cannot inject or tap mid-call audio; "
                   "the webhook loop is ticket #203")


def open_session(config: dict) -> Session:
    """Open a session. config: transport local|blackhole|elks, tts, voice."""
    transport = config.get("transport", "local")
    if transport not in ("local", "blackhole", "elks"):
        raise AudioConfigError(f"unknown transport: {transport}")
    session = Session(session_id=uuid.uuid4().hex[:8], transport=transport,
                      tts=config.get("tts", "say"),
                      voice=config.get("voice", "Oskar"),
                      lang=config.get("lang", "sv-SE"))
    _SESSIONS[session.session_id] = session
    return session


def close_session(session_id: str) -> None:
    session = _need(session_id)
    for call in session.calls.values():
        if call.rec:
            rec_stop(session_id, call.rec["rec_id"])
    del _SESSIONS[session_id]


# ---------------------------------------------------------------- dial

def dial(session_id: str, to_e164: str, record: bool = False,
         timeout_s: int = 30, greeting: str = "") -> dict:
    """Ring up. Local answers instantly (loopback); elks dials for real."""
    session = _need(session_id)
    if not valid_e164(to_e164):
        raise ValueError(f"not E.164: {to_e164}")
    call = _Call(call_id=uuid.uuid4().hex[:8], to_e164=to_e164)
    if session.transport == "elks":
        return _elks_dial(session, call, greeting)
    if session.transport == "blackhole":
        _blackhole_dial(to_e164)
        call.state = "active"  # tel: gives no answer signal; assume up
    else:
        call.state = "active"
    session.calls[call.call_id] = call
    rec_info = rec_start(session_id, call.call_id) if record else None
    return {"call_id": call.call_id, "state": call.state, "rec": rec_info}


def _elks_dial(session: Session, call: _Call, greeting: str) -> dict:
    """Real outbound call via 46elks. Stays dialing: REST has no answer
    signal without the webhook loop (#203). Recording happens at 46elks."""
    if _ELKS_LIVE:
        raise DeviceBusyError("one 46elks call at a time (cost guard)")
    cap = int(os.environ.get("ELKS_MAX_MINUTES", "10"))
    if _ELKS_BILLED_MIN >= cap:
        raise DeviceBusyError(f"46elks budget spent ({_ELKS_BILLED_MIN}/{cap} min)")
    from_number = os.environ.get("ELKS_FROM", "")
    if not valid_e164(from_number):
        raise AudioConfigError("set $ELKS_FROM to your 46elks voice number")
    client = ElksClient()  # raises when ELKS_API_USER/PASS are missing
    opening = greeting or ("Hej, det här är Holdmate som ringer upp. "
                           "Lägg på om samtalet kom fel.")
    resp = client.place_call(to=call.to_e164, from_number=from_number,
                             recordcall="true",
                             whenhangup=os.environ.get("ELKS_WHENHANGUP", ""),
                             voice_start=opening)
    call.state = "dialing"
    call.reason = f"elks:{resp.get('id', '?')}"
    session.calls[call.call_id] = call
    _ELKS_LIVE.add(call.call_id)
    return {"call_id": call.call_id, "state": call.state,
            "elks_id": resp.get("id"), "rec": "46elks-side"}


def _blackhole_dial(number: str) -> None:
    if shutil.which("open") is None:
        raise DeviceNotFoundError("macOS 'open' missing; cannot dial tel: URL")
    proc = _run(["open", f"tel:{number}"])
    if proc.returncode != 0:
        raise TransportError(f"tel: dial failed: {proc.stderr.strip()}")


def hangup(session_id: str, call_id: str) -> dict:
    """Hang up. Idempotent: second call returns ended, never crashes."""
    global _ELKS_BILLED_MIN
    session = _need(session_id)
    call = _need_call(session, call_id)
    rec_path = None
    if call.rec:
        rec_path = rec_stop(session_id, call.rec["rec_id"])["path_mix"]
    call.state = "ended"
    result = {"call_id": call_id, "state": "ended",
              "duration_s": round(time.time() - call.started, 1),
              "rec_path": rec_path}
    if session.transport == "elks" and call_id in _ELKS_LIVE:
        _ELKS_LIVE.discard(call_id)
        billed = max(1, math.ceil(result["duration_s"] / 60))
        _ELKS_BILLED_MIN += billed  # 46elks bills per started minute
        result["billed_min"] = billed
        result["rec_path"] = "46elks dashboard (recordcall=true)"
    return result


def call_status(session_id: str, call_id: str) -> dict:
    call = _need_call(_need(session_id), call_id)
    return {"state": call.state, "reason": call.reason}


def send_dtmf(session_id: str, call_id: str, digits: str) -> None:
    """Synth DTMF frames OUT (works on every transport)."""
    session = _need(session_id)
    call = _need_call(session, call_id)
    for digit in digits:
        if digit not in DTMF_FREQS:
            raise ValueError(f"not a DTMF key: {digit!r}")
        push_outbound(session_id, call_id,
                      _tone_frames(*DTMF_FREQS[digit], seconds=0.15))
        push_outbound(session_id, call_id, _quiet_frames(seconds=0.05))
    void = session  # session owns routing; frames ride the call


def _tone_frames(low: float, high: float, seconds: float) -> list[Frame]:
    count = int(SAMPLE_RATE * seconds)
    raw = struct.pack(
        f"<{count}h",
        *[int(8192 * (math.sin(2 * math.pi * low * i / SAMPLE_RATE)
                      + math.sin(2 * math.pi * high * i / SAMPLE_RATE)))
          for i in range(count)])
    return _to_frames(raw, 0)


def _quiet_frames(seconds: float) -> list[Frame]:
    return _to_frames(b"\x00" * int(SAMPLE_RATE * seconds) * 2, 0)


def _to_frames(raw: bytes, start_seq: int) -> list[Frame]:
    frames = []
    now = int(time.time() * 1000)
    for i in range(0, len(raw), FRAME_BYTES):
        chunk = raw[i:i + FRAME_BYTES].ljust(FRAME_BYTES, b"\x00")
        frames.append(Frame(seq=start_seq + len(frames), ts_ms=now, pcm=chunk))
    return frames


# ---------------------------------------------------------------- outbound

def say_text(session_id: str, call_id: str, text: str,
             voice: str | None = None) -> dict:
    """Speak text OUT. macOS say when present, else deterministic synth."""
    session = _need(session_id)
    call = _need_call(session, call_id)
    if session.transport == "elks":
        raise TransportError(ELKS_NO_MIDCALL)
    frames = _speak(text, voice or session.voice)
    accepted = push_outbound(session_id, call.call_id, frames)
    return {"bytes_sent": accepted * FRAME_BYTES,
            "duration_s": round(accepted * FRAME_MS / 1000, 2)}


def _speak(text: str, voice: str) -> list[Frame]:
    if shutil.which("say") and shutil.which("afconvert"):
        try:
            frames = _speak_mac(text, voice)
        except TTSError:
            frames = []
        if frames:  # sandboxed say yields silence; synth instead
            return frames
    return _speak_synth(text)


def _speak_mac(text: str, voice: str) -> list[Frame]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tag = uuid.uuid4().hex[:8]
    aiff = OUT_DIR / f"tts-{tag}.aiff"
    wav_path = OUT_DIR / f"tts-{tag}.wav"
    proc = _run(["say", "-v", voice, "-o", str(aiff), text or " "],
                timeout=60)
    if proc.returncode != 0:
        raise TTSError(proc.stderr.strip() or "say failed")
    conv = _run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000",
                 str(aiff), str(wav_path)], timeout=60)
    aiff.unlink(missing_ok=True)
    if conv.returncode != 0:
        raise TTSError(conv.stderr.strip() or "afconvert failed")
    with wave.open(str(wav_path), "rb") as handle:
        raw = handle.readframes(handle.getnframes())
    wav_path.unlink(missing_ok=True)
    return _to_frames(raw, 0)


def _speak_synth(text: str) -> list[Frame]:
    """Deterministic fallback: 60 ms per char of soft beep + silence."""
    seconds = max(0.5, 0.06 * len(text))
    return _tone_frames(440.0, 0.0, seconds)


def push_outbound(session_id: str, call_id: str,
                  frames: list[Frame]) -> int:
    """Push PCM frames OUT. Local transport loops them back as echo."""
    session = _need(session_id)
    call = _need_call(session, call_id)
    if session.transport == "elks":
        raise TransportError(ELKS_NO_MIDCALL)
    for frame in frames:
        call.seq_out += 1
        _rec_frame(call, "out", frame.pcm)
        if session.transport == "local":
            call.seq_in += 1
            echo = Frame(seq=call.seq_in, ts_ms=frame.ts_ms, pcm=frame.pcm)
            call.inbox.append(echo)
            _rec_frame(call, "in", echo.pcm)
    if session.transport == "blackhole" and frames:
        _play_out(frames)
    return len(frames)


def _play_out(frames: list[Frame]) -> None:
    """Fire-and-forget playback to system output.

    Works when system output is routed through the Agent aggregate
    (speakers/AirPods + BlackHole): the call hears it via BlackHole.
    """
    if shutil.which("afplay") is None:
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clip = OUT_DIR / f"out-{uuid.uuid4().hex[:8]}.wav"
    _write_wav(str(clip), [frame.pcm for frame in frames])
    subprocess.Popen(["afplay", str(clip)],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------- inbound

def poll_inbound(session_id: str, call_id: str, max_frames: int = 50,
                 timeout_ms: int = 2000) -> list[Frame]:
    """Take inbound frames. Blackhole pulls from the device on demand."""
    session = _need(session_id)
    call = _need_call(session, call_id)
    if session.transport == "elks":
        raise TransportError(ELKS_NO_MIDCALL)
    if session.transport == "blackhole":
        _blackhole_pull(session, call, timeout_ms)
    out, call.inbox = call.inbox[:max_frames], call.inbox[max_frames:]
    return out


def _blackhole_pull(session: Session, call: _Call, timeout_ms: int) -> None:
    if shutil.which("ffmpeg") is None:
        raise DeviceNotFoundError("ffmpeg missing; cannot read BlackHole")
    if not _device_present(BLACKHOLE_DEVICE):
        raise DeviceNotFoundError(
            f"{BLACKHOLE_DEVICE} not found. Install BlackHole and route "
            "system audio through the Agent aggregate (see T3).")
    seconds = max(0.2, timeout_ms / 1000)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clip = OUT_DIR / f"in-{call.call_id}.wav"
    proc = _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-f", "avfoundation", "-i", f"none:{BLACKHOLE_DEVICE}",
                 "-t", str(seconds), "-c:a", "pcm_s16le",
                 "-af", "aresample=16000,aformat=channel_layouts=mono",
                 str(clip)], timeout=int(seconds) + 10)
    if proc.returncode != 0:
        raise TransportError(f"BlackHole read failed: {proc.stderr.strip()}")
    with wave.open(str(clip), "rb") as handle:
        raw = handle.readframes(handle.getnframes())
    clip.unlink(missing_ok=True)
    for frame in _to_frames(raw, call.seq_in):
        call.seq_in += 1
        call.inbox.append(frame)
        _rec_frame(call, "in", frame.pcm)


def _device_present(name: str) -> bool:
    proc = _run(["ffmpeg", "-f", "avfoundation", "-list_devices", "true",
                 "-i", ""])
    return name in (proc.stderr + proc.stdout)


def transcribe_inbound(session_id: str, call_id: str,
                       window_s: float = 5.0) -> dict:
    """Stub until T5 streaming STT lands: always honest silence."""
    _need_call(_need(session_id), call_id)
    void = window_s
    return {"text": SILENCE, "confidence": 0.0, "source": "stub"}


# ---------------------------------------------------------------- record

def rec_start(session_id: str, call_id: str, mode: str = "both",
              path: str | None = None) -> dict:
    """Start recording. mode: mix|split|both. Always valid wav output."""
    call = _need_call(_need(session_id), call_id)
    if call.rec:
        raise DeviceBusyError("already recording this call")
    if mode not in ("mix", "split", "both"):
        raise AudioConfigError(f"bad rec mode: {mode}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = Path(path) if path else OUT_DIR / f"call-{call.call_id}"
    rec_id = uuid.uuid4().hex[:8]
    rec = {"rec_id": rec_id, "mode": mode, "started": time.time(),
           "in_frames": [], "out_frames": []}
    if mode in ("split", "both"):
        rec["path_in"] = str(base) + ".in.wav"
        rec["path_out"] = str(base) + ".out.wav"
    if mode in ("mix", "both"):
        rec["path_mix"] = str(base) + ".mix.wav"
    call.rec = rec
    return {"rec_id": rec_id, "path": str(base)}


def _rec_frame(call: _Call, side: str, pcm: bytes) -> None:
    if not call.rec:
        return
    call.rec["in_frames" if side == "in" else "out_frames"].append(pcm)


def _write_wav(path: str, chunks: list[bytes]) -> None:
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(b"".join(chunks) or b"\x00" * FRAME_BYTES)


def rec_stop(session_id: str, rec_id: str) -> dict:
    call = _find_rec(_need(session_id), rec_id)
    rec = call.rec
    call.rec = None
    result = {"duration_s": round(time.time() - rec["started"], 1)}
    if "path_in" in rec:
        _write_wav(rec["path_in"], rec["in_frames"])
        _write_wav(rec["path_out"], rec["out_frames"])
        result["path_in"] = rec["path_in"]
        result["path_out"] = rec["path_out"]
    if "path_mix" in rec:
        _write_wav(rec["path_mix"], rec["out_frames"] + rec["in_frames"])
        result["path_mix"] = rec["path_mix"]
    return result


def _find_rec(session: Session, rec_id: str) -> _Call:
    for call in session.calls.values():
        if call.rec and call.rec["rec_id"] == rec_id:
            return call
    raise UnknownCallError(rec_id)


def rec_status(session_id: str, call_id: str) -> dict:
    call = _need_call(_need(session_id), call_id)
    if not call.rec:
        return {"recording": False, "seconds": 0.0, "path": None}
    return {"recording": True,
            "seconds": round(time.time() - call.rec["started"], 1),
            "path": call.rec.get("path_mix")}


# ---------------------------------------------------------------- health

def audio_health(session_id: str) -> dict:
    session = _need(session_id)
    if session.transport == "local":
        transport_ok = True
    elif session.transport == "elks":
        transport_ok = bool(os.environ.get("ELKS_API_USER")
                            and os.environ.get("ELKS_API_PASS")
                            and valid_e164(os.environ.get("ELKS_FROM", "")))
    else:
        transport_ok = _device_present(BLACKHOLE_DEVICE)
    return {"transport_ok": transport_ok,
            "tts_ok": True,  # say when present, else synth fallback
            "tts_engine": "say" if shutil.which("say") else "synth",
            "stt_ok": False,
            "stt_note": "streaming STT is T5; stub returns (silence)",
            "rtt_ms": None,
            "last_error": None}
