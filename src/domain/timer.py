"""Pure Pomodoro timer rules driven by an injectable monotonic clock.

The timer never starts the next phase automatically after a transition;
every transition leaves the timer STOPPED so a caller (application layer)
decides whether to auto-start it, per the configurable auto-start preference.
"""

import time
from collections.abc import Callable

from src.domain.timer_state import CycleConfig, EndAction, Phase, TimerStatus


class PomodoroTimer:
    def __init__(
        self,
        config: CycleConfig,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._config = config
        self._now = now
        self.phase = Phase.FOCUS
        self.status = TimerStatus.STOPPED
        self.completed_sessions = 0
        self._remaining: float = float(config.focus_duration)
        self._deadline: float | None = None

    @property
    def total_sessions(self) -> int:
        return self._config.total_sessions

    @property
    def current_session(self) -> int:
        return min(self.completed_sessions + 1, self.total_sessions)

    def remaining_seconds(self) -> float:
        if self.status == TimerStatus.RUNNING and self._deadline is not None:
            return max(0.0, self._deadline - self._now())
        return self._remaining

    def start(self) -> None:
        if self.status == TimerStatus.RUNNING:
            return
        self._deadline = self._now() + self._remaining
        self.status = TimerStatus.RUNNING

    def pause(self) -> None:
        if self.status != TimerStatus.RUNNING:
            return
        self._remaining = self.remaining_seconds()
        self._deadline = None
        self.status = TimerStatus.PAUSED

    def reset(self) -> None:
        self._remaining = float(self._duration_for(self.phase))
        self._deadline = None
        self.status = TimerStatus.STOPPED

    def skip(self) -> None:
        if self.phase == Phase.FOCUS:
            self._advance_from_focus(genuine=False)
        else:
            self._advance_from_break()

    def tick(self) -> None:
        if self.status != TimerStatus.RUNNING or self.remaining_seconds() > 0:
            return
        if self.phase == Phase.FOCUS:
            self._advance_from_focus(genuine=True)
        else:
            self._advance_from_break()

    def _duration_for(self, phase: Phase) -> int:
        if phase == Phase.FOCUS:
            return self._config.focus_duration
        if phase == Phase.SHORT_BREAK:
            return self._config.short_break_duration
        return self._config.long_break_duration or 0

    def _enter_phase(self, phase: Phase) -> None:
        self.phase = phase
        self._remaining = float(self._duration_for(phase))
        self._deadline = None
        self.status = TimerStatus.STOPPED

    def _advance_from_focus(self, genuine: bool) -> None:
        if genuine:
            self.completed_sessions += 1
        if self.completed_sessions < self.total_sessions:
            self._enter_phase(Phase.SHORT_BREAK)
            return
        self._complete_cycle()

    def _advance_from_break(self) -> None:
        self._enter_phase(Phase.FOCUS)

    def _complete_cycle(self) -> None:
        self.completed_sessions = 0
        end_action = self._config.end_action
        if end_action == EndAction.STOP:
            self._enter_phase(Phase.FOCUS)
        elif end_action == EndAction.LONG_BREAK:
            self._enter_phase(Phase.LONG_BREAK)
        elif self._config.long_break_duration is not None:
            self._enter_phase(Phase.LONG_BREAK)
        else:
            self._enter_phase(Phase.SHORT_BREAK)
