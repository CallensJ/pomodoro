"""Timer phases, statuses and cycle configuration."""

from dataclasses import dataclass
from enum import Enum, auto


class Phase(Enum):
    FOCUS = auto()
    SHORT_BREAK = auto()
    LONG_BREAK = auto()


class TimerStatus(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()


class EndAction(Enum):
    STOP = auto()
    LONG_BREAK = auto()
    REPEAT = auto()


@dataclass(frozen=True)
class CycleConfig:
    focus_duration: int
    short_break_duration: int
    long_break_duration: int | None
    total_sessions: int
    end_action: EndAction

    def __post_init__(self) -> None:
        if self.total_sessions < 1:
            raise ValueError("total_sessions must be at least 1")
        if self.end_action == EndAction.LONG_BREAK and self.long_break_duration is None:
            raise ValueError(
                "long_break_duration is required when end_action is LONG_BREAK"
            )

    @classmethod
    def classic(cls) -> "CycleConfig":
        return cls(
            focus_duration=25 * 60,
            short_break_duration=5 * 60,
            long_break_duration=15 * 60,
            total_sessions=4,
            end_action=EndAction.REPEAT,
        )
