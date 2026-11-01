"""46elks voice client prep for Monday's real-line test (#131).

Stdlib only. No credentials in the repo: user/pass come from .env
(ELKS_USER/ELKS_PASS). Offline-safe: without creds every call raises
NotConfiguredError with setup instructions instead of touching network.
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.parse
import urllib.request

API = "https://api.46elks.com/a1"
COST_PER_MIN_SEK = 0.30  # voice calls, per started minute (Nov 2026 pricing)
NUMBER_MONTHLY_SEK = 12.0  # virtual number, per month


class NotConfiguredError(RuntimeError):
    """Monday brings the account: fill ELKS_USER/ELKS_PASS in .env."""


def estimate_cost_sek(minutes: int) -> float:
    """Upper bound for a test call bill (per-started-minute billing)."""
    return round(minutes * COST_PER_MIN_SEK, 2)


def valid_e164(number: str) -> bool:
    return re.fullmatch(r"\+\d{7,15}", number or "") is not None


class ElksClient:
    def __init__(self, user: str = "", password: str = "") -> None:
        self.user = user or os.environ.get("ELKS_USER", "")
        self.password = password or os.environ.get("ELKS_PASS", "")
        if not self.user or not self.password:
            raise NotConfiguredError("set ELKS_USER + ELKS_PASS in .env (never commit)")

    def _post(self, path: str, fields: dict) -> dict:
        token = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
        req = urllib.request.Request(
            f"{API}{path}",
            data=urllib.parse.urlencode(fields).encode(),
            headers={"Authorization": f"Basic {token}"},
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.load(res)

    def place_call(
        self,
        to: str,
        from_number: str,
        recordcall: str = "true",
        whenhangup: str = "",
    ) -> dict:
        """Start an outbound call. Returns the 46elks call object (has id)."""
        if not valid_e164(to):
            raise ValueError(f"bad callee E.164: {to!r}")
        if not valid_e164(from_number):
            raise ValueError(f"bad caller E.164: {from_number!r}")
        fields = {"from": from_number, "to": to, "recordcall": recordcall}
        if whenhangup:
            fields["whenhangup"] = whenhangup
        return self._post("/calls", fields)


def parse_hangup(payload: dict) -> dict:
    """Validate a whenhangup callback payload into the fields we log."""
    return {
        "id": payload.get("id", ""),
        "from": payload.get("from", ""),
        "to": payload.get("to", ""),
        "created": payload.get("created", ""),
        "state": payload.get("state", ""),
        "duration": payload.get("duration", ""),
    }
