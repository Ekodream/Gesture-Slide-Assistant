from __future__ import annotations

from src.app import _reached_frame_limit, _should_move_pointer
from src.gesture_classifier import Gesture


def test_pointer_moves_for_raw_index_only_without_waiting_for_stable_gesture() -> None:
    assert _should_move_pointer(Gesture.INDEX_ONLY, object()) is True


def test_pointer_does_not_move_without_hand() -> None:
    assert _should_move_pointer(Gesture.INDEX_ONLY, None) is False


def test_frame_limit_helper() -> None:
    assert _reached_frame_limit(5, None) is False
    assert _reached_frame_limit(4, 5) is False
    assert _reached_frame_limit(5, 5) is True
