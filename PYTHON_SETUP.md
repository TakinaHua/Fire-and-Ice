# Python 3.13 setup

The setup in this folder now uses Python 3.13.3, CMU Graphics 2.0.5, MediaPipe
1.1.0 (Tasks API), OpenCV contrib 4.11.0.86, NumPy 2.5.3, and Pillow 12.3.0.
The `.venv` environment is isolated from Conda base and global Python packages.
Only OpenCV contrib is installed: it provides `cv2`, so do not also install
`opencv-python` into this environment.

## Start playing

Double-click **Play Fire and Ice.command**, or run these commands in Terminal:

```sh
cd "/Users/huashan/Desktop/ALL/Fire and ice"
./.venv/bin/python src/Game.py
```

Alternatively, `python3 run_game.py` selects the project environment automatically.
If macOS requests camera access, allow it for the terminal/editor running Python.
If the camera cannot open, keyboard controls remain available. Press **H** to retry
or toggle gesture detection, and **C** to toggle the camera preview. The original
startup instructions gate consumes the first keypress.

In VS Code, open this whole folder. Choose **Python: Select Interpreter** and
select `.venv/bin/python` if VS Code retains an earlier interpreter selection.
The provided **Fire and Ice (Python 3.13)** debug configuration explicitly uses
that environment. Running `/usr/local/bin/python3.13 src/Game.py` directly uses
global packages instead; use the project interpreter or launcher above.

## Recreate the environment

These pinned packages were verified on this Apple Silicon Mac. Other platforms
may require different wheels. Virtual environments should be recreated if this
project is moved again.

```sh
/usr/local/bin/python3.13 -m venv .venv
./.venv/bin/python -m pip install -r requirements-lock.txt
./.venv/bin/python tools/download_hand_model.py
```

The model downloader uses Google's official version-1 model and verifies SHA-256.
No webcam images are uploaded; detection runs locally. The downloaded model is
already present, so normal play does not download it again.

## What changed

- Both old `cmu_graphics` folders were moved intact into
  `upgrade-backup-2026-10-08/`, so they no longer shadow the installed package.
- `src/input/hand_tracking.py` adapts the modern Hand Landmarker output to the
  existing gesture code. It preserves landmark indices, Left/Right labels,
  two-hand detection, and the previous 0.5 detection / 0.3 tracking settings.
  VIDEO mode uses strictly increasing timestamps. Its new hand-presence threshold
  is 0.5; model behavior can still differ from the legacy detector.
- The original `processHandGestures` decision function is unchanged. A synthetic
  thumb-up test checks the existing handedness-to-player mapping.
- Preview landmarks now use OpenCV drawing rather than removed `mp.solutions`
  drawing helpers; the overlay appearance differs slightly.
- H now closes and recreates camera/model resources; full result queues no longer
  block the worker during shutdown. Missing model/camera falls back to keyboard.
- `Game.py` imports CMU's initial `app` binding as required by `runApp`.

References: [MediaPipe Python guide](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python),
[official model](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker#models),
[CMU Graphics](https://github.com/cmu-cs-academy/desktop-cmu-graphics).

## Verification

```sh
./.venv/bin/python -m pip check
(cd src && ../.venv/bin/python -m unittest discover -s tests -v)
./.venv/bin/python -m compileall -q src/Game.py src/engine src/entities src/input src/levels src/rendering src/tests tools
./.venv/bin/python tools/smoke_graphics.py
```

34 headless tests passed, including API adaptation, strict timestamps, failed
camera/model handling, H restart, full-queue shutdown, and the original game tests.
Real MediaPipe inference on a blank frame passed. The actual CMU renderer drew all
five screens using an offscreen display. These checks do not establish real webcam
recognition accuracy or the on-screen appearance; playtest both gesture-controlled
characters, H/C, and closing the game on this Mac.

Git history has been reattached to the moved folder. The earlier
`tools/check_architecture.py` compares the architecture-only gameplay with the
original commit; use it before introducing intentional physics changes.

## Restore the prior setup

Original libraries and each changed pre-upgrade source/setup file are preserved
under `upgrade-backup-2026-10-08/` at their original relative paths. To roll back,
close the game, preserve any newer edits, then copy those files back and use
Python 3.12. The backup also contains the old camera tests. No global packages
were changed and nothing was pushed to GitHub.

## Camera startup fix

CMU Graphics recursively checks app state during drawing. Camera, detector, and
worker objects now use opaque runtime handles, keeping independently changing
native resources outside that traversal while normal gameplay state stays checked.
OpenCV contrib is pinned to 4.11.0.86 to avoid the duplicate SDL runtime bundled
by OpenCV 5 on this Mac. Do not upgrade that pin without a combined graphics/camera check.

Run `.venv/bin/python tools/smoke_camera.py` to exercise the real CMU renderer,
MediaPipe model, resource hashing, H toggles, and cleanup with generated frames.
This check does not access the webcam.
