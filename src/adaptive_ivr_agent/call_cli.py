"""holdmate-call CLI: the full audio contract from the terminal (#195).

State persists in a JSON file between invocations (one active call).
Default transport is local (safe loopback); pass --transport blackhole
for real calls. --to defaults to $CALL_NUMBER.
"""
import argparse
import json
import os
import sys
import time

from . import audio

STATE_PATH = os.environ.get("HOLDMATE_CALL_STATE", "/tmp/holdmate-call.json")


def _load():
    try:
        with open(STATE_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def _save(state):
    with open(STATE_PATH, "w", encoding="utf-8") as handle:
        json.dump(state, handle)


def _resume(state):
    """Re-register persisted session/call in this process."""
    session = audio.Session(session_id=state["session_id"],
                            transport=state["transport"])
    audio._SESSIONS[session.session_id] = session
    call = audio._Call(call_id=state["call_id"], to_e164=state["to"],
                       state=state.get("call_state", "active"))
    session.calls[call.call_id] = call
    return session, call


def cmd_dial(args):
    to_number = args.to or os.environ.get("CALL_NUMBER", "")
    if not to_number:
        return "--to or $CALL_NUMBER is required"
    session = audio.open_session({"transport": args.transport})
    info = audio.dial(session.session_id, to_number,
                      record=args.record,
                      greeting=getattr(args, "greeting", "") or "")
    _save({"session_id": session.session_id, "transport": args.transport,
           "call_id": info["call_id"], "to": to_number,
           "call_state": info["state"]})
    return f"call {info['call_id']} to {to_number}: {info['state']}"


def _active():
    state = _load()
    if not state.get("call_id"):
        return None, "no active call (dial first)"
    return _resume(state), None


def cmd_say(args):
    pair, err = _active()
    if err:
        return err
    session, call = pair
    result = audio.say_text(session.session_id, call.call_id, args.text,
                            voice=args.voice)
    return (f"said {result['bytes_sent']} bytes "
            f"({result['duration_s']}s)")


def cmd_listen(args):
    pair, err = _active()
    if err:
        return err
    session, call = pair
    frames = audio.poll_inbound(session.session_id, call.call_id,
                                timeout_ms=args.seconds * 1000)
    seconds = len(frames) * audio.FRAME_MS / 1000
    text = audio.transcribe_inbound(session.session_id,
                                    call.call_id)["text"]
    return f"heard {len(frames)} frames ({seconds:.1f}s): {text}"


def cmd_dtmf(args):
    pair, err = _active()
    if err:
        return err
    session, call = pair
    audio.send_dtmf(session.session_id, call.call_id, args.digits)
    return f"sent DTMF {args.digits}"


def cmd_rec_start(args):
    pair, err = _active()
    if err:
        return err
    session, call = pair
    info = audio.rec_start(session.session_id, call.call_id,
                           mode=args.mode)
    state = _load()
    state["rec_id"] = info["rec_id"]
    _save(state)
    return f"recording {info['rec_id']} -> {info['path']}"


def cmd_rec_stop(args):
    pair, err = _active()
    if err:
        return err
    void = args
    session, call = pair
    state = _load()
    if not state.get("rec_id"):
        return "not recording"
    out = audio.rec_stop(session.session_id, state["rec_id"])
    state.pop("rec_id", None)
    _save(state)
    paths = " ".join(out[key] for key in ("path_mix", "path_in", "path_out")
                     if key in out)
    return f"saved ({out['duration_s']}s): {paths}"


def cmd_status(args):
    void = args
    pair, err = _active()
    if err:
        return err
    session, call = pair
    call_info = audio.call_status(session.session_id, call.call_id)
    health = audio.audio_health(session.session_id)
    rec = audio.rec_status(session.session_id, call.call_id)
    return (f"call {call.call_id} {call.to_e164}: {call_info['state']} | "
            f"transport={session.transport} "
            f"tts={health['tts_engine']} stt=stub | "
            f"rec={rec['recording']}")


def cmd_hangup(args):
    void = args
    pair, err = _active()
    if err:
        return err
    session, call = pair
    info = audio.hangup(session.session_id, call.call_id)
    _save({})
    return f"call {info['call_id']} ended after {info['duration_s']}s"


def build_parser():
    parser = argparse.ArgumentParser(prog="holdmate-call")
    sub = parser.add_subparsers(dest="cmd", required=True)
    dial = sub.add_parser("dial", help="ring up")
    dial.add_argument("--to", default=None)
    dial.add_argument("--from", dest="from_", default=None)
    dial.add_argument("--record", action="store_true")
    dial.add_argument("--transport", default="local",
                      choices=["local", "blackhole", "elks"])
    dial.add_argument("--greeting", default="",
                      help="elks: first line said on answer")
    dial.set_defaults(func=cmd_dial)
    say = sub.add_parser("say", help="speak into the call")
    say.add_argument("--text", required=True)
    say.add_argument("--voice", default=None)
    say.set_defaults(func=cmd_say)
    listen = sub.add_parser("listen", help="capture inbound audio")
    listen.add_argument("--seconds", type=int, default=10)
    listen.set_defaults(func=cmd_listen)
    dtmf = sub.add_parser("dtmf", help="send touch tones")
    dtmf.add_argument("--digits", required=True)
    dtmf.set_defaults(func=cmd_dtmf)
    rec_start = sub.add_parser("rec-start", help="start recording")
    rec_start.add_argument("--mode", default="both",
                           choices=["mix", "split", "both"])
    rec_start.set_defaults(func=cmd_rec_start)
    rec_stop = sub.add_parser("rec-stop", help="stop recording")
    rec_stop.set_defaults(func=cmd_rec_stop)
    status = sub.add_parser("status", help="call + health status")
    status.set_defaults(func=cmd_status)
    hangup = sub.add_parser("hangup", help="hang up")
    hangup.set_defaults(func=cmd_hangup)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    print(args.func(args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
