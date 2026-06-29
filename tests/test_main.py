from __future__ import annotations

import json

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
            "--start-delay",
            "5",
        ]
    )

    config = build_config(args)

    assert config.camera_index == 1
    assert config.dry_run is True
    assert config.debug is True
    assert config.stable_frames == 3
    assert config.cooldown_seconds == 0.5
    assert config.max_frames == 10
    assert config.start_delay_seconds == 5


def test_invalid_max_frames_is_rejected() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--max-frames", "0"])


def test_invalid_start_delay_is_rejected() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--start-delay", "-1"])


def test_cli_arguments_override_config_file(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "camera_index": 2,
                "dry_run": True,
                "debug": True,
                "stable_frames": 9,
                "cooldown_seconds": 2.0,
                "start_delay_seconds": 10,
            }
        ),
        encoding="utf-8",
    )

    args = parse_args(
        [
            "--config",
            str(config_path),
            "--camera",
            "1",
            "--no-dry-run",
            "--stable-frames",
            "3",
            "--cooldown",
            "0.5",
            "--start-delay",
            "5",
        ]
    )

    config = build_config(args)

    assert config.camera_index == 1
    assert config.dry_run is False
    assert config.debug is True
    assert config.stable_frames == 3
    assert config.cooldown_seconds == 0.5
    assert config.start_delay_seconds == 5
