"""Compact dark timer window: displays state and forwards user intent."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.application.timer_controller import TimerController
from src.domain.timer_state import Phase, TimerStatus

PHASE_LABELS = {
    Phase.FOCUS: "FOCUS",
    Phase.SHORT_BREAK: "SHORT BREAK",
    Phase.LONG_BREAK: "LONG BREAK",
}


def format_remaining(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    minutes, secs = divmod(total_seconds, 60)
    return f"{minutes:02d}:{secs:02d}"


class MainWindow(QWidget):
    def __init__(
        self, controller: TimerController, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Focus Timer")
        self.resize(340, 430)
        self.setMinimumSize(300, 400)

        self._build_ui()
        self._connect_signals()
        self._refresh_all()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.phase_label = QLabel(objectName="phaseLabel", alignment=Qt.AlignCenter)
        self.time_label = QLabel(objectName="timeLabel", alignment=Qt.AlignCenter)
        self.session_label = QLabel(objectName="sessionLabel", alignment=Qt.AlignCenter)

        self.task_input = QLineEdit(objectName="taskInput")
        self.task_input.setPlaceholderText("What are you working on?")

        layout.addWidget(self.phase_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.session_label)
        layout.addStretch()
        layout.addWidget(self.task_input)
        layout.addLayout(self._build_button_row())

        self._build_shortcuts()

    def _build_button_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.start_pause_button = QPushButton("Start", objectName="startPauseButton")
        self.skip_button = QPushButton("Skip")
        row.addWidget(self.reset_button)
        row.addWidget(self.start_pause_button, stretch=1)
        row.addWidget(self.skip_button)
        return row

    def _build_shortcuts(self) -> None:
        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self._on_space_shortcut)
        QShortcut(QKeySequence(Qt.Key_R), self, activated=self._on_reset_shortcut)
        QShortcut(QKeySequence(Qt.Key_S), self, activated=self._on_skip_shortcut)

    def _connect_signals(self) -> None:
        self.start_pause_button.clicked.connect(self.controller.toggle_start_pause)
        self.reset_button.clicked.connect(self.controller.reset)
        self.skip_button.clicked.connect(self.controller.skip)

        self.controller.phase_changed.connect(self._update_phase)
        self.controller.status_changed.connect(self._update_status)
        self.controller.remaining_changed.connect(self._update_remaining)
        self.controller.session_changed.connect(self._update_session)

    def _on_space_shortcut(self) -> None:
        if not self.task_input.hasFocus():
            self.controller.toggle_start_pause()

    def _on_reset_shortcut(self) -> None:
        if not self.task_input.hasFocus():
            self.controller.reset()

    def _on_skip_shortcut(self) -> None:
        if not self.task_input.hasFocus():
            self.controller.skip()

    def _refresh_all(self) -> None:
        self._update_phase(self.controller.phase)
        self._update_status(self.controller.status)
        self._update_remaining(self.controller.remaining_seconds())
        self._update_session(
            self.controller.current_session, self.controller.total_sessions
        )

    def _update_phase(self, phase: Phase) -> None:
        self.phase_label.setText(PHASE_LABELS[phase])

    def _update_status(self, status: TimerStatus) -> None:
        self.start_pause_button.setText(
            "Pause" if status == TimerStatus.RUNNING else "Start"
        )

    def _update_remaining(self, seconds: float) -> None:
        self.time_label.setText(format_remaining(seconds))

    def _update_session(self, current: int, total: int) -> None:
        self.session_label.setText(f"Session {current}/{total}")
