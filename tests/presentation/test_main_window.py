from pathlib import Path

from PySide6.QtCore import QSettings, Qt

from src.application.timer_controller import TimerController
from src.domain.timer import PomodoroTimer
from src.domain.timer_state import CycleConfig
from src.infrastructure.settings_store import SettingsStore
from src.presentation.main_window import MainWindow, format_remaining


def make_settings_store(tmp_path: Path) -> SettingsStore:
    ini_path = tmp_path / "settings.ini"
    qsettings = QSettings(str(ini_path), QSettings.Format.IniFormat)
    return SettingsStore(qsettings)


def test_format_remaining_renders_minutes_and_seconds() -> None:
    assert format_remaining(125.9) == "02:05"
    assert format_remaining(0) == "00:00"
    assert format_remaining(-5) == "00:00"


def test_main_window_shows_initial_timer_state(qtbot, tmp_path) -> None:
    controller = TimerController(PomodoroTimer(CycleConfig.classic()))
    window = MainWindow(controller, make_settings_store(tmp_path))
    qtbot.addWidget(window)

    assert window.windowTitle() == "Focus Timer"
    assert window.phase_label.text() == "FOCUS"
    assert window.time_label.text() == "25:00"
    assert window.session_label.text() == "Session 1/4"
    assert window.start_pause_button.text() == "Start"


def test_start_pause_button_click_toggles_label(qtbot, tmp_path) -> None:
    controller = TimerController(PomodoroTimer(CycleConfig.classic()))
    window = MainWindow(controller, make_settings_store(tmp_path))
    qtbot.addWidget(window)

    qtbot.mouseClick(window.start_pause_button, Qt.MouseButton.LeftButton)
    assert window.start_pause_button.text() == "Pause"


def test_main_window_applies_always_on_top_from_settings(qtbot, tmp_path) -> None:
    store = make_settings_store(tmp_path)
    store.set_always_on_top(True)
    controller = TimerController(PomodoroTimer(CycleConfig.classic()))
    window = MainWindow(controller, store)
    qtbot.addWidget(window)

    assert bool(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
