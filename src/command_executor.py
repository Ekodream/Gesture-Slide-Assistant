from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.config import KeyBindings
from src.gesture_classifier import Gesture


class Action(str, Enum):
    NEXT_PAGE = "NEXT_PAGE"
    PREVIOUS_PAGE = "PREVIOUS_PAGE"
    START_PAUSE = "START_PAUSE"
    POINTER_MOVE = "POINTER_MOVE"
    NONE = "NONE"


GESTURE_ACTIONS: dict[Gesture, Action] = {
    Gesture.V_SIGN: Action.NEXT_PAGE,
    Gesture.THREE_FINGERS: Action.PREVIOUS_PAGE,
    Gesture.FIST: Action.START_PAUSE,
    Gesture.INDEX_ONLY: Action.POINTER_MOVE,
    Gesture.UNKNOWN: Action.NONE,
}


@dataclass(frozen=True)
class ExecutionResult:
    action: Action
    success: bool
    note: str = ""
    error: str = ""


def action_for_gesture(gesture: Gesture) -> Action:
    return GESTURE_ACTIONS.get(gesture, Action.NONE)


class CommandExecutor:
    def __init__(self, dry_run: bool, key_bindings: KeyBindings) -> None:
        self.dry_run = dry_run
        self.key_bindings = key_bindings

    def execute(self, action: Action) -> ExecutionResult:
        action = self._normalize_action(action)
        if action in {Action.NONE, Action.POINTER_MOVE}:
            return ExecutionResult(action, True, "无键盘动作需要执行")

        key = self._key_for_action(action)
        if self.dry_run:
            note = f"[dry-run] 计划执行 {action.value}: press {key}"
            print(note)
            return ExecutionResult(action, True, note)

        return self._press_key(action, key)

    def _press_key(self, action: Action, key: str) -> ExecutionResult:
        try:
            import pyautogui

            pyautogui.FAILSAFE = True
            pyautogui.press(key)
            return ExecutionResult(action, True, f"已发送按键 {key}")
        except Exception as exc:  # pragma: no cover - depends on local desktop
            return ExecutionResult(action, False, error=str(exc))

    def _key_for_action(self, action: Action) -> str:
        if action == Action.NEXT_PAGE:
            return self.key_bindings.next_page
        if action == Action.PREVIOUS_PAGE:
            return self.key_bindings.previous_page
        if action == Action.START_PAUSE:
            return self.key_bindings.start_pause
        raise ValueError(f"动作 {action.value} 没有绑定按键")

    @staticmethod
    def _normalize_action(action: Action) -> Action:
        if isinstance(action, Action):
            return action
        try:
            return Action(str(action))
        except ValueError:
            return Action.NONE
