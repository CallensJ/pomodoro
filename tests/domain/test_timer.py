from src.domain.timer import PomodoroTimer
from src.domain.timer_state import CycleConfig, EndAction, Phase, TimerStatus


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def custom_config(
    focus: int = 40,
    short_break: int = 10,
    long_break: int | None = None,
    total_sessions: int = 2,
    end_action: EndAction = EndAction.STOP,
) -> CycleConfig:
    return CycleConfig(
        focus_duration=focus,
        short_break_duration=short_break,
        long_break_duration=long_break,
        total_sessions=total_sessions,
        end_action=end_action,
    )


def test_initial_state_is_stopped_focus() -> None:
    timer = PomodoroTimer(custom_config())
    assert timer.phase == Phase.FOCUS
    assert timer.status == TimerStatus.STOPPED
    assert timer.completed_sessions == 0


def test_start_sets_monotonic_deadline_not_ui_dependent() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(custom_config(focus=40), now=clock)
    timer.start()
    assert timer.status == TimerStatus.RUNNING
    assert timer.remaining_seconds() == 40
    clock.advance(15)
    assert timer.remaining_seconds() == 25


def test_pause_then_resume_does_not_lose_or_add_time() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(custom_config(focus=40), now=clock)
    timer.start()
    clock.advance(15)
    timer.pause()
    assert timer.status == TimerStatus.PAUSED
    assert timer.remaining_seconds() == 25
    clock.advance(100)
    assert timer.remaining_seconds() == 25
    timer.start()
    assert timer.status == TimerStatus.RUNNING
    assert timer.remaining_seconds() == 25
    clock.advance(5)
    assert timer.remaining_seconds() == 20


def test_remaining_time_never_negative() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(custom_config(focus=40), now=clock)
    timer.start()
    clock.advance(999)
    assert timer.remaining_seconds() == 0


def test_completed_focus_session_increments_counter_and_starts_break() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(
        custom_config(focus=40, short_break=10, total_sessions=2), now=clock
    )
    timer.start()
    clock.advance(40)
    timer.tick()
    assert timer.completed_sessions == 1
    assert timer.phase == Phase.SHORT_BREAK
    assert timer.status == TimerStatus.STOPPED
    assert timer.remaining_seconds() == 10


def test_completed_break_returns_to_next_focus_session() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(
        custom_config(focus=40, short_break=10, total_sessions=2), now=clock
    )
    timer.start()
    clock.advance(40)
    timer.tick()
    timer.start()
    clock.advance(10)
    timer.tick()
    assert timer.phase == Phase.FOCUS
    assert timer.status == TimerStatus.STOPPED
    assert timer.current_session == 2


def test_custom_cycle_two_by_forty_ten_minute_break_then_stop() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(
        custom_config(
            focus=40, short_break=10, total_sessions=2, end_action=EndAction.STOP
        ),
        now=clock,
    )
    timer.start()
    clock.advance(40)
    timer.tick()
    assert timer.phase == Phase.SHORT_BREAK
    timer.start()
    clock.advance(10)
    timer.tick()
    assert timer.phase == Phase.FOCUS
    timer.start()
    clock.advance(40)
    timer.tick()
    assert timer.phase == Phase.FOCUS
    assert timer.status == TimerStatus.STOPPED
    assert timer.completed_sessions == 0
    assert timer.remaining_seconds() == 40


def test_custom_cycle_end_action_long_break_then_stops() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(
        custom_config(
            focus=40,
            short_break=10,
            long_break=100,
            total_sessions=1,
            end_action=EndAction.LONG_BREAK,
        ),
        now=clock,
    )
    timer.start()
    clock.advance(40)
    timer.tick()
    assert timer.phase == Phase.LONG_BREAK
    assert timer.remaining_seconds() == 100
    timer.start()
    clock.advance(100)
    timer.tick()
    assert timer.phase == Phase.FOCUS
    assert timer.status == TimerStatus.STOPPED
    assert timer.completed_sessions == 0


def test_custom_cycle_end_action_repeat_without_long_break_wraps_with_short_break() -> (
    None
):
    clock = FakeClock()
    timer = PomodoroTimer(
        custom_config(
            focus=40, short_break=10, total_sessions=1, end_action=EndAction.REPEAT
        ),
        now=clock,
    )
    timer.start()
    clock.advance(40)
    timer.tick()
    assert timer.phase == Phase.SHORT_BREAK
    timer.start()
    clock.advance(10)
    timer.tick()
    assert timer.phase == Phase.FOCUS
    assert timer.completed_sessions == 0


def test_classic_pomodoro_cycle_matches_defaults() -> None:
    config = CycleConfig.classic()
    assert config.focus_duration == 25 * 60
    assert config.short_break_duration == 5 * 60
    assert config.long_break_duration == 15 * 60
    assert config.total_sessions == 4
    assert config.end_action == EndAction.REPEAT


def test_classic_pomodoro_long_break_after_four_sessions_then_repeats() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(CycleConfig.classic(), now=clock)
    for _ in range(3):
        timer.start()
        clock.advance(25 * 60)
        timer.tick()
        assert timer.phase == Phase.SHORT_BREAK
        timer.start()
        clock.advance(5 * 60)
        timer.tick()
        assert timer.phase == Phase.FOCUS

    timer.start()
    clock.advance(25 * 60)
    timer.tick()
    assert timer.phase == Phase.LONG_BREAK
    assert timer.completed_sessions == 0

    timer.start()
    clock.advance(15 * 60)
    timer.tick()
    assert timer.phase == Phase.FOCUS
    assert timer.status == TimerStatus.STOPPED
    assert timer.current_session == 1


def test_reset_restores_full_duration_of_current_phase() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(custom_config(focus=40), now=clock)
    timer.start()
    clock.advance(15)
    timer.reset()
    assert timer.status == TimerStatus.STOPPED
    assert timer.remaining_seconds() == 40


def test_skip_focus_does_not_count_completed_session() -> None:
    clock = FakeClock()
    timer = PomodoroTimer(
        custom_config(focus=40, short_break=10, total_sessions=2), now=clock
    )
    timer.start()
    clock.advance(1)
    timer.skip()
    assert timer.phase == Phase.SHORT_BREAK
    assert timer.completed_sessions == 0


def test_skip_break_advances_to_next_focus_session() -> None:
    timer = PomodoroTimer(custom_config(focus=40, short_break=10, total_sessions=2))
    timer.start()
    timer.skip()
    assert timer.phase == Phase.SHORT_BREAK
    timer.skip()
    assert timer.phase == Phase.FOCUS


def test_invalid_config_raises_when_long_break_end_action_missing_duration() -> None:
    try:
        custom_config(long_break=None, end_action=EndAction.LONG_BREAK)
    except ValueError:
        return
    raise AssertionError("expected ValueError for missing long_break_duration")


def test_invalid_config_raises_for_zero_total_sessions() -> None:
    try:
        custom_config(total_sessions=0)
    except ValueError:
        return
    raise AssertionError("expected ValueError for total_sessions < 1")
