"""input / gestures extracted from the original game."""
from engine.world import jump
import math
import time
import threading
import queue
from queue import Queue
from input import hand_tracking
from input.hand_tracking import HandDetector
from input.runtime_resource import RuntimeResource

gestureStatus = {"left_hand": None, "right_hand": None}
gestureQueue = Queue(maxsize=10)
from entities.players import applyContinuousMovement, fireboylevelselectstat, icegirllevelselectStat
from levels.selection import fireboynear, icegirlnear


class HandGestureThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.running = True
        self.daemon = True
        # !! because the hand gesture thread is run as a daemon (kinda like a background thread),
        # !! when we quit the main program (Game.py), the thread will also quit automatically
        # learned the implementaion in the 2 thread tutorials linked in citations.txt

    def run(self):
        import cv2
        while self.running:
            if not self.app.useHandGestures or not hasattr(self.app, 'cap') or not self.app.cap.isOpened():
                time.sleep(0.1)  # Sleep briefly if not processing
                continue

            ret, frame = self.app.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            processFrame = frame
            processFrame.flags.writeable = False
            frameRgb = cv2.cvtColor(processFrame, cv2.COLOR_BGR2RGB)
            results = self.app.hands.process(frameRgb)
            processFrame.flags.writeable = True

            # Put results in queue for main thread to process
            # Never block shutdown when the game pauses or the queue fills.
            try:
                gestureQueue.put_nowait((frame, results))
            except queue.Full:
                pass

            # Control processing rate
            time.sleep(0.01)  # 100 FPS max processing rate

    def stop(self):
        self.running = False


def initHandDetection(app):
    import cv2
    app.fireboyMovingDirection = app.icegirlMovingDirection = None
    app.showCameraWindow = False
    try:
        app.hands = RuntimeResource(HandDetector())
    except Exception as error:
        print(f'Hand detection unavailable: {error}. Keyboard controls remain available.')
        app.useHandGestures = False
        return False
    app.cap = RuntimeResource(cv2.VideoCapture(0))
    if not app.cap.isOpened():
        print('Could not open camera. Keyboard controls remain available; press H to retry.')
        app.cap.release()
        app.hands.close()
        del app.cap, app.hands
        app.useHandGestures = False
        return False

    app.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    app.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    app.frameSkipCounter = 0

    app.lastJumpTimeLeft = 0
    app.lastJumpTimeRight = 0
    app.lastLeftTimeLeft = 0
    app.lastRightTimeLeft = 0
    app.lastLeftTimeRight = 0
    app.lastRightTimeRight = 0
    app.lastConfirmTimeLeft = 0
    app.lastConfirmTimeRight = 0
    app.lastMainMenuConfirmTime = 0  # for menu and prevent accidental triggers

    app.showCameraWindow = False
    app.useHandGestures = True

    # keep track of which way players are moving
    app.fireboyMovingDirection = None  # left, right, or nothing
    app.icegirlMovingDirection = None  # left, right, or nothing

    # Initialize and start the hand gesture thread
    app.handGestureThread = RuntimeResource(HandGestureThread(app))
    app.handGestureThread.start()

    return True


