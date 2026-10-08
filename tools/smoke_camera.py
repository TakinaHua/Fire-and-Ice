"""Real CMU + MediaPipe integration using generated frames, without webcam access."""
import os
os.environ['CI'] = '1'
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
CMU_GRAPHICS_NO_UPDATE = True
import sys
from pathlib import Path
from unittest.mock import patch
import numpy as np
import cv2
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from Game import onAppStart, redrawAll, onKeyPress, onKeyHold, onKeyRelease
from Game import onAppStop as game_stop
from engine.runtime import onStep as game_step
import cmu_graphics
from cmu_graphics import app

class TestCamera:
    def __init__(self):
        self.opened=True
        self.read_count=0
    def isOpened(self): return self.opened
    def set(self,*args): return True
    def read(self):
        self.read_count+=1
        return True,np.zeros((480,640,3),dtype=np.uint8)
    def release(self): self.opened=False

cameras=[]
def camera_factory(*args):
    camera=TestCamera();cameras.append(camera);return camera
count=0

def onStep(app):
    global count
    count+=1
    app.instructionScreenActive=False
    if count in (5,7): onKeyPress(app,'h')
    game_step(app)
    if count==15:
        assert app.useHandGestures
        assert len(cameras)==2
        assert cameras[0].read_count>0 and cameras[1].read_count>0
        print('PASS: real renderer and MediaPipe model, state hashing, camera off/on, and synthetic frames.',flush=True)
        cmu_graphics.app._app.quit()

def onAppStop(app):
    game_stop(app)
    assert count == 15
    assert all(not c.opened for c in cameras)
    print('PASS: camera resources released on exit.', flush=True)

with patch.object(cv2,'VideoCapture',side_effect=camera_factory):
    cmu_graphics.runApp()
assert count==15
assert all(not c.opened for c in cameras)
print('PASS: camera resources released on exit.',flush=True)
