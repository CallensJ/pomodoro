"""Application entry point: wires domain, application and presentation layers."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.application.timer_controller import TimerController
from src.domain.timer import PomodoroTimer
from src.domain.timer_state import CycleConfig
from src.presentation.main_window import MainWindow

STYLES_PATH = Path(__file__).parent / "presentation" / "styles.qss"


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLES_PATH.read_text())

    timer = PomodoroTimer(CycleConfig.classic())
    controller = TimerController(timer)
    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