def processHandGestures(app):
    import cv2
    if not app.useHandGestures or not hasattr(app, 'cap') or not app.cap.isOpened():
        return

    # Process any available results from the queue
    try:
        while not gestureQueue.empty():
            frame, results = gestureQueue.get_nowait()
            currentTime = time.time()

            # Track which hands are currently detected
            detectedHands = set()

            # if no hands found, reset everything
            if not results.multi_hand_landmarks:
                gestureStatus["left_hand"] = None
                gestureStatus["right_hand"] = None
                # stop players from moving if no hands
                app.fireboyMovingDirection = None
                app.icegirlMovingDirection = None

            if results.multi_hand_landmarks:
                for handIdx, handLandmarks in enumerate(results.multi_hand_landmarks):
                    handedness = results.multi_handedness[handIdx].classification[0].label
                    handKey = "right_hand" if handedness == "Left" else "left_hand"
                    detectedHands.add(handKey)

                    gestureStatus[handKey] = "idle"

                    h, w, c = frame.shape

                    wrist = handLandmarks.landmark[hand_tracking.HandLandmark.WRIST]
                    thumbMcp = handLandmarks.landmark[hand_tracking.HandLandmark.THUMB_MCP]
                    thumbTip = handLandmarks.landmark[hand_tracking.HandLandmark.THUMB_TIP]
                    indexMcp = handLandmarks.landmark[hand_tracking.HandLandmark.INDEX_FINGER_MCP]
                    indexPip = handLandmarks.landmark[hand_tracking.HandLandmark.INDEX_FINGER_PIP]
                    indexTip = handLandmarks.landmark[hand_tracking.HandLandmark.INDEX_FINGER_TIP]
                    middleTip = handLandmarks.landmark[hand_tracking.HandLandmark.MIDDLE_FINGER_TIP]
                    ringTip = handLandmarks.landmark[hand_tracking.HandLandmark.RING_FINGER_TIP]
                    pinkyTip = handLandmarks.landmark[hand_tracking.HandLandmark.PINKY_TIP]
                    middleMcp = handLandmarks.landmark[hand_tracking.HandLandmark.MIDDLE_FINGER_MCP]

                    wristX, wristY = int(wrist.x * w), int(wrist.y * h)
                    thumbMcpX, thumbMcpY = int(thumbMcp.x * w), int(thumbMcp.y * h)
                    thumbTipX, thumbTipY = int(thumbTip.x * w), int(thumbTip.y * h)

                    indexMcpX, indexMcpY = int(indexMcp.x * w), int(indexMcp.y * h)
                    indexPipX, indexPipY = int(indexPip.x * w), int(indexPip.y * h)
                    indexTipX, indexTipY = int(indexTip.x * w), int(indexTip.y * h)

                    middleMcpX, middleMcpY = int(middleMcp.x * w), int(middleMcp.y * h)

                    thumbDirX = thumbTipX - thumbMcpX
                    thumbDirY = thumbTipY - thumbMcpY

                    thumbMagnitude = math.sqrt(thumbDirX**2 + thumbDirY**2)
                    if thumbMagnitude > 0:
                        thumbDirX /= thumbMagnitude
                        thumbDirY /= thumbMagnitude

                    verticalAngle = math.degrees(math.atan2(-thumbDirY, thumbDirX)) - 90
                    if verticalAngle < 0:
                        verticalAngle += 360

                    isThumbUp = verticalAngle < 30 or verticalAngle > 330

                    middleTipY = int(middleTip.y * h)
                    ringTipY = int(ringTip.y * h)
                    pinkyTipY = int(pinkyTip.y * h)

                    palmY = indexMcpY
                    fingersCurled = (
                        indexTipY > palmY and
                        middleTipY > palmY and
                        ringTipY > palmY and
                        pinkyTipY > palmY
                    )

                    fistDirX = middleMcpX - wristX
                    fistDirY = middleMcpY - wristY

                    fistAngle = math.degrees(math.atan2(fistDirY, fistDirX)) + 90
                    if fistAngle < 0:
                        fistAngle += 360

                    isFistUp = fistAngle < 45 or fistAngle > 315

                    if fingersCurled and isFistUp:
                        gestureStatus[handKey] = "confirm"
                        # Stop movement when switching to fist
                        if handedness == "Left":  # watergirl - right hand
                            app.icegirlMovingDirection = None
                            if app.icegirlstatus in ['turn left', 'turn right']:
                                app.icegirlstatus = 'stand'
                            #  level 2 confirm for watergirl
                            if app.gamemode == 'level2' and currentTime - app.lastConfirmTimeRight > 0.5:
                                if 70 <= app.icegirlx < 130 and 640 <= app.icegirly < 665:
                                    app.icegirlstatus = 'win'
                                app.lastConfirmTimeRight = currentTime
                        else:  # fireboy - left hand
                            app.fireboyMovingDirection = None
                            if app.fireboystatus in ['turn left', 'turn right']:
                                app.fireboystatus = 'stand'
                            #  level 2 confirm for fireboy
                            if app.gamemode == 'level2' and currentTime - app.lastConfirmTimeLeft > 0.5:
                                if 870 < app.fireboyx < 930 and 640 <= app.fireboyy < 665:
                                    app.fireboystatus = 'win'
                                app.lastConfirmTimeLeft = currentTime
                        # Handle main menu fist gesture
                        if app.gamemode == 'desktopInitialize' and currentTime - app.lastMainMenuConfirmTime > 0.5:
                            fireboylevelselectstat(app)
                            icegirllevelselectStat(app)
                            app.lastMainMenuConfirmTime = currentTime
                    elif isThumbUp:
                        gestureStatus[handKey] = "jump"

                    if fingersCurled and isFistUp:
                        if handedness == "Left" and currentTime - app.lastConfirmTimeRight > 0.5:
                            if app.gamemode == 'level0':
                                if (850 < app.icegirlx < 910 and 150 <= app.icegirly < 150 + 200):
                                    app.icegirlstatus = 'win'
                            elif app.gamemode == 'level2':
                                if (70 <= app.icegirlx < 130 and 640 <= app.icegirly < 665):
                                    app.icegirlstatus = 'win'
                            elif app.gamemode == 'levelSelection':
                                for i in range(app.totalLevel):
                                    if fireboynear(app, i) and icegirlnear(app, i) and i in app.levelUnlock:
                                        app.icegirlstatus = 'win'
                            app.lastConfirmTimeRight = currentTime
                        elif handedness == "Right" and currentTime - app.lastConfirmTimeLeft > 0.5:
                            if app.gamemode == 'level0':
                                if (770 < app.fireboyx < 830 and 150 <= app.fireboyy < 150 + 200):
                                    app.fireboystatus = 'win'
                            elif app.gamemode == 'level2':
                                if (870 < app.fireboyx < 930 and 640 <= app.fireboyy < 665):
                                    app.fireboystatus = 'win'
                            elif app.gamemode == 'levelSelection':
                                for i in range(app.totalLevel):
                                    if fireboynear(app, i) and icegirlnear(app, i) and i in app.levelUnlock:
                                        app.fireboystatus = 'win'
                                        app.levelselected = i
                            app.lastConfirmTimeLeft = currentTime

                    if isThumbUp and not (fingersCurled and isFistUp):
                        if handedness == "Left" and currentTime - app.lastJumpTimeRight > 0.5:
                            if app.icegirlCanJump:
                                jump(app, 'icegirl')
                            app.lastJumpTimeRight = currentTime
                        elif handedness == "Right" and currentTime - app.lastJumpTimeLeft > 0.5:
                            if app.fireboyCanJump:
                                jump(app, 'fireboy')
                            app.lastJumpTimeLeft = currentTime

                    def calculateAngle(a, b, c):
                        angle = math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0])
                        return math.degrees(angle) % 360

                    angle = calculateAngle(
                        (indexMcpX, indexMcpY),
                        (indexPipX, indexPipY),
                        (indexTipX, indexTipY)
                    )

                    isPointing = 160 <= angle <= 200 or 160 <= (360 - angle) <= 200

                    if isPointing:
                        directionX = indexTipX - wristX
                        pointingDirection = "right" if directionX > 0 else "left"

                        gestureStatus[handKey] = f"point_{pointingDirection}"

                        if handedness == "Left":  # watergirl - right hand
                            app.icegirlMovingDirection = pointingDirection
                            app.icegirlstatus = 'turn right' if pointingDirection == "right" else 'turn left'
                        else:  # fireboy - left hand
                            app.fireboyMovingDirection = pointingDirection
                            app.fireboystatus = 'turn right' if pointingDirection == "right" else 'turn left'
                    else:
                        if handedness == "Left" and gestureStatus[handKey] != "jump" and gestureStatus[handKey] != "confirm":
                            app.icegirlMovingDirection = None
                            if app.icegirlstatus in ['turn left', 'turn right']:
                                app.icegirlstatus = 'stand'
                        elif handedness == "Right" and gestureStatus[handKey] != "jump" and gestureStatus[handKey] != "confirm":
                            app.fireboyMovingDirection = None
                            if app.fireboystatus in ['turn left', 'turn right']:
                                app.fireboystatus = 'stand'

            # Stop movement for hands that are no longer detected
            if "left_hand" not in detectedHands:
                app.fireboyMovingDirection = None
                if app.fireboystatus in ['turn left', 'turn right']:
                    app.fireboystatus = 'stand'
            if "right_hand" not in detectedHands:
                app.icegirlMovingDirection = None
                if app.icegirlstatus in ['turn left', 'turn right']:
                    app.icegirlstatus = 'stand'

            # move players based on what we found
            applyContinuousMovement(app)

            if app.showCameraWindow:
                try:
                    cv2.putText(frame, "Player 1 (Fireboy) - Left Hand", (10, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(frame, "Player 2 (Watergirl) - Right Hand", (frame.shape[1] - 350, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    if results.multi_hand_landmarks:
                        for handLandmarks in results.multi_hand_landmarks:
                            hand_tracking.draw_landmarks(
                                frame,
                                handLandmarks,
                                hand_tracking.HAND_CONNECTIONS)

                    cv2.imshow('Hand Detection', frame)
                    cv2.waitKey(1)
                except Exception as e:
                    print(f"Warning: Could not display camera window: {e}")
                    app.showCameraWindow = False

    except queue.Empty:
        pass


def stopHandDetection(app):
    """Stop the producer before releasing its camera and model."""
    app.useHandGestures = False
    if hasattr(app, 'handGestureThread'):
        app.handGestureThread.stop()
        app.handGestureThread.join()
        del app.handGestureThread
    if hasattr(app, 'cap'):
        app.cap.release()
        del app.cap
    if hasattr(app, 'hands'):
        app.hands.close()
        del app.hands
    if getattr(app, 'showCameraWindow', False):
        try:
            closeCameraWindow()
        except Exception:
            pass
    app.showCameraWindow = False
    app.fireboyMovingDirection = app.icegirlMovingDirection = None
    gestureStatus.update(left_hand=None, right_hand=None)
    while True:
        try:
            gestureQueue.get_nowait()
        except queue.Empty:
            break


def onAppStop(app):
    stopHandDetection(app)


def closeCameraWindow():
    import cv2
    cv2.destroyAllWindows()
