"""Single QSettings wrapper for all local preferences."""

from PySide6.QtCore import QSettings

from src.domain.timer_state import CycleConfig, EndAction, TimerMode

ORG_NAME = "FocusTimer"
APP_NAME = "FocusTimer"


def _as_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes")


class SettingsStore:
    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = (
            settings if settings is not None else QSettings(ORG_NAME, APP_NAME)
        )

    def load_mode(self) -> TimerMode:
        mode_name = self._settings.value("cycle/mode", TimerMode.CLASSIC.name)
        if mode_name in TimerMode.__members__:
            return TimerMode[mode_name]
        return TimerMode.CLASSIC

    def load_cycle_config(self) -> CycleConfig:
        if self.load_mode() == TimerMode.CLASSIC:
            return CycleConfig.classic()
        return self._load_custom_cycle_config()

    def _load_custom_cycle_config(self) -> CycleConfig:
        end_action_name = self._settings.value("cycle/end_action", EndAction.STOP.name)
        end_action = (
            EndAction[end_action_name]
            if end_action_name in EndAction.__members__
            else EndAction.STOP
        )
        long_break_raw = self._settings.value("cycle/long_break_duration", "")
        long_break = int(long_break_raw) if str(long_break_raw) != "" else None
        return CycleConfig(
            focus_duration=int(self._settings.value("cycle/focus_duration", 25 * 60)),
            short_break_duration=int(
                self._settings.value("cycle/short_break_duration", 5 * 60)
            ),
            long_break_duration=long_break,
            total_sessions=int(self._settings.value("cycle/total_sessions", 4)),
            end_action=end_action,
        )

    def save_cycle_config(self, mode: TimerMode, config: CycleConfig) -> None:
        self._settings.setValue("cycle/mode", mode.name)
        self._settings.setValue("cycle/focus_duration", config.focus_duration)
        self._settings.setValue(
            "cycle/short_break_duration", config.short_break_duration
        )
        self._settings.setValue(
            "cycle/long_break_duration",
            config.long_break_duration
            if config.long_break_duration is not None
            else "",
        )
        self._settings.setValue("cycle/total_sessions", config.total_sessions)
        self._settings.setValue("cycle/end_action", config.end_action.name)

    def restore_classic_defaults(self) -> None:
        self.save_cycle_config(TimerMode.CLASSIC, CycleConfig.classic())

    def alarm_enabled(self) -> bool:
        return _as_bool(self._settings.value("alarm/enabled"), default=True)

    def set_alarm_enabled(self, enabled: bool) -> None:
        self._settings.setValue("alarm/enabled", enabled)

    def auto_start_next_phase(self) -> bool:
        return _as_bool(
            self._settings.value("behavior/auto_start_next_phase"), default=False
        )

    def set_auto_start_next_phase(self, enabled: bool) -> None:
        self._settings.setValue("behavior/auto_start_next_phase", enabled)

    def always_on_top(self) -> bool:
        return _as_bool(self._settings.value("behavior/always_on_top"), default=False)

    def set_always_on_top(self, enabled: bool) -> None:
        self._settings.setValue("behavior/always_on_top", enabled)
