from src.application.timer_controller import TimerController
from src.domain.timer import PomodoroTimer
from src.domain.timer_state import CycleConfig, EndAction, Phase, TimerStatus


def make_controller() -> TimerController:
    config = CycleConfig(
        focus_duration=1,
        short_break_duration=1,
        long_break_duration=None,
        total_sessions=2,
        end_action=EndAction.STOP,
    )
    timer = PomodoroTimer(config)
    return TimerController(timer)


def test_initial_state_exposed_through_controller(qtbot) -> None:
    controller = make_controller()
    assert controller.phase == Phase.FOCUS
    assert controller.status == TimerStatus.STOPPED
    assert controller.current_session == 1
    assert controller.total_sessions == 2


def test_toggle_start_pause_switches_status(qtbot) -> None:
    controller = make_controller()

    with qtbot.waitSignal(controller.status_changed, timeout=1000):
        controller.toggle_start_pause()
    assert controller.status == TimerStatus.RUNNING

    with qtbot.waitSignal(controller.status_changed, timeout=1000):
        controller.toggle_start_pause()
    assert controller.status == TimerStatus.PAUSED


def test_reset_emits_signals_and_restores_full_duration(qtbot) -> None:
    controller = make_controller()
    controller.start()

    with qtbot.waitSignal(controller.remaining_changed, timeout=1000):
        controller.reset()
    assert controller.status == TimerStatus.STOPPED
    assert controller.remaining_seconds() == 1


def test_skip_advances_phase_without_waiting_for_deadline(qtbot) -> None:
    controller = make_controller()
    controller.start()

    with qtbot.waitSignal(controller.phase_changed, timeout=1000):
        controller.skip()
    assert controller.phase == Phase.SHORT_BREAK


def test_refresh_loop_advances_phase_after_deadline(qtbot) -> None:
    controller = make_controller()
    controller.start()

    qtbot.waitUntil(lambda: controller.phase == Phase.SHORT_BREAK, timeout=2000)
    assert controller.status == TimerStatus.STOPPED
