from pathlib import Path

from src.infrastructure.audio_player import DEFAULT_ALARM_PATH, AudioPlayer


def test_default_alarm_asset_exists() -> None:
    assert DEFAULT_ALARM_PATH.exists()


def test_play_alarm_with_bundled_asset_does_not_raise(qapp) -> None:
    player = AudioPlayer()
    player.play_alarm()


def test_play_alarm_with_missing_file_does_not_raise(qapp) -> None:
    player = AudioPlayer(alarm_path=Path("/nonexistent/alarm.wav"))
    player.play_alarm()
