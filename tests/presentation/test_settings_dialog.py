from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMessageBox

from src.domain.timer_state import CycleConfig, EndAction, TimerMode
from src.infrastructure.settings_store import SettingsStore
from src.presentation.settings_dialog import SettingsDialog


def make_settings_store(tmp_path: Path) -> SettingsStore:
    ini_path = tmp_path / "settings.ini"
    return SettingsStore(QSettings(str(ini_path), QSettings.Format.IniFormat))


def test_dialog_loads_classic_defaults(qtbot, tmp_path) -> None:
    dialog = SettingsDialog(make_settings_store(tmp_path))
    qtbot.addWidget(dialog)

    assert dialog.selected_mode() == TimerMode.CLASSIC
    assert dialog.selected_config() == CycleConfig.classic()
    assert not dialog.focus_spin.isEnabled()


def test_switching_to_custom_enables_fields_and_edits_apply(qtbot, tmp_path) -> None:
    dialog = SettingsDialog(make_settings_store(tmp_path))
    qtbot.addWidget(dialog)

    dialog.mode_combo.setCurrentIndex(1)
    assert dialog.focus_spin.isEnabled()

    dialog.focus_spin.setValue(40)
    dialog.short_break_spin.setValue(10)
    dialog.long_break_checkbox.setChecked(False)
    dialog.total_sessions_spin.setValue(2)
    dialog.end_action_combo.setCurrentText("Stop")

    config = dialog.selected_config()
    assert config == CycleConfig(
        focus_duration=40 * 60,
        short_break_duration=10 * 60,
        long_break_duration=None,
        total_sessions=2,
        end_action=EndAction.STOP,
    )


def test_restore_classic_defaults_resets_fields(qtbot, tmp_path) -> None:
    dialog = SettingsDialog(make_settings_store(tmp_path))
    qtbot.addWidget(dialog)

    dialog.mode_combo.setCurrentIndex(1)
    dialog.focus_spin.setValue(90)
    dialog._restore_classic_defaults()

    assert dialog.selected_mode() == TimerMode.CLASSIC
    assert dialog.focus_spin.value() == 25


def test_invalid_long_break_configuration_is_rejected(
    qtbot, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)
    dialog = SettingsDialog(make_settings_store(tmp_path))
    qtbot.addWidget(dialog)

    dialog.mode_combo.setCurrentIndex(1)
    dialog.long_break_checkbox.setChecked(False)
    dialog.end_action_combo.setCurrentText("Long break")

    dialog.accept()
    assert dialog.result() != dialog.DialogCode.Accepted
