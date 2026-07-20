"""Application entry point: wires domain, application and presentation layers."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.application.timer_controller import TimerController
from src.domain.timer import PomodoroTimer
from src.infrastructure.audio_player import AudioPlayer
from src.infrastructure.notification_service import NotificationService
from src.infrastructure.settings_store import SettingsStore
from src.presentation.main_window import MainWindow

if getattr(sys, "frozen", False):
    _SRC_DIR = Path(sys._MEIPASS) / "src"
else:
    _SRC_DIR = Path(__file__).parent

STYLES_PATH = _SRC_DIR / "presentation" / "styles.qss"


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLES_PATH.read_text())

    settings_store = SettingsStore()
    timer = PomodoroTimer(settings_store.load_cycle_config())
    controller = TimerController(
        timer,
        alarm_player=AudioPlayer(),
        notifier=NotificationService(),
        settings=settings_store,
    )
    window = MainWindow(controller, settings_store)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
