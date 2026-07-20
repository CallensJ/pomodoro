"""Plays the bundled alarm sound; failures are logged and never propagate."""

import logging
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

logger = logging.getLogger(__name__)

DEFAULT_ALARM_PATH = Path(__file__).resolve().parent.parent / "assets" / "alarm.wav"


class AudioPlayer:
    def __init__(self, alarm_path: Path = DEFAULT_ALARM_PATH) -> None:
        self._effect = QSoundEffect()
        try:
            self._effect.setSource(QUrl.fromLocalFile(str(alarm_path)))
            self._effect.setVolume(0.6)
        except OSError:
            logger.exception("Failed to load alarm sound from %s", alarm_path)

    def play_alarm(self) -> None:
        try:
            self._effect.play()
        except OSError:
            logger.exception("Failed to play alarm sound")
