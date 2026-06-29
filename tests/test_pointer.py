from __future__ import annotations

from dataclasses import dataclass

from src.pointer import PointerController


@dataclass
class Landmark:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


def make_landmarks(index_x: float, index_y: float) -> list[Landmark]:
    landmarks = [Landmark() for _ in range(21)]
    landmarks[8] = Landmark(index_x, index_y, 0.0)
    return landmarks


def test_dry_run_maps_index_tip_with_mirror() -> None:
    pointer = PointerController(dry_run=True, smoothing=0.5, mirror_x=True)

    result = pointer.move_to_index_tip(make_landmarks(0.25, 0.5))

    assert result.target_x == 1440
    assert result.target_y == 540
    assert result.moved is False
    assert result.screen_source == "dry-run-default"


def test_dry_run_maps_index_tip_without_mirror() -> None:
    pointer = PointerController(dry_run=True, smoothing=0.5, mirror_x=False)

    result = pointer.move_to_index_tip(make_landmarks(0.25, 0.5))

    assert result.target_x == 480
    assert result.target_y == 540


def test_pointer_smoothing_uses_previous_position() -> None:
    pointer = PointerController(dry_run=True, smoothing=0.5, mirror_x=False)
    pointer.move_to_index_tip(make_landmarks(0.0, 0.0))

    result = pointer.move_to_index_tip(make_landmarks(1.0, 1.0))

    assert result.target_x == 960
    assert result.target_y == 540


def test_missing_index_tip_does_not_move() -> None:
    pointer = PointerController(dry_run=True)

    result = pointer.move_to_index_tip([Landmark() for _ in range(3)])

    assert result.moved is False
    assert result.target_x == 0
    assert result.target_y == 0
