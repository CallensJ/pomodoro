"""Dialog for editing timer mode, cycle durations and preferences."""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from src.domain.timer_state import CycleConfig, EndAction, TimerMode
from src.infrastructure.settings_store import SettingsStore

END_ACTION_LABELS = {
    EndAction.STOP: "Stop",
    EndAction.LONG_BREAK: "Long break",
    EndAction.REPEAT: "Repeat",
}


class SettingsDialog(QDialog):
    def __init__(self, settings_store: SettingsStore, parent=None) -> None:
        super().__init__(parent)
        self._settings_store = settings_store
        self.setWindowTitle("Settings")
        self._build_ui()
        self._load_current_values()
        self._update_field_states()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._build_cycle_fields(form)
        self._build_toggle_fields(form)
        layout.addLayout(form)
        self._build_actions(layout)

    def _build_cycle_fields(self, form: QFormLayout) -> None:
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Classic", "Custom"])
        self.mode_combo.currentIndexChanged.connect(self._update_field_states)
        form.addRow("Mode", self.mode_combo)

        self.focus_spin = self._minutes_spin(1, 180)
        form.addRow("Focus duration (min)", self.focus_spin)

        self.short_break_spin = self._minutes_spin(1, 60)
        form.addRow("Break duration (min)", self.short_break_spin)

        self.long_break_checkbox = QCheckBox("Enable long break")
        self.long_break_checkbox.toggled.connect(self._update_field_states)
        form.addRow(self.long_break_checkbox)

        self.long_break_spin = self._minutes_spin(1, 120)
        form.addRow("Long break duration (min)", self.long_break_spin)

        self.total_sessions_spin = QSpinBox()
        self.total_sessions_spin.setRange(1, 20)
        form.addRow("Total focus sessions", self.total_sessions_spin)

        self.end_action_combo = QComboBox()
        self.end_action_combo.addItems(END_ACTION_LABELS.values())
        form.addRow("End action", self.end_action_combo)

    def _build_toggle_fields(self, form: QFormLayout) -> None:
        self.alarm_checkbox = QCheckBox("Play alarm sound")
        form.addRow(self.alarm_checkbox)

        self.auto_start_checkbox = QCheckBox("Automatically start next phase")
        form.addRow(self.auto_start_checkbox)

        self.always_on_top_checkbox = QCheckBox("Keep window always on top")
        form.addRow(self.always_on_top_checkbox)

    def _build_actions(self, layout: QVBoxLayout) -> None:
        restore_button = QPushButton("Restore Classic Defaults")
        restore_button.clicked.connect(self._restore_classic_defaults)
        layout.addWidget(restore_button)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _minutes_spin(self, minimum: int, maximum: int) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        return spin

    def _load_current_values(self) -> None:
        mode = self._settings_store.load_mode()
        config = self._settings_store.load_cycle_config()
        self._apply_config_to_fields(mode, config)
        self.alarm_checkbox.setChecked(self._settings_store.alarm_enabled())
        self.auto_start_checkbox.setChecked(
            self._settings_store.auto_start_next_phase()
        )
        self.always_on_top_checkbox.setChecked(self._settings_store.always_on_top())

    def _apply_config_to_fields(self, mode: TimerMode, config: CycleConfig) -> None:
        self.mode_combo.setCurrentIndex(0 if mode == TimerMode.CLASSIC else 1)
        self.focus_spin.setValue(config.focus_duration // 60)
        self.short_break_spin.setValue(config.short_break_duration // 60)
        self.long_break_checkbox.setChecked(config.long_break_duration is not None)
        self.long_break_spin.setValue((config.long_break_duration or 60) // 60)
        self.total_sessions_spin.setValue(config.total_sessions)
        self.end_action_combo.setCurrentText(END_ACTION_LABELS[config.end_action])

    def _restore_classic_defaults(self) -> None:
        self._apply_config_to_fields(TimerMode.CLASSIC, CycleConfig.classic())

    def _update_field_states(self) -> None:
        is_custom = self.mode_combo.currentIndex() == 1
        for widget in (
            self.focus_spin,
            self.short_break_spin,
            self.long_break_checkbox,
            self.total_sessions_spin,
            self.end_action_combo,
        ):
            widget.setEnabled(is_custom)
        self.long_break_spin.setEnabled(
            is_custom and self.long_break_checkbox.isChecked()
        )

    def selected_mode(self) -> TimerMode:
        return (
            TimerMode.CUSTOM
            if self.mode_combo.currentIndex() == 1
            else TimerMode.CLASSIC
        )

    def selected_config(self) -> CycleConfig:
        if self.selected_mode() == TimerMode.CLASSIC:
            return CycleConfig.classic()
        long_break = (
            self.long_break_spin.value() * 60
            if self.long_break_checkbox.isChecked()
            else None
        )
        end_action = next(
            action
            for action, label in END_ACTION_LABELS.items()
            if label == self.end_action_combo.currentText()
        )
        return CycleConfig(
            focus_duration=self.focus_spin.value() * 60,
            short_break_duration=self.short_break_spin.value() * 60,
            long_break_duration=long_break,
            total_sessions=self.total_sessions_spin.value(),
            end_action=end_action,
        )

    def alarm_enabled(self) -> bool:
        return self.alarm_checkbox.isChecked()

    def auto_start_next_phase(self) -> bool:
        return self.auto_start_checkbox.isChecked()

    def always_on_top(self) -> bool:
        return self.always_on_top_checkbox.isChecked()

    def accept(self) -> None:
        try:
            self.selected_config()
        except ValueError as error:
            QMessageBox.warning(self, "Invalid Settings", str(error))
            return
        super().accept()
