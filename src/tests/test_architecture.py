"""Headless integration tests for the extracted architecture."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from engine.runtime import onStep
from engine.state import initialstats, calculateScore
from entities.enemies import ghostMove
from entities.platforms import moveTrap, onFan
from entities.players import applyContinuousMovement
from input import gestures, keyboard
from levels.state import level1initialstat, level2initialstat, checkDiamond
from rendering.assets import getAssetPath
from rendering import screens, sprites

SRC = Path(__file__).resolve().parents[1]


def new_game(mode='level0'):
    app = SimpleNamespace(instructionScreenActive=False, useHandGestures=False,
                          levelUnlock=[0], levelLocked=[1, 2])
    initialstats(app)
    app.gamemode = mode
    if mode in ('level0', 'level1'):
        level1initialstat(app)
    elif mode == 'level2':
        level2initialstat(app)
    return app


class ArchitectureTests(unittest.TestCase):
    def test_imports_do_not_load_hardware_or_graphics(self):
        script = """
import sys
import Game
assert not {'cv2', 'mediapipe', 'cmu_graphics', 'PIL'} & set(sys.modules)
for name in ('onAppStart', 'onStep', 'onKeyPress', 'onKeyRelease',
             'onKeyHold', 'onAppStop', 'redrawAll'):
    assert callable(getattr(Game, name))
