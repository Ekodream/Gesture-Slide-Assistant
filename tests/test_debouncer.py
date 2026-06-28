from __future__ import annotations

from src.debouncer import GestureDebouncer
from src.gesture_classifier import Gesture


class Clock:
    def __init__(self, value: float = 100.0) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def feed(
    debouncer: GestureDebouncer,
    gesture: Gesture,
    frames: int,
):
    result = None
    for _ in range(frames):
        result = debouncer.update(gesture)
    assert result is not None
    return result


def test_not_triggered_before_stable_frames() -> None:
    debouncer = GestureDebouncer(stable_frames=3, cooldown_seconds=1.0)

    result = feed(debouncer, Gesture.V_SIGN, 2)

    assert result.should_trigger is False
    assert result.stable_gesture == Gesture.UNKNOWN


def test_triggers_when_stable_frames_reached() -> None:
    debouncer = GestureDebouncer(stable_frames=3, cooldown_seconds=1.0)

    result = feed(debouncer, Gesture.V_SIGN, 3)

    assert result.should_trigger is True
    assert result.stable_gesture == Gesture.V_SIGN


def test_stable_gesture_triggers_only_once_while_held() -> None:
    clock = Clock()
    debouncer = GestureDebouncer(
        stable_frames=2,
        cooldown_seconds=1.0,
        time_provider=clock,
    )
    first = feed(debouncer, Gesture.V_SIGN, 2)
    clock.advance(2.0)
    second = debouncer.update(Gesture.V_SIGN)

    assert first.should_trigger is True
    assert second.should_trigger is False


def test_cooldown_blocks_repeated_trigger() -> None:
    clock = Clock()
    debouncer = GestureDebouncer(
        stable_frames=2,
        cooldown_seconds=1.0,
        time_provider=clock,
    )
    first = feed(debouncer, Gesture.V_SIGN, 2)
    feed(debouncer, Gesture.UNKNOWN, 2)
    clock.advance(0.5)
    repeated = feed(debouncer, Gesture.V_SIGN, 2)

    assert first.should_trigger is True
    assert repeated.should_trigger is False


def test_unknown_never_triggers() -> None:
    debouncer = GestureDebouncer(stable_frames=2, cooldown_seconds=1.0)

    result = feed(debouncer, Gesture.UNKNOWN, 3)

    assert result.should_trigger is False
    assert result.stable_gesture == Gesture.UNKNOWN


def test_index_only_is_continuous_not_discrete_trigger() -> None:
    debouncer = GestureDebouncer(stable_frames=2, cooldown_seconds=1.0)

    result = feed(debouncer, Gesture.INDEX_ONLY, 2)

    assert result.should_trigger is False
    assert result.stable_gesture == Gesture.INDEX_ONLY
