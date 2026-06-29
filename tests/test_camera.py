from __future__ import annotations

import pytest

from src.camera import CameraError, VideoCamera


def test_read_before_open_raises_camera_error() -> None:
    camera = VideoCamera(0)

    with pytest.raises(CameraError):
        camera.read()


def test_invalid_camera_index_fails_cleanly() -> None:
    camera = VideoCamera(-1)

    with pytest.raises(CameraError):
        camera.open()

    camera.release()
