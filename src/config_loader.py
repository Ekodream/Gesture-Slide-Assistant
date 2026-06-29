from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from src.config import AppConfig, KeyBindings


class ConfigError(ValueError):
    pass


_MISSING = object()

_CONFIG_KEYS = {
    "camera_index",
    "dry_run",
    "debug",
    "stable_frames",
    "cooldown_seconds",
    "max_num_hands",
    "min_detection_confidence",
    "min_tracking_confidence",
    "key_bindings",
    "logs_dir",
    "pointer_smoothing",
    "mirror_pointer_x",
    "start_delay_seconds",
    "max_frames",
}

_KEY_BINDING_KEYS = {
    "next_page",
    "previous_page",
    "start_pause",
}


def load_config_file(config_path: Path | None) -> AppConfig:
    if config_path is None:
        return AppConfig()

    path = Path(config_path)
    if not path.exists():
        return AppConfig()
    if not path.is_file():
        raise ConfigError(f"配置路径不是文件: {path}")

    data = _read_json_object(path)
    return config_from_mapping(data, str(path))


def config_from_mapping(data: Mapping[str, Any], source: str = "config") -> AppConfig:
    _reject_unknown_keys(data, _CONFIG_KEYS, source)

    key_bindings = _load_key_bindings(data, source)
    values: dict[str, Any] = {
        "key_bindings": key_bindings,
    }

    _set_if_present(values, "camera_index", _read_int(data, "camera_index", source))
    _set_if_present(values, "dry_run", _read_bool(data, "dry_run", source))
    _set_if_present(values, "debug", _read_bool(data, "debug", source))
    _set_if_present(values, "stable_frames", _read_int(data, "stable_frames", source))
    _set_if_present(
        values,
        "cooldown_seconds",
        _read_float(data, "cooldown_seconds", source),
    )
    _set_if_present(values, "max_num_hands", _read_int(data, "max_num_hands", source))
    _set_if_present(
        values,
        "min_detection_confidence",
        _read_float(data, "min_detection_confidence", source),
    )
    _set_if_present(
        values,
        "min_tracking_confidence",
        _read_float(data, "min_tracking_confidence", source),
    )
    _set_if_present(values, "logs_dir", _read_path(data, "logs_dir", source))
    _set_if_present(
        values,
        "pointer_smoothing",
        _read_float(data, "pointer_smoothing", source),
    )
    _set_if_present(
        values,
        "mirror_pointer_x",
        _read_bool(data, "mirror_pointer_x", source),
    )
    _set_if_present(
        values,
        "start_delay_seconds",
        _read_non_negative_int(data, "start_delay_seconds", source),
    )
    _set_if_present(
        values,
        "max_frames",
        _read_optional_int(data, "max_frames", source),
    )

    return replace(AppConfig(), **values)


def _read_json_object(path: Path) -> Mapping[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"配置文件 JSON 格式错误: {path} 第 {exc.lineno} 行第 {exc.colno} 列: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ConfigError(f"无法读取配置文件: {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"配置文件必须是 JSON 对象: {path}")
    return data


def _load_key_bindings(data: Mapping[str, Any], source: str) -> KeyBindings:
    raw = data.get("key_bindings", _MISSING)
    if raw is _MISSING:
        return KeyBindings()
    if not isinstance(raw, dict):
        raise ConfigError(f"{source}: key_bindings 必须是 JSON 对象")

    _reject_unknown_keys(raw, _KEY_BINDING_KEYS, f"{source}.key_bindings")
    values: dict[str, Any] = {}
    _set_if_present(values, "next_page", _read_str(raw, "next_page", source))
    _set_if_present(values, "previous_page", _read_str(raw, "previous_page", source))
    _set_if_present(values, "start_pause", _read_str(raw, "start_pause", source))
    return replace(KeyBindings(), **values)


def _reject_unknown_keys(
    data: Mapping[str, Any],
    allowed_keys: set[str],
    source: str,
) -> None:
    unknown_keys = sorted(set(data) - allowed_keys)
    if unknown_keys:
        keys = ", ".join(unknown_keys)
        raise ConfigError(f"{source}: 未知配置字段: {keys}")


def _read_int(data: Mapping[str, Any], key: str, source: str) -> int | object:
    value = data.get(key, _MISSING)
    if value is _MISSING:
        return _MISSING
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{source}: {key} 必须是整数")
    return value


def _read_optional_int(
    data: Mapping[str, Any],
    key: str,
    source: str,
) -> int | None | object:
    value = data.get(key, _MISSING)
    if value is _MISSING or value is None:
        return value
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{source}: {key} 必须是整数或 null")
    return value


def _read_non_negative_int(
    data: Mapping[str, Any],
    key: str,
    source: str,
) -> int | object:
    value = _read_int(data, key, source)
    if value is _MISSING:
        return _MISSING
    if value < 0:
        raise ConfigError(f"{source}: {key} 必须大于等于 0")
    return value


def _read_float(data: Mapping[str, Any], key: str, source: str) -> float | object:
    value = data.get(key, _MISSING)
    if value is _MISSING:
        return _MISSING
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{source}: {key} 必须是数字")
    return float(value)


def _read_bool(data: Mapping[str, Any], key: str, source: str) -> bool | object:
    value = data.get(key, _MISSING)
    if value is _MISSING:
        return _MISSING
    if not isinstance(value, bool):
        raise ConfigError(f"{source}: {key} 必须是 true 或 false")
    return value


def _read_str(data: Mapping[str, Any], key: str, source: str) -> str | object:
    value = data.get(key, _MISSING)
    if value is _MISSING:
        return _MISSING
    if not isinstance(value, str):
        raise ConfigError(f"{source}: {key} 必须是字符串")
    return value


def _read_path(data: Mapping[str, Any], key: str, source: str) -> Path | object:
    value = _read_str(data, key, source)
    if value is _MISSING:
        return _MISSING
    return Path(value)


def _set_if_present(values: dict[str, Any], key: str, value: Any) -> None:
    if value is not _MISSING:
        values[key] = value
