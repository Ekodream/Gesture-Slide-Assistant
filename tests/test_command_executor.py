from __future__ import annotations

import builtins

from src.command_executor import Action, CommandExecutor, action_for_gesture
from src.config import KeyBindings
from src.gesture_classifier import Gesture


def test_gesture_to_action_mapping() -> None:
    assert action_for_gesture(Gesture.V_SIGN) == Action.NEXT_PAGE
    assert action_for_gesture(Gesture.THREE_FINGERS) == Action.PREVIOUS_PAGE
    assert action_for_gesture(Gesture.FIST) == Action.START_PAUSE
    assert action_for_gesture(Gesture.INDEX_ONLY) == Action.POINTER_MOVE
    assert action_for_gesture(Gesture.UNKNOWN) == Action.NONE


def test_dry_run_does_not_import_pyautogui(monkeypatch) -> None:
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "pyautogui":
            raise AssertionError("dry-run 不应导入或调用 pyautogui")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    executor = CommandExecutor(dry_run=True, key_bindings=KeyBindings())

    result = executor.execute(Action.NEXT_PAGE)

    assert result.success is True
    assert "dry-run" in result.note


def test_none_action_does_not_import_pyautogui(monkeypatch) -> None:
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "pyautogui":
            raise AssertionError("NONE 不应导入或调用 pyautogui")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    executor = CommandExecutor(dry_run=False, key_bindings=KeyBindings())

    result = executor.execute(Action.NONE)

    assert result.success is True
    assert result.action == Action.NONE
