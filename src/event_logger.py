from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from src.command_executor import Action
from src.gesture_classifier import Gesture


class EventLogger:
    def __init__(self, logs_dir: Path) -> None:
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        date_text = datetime.now().strftime("%Y%m%d")
        self.path = self.logs_dir / f"events_{date_text}.csv"
        self._ensure_header()

    def log(
        self,
        raw_gesture: Gesture,
        stable_gesture: Gesture,
        action: Action,
        dry_run: bool,
        success: bool,
        note: str = "",
    ) -> None:
        with self.path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    datetime.now().isoformat(timespec="seconds"),
                    _enum_value(raw_gesture),
                    _enum_value(stable_gesture),
                    _enum_value(action),
                    dry_run,
                    success,
                    note,
                ]
            )

    def _ensure_header(self) -> None:
        if self.path.exists() and self.path.stat().st_size > 0:
            return

        with self.path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "timestamp",
                    "raw_gesture",
                    "stable_gesture",
                    "action",
                    "dry_run",
                    "success",
                    "note_or_error",
                ]
            )


def _enum_value(value: object) -> object:
    return getattr(value, "value", value)
