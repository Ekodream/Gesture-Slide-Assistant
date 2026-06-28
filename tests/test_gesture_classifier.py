from __future__ import annotations

from dataclasses import dataclass

from src.gesture_classifier import Gesture, classify_hand


@dataclass
class Landmark:
    x: float = 0.0
    y: float = 0.5
    z: float = 0.0


def make_landmarks(
    *,
    index: bool,
    middle: bool,
    ring: bool,
    pinky: bool,
) -> list[Landmark]:
    landmarks = [Landmark() for _ in range(21)]
    finger_points = {
        "index": (8, 6, index),
        "middle": (12, 10, middle),
        "ring": (16, 14, ring),
        "pinky": (20, 18, pinky),
    }

    for tip_index, pip_index, extended in finger_points.values():
        landmarks[pip_index].y = 0.5
        landmarks[tip_index].y = 0.2 if extended else 0.8

    return landmarks


def test_classifies_index_only() -> None:
    landmarks = make_landmarks(index=True, middle=False, ring=False, pinky=False)

    assert classify_hand(landmarks) == Gesture.INDEX_ONLY


def test_classifies_v_sign() -> None:
    landmarks = make_landmarks(index=True, middle=True, ring=False, pinky=False)

    assert classify_hand(landmarks) == Gesture.V_SIGN


def test_classifies_three_fingers() -> None:
    landmarks = make_landmarks(index=True, middle=True, ring=True, pinky=False)

    assert classify_hand(landmarks) == Gesture.THREE_FINGERS


def test_classifies_fist() -> None:
    landmarks = make_landmarks(index=False, middle=False, ring=False, pinky=False)

    assert classify_hand(landmarks) == Gesture.FIST


def test_classifies_unknown_state() -> None:
    landmarks = make_landmarks(index=False, middle=True, ring=False, pinky=False)

    assert classify_hand(landmarks) == Gesture.UNKNOWN


def test_short_landmark_list_is_unknown() -> None:
    assert classify_hand([Landmark() for _ in range(5)]) == Gesture.UNKNOWN
