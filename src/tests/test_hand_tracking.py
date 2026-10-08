"""Regression checks for Tasks adaptation and camera restart/shutdown."""
import queue
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch
import numpy as np
from input import gestures, keyboard, hand_tracking
from test_architecture import new_game


class HandTrackingTests(unittest.TestCase):
    def test_results_preserve_landmarks_and_handedness(self):
        points = [NS(x=0.1, y=0.2, z=0.0)] * 21
        result = hand_tracking.adapt_result(NS(hand_landmarks=[points], handedness=[[NS(category_name='Left')]]))
        self.assertIs(result.multi_hand_landmarks[0].landmark, points)
        self.assertEqual(result.multi_handedness[0].classification[0].label, 'Left')

    def test_video_timestamps_strictly_increase(self):
        detector = object.__new__(hand_tracking.HandDetector)
        detector._timestamp = -1
        detector._mp = Mock()
        detector._detector = Mock()
        detector._detector.detect_for_video.return_value = NS(hand_landmarks=[], handedness=[])
        with patch.object(hand_tracking.time, 'monotonic_ns', return_value=10000000):
            detector.process(np.zeros((2, 2, 3), dtype=np.uint8))
            detector.process(np.zeros((2, 2, 3), dtype=np.uint8))
        self.assertEqual([call.args[1] for call in detector._detector.detect_for_video.call_args_list], [10, 11])

    def test_failed_camera_closes_model(self):
        app = new_game()
        cv = Mock()
        cv.VideoCapture.return_value.isOpened.return_value = False
        with patch.dict('sys.modules', {'cv2': cv}), patch.object(gestures, 'HandDetector') as detector:
            self.assertFalse(gestures.initHandDetection(app))
            detector.return_value.close.assert_called_once()
            cv.VideoCapture.return_value.release.assert_called_once()
        self.assertFalse(app.useHandGestures)
        self.assertFalse(hasattr(app, 'cap'))

    def test_missing_model_falls_back_to_keyboard(self):
        app = new_game()
        with patch.object(gestures, 'HandDetector', side_effect=FileNotFoundError('model')):
            self.assertFalse(gestures.initHandDetection(app))
        self.assertFalse(app.useHandGestures)

    def test_h_toggle_reopens_camera(self):
        app = new_game()
        app.useHandGestures = True
        with patch.object(keyboard, 'stopHandDetection', side_effect=lambda a: setattr(a, 'useHandGestures', False)) as stop, patch.object(keyboard, 'initHandDetection') as start:
            keyboard.onKeyPress(app, 'h')
            keyboard.onKeyPress(app, 'h')
            stop.assert_called_once_with(app)
            start.assert_called_once_with(app)

    def test_full_queue_does_not_block_worker_shutdown(self):
        app = new_game()
        app.useHandGestures = True
        app.cap = Mock()
        app.hands = Mock()
        worker = gestures.HandGestureThread(app)
        frame = np.zeros((2, 2, 3), dtype=np.uint8)
        def read():
            worker.stop()
            return True, frame
        app.cap.read.side_effect = read
        full = queue.Queue(maxsize=1)
        full.put('existing frame')
        with patch.object(gestures, 'gestureQueue', full):
            worker.run()
        self.assertEqual(full.get_nowait(), 'existing frame')

    def test_adapted_thumb_up_keeps_right_hand_player_mapping(self):
        app = new_game()
        app.useHandGestures = True
        app.cap = Mock()
        app.mpHands = hand_tracking
        app.showCameraWindow = False
        app.fireboyMovingDirection = app.icegirlMovingDirection = None
        app.lastJumpTimeLeft = app.lastJumpTimeRight = 0
        # Raised thumb, extended fingers: jump rather than fist confirmation.
        points = [NS(x=0.5, y=0.3, z=0.0) for _ in range(21)]
        points[0] = NS(x=0.5, y=0.9, z=0.0)
        points[2] = NS(x=0.5, y=0.7, z=0.0)
        points[4] = NS(x=0.5, y=0.2, z=0.0)
        points[5] = NS(x=0.5, y=0.6, z=0.0)
        result = hand_tracking.adapt_result(NS(hand_landmarks=[points], handedness=[[NS(category_name='Right')]]))
        pending = queue.Queue()
        pending.put((np.zeros((480, 640, 3), dtype=np.uint8), result))
        with patch.object(gestures, 'gestureQueue', pending):
            gestures.processHandGestures(app)
        self.assertEqual(app.fireboyVelY, app.jumpSpeed)
        self.assertFalse(app.fireboyCanJump)
        self.assertTrue(app.icegirlCanJump)
