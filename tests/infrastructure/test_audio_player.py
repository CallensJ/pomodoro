import subprocess
from pathlib import Path

from src.infrastructure.audio_player import DEFAULT_ALARM_PATH, AudioPlayer


def test_default_alarm_asset_exists() -> None:
    assert DEFAULT_ALARM_PATH.exists()


def test_play_alarm_invokes_linux_player_non_blocking(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/paplay" if name == "paplay" else None
    )
    calls = []
    monkeypatch.setattr(
        subprocess, "Popen", lambda args, **kwargs: calls.append(args) or None
    )

    AudioPlayer().play_alarm()

    assert calls == [["/usr/bin/paplay", str(DEFAULT_ALARM_PATH)]]


def test_play_alarm_falls_back_to_aplay_when_paplay_missing(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/aplay" if name == "aplay" else None
    )
    calls = []
    monkeypatch.setattr(
        subprocess, "Popen", lambda args, **kwargs: calls.append(args) or None
    )

    AudioPlayer().play_alarm()

    assert calls == [["/usr/bin/aplay", str(DEFAULT_ALARM_PATH)]]


def test_play_alarm_with_missing_file_does_not_raise(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("should not attempt playback for a missing file")

    monkeypatch.setattr(subprocess, "Popen", fail_if_called)

    AudioPlayer(alarm_path=Path("/nonexistent/alarm.wav")).play_alarm()


def test_play_alarm_swallows_missing_binary_error(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/paplay")

    def raise_missing(*args, **kwargs):
        raise FileNotFoundError("paplay not found")

    monkeypatch.setattr(subprocess, "Popen", raise_missing)

    AudioPlayer().play_alarm()


def test_play_alarm_does_nothing_when_no_linux_player_found(monkeypatch) -> None:
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("shutil.which", lambda name: None)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("should not attempt playback with no player available")

    monkeypatch.setattr(subprocess, "Popen", fail_if_called)

    AudioPlayer().play_alarm()
