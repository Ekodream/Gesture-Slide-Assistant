from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class KeyBindings:
    next_page: str = "right"
    previous_page: str = "left"
    start_pause: str = "f5"


@dataclass(frozen=True)
class AppConfig:
    camera_index: int = 0
    dry_run: bool = False
    debug: bool = False
    stable_frames: int = 8
    cooldown_seconds: float = 1.0
    max_num_hands: int = 1
    min_detection_confidence: float = 0.6
    min_tracking_confidence: float = 0.6
    key_bindings: KeyBindings = field(default_factory=KeyBindings)
    logs_dir: Path = Path("logs")
    pointer_smoothing: float = 0.35
    mirror_pointer_x: bool = True
