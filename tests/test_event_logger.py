from __future__ import annotations

import csv

from src.command_executor import Action
from src.event_logger import EventLogger
from src.gesture_classifier import Gesture


def test_event_logger_writes_header_and_event(tmp_path) -> None:
    logger = EventLogger(tmp_path)

    logger.log(
        raw_gesture=Gesture.V_SIGN,
        stable_gesture=Gesture.V_SIGN,
        action=Action.NEXT_PAGE,
        dry_run=True,
        success=True,
        note="dry-run ok",
    )

    with logger.path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    assert rows[0] == [
        "timestamp",
        "raw_gesture",
        "stable_gesture",
        "action",
        "dry_run",
        "success",
        "note_or_error",
    ]
    assert rows[1][1:] == [
        "V_SIGN",
        "V_SIGN",
        "NEXT_PAGE",
        "True",
        "True",
        "dry-run ok",
    ]