"""
        subprocess.run([sys.executable, '-c', script], cwd=SRC, check=True)

    def test_assets_resolve_outside_source_directory(self):
        original = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as directory:
                os.chdir(directory)
                path = Path(getAssetPath('doors/doorout.png'))
                self.assertTrue(path.is_absolute())
                self.assertTrue(path.is_file())
        finally:
            os.chdir(original)

    def test_startup_camera_failure_preserves_keyboard_mode(self):
        from engine import runtime
        app = SimpleNamespace()
        with patch.object(runtime, 'initHandDetection', return_value=False):
            runtime.onAppStart(app)
        self.assertFalse(app.useHandGestures)
        self.assertTrue(app.instructionScreenActive)
        self.assertEqual(app.gamemode, 'desktopInitialize')

    def test_level_resets_and_unlocks(self):
        app = new_game('level2')
        self.assertEqual((app.fireboyx, app.icegirlx, app.groundLevel), (50, 880, 645))
        self.assertTrue(app.blueDia4)
        level1initialstat(app)
        self.assertEqual((app.fireboyx, app.icegirlx, app.groundLevel), (50, 80, 655))
        initialstats(app)
        self.assertEqual(app.levelUnlock, [0])
        self.assertEqual(app.gamemode, 'desktopInitialize')

    def test_instruction_and_frozen_frames_do_not_advance(self):
        app = new_game()
        app.instructionScreenActive = True
        onStep(app)
        self.assertEqual(app.frameCount, 0)
        app.instructionScreenActive = False
        app.gameFrozen = True
        onStep(app)
        self.assertEqual(app.frameCount, 0)

    def test_keyboard_jump_and_landing(self):
        app = new_game()
        keyboard.onKeyPress(app, 'up')
        self.assertEqual(app.fireboyVelY, -15)
        self.assertFalse(app.fireboyCanJump)
        onStep(app)
        self.assertEqual(app.fireboyy, 611)
        for _ in range(40):
            onStep(app)
        self.assertTrue(app.fireboyCanJump)
        self.assertEqual(app.fireboyy, app.fireboyground)

    def test_menu_navigation_and_restart(self):
        app = new_game('desktopInitialize')
        keyboard.onKeyPress(app, 'up')
        self.assertEqual(app.gamemode, 'levelSelection')
        keyboard.onKeyPress(app, 'down')
        self.assertEqual(app.gamemode, 'desktopInitialize')
        app.gameFrozen = True
        keyboard.onKeyPress(app, 'r')
        self.assertFalse(app.gameFrozen)

    def test_keyboard_hold_and_release(self):
        app = new_game()
        keyboard.onKeyHold(app, ['right', 'a'])
        self.assertEqual((app.fireboyx, app.icegirlx), (55, 75))
        keyboard.onKeyRelease(app, 'right')
        self.assertEqual((app.fireboystatus, app.icegirlstatus), ('stand', 'stand'))

    def test_ghost_activation_and_path(self):
        app = new_game('level1')
        app.frameCount = 349
        ghostMove(app)
        self.assertEqual(app.ghostX, 20)
        app.frameCount = 350
        ghostMove(app)
        self.assertTrue(app.ghostActive)
        self.assertEqual(app.ghostX, 25)

    def test_platform_switch_and_fan(self):
        app = new_game()
        app.fireboyx, app.fireboyy = 570, 350
        moveTrap(app)
        self.assertEqual(app.platformY, 185)
        app.fireboyx, app.fireboyy = 900, 640
        onFan(app)
        self.assertEqual(app.fireboyVelY, -5)

    def test_collectibles_and_score(self):
        app = new_game()
        app.fireboyx, app.fireboyy = 650, 150
        checkDiamond(app)
        self.assertFalse(app.redDiamond2)
        self.assertEqual(calculateScore(app), 25)

    def test_gesture_movement(self):
        app = new_game()
        app.fireboyMovingDirection = 'right'
        app.icegirlMovingDirection = 'left'
        applyContinuousMovement(app)
        self.assertEqual((app.fireboyx, app.icegirlx), (55, 75))

    def test_no_hands_stops_movement(self):
        app = new_game()
        app.useHandGestures = True
        app.cap = Mock()
        app.fireboyMovingDirection = app.icegirlMovingDirection = 'right'
        app.showCameraWindow = False
        with patch.object(gestures, 'gestureQueue') as queue, patch.dict(sys.modules, {'cv2': Mock()}):
            queue.empty.side_effect = [False, True]
            queue.get_nowait.return_value = (None, SimpleNamespace(multi_hand_landmarks=None))
            gestures.processHandGestures(app)
        self.assertIsNone(app.fireboyMovingDirection)
        self.assertIsNone(app.icegirlMovingDirection)
        self.assertEqual((app.fireboyx, app.icegirlx), (50, 80))

    def test_gesture_queue_empty_race_is_harmless(self):
        import queue
        app = new_game()
        app.useHandGestures = True
        app.cap = Mock()
        with patch.object(gestures, 'gestureQueue') as pending, patch.dict(sys.modules, {'cv2': Mock()}):
            pending.empty.return_value = False
            pending.get_nowait.side_effect = queue.Empty
            gestures.processHandGestures(app)
        self.assertEqual(app.fireboyx, 50)

    def test_camera_initialization_starts_worker(self):
        app = new_game()
        cv = Mock()
        with patch.dict(sys.modules, {'cv2': cv}), patch.object(gestures, 'HandDetector') as detector, patch.object(gestures, 'HandGestureThread') as worker:
            self.assertTrue(gestures.initHandDetection(app))
            cv.VideoCapture.assert_called_once_with(0)
            detector.assert_called_once_with()
            worker.return_value.start.assert_called_once()
        self.assertTrue(app.useHandGestures)
        self.assertIsNone(app.fireboyMovingDirection)

    def test_camera_cleanup(self):
        app = SimpleNamespace(handGestureThread=Mock(), cap=Mock(), hands=Mock(), showCameraWindow=True)
        worker, camera, detector = app.handGestureThread, app.cap, app.hands
        with patch.dict(sys.modules, {'cv2': Mock()}) as modules:
            gestures.onAppStop(app)
            modules['cv2'].destroyAllWindows.assert_called_once()
        worker.stop.assert_called_once()
        worker.join.assert_called_once()
        camera.release.assert_called_once()
        detector.close.assert_called_once()
        self.assertFalse(hasattr(app, "cap"))

    def test_every_screen_and_sprite_state_draws_existing_assets(self):
        image_paths = []
        def draw_image(path, *args, **kwargs):
            image_paths.append(path)
            self.assertTrue(Path(path).is_file(), path)
        with patch.multiple(screens, drawImage=draw_image, drawLabel=Mock(), drawRect=Mock(), rgb=lambda *v: v), patch.object(sprites, 'drawImage', draw_image):
            for mode in ('desktopInitialize', 'levelSelection', 'level0', 'level1', 'level2'):
                for status in ('stand', 'turn left', 'turn right', 'up', 'win'):
                    app = new_game(mode)
                    app.fireboystatus = app.icegirlstatus = status
                    screens.redrawAll(app)
        self.assertGreater(len(image_paths), 100)


if __name__ == '__main__':
    unittest.main()
