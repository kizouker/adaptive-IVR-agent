"""Mac queue alert (FN-REQ-IVR-012): notification injected, never real in tests."""
from adaptive_ivr_agent.alerter import ALERT_THRESHOLD, QueueAlert


def test_alert_fires_at_number_two():
    calls = []
    alert = QueueAlert(notify=calls.append)
    assert alert.check(ALERT_THRESHOLD) is True
    assert len(calls) == 1
    assert str(ALERT_THRESHOLD) in calls[0]


def test_no_alert_above_threshold_or_without_number():
    calls = []
    alert = QueueAlert(notify=calls.append)
    assert alert.check(ALERT_THRESHOLD + 1) is False
    assert alert.check(None) is False
    assert calls == []
