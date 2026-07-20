"""Non-blocking local MP3 playback.

QtMultimedia (QSoundEffect/QMediaPlayer) is avoided: both were found to
block the calling thread for many seconds on some audio backends. This
uses OS-native playback instead — an external process on Linux
(paused/resumed via SIGSTOP/SIGCONT) and the Windows MCI API on Windows.
"""

import logging
import os
import platform
import shutil
import signal
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

logger = logging.getLogger(__name__)

MCI_POLL_INTERVAL_MS = 1000
MCI_ALIAS = "focus_timer_track"


class LocalMusicPlayer(QObject):
    track_finished = Signal()
    playback_error = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process: QProcess | None = None
        self._mci_loaded = False
        self._mci_poll_timer: QTimer | None = None
        if platform.system() == "Windows":
            self._mci_poll_timer = QTimer(self)
            self._mci_poll_timer.setInterval(MCI_POLL_INTERVAL_MS)
            self._mci_poll_timer.timeout.connect(self._poll_mci_status)

    def play(self, file_path: Path) -> None:
        self.stop()
        try:
            if platform.system() == "Windows":
                self._play_windows(file_path)
            else:
                self._play_linux(file_path)
        except OSError:
            logger.exception("Failed to start music playback for %s", file_path)

    def pause(self) -> None:
        if platform.system() == "Windows":
            if self._mci_loaded:
                self._mci_command(f"pause {MCI_ALIAS}")
            return
        if self._process is not None:
            try:
                os.kill(self._process.processId(), signal.SIGSTOP)
            except OSError:
                logger.exception("Failed to pause music playback")

    def resume(self) -> None:
        if platform.system() == "Windows":
            if self._mci_loaded:
                self._mci_command(f"resume {MCI_ALIAS}")
            return
        if self._process is not None:
            try:
                os.kill(self._process.processId(), signal.SIGCONT)
            except OSError:
                logger.exception("Failed to resume music playback")

    def stop(self) -> None:
        if platform.system() == "Windows":
            self._stop_windows()
            return
        if self._process is None:
            return
        try:
            self._process.finished.disconnect(self._on_process_finished)
        except (RuntimeError, TypeError):
            pass
        try:
            self._process.kill()
        except OSError:
            logger.exception("Failed to stop music playback")
        self._process = None

    # -- Linux -----------------------------------------------------------

    def _play_linux(self, file_path: Path) -> None:
        player = shutil.which("ffplay") or shutil.which("cvlc")
        if player is None:
            logger.warning("No audio player (ffplay/cvlc) found; skipping playback")
            self.playback_error.emit(
                "No audio player found. Install ffmpeg (ffplay) or VLC to enable music."
            )
            return
        process = QProcess(self)
        process.finished.connect(self._on_process_finished)
        args = self._linux_player_args(player, file_path)
        process.start(args[0], args[1:])
        self._process = process

    def _linux_player_args(self, player: str, file_path: Path) -> list[str]:
        if player.endswith("cvlc"):
            return [player, "--play-and-exit", "--intf", "dummy", str(file_path)]
        return [player, "-nodisp", "-autoexit", "-loglevel", "quiet", str(file_path)]

    def _on_process_finished(self, exit_code: int, exit_status: object) -> None:
        self._process = None
        self.track_finished.emit()

    # -- Windows -----------------------------------------------------------

    def _play_windows(self, file_path: Path) -> None:
        self._mci_command(f'open "{file_path}" type mpegvideo alias {MCI_ALIAS}')
        self._mci_command(f"play {MCI_ALIAS}")
        self._mci_loaded = True
        if self._mci_poll_timer is not None:
            self._mci_poll_timer.start()

    def _stop_windows(self) -> None:
        if self._mci_poll_timer is not None:
            self._mci_poll_timer.stop()
        if self._mci_loaded:
            self._mci_command(f"stop {MCI_ALIAS}")
            self._mci_command(f"close {MCI_ALIAS}")
            self._mci_loaded = False

    def _poll_mci_status(self) -> None:
        if self._mci_query_status() == "stopped":
            self._stop_windows()
            self.track_finished.emit()

    def _mci_command(self, command: str) -> None:
        import ctypes

        buffer = ctypes.create_unicode_buffer(128)
        ctypes.windll.winmm.mciSendStringW(command, buffer, len(buffer), 0)

    def _mci_query_status(self) -> str:
        import ctypes

        buffer = ctypes.create_unicode_buffer(128)
        ctypes.windll.winmm.mciSendStringW(
            f"status {MCI_ALIAS} mode", buffer, len(buffer), 0
        )
        return buffer.value.strip().lower()
