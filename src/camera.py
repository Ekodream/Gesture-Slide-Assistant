from __future__ import annotations

from dataclasses import dataclass

import cv2


class CameraError(RuntimeError):
    """Raised when the camera cannot be opened or read."""


@dataclass
class VideoCamera:
    index: int = 0

    def __post_init__(self) -> None:
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        self._capture = cv2.VideoCapture(self.index)
        if not self._capture.isOpened():
            self.release()
            raise CameraError(
                f"无法打开摄像头 {self.index}。请检查编号、系统权限，或是否被其他应用占用。"
            )

    def read(self):
        if self._capture is None or not self._capture.isOpened():
            raise CameraError("摄像头尚未打开。")

        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise CameraError("无法从摄像头读取画面。")
        return frame

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
