from src.application.timer_controller import TimerController
from src.domain.timer import PomodoroTimer
from src.domain.timer_state import CycleConfig, EndAction, Phase, TimerStatus


class FakeAlarmPlayer:
    def __init__(self) -> None:
        self.play_count = 0

    def play_alarm(self) -> None:
        self.play_count += 1


class FakeNotifier:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def notify(self, title: str, message: str) -> None:
        self.messages.append((title, message))


class FakeSettings:
    def __init__(self, alarm_enabled: bool = True, auto_start: bool = False) -> None:
        self._alarm_enabled = alarm_enabled
        self._auto_start = auto_start

    def alarm_enabled(self) -> bool:
        return self._alarm_enabled

    def auto_start_next_phase(self) -> bool:
        return self._auto_start


def make_config() -> CycleConfig:
    return CycleConfig(
        focus_duration=1,
        short_break_duration=1,
        long_break_duration=None,
        total_sessions=2,
        end_action=EndAction.STOP,
    )


def make_controller(**kwargs) -> TimerController:
    return TimerController(PomodoroTimer(make_config()), **kwargs)


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


def test_alarm_and_notification_fire_on_natural_phase_completion(qtbot) -> None:
    alarm = FakeAlarmPlayer()
    notifier = FakeNotifier()
    controller = make_controller(alarm_player=alarm, notifier=notifier)
    controller.start()

    qtbot.waitUntil(lambda: controller.phase == Phase.SHORT_BREAK, timeout=2000)
    assert alarm.play_count == 1
    assert notifier.messages == [("Focus Timer", "Focus finished")]


def test_alarm_does_not_fire_on_manual_skip(qtbot) -> None:
    alarm = FakeAlarmPlayer()
    notifier = FakeNotifier()
    controller = make_controller(alarm_player=alarm, notifier=notifier)
    controller.start()
    controller.skip()

    assert alarm.play_count == 0
    assert notifier.messages == []


def test_alarm_respects_disabled_setting(qtbot) -> None:
    alarm = FakeAlarmPlayer()
    settings = FakeSettings(alarm_enabled=False)
    controller = make_controller(alarm_player=alarm, settings=settings)
    controller.start()

    qtbot.waitUntil(lambda: controller.phase == Phase.SHORT_BREAK, timeout=2000)
    assert alarm.play_count == 0


def test_auto_start_next_phase_when_enabled(qtbot) -> None:
    settings = FakeSettings(auto_start=True)
    controller = make_controller(settings=settings)
    controller.start()

    qtbot.waitUntil(lambda: controller.phase == Phase.SHORT_BREAK, timeout=2000)
    assert controller.status == TimerStatus.RUNNING


def test_no_auto_start_when_disabled(qtbot) -> None:
    settings = FakeSettings(auto_start=False)
    controller = make_controller(settings=settings)
    controller.start()

    qtbot.waitUntil(lambda: controller.phase == Phase.SHORT_BREAK, timeout=2000)
    assert controller.status == TimerStatus.STOPPED


def test_apply_new_config_resets_to_fresh_focus_phase(qtbot) -> None:
    controller = make_controller()
    controller.start()

    new_config = CycleConfig(
        focus_duration=99,
        short_break_duration=5,
        long_break_duration=None,
        total_sessions=1,
        end_action=EndAction.STOP,
    )
    controller.apply_new_config(new_config)

    assert controller.phase == Phase.FOCUS
    assert controller.status == TimerStatus.STOPPED
    assert controller.remaining_seconds() == 99
