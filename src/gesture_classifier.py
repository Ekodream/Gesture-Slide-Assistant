from __future__ import annotations

from enum import Enum
from typing import Iterable, Protocol


class LandmarkLike(Protocol):
    x: float
    y: float
    z: float


class Gesture(str, Enum):
    INDEX_ONLY = "INDEX_ONLY"
    V_SIGN = "V_SIGN"
    THREE_FINGERS = "THREE_FINGERS"
    FIST = "FIST"
    UNKNOWN = "UNKNOWN"


FINGER_POINTS = {
    "index": (8, 6),
    "middle": (12, 10),
    "ring": (16, 14),
    "pinky": (20, 18),
}


def classify_hand(hand_landmarks: object | None) -> Gesture:
    landmarks = _extract_landmarks(hand_landmarks)
    if len(landmarks) < 21:
        return Gesture.UNKNOWN

    states = tuple(
        _is_finger_extended(landmarks, tip_index, pip_index)
        for tip_index, pip_index in FINGER_POINTS.values()
    )
    return _classify_finger_states(states)


def _extract_landmarks(hand_landmarks: object | None) -> list[LandmarkLike]:
    if hand_landmarks is None:
        return []

    source = getattr(hand_landmarks, "landmark", hand_landmarks)
    if not isinstance(source, Iterable):
        return []

    return list(source)


def _is_finger_extended(
    landmarks: list[LandmarkLike],
    tip_index: int,
    pip_index: int,
) -> bool:
    return landmarks[tip_index].y < landmarks[pip_index].y


def _classify_finger_states(states: tuple[bool, bool, bool, bool]) -> Gesture:
    index, middle, ring, pinky = states
    if index and not middle and not ring and not pinky:
        return Gesture.INDEX_ONLY
    if index and middle and not ring and not pinky:
        return Gesture.V_SIGN
    if index and middle and ring and not pinky:
        return Gesture.THREE_FINGERS
    if not index and not middle and not ring and not pinky:
        return Gesture.FIST
    return Gesture.UNKNOWN
