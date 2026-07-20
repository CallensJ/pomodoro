"""Coordinates the domain timer with a Qt refresh loop and UI signals."""

from typing import Protocol

from PySide6.QtCore import QObject, QTimer, Signal

from src.domain.timer import PomodoroTimer
from src.domain.timer_state import CycleConfig, Phase, TimerStatus

TICK_INTERVAL_MS = 200


class AlarmPlayer(Protocol):
    def play_alarm(self) -> None: ...


class Notifier(Protocol):
    def notify(self, title: str, message: str) -> None: ...


class SettingsProvider(Protocol):
    def alarm_enabled(self) -> bool: ...
    def auto_start_next_phase(self) -> bool: ...


class TimerController(QObject):
    phase_changed = Signal(Phase)
    status_changed = Signal(TimerStatus)
    remaining_changed = Signal(float)
    session_changed = Signal(int, int)

    def __init__(
        self,
        timer: PomodoroTimer,
        alarm_player: AlarmPlayer | None = None,
        notifier: Notifier | None = None,
        settings: SettingsProvider | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._timer = timer
        self._alarm_player = alarm_player
        self._notifier = notifier
        self._settings = settings
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

    def apply_new_config(self, config: CycleConfig) -> None:
        self._refresh_timer.stop()
        self._timer = PomodoroTimer(config)
        self._emit_all()

    def _on_tick(self) -> None:
        previous_phase = self._timer.phase
        self._timer.tick()
        if self._timer.phase != previous_phase:
            self._handle_phase_completed(previous_phase)
        if self._timer.status != TimerStatus.RUNNING:
            self._refresh_timer.stop()
        self._emit_all()

    def _handle_phase_completed(self, completed_phase: Phase) -> None:
        self._play_alarm_if_enabled()
        self._send_notification(completed_phase)
        if self._settings is not None and self._settings.auto_start_next_phase():
            self.start()

    def _play_alarm_if_enabled(self) -> None:
        if self._alarm_player is None:
            return
        if self._settings is not None and not self._settings.alarm_enabled():
            return
        self._alarm_player.play_alarm()

    def _send_notification(self, completed_phase: Phase) -> None:
        if self._notifier is None:
            return
        label = completed_phase.name.replace("_", " ").title()
        self._notifier.notify("Focus Timer", f"{label} finished")

    def _emit_all(self) -> None:
        self.phase_changed.emit(self._timer.phase)
        self.status_changed.emit(self._timer.status)
        self.remaining_changed.emit(self._timer.remaining_seconds())
        self.session_changed.emit(
            self._timer.current_session, self._timer.total_sessions
        )
