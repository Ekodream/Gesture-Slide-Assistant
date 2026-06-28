from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.config import AppConfig


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gesture Slide Assistant - 手势控制演示助手"
    )
    parser.add_argument("--camera", type=int, default=0, help="摄像头编号，默认 0")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印和记录动作，不控制键盘或鼠标",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="显示摄像头窗口和调试叠加信息",
    )
    parser.add_argument(
        "--stable-frames",
        type=int,
        default=8,
        help="触发前要求连续稳定的帧数，默认 8",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=1.0,
        help="离散动作重复触发的间隔秒数，默认 1.0",
    )
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> AppConfig:
    return AppConfig(
        camera_index=args.camera,
        dry_run=args.dry_run,
        debug=args.debug,
        stable_frames=args.stable_frames,
        cooldown_seconds=args.cooldown,
        logs_dir=Path("logs"),
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = build_config(args)

    from src.app import run_app

    return run_app(config)


if __name__ == "__main__":
    sys.exit(main())
