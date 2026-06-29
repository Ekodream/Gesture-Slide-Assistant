from __future__ import annotations

from typing import Any

import cv2
import mediapipe as mp

from src.config import AppConfig


class HandTracker:
    def __init__(self, config: AppConfig) -> None:
        self._mp_hands = mp.solutions.hands
        self._drawing = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.max_num_hands,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )

    def detect(self, frame_bgr: Any) -> Any | None:
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb_frame)
        if not results.multi_hand_landmarks:
            return None
        return results.multi_hand_landmarks[0]

    def draw_landmarks(self, frame_bgr: Any, hand_landmarks: Any | None) -> None:
        if hand_landmarks is None:
            return
        self._drawing.draw_landmarks(
            frame_bgr,
            hand_landmarks,
            self._mp_hands.HAND_CONNECTIONS,
        )

    def close(self) -> None:
        self._hands.close()
