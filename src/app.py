from __future__ import annotations

import cv2

from src.camera import CameraError, VideoCamera
from src.command_executor import Action, CommandExecutor, action_for_gesture
from src.config import AppConfig
from src.debouncer import DebounceResult, GestureDebouncer
from src.event_logger import EventLogger
from src.gesture_classifier import Gesture, classify_hand
from src.hand_tracker import HandTracker
from src.pointer import PointerController


def run_app(config: AppConfig) -> int:
    print(f"当前配置: {config}")

    camera = VideoCamera(config.camera_index)
    tracker: HandTracker | None = None

    try:
        camera.open()
        tracker = HandTracker(config)
        debouncer = GestureDebouncer(
            stable_frames=config.stable_frames,
            cooldown_seconds=config.cooldown_seconds,
        )
        executor = CommandExecutor(
            dry_run=config.dry_run,
            key_bindings=config.key_bindings,
        )
        pointer = PointerController(
            dry_run=config.dry_run,
            smoothing=config.pointer_smoothing,
            mirror_x=config.mirror_pointer_x,
        )
        logger = EventLogger(config.logs_dir)
        _main_loop(config, camera, tracker, debouncer, executor, pointer, logger)
        return 0
    except CameraError as exc:
        print(f"摄像头错误: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\n用户中断，正在退出。")
        return 0
    finally:
        if tracker is not None:
            tracker.close()
        camera.release()
        if config.debug:
            cv2.destroyAllWindows()


def _main_loop(
    config: AppConfig,
    camera: VideoCamera,
    tracker: HandTracker,
    debouncer: GestureDebouncer,
    executor: CommandExecutor,
    pointer: PointerController,
    logger: EventLogger,
) -> None:
    last_action = Action.NONE
    last_pointer_note = ""

    while True:
        frame = camera.read()
        hand_landmarks = tracker.detect(frame)
        raw_gesture = classify_hand(hand_landmarks)
        debounce_result = debouncer.update(raw_gesture)

        if hand_landmarks is not None:
            tracker.draw_landmarks(frame, hand_landmarks)

        if debounce_result.should_trigger:
            last_action = _execute_and_log(
                debounce_result,
                executor,
                logger,
                config.dry_run,
            )

        if _should_move_pointer(raw_gesture, debounce_result, hand_landmarks):
            pointer_result = pointer.move_to_index_tip(hand_landmarks)
            last_pointer_note = (
                f"pointer=({pointer_result.target_x}, {pointer_result.target_y}) "
                f"{pointer_result.note}"
            )

        if config.debug:
            _draw_debug_overlay(
                frame,
                raw_gesture,
                debounce_result,
                last_action,
                last_pointer_note,
                config.dry_run,
            )
            cv2.imshow("Gesture Slide Assistant", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


def _execute_and_log(
    debounce_result: DebounceResult,
    executor: CommandExecutor,
    logger: EventLogger,
    dry_run: bool,
) -> Action:
    action = action_for_gesture(debounce_result.stable_gesture)
    execution = executor.execute(action)
    note = execution.note or execution.error or debounce_result.note
    logger.log(
        raw_gesture=debounce_result.raw_gesture,
        stable_gesture=debounce_result.stable_gesture,
        action=action,
        dry_run=dry_run,
        success=execution.success,
        note=note,
    )
    return action


def _should_move_pointer(
    raw_gesture: Gesture,
    debounce_result: DebounceResult,
    hand_landmarks: object | None,
) -> bool:
    return (
        hand_landmarks is not None
        and raw_gesture == Gesture.INDEX_ONLY
        and debounce_result.stable_gesture == Gesture.INDEX_ONLY
    )


def _draw_debug_overlay(
    frame,
    raw_gesture: Gesture,
    debounce_result: DebounceResult,
    last_action: Action,
    pointer_note: str,
    dry_run: bool,
) -> None:
    lines = [
        f"raw: {raw_gesture.value}",
        f"stable: {debounce_result.stable_gesture.value}",
        f"trigger: {debounce_result.should_trigger} ({debounce_result.note})",
        f"last action: {last_action.value}",
        f"dry-run: {dry_run}",
        "press q to quit",
    ]
    if pointer_note:
        lines.append(pointer_note)

    for index, text in enumerate(lines):
        y = 28 + index * 24
        cv2.putText(
            frame,
            text,
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
