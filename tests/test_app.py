from __future__ import annotations

from src.app import _reached_frame_limit, _run_start_delay, _should_move_pointer, run_app
from src.config import AppConfig
from src.gesture_classifier import Gesture


def test_pointer_moves_for_raw_index_only_without_waiting_for_stable_gesture() -> None:
    assert _should_move_pointer(Gesture.INDEX_ONLY, object()) is True


def test_pointer_does_not_move_without_hand() -> None:
    assert _should_move_pointer(Gesture.INDEX_ONLY, None) is False


def test_frame_limit_helper() -> None:
    assert _reached_frame_limit(5, None) is False
    assert _reached_frame_limit(4, 5) is False
    assert _reached_frame_limit(5, 5) is True


def test_dry_run_skips_start_delay(capsys) -> None:
    sleeps: list[float] = []

    _run_start_delay(
        AppConfig(dry_run=True, start_delay_seconds=5),
        sleeper=sleeps.append,
    )

    assert sleeps == []
    assert capsys.readouterr().out == ""


def test_non_dry_run_start_delay_counts_down(capsys) -> None:
    sleeps: list[float] = []

    _run_start_delay(
        AppConfig(dry_run=False, start_delay_seconds=3),
        sleeper=sleeps.append,
    )

    assert sleeps == [1, 1, 1]
    output = capsys.readouterr().out
    assert "即将进入真实控制模式。" in output
    assert "请在 3 秒内切换到 PPT/PDF 窗口。" in output
    assert "3..." in output
    assert "2..." in output
    assert "1..." in output
    assert "开始识别。" in output


def test_run_app_returns_zero_when_start_delay_is_interrupted(monkeypatch) -> None:
    events: list[str] = []

    class FakeCamera:
        def __init__(self, camera_index: int) -> None:
            self.camera_index = camera_index

        def open(self) -> None:
            events.append("camera_open")

        def release(self) -> None:
            events.append("camera_release")

    class FakeTracker:
        def __init__(self, config: AppConfig) -> None:
            self.config = config

        def close(self) -> None:
            events.append("tracker_close")

    class FakeComponent:
        def __init__(self, *args, **kwargs) -> None:
            pass

    def interrupted_delay(config: AppConfig) -> None:
        raise KeyboardInterrupt

    def unexpected_main_loop(*args, **kwargs) -> None:
        raise AssertionError("倒计时被中断后不应进入主循环")

    monkeypatch.setattr("src.app.VideoCamera", FakeCamera)
    monkeypatch.setattr("src.app.HandTracker", FakeTracker)
    monkeypatch.setattr("src.app.GestureDebouncer", FakeComponent)
    monkeypatch.setattr("src.app.CommandExecutor", FakeComponent)
    monkeypatch.setattr("src.app.PointerController", FakeComponent)
    monkeypatch.setattr("src.app.EventLogger", FakeComponent)
    monkeypatch.setattr("src.app._run_start_delay", interrupted_delay)
    monkeypatch.setattr("src.app._main_loop", unexpected_main_loop)

    exit_code = run_app(AppConfig(dry_run=False, start_delay_seconds=5))

    assert exit_code == 0
    assert events == ["camera_open", "tracker_close", "camera_release"]
