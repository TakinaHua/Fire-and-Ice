"""MediaPipe Tasks adapter; preserves the game's landmark and handedness interface.

Inference stays on the camera worker. VIDEO mode tracks across frames using
strictly increasing monotonic timestamps. No model or camera is opened on import.
"""
from enum import IntEnum
from pathlib import Path
from types import SimpleNamespace
import time

MODEL_PATH = Path(__file__).resolve().parents[2] / 'models' / 'hand_landmarker.task'


class HandLandmark(IntEnum):
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
    (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
)


def adapt_result(result):
    """Keep coordinates and Left/Right labels unchanged for existing gesture rules."""
    return SimpleNamespace(
        multi_hand_landmarks=[SimpleNamespace(landmark=points) for points in result.hand_landmarks],
        multi_handedness=[SimpleNamespace(classification=[
            SimpleNamespace(label=categories[0].category_name)
        ]) for categories in result.handedness],
    )


class HandDetector:
    def __init__(self, model_path=MODEL_PATH):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode
        if not Path(model_path).is_file():
            raise FileNotFoundError(f'Hand model missing: {model_path}. Run tools/download_hand_model.py.')
        self._mp = mp
        self._timestamp = -1
        self._detector = HandLandmarker.create_from_options(HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.3,
        ))

    def process(self, rgb_frame):
        self._timestamp = max(self._timestamp + 1, time.monotonic_ns() // 1_000_000)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb_frame)
        return adapt_result(self._detector.detect_for_video(image, self._timestamp))

    def close(self):
        self._detector.close()


def draw_landmarks(frame, hand, connections=HAND_CONNECTIONS):
    """Draw the preview skeleton without the removed mp.solutions drawing helpers."""
    import cv2
    height, width = frame.shape[:2]
    points = [(int(p.x * width), int(p.y * height)) for p in hand.landmark]
    for start, end in connections:
        cv2.line(frame, points[start], points[end], (0, 255, 0), 2)
    for point in points:
        cv2.circle(frame, point, 3, (0, 0, 255), -1)
