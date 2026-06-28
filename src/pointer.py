from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class LandmarkLike(Protocol):
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class PointerMoveResult:
    target_x: int
    target_y: int
    moved: bool
    note: str = ""


class PointerController:
    def __init__(
        self,
        dry_run: bool,
        smoothing: float = 0.35,
        mirror_x: bool = True,
    ) -> None:
        self.dry_run = dry_run
        self.smoothing = min(1.0, max(0.0, smoothing))
        self.mirror_x = mirror_x
        self._last_x: float | None = None
        self._last_y: float | None = None
        self._screen_width, self._screen_height = self._detect_screen_size()

    def move_to_index_tip(self, hand_landmarks: object) -> PointerMoveResult:
        tip = self._index_tip(hand_landmarks)
        if tip is None:
            return PointerMoveResult(0, 0, False, "没有可用的食指指尖坐标")

        target_x, target_y = self._landmark_to_screen(tip)
        smooth_x, smooth_y = self._smooth(target_x, target_y)

        if self.dry_run:
            return PointerMoveResult(smooth_x, smooth_y, False, "dry-run 不移动鼠标")

        try:
            import pyautogui

            pyautogui.FAILSAFE = True
            pyautogui.moveTo(smooth_x, smooth_y, duration=0)
            return PointerMoveResult(smooth_x, smooth_y, True, "指针已移动")
        except Exception as exc:  # pragma: no cover - depends on local desktop
            return PointerMoveResult(smooth_x, smooth_y, False, str(exc))

    def _detect_screen_size(self) -> tuple[int, int]:
        if self.dry_run:
            return 1920, 1080

        try:
            import pyautogui

            pyautogui.FAILSAFE = True
            size = pyautogui.size()
            return int(size.width), int(size.height)
        except Exception:
            return 1920, 1080

    def _landmark_to_screen(self, landmark: LandmarkLike) -> tuple[int, int]:
        x = 1.0 - landmark.x if self.mirror_x else landmark.x
        y = landmark.y
        x = min(1.0, max(0.0, x))
        y = min(1.0, max(0.0, y))
        return int(x * self._screen_width), int(y * self._screen_height)

    def _smooth(self, target_x: int, target_y: int) -> tuple[int, int]:
        if self._last_x is None or self._last_y is None:
            self._last_x = float(target_x)
            self._last_y = float(target_y)
        else:
            self._last_x += (target_x - self._last_x) * self.smoothing
            self._last_y += (target_y - self._last_y) * self.smoothing
        return int(self._last_x), int(self._last_y)

    @staticmethod
    def _index_tip(hand_landmarks: object) -> LandmarkLike | None:
        source = getattr(hand_landmarks, "landmark", hand_landmarks)
        if not isinstance(source, Iterable):
            return None
        landmarks = list(source)
        if len(landmarks) <= 8:
            return None
        return landmarks[8]
