from __future__ import annotations

import argparse
from dataclasses import replace
import sys
from pathlib import Path

from src.config import AppConfig
from src.config_loader import ConfigError, load_config_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gesture Slide Assistant - 手势控制演示助手"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="JSON 配置文件路径；命令行参数会覆盖配置文件",
    )
    parser.add_argument("--camera", type=int, default=None, help="摄像头编号，默认 0")
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="只打印和记录动作，不控制键盘或鼠标",
    )
    parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="显示摄像头窗口和调试叠加信息",
    )
    parser.add_argument(
        "--stable-frames",
        type=int,
        default=None,
        help="触发前要求连续稳定的帧数，默认 8",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=None,
        help="离散动作重复触发的间隔秒数，默认 1.0",
    )
    parser.add_argument(
        "--max-frames",
        type=_positive_int,
        default=None,
        help="最多处理的帧数，主要用于非 debug 模式下的自动化 smoke test",
    )
    parser.add_argument(
        "--start-delay",
        type=_non_negative_int,
        default=None,
        help="非 dry-run 模式启动识别前的倒计时秒数，默认 0",
    )
    return parser.parse_args(argv)


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("--max-frames 必须大于等于 1")
    return parsed


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("必须大于等于 0")
    return parsed


def build_config(args: argparse.Namespace) -> AppConfig:
    config = load_config_file(getattr(args, "config", None))
    overrides: dict[str, object] = {}
    _set_override(overrides, "camera_index", args.camera)
    _set_override(overrides, "dry_run", args.dry_run)
    _set_override(overrides, "debug", args.debug)
    _set_override(overrides, "stable_frames", args.stable_frames)
    _set_override(overrides, "cooldown_seconds", args.cooldown)
    _set_override(overrides, "max_frames", args.max_frames)
    _set_override(overrides, "start_delay_seconds", getattr(args, "start_delay", None))
    return replace(config, **overrides)


def _set_override(overrides: dict[str, object], key: str, value: object | None) -> None:
    if value is not None:
        overrides[key] = value


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = build_config(args)
    except ConfigError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2

    from src.app import run_app

    return run_app(config)


if __name__ == "__main__":
    sys.exit(main())
