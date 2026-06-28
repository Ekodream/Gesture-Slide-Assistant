from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from src.gesture_classifier import Gesture


@dataclass(frozen=True)
class DebounceResult:
    raw_gesture: Gesture
    stable_gesture: Gesture
    should_trigger: bool
    note: str = ""


class GestureDebouncer:
    def __init__(
        self,
        stable_frames: int = 8,
        cooldown_seconds: float = 1.0,
        time_provider: Callable[[], float] | None = None,
    ) -> None:
        self.stable_frames = max(1, stable_frames)
        self.cooldown_seconds = max(0.0, cooldown_seconds)
        self._time_provider = time_provider or time.monotonic
        self._candidate = Gesture.UNKNOWN
        self._candidate_count = 0
        self._stable_gesture = Gesture.UNKNOWN
        self._last_trigger_times: dict[Gesture, float] = {}
        self._triggerable_gestures = {
            Gesture.V_SIGN,
            Gesture.THREE_FINGERS,
            Gesture.FIST,
        }

    @property
    def stable_gesture(self) -> Gesture:
        return self._stable_gesture

    def update(self, gesture: Gesture, now: float | None = None) -> DebounceResult:
        current_time = self._time_provider() if now is None else now
        gesture = self._normalize_gesture(gesture)
        self._update_candidate(gesture)

        if self._candidate_count < self.stable_frames:
            return DebounceResult(
                raw_gesture=gesture,
                stable_gesture=self._stable_gesture,
                should_trigger=False,
                note="等待更多稳定帧",
            )

        if self._stable_gesture == gesture:
            return DebounceResult(
                raw_gesture=gesture,
                stable_gesture=self._stable_gesture,
                should_trigger=False,
                note="稳定手势未变化",
            )

        self._stable_gesture = gesture
        return self._build_stable_result(gesture, current_time)

    def _update_candidate(self, gesture: Gesture) -> None:
        if gesture != self._candidate:
            self._candidate = gesture
            self._candidate_count = 1
            return
        self._candidate_count += 1

    def _build_stable_result(self, gesture: Gesture, now: float) -> DebounceResult:
        if gesture == Gesture.UNKNOWN:
            return DebounceResult(gesture, gesture, False, "UNKNOWN 不触发命令")

        if gesture not in self._triggerable_gestures:
            return DebounceResult(gesture, gesture, False, "连续控制手势不触发离散命令")

        if not self._passes_cooldown(gesture, now):
            return DebounceResult(gesture, gesture, False, "冷却时间内阻止重复触发")

        self._last_trigger_times[gesture] = now
        return DebounceResult(gesture, gesture, True, "稳定手势触发命令")

    def _passes_cooldown(self, gesture: Gesture, now: float) -> bool:
        last_time = self._last_trigger_times.get(gesture)
        if last_time is None:
            return True
        return now - last_time >= self.cooldown_seconds

    @staticmethod
    def _normalize_gesture(gesture: Gesture) -> Gesture:
        if isinstance(gesture, Gesture):
            return gesture
        try:
            return Gesture(str(gesture))
        except ValueError:
            return Gesture.UNKNOWN
