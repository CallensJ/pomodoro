from pathlib import Path

from PySide6.QtCore import QSettings

from src.domain.timer_state import CycleConfig, EndAction, TimerMode
from src.infrastructure.settings_store import SettingsStore


def make_store(tmp_path: Path) -> SettingsStore:
    ini_path = tmp_path / "settings.ini"
    return SettingsStore(QSettings(str(ini_path), QSettings.Format.IniFormat))


def test_defaults_are_classic_and_alarm_enabled(tmp_path) -> None:
    store = make_store(tmp_path)
    assert store.load_mode() == TimerMode.CLASSIC
    assert store.load_cycle_config() == CycleConfig.classic()
    assert store.alarm_enabled() is True
    assert store.auto_start_next_phase() is False
    assert store.always_on_top() is False


def test_save_and_load_custom_cycle_config_round_trips(tmp_path) -> None:
    store = make_store(tmp_path)
    config = CycleConfig(
        focus_duration=40 * 60,
        short_break_duration=10 * 60,
        long_break_duration=None,
        total_sessions=2,
        end_action=EndAction.STOP,
    )
    store.save_cycle_config(TimerMode.CUSTOM, config)

    assert store.load_mode() == TimerMode.CUSTOM
    assert store.load_cycle_config() == config


def test_save_and_load_custom_cycle_with_long_break(tmp_path) -> None:
    store = make_store(tmp_path)
    config = CycleConfig(
        focus_duration=50 * 60,
        short_break_duration=10 * 60,
        long_break_duration=20 * 60,
        total_sessions=3,
        end_action=EndAction.LONG_BREAK,
    )
    store.save_cycle_config(TimerMode.CUSTOM, config)

    assert store.load_cycle_config() == config


def test_restore_classic_defaults_overwrites_custom(tmp_path) -> None:
    store = make_store(tmp_path)
    store.save_cycle_config(
        TimerMode.CUSTOM,
        CycleConfig(
            focus_duration=1,
            short_break_duration=1,
            long_break_duration=None,
            total_sessions=1,
            end_action=EndAction.STOP,
        ),
    )
    store.restore_classic_defaults()

    assert store.load_mode() == TimerMode.CLASSIC
    assert store.load_cycle_config() == CycleConfig.classic()


def test_boolean_preferences_round_trip(tmp_path) -> None:
    store = make_store(tmp_path)
    store.set_alarm_enabled(False)
    store.set_auto_start_next_phase(True)
    store.set_always_on_top(True)

    assert store.alarm_enabled() is False
    assert store.auto_start_next_phase() is True
    assert store.always_on_top() is True
