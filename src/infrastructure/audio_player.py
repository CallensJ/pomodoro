"""Plays the bundled alarm sound; failures are logged and never propagate.

Uses non-blocking OS-native playback (not QSoundEffect/QtMultimedia): on some
platforms QSoundEffect's synchronous backend negotiation can stall for many
seconds, which would block the UI thread on every phase completion.
"""

import logging
import platform
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_ALARM_PATH = Path(__file__).resolve().parent.parent / "assets" / "alarm.wav"


class AudioPlayer:
    def __init__(self, alarm_path: Path = DEFAULT_ALARM_PATH) -> None:
        self._alarm_path = alarm_path

    def play_alarm(self) -> None:
        if not self._alarm_path.exists():
            logger.warning("Alarm sound not found at %s", self._alarm_path)
            return
        try:
            if platform.system() == "Windows":
                self._play_windows()
            else:
                self._play_linux()
        except (OSError, subprocess.SubprocessError):
            logger.exception("Failed to play alarm sound")

    def _play_linux(self) -> None:
        player = shutil.which("paplay") or shutil.which("aplay")
        if player is None:
            logger.warning("No audio player (paplay/aplay) found; skipping alarm")
            return
        subprocess.Popen(
            [player, str(self._alarm_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _play_windows(self) -> None:
        import winsound

        winsound.PlaySound(
            str(self._alarm_path), winsound.SND_FILENAME | winsound.SND_ASYNC
        )
