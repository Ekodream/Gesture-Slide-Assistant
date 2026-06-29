from __future__ import annotations

import json

import pytest

from src.config_loader import ConfigError, load_config_file


def test_missing_config_file_uses_defaults(tmp_path) -> None:
    config = load_config_file(tmp_path / "missing.json")

    assert config.camera_index == 0
    assert config.dry_run is False
    assert config.debug is False
    assert config.stable_frames == 8
    assert config.key_bindings.next_page == "right"


def test_existing_config_file_is_loaded(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "camera_index": 2,
                "dry_run": True,
                "debug": True,
                "stable_frames": 4,
                "cooldown_seconds": 0.25,
                "min_detection_confidence": 0.7,
                "min_tracking_confidence": 0.8,
                "key_bindings": {
                    "next_page": "pagedown",
                    "previous_page": "pageup",
                    "start_pause": "space",
                },
                "pointer_smoothing": 0.5,
                "mirror_pointer_x": False,
                "start_delay_seconds": 5,
            }
        ),
        encoding="utf-8",
    )

    config = load_config_file(config_path)

    assert config.camera_index == 2
    assert config.dry_run is True
    assert config.debug is True
    assert config.stable_frames == 4
    assert config.cooldown_seconds == 0.25
    assert config.min_detection_confidence == 0.7
    assert config.min_tracking_confidence == 0.8
    assert config.key_bindings.next_page == "pagedown"
    assert config.key_bindings.previous_page == "pageup"
    assert config.key_bindings.start_pause == "space"
    assert config.pointer_smoothing == 0.5
    assert config.mirror_pointer_x is False
    assert config.start_delay_seconds == 5


def test_missing_json_fields_keep_defaults(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"stable_frames": 12}', encoding="utf-8")

    config = load_config_file(config_path)

    assert config.stable_frames == 12
    assert config.camera_index == 0
    assert config.cooldown_seconds == 1.0
    assert config.key_bindings.start_pause == "f5"
    assert config.start_delay_seconds == 0


def test_invalid_json_reports_clear_error(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"stable_frames": 8,', encoding="utf-8")

    with pytest.raises(ConfigError, match="JSON 格式错误"):
        load_config_file(config_path)


def test_invalid_field_type_reports_clear_error(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"stable_frames": "8"}', encoding="utf-8")

    with pytest.raises(ConfigError, match="stable_frames 必须是整数"):
        load_config_file(config_path)


def test_negative_start_delay_reports_clear_error(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"start_delay_seconds": -1}', encoding="utf-8")

    with pytest.raises(ConfigError, match="start_delay_seconds 必须大于等于 0"):
        load_config_file(config_path)
