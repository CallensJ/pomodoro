import subprocess

from src.infrastructure.notification_service import NotificationService


def test_notify_on_linux_invokes_notify_send(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")
    calls = []
    monkeypatch.setattr(
        subprocess, "Popen", lambda args, **kwargs: calls.append(args) or None
    )

    NotificationService().notify("Focus Timer", "Focus finished")

    assert calls == [["notify-send", "Focus Timer", "Focus finished"]]


def test_notify_on_windows_invokes_powershell(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Windows")
    calls = []
    monkeypatch.setattr(
        subprocess, "Popen", lambda args, **kwargs: calls.append(args) or None
    )

    NotificationService().notify("Focus Timer", "Focus finished")

    assert calls[0][0] == "powershell"
    assert "Focus finished" in calls[0][-1]


def test_notify_swallows_missing_binary_error(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")

    def raise_missing(*args, **kwargs):
        raise FileNotFoundError("notify-send not found")

    monkeypatch.setattr(subprocess, "Popen", raise_missing)

    NotificationService().notify("Focus Timer", "Focus finished")


def test_notify_on_unsupported_platform_does_nothing(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Darwin")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Popen should not be called on unsupported platforms")

    monkeypatch.setattr(subprocess, "Popen", fail_if_called)

    NotificationService().notify("Focus Timer", "Focus finished")
