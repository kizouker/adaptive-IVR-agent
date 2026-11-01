"""Mac queue alert (FN-REQ-IVR-012)."""
import shutil
import subprocess

ALERT_TITLE = "Holdmate"
ALERT_THRESHOLD = 2
OSASCRIPT = "osascript"


def mac_notify(message: str) -> None:
    """Show a Mac notification (real runs only, never tests)."""
    if shutil.which(OSASCRIPT) is None:
        raise RuntimeError(f"{OSASCRIPT} is not available on this machine")
    safe = message.replace("\\", "\\\\").replace('"', '\\"')
    script = f'display notification "{safe}" with title "{ALERT_TITLE}"'
    subprocess.run([OSASCRIPT, "-e", script], check=True)


class QueueAlert:
    """Fires the injected notifier when the queue place reaches the threshold."""

    def __init__(self, notify, threshold: int = ALERT_THRESHOLD) -> None:
        self._notify = notify
        self._threshold = threshold

    def check(self, place: int | None) -> bool:
        """Alert at the threshold; return whether it fired."""
        if place == self._threshold:
            self._notify(f"Du har plats {place} i kön.")
            return True
        return False
