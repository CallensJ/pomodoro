from PySide6.QtCore import Qt

from src.application.timer_controller import TimerController
from src.domain.timer import PomodoroTimer
from src.domain.timer_state import CycleConfig
from src.presentation.main_window import MainWindow, format_remaining


def test_format_remaining_renders_minutes_and_seconds() -> None:
    assert format_remaining(125.9) == "02:05"
    assert format_remaining(0) == "00:00"
    assert format_remaining(-5) == "00:00"


def test_main_window_shows_initial_timer_state(qtbot) -> None:
    controller = TimerController(PomodoroTimer(CycleConfig.classic()))
    window = MainWindow(controller)
    qtbot.addWidget(window)

    assert window.windowTitle() == "Focus Timer"
    assert window.phase_label.text() == "FOCUS"
    assert window.time_label.text() == "25:00"
    assert window.session_label.text() == "Session 1/4"
    assert window.start_pause_button.text() == "Start"


def test_start_pause_button_click_toggles_label(qtbot) -> None:
    controller = TimerController(PomodoroTimer(CycleConfig.classic()))
    window = MainWindow(controller)
    qtbot.addWidget(window)

    qtbot.mouseClick(window.start_pause_button, Qt.MouseButton.LeftButton)
    assert window.start_pause_button.text() == "Pause"
