"""Coordinates the domain timer with a Qt refresh loop and UI signals."""

from PySide6.QtCore import QObject, QTimer, Signal

from src.domain.timer import PomodoroTimer
from src.domain.timer_state import Phase, TimerStatus

TICK_INTERVAL_MS = 200


class TimerController(QObject):
    phase_changed = Signal(Phase)
    status_changed = Signal(TimerStatus)
    remaining_changed = Signal(float)
    session_changed = Signal(int, int)

    def __init__(self, timer: PomodoroTimer, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(TICK_INTERVAL_MS)
        self._refresh_timer.timeout.connect(self._on_tick)

    @property
    def phase(self) -> Phase:
        return self._timer.phase

    @property
    def status(self) -> TimerStatus:
        return self._timer.status

    @property
    def current_session(self) -> int:
        return self._timer.current_session

    @property
    def total_sessions(self) -> int:
        return self._timer.total_sessions

    def remaining_seconds(self) -> float:
        return self._timer.remaining_seconds()

    def toggle_start_pause(self) -> None:
        if self._timer.status == TimerStatus.RUNNING:
            self.pause()
        else:
            self.start()

    def start(self) -> None:
        self._timer.start()
        self._refresh_timer.start()
        self._emit_all()

    def pause(self) -> None:
        self._timer.pause()
        self._refresh_timer.stop()
        self._emit_all()

    def reset(self) -> None:
        self._timer.reset()
        self._refresh_timer.stop()
        self._emit_all()

    def skip(self) -> None:
        self._timer.skip()
        self._refresh_timer.stop()
        self._emit_all()

    def _on_tick(self) -> None:
        self._timer.tick()
        if self._timer.status != TimerStatus.RUNNING:
            self._refresh_timer.stop()
        self._emit_all()

    def _emit_all(self) -> None:
        self.phase_changed.emit(self._timer.phase)
        self.status_changed.emit(self._timer.status)
        self.remaining_changed.emit(self._timer.remaining_seconds())
        self.session_changed.emit(
            self._timer.current_session, self._timer.total_sessions
        )
