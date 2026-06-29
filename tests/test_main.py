from __future__ import annotations

import pytest

from main import build_config, parse_args


def test_build_config_includes_max_frames() -> None:
    args = parse_args(
        [
            "--camera",
            "1",
            "--dry-run",
            "--debug",
            "--stable-frames",
            "3",
            "--cooldown",
            "0.5",
            "--max-frames",
            "10",
        ]
    )

    config = build_config(args)

    assert config.camera_index == 1
    assert config.dry_run is True
    assert config.debug is True
    assert config.stable_frames == 3
    assert config.cooldown_seconds == 0.5
    assert config.max_frames == 10


def test_invalid_max_frames_is_rejected() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--max-frames", "0"])
