from cmu_graphics import *
from PIL import Image
import os
import cv2
import mediapipe as mp
import math
import time
import threading
from queue import Queue
from engine.collision import Rect, overlaps, player_hitbox, ghost_hitbox, hazard_rectangles
from engine.physics import advance_vertical
from engine.terrain import update_ground_levels

gestureStatus = {"left_hand": None, "right_hand": None}  # this dicitonary stores the current gesture status
showCameraWindow = False  # this flag controls whether the camera window is shown

# Thread-safe queue
gestureQueue = Queue(maxsize=10)
# !!! the reason we use a queue is two-fold:
# 1. to avoid race conditions
# 2. to avoid decoupling
# queues have built-in thread synchronization, meaning that only one thread can access data at a time
# queues also allow frames to accumulate in the queue if the main thread falls behind allowing for the game and camere to run at different FPS
# learned the implementaion in the queues documentation linked in citations.txt
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
            gestureQueue.put((frame, results))
            
            # Control processing rate
            time.sleep(0.01)  # 100 FPS max processing rate
            
    def stop(self):
        self.running = False

# Initialize MediaPipe and OpenCV variables
# most of the initialization code for MediaPipe and OpenCV was taken from the MediaPipe documentation linked in citations.txt
def initHandDetection(app):
    app.mpHands = mp.solutions.hands
    app.mpDrawing = mp.solutions.drawing_utils
    app.hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.3
    )
    
    app.cap = cv2.VideoCapture(0)
    if not app.cap.isOpened():
        print("Error: Could not open camera.")
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
    app.handGestureThread = HandGestureThread(app)
    app.handGestureThread.start()
    
    return True

# Process a single frame from the camera
def processHandGestures(app):
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
                    
                    wrist = handLandmarks.landmark[app.mpHands.HandLandmark.WRIST]
                    thumbMcp = handLandmarks.landmark[app.mpHands.HandLandmark.THUMB_MCP]
                    thumbTip = handLandmarks.landmark[app.mpHands.HandLandmark.THUMB_TIP]
                    indexMcp = handLandmarks.landmark[app.mpHands.HandLandmark.INDEX_FINGER_MCP]
                    indexPip = handLandmarks.landmark[app.mpHands.HandLandmark.INDEX_FINGER_PIP]
                    indexTip = handLandmarks.landmark[app.mpHands.HandLandmark.INDEX_FINGER_TIP]
                    middleTip = handLandmarks.landmark[app.mpHands.HandLandmark.MIDDLE_FINGER_TIP]
                    ringTip = handLandmarks.landmark[app.mpHands.HandLandmark.RING_FINGER_TIP]
                    pinkyTip = handLandmarks.landmark[app.mpHands.HandLandmark.PINKY_TIP]
                    middleMcp = handLandmarks.landmark[app.mpHands.HandLandmark.MIDDLE_FINGER_MCP]
                    
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
                                app.icegirlVelY = app.jumpSpeed
                                app.icegirlCanJump = False
                                app.icegirlstatus = 'up'
                            app.lastJumpTimeRight = currentTime
                        elif handedness == "Right" and currentTime - app.lastJumpTimeLeft > 0.5:
                            if app.fireboyCanJump:
                                app.fireboyVelY = app.jumpSpeed
                                app.fireboyCanJump = False
                                app.fireboystatus = 'up'
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
                            app.mpDrawing.draw_landmarks(
                                frame,
                                handLandmarks,
                                app.mpHands.HAND_CONNECTIONS)
                    
                    cv2.imshow('Hand Detection', frame)
                    cv2.waitKey(1)
                except Exception as e:
                    print(f"Warning: Could not display camera window: {e}")
                    app.showCameraWindow = False
                    
    except queue.Empty:
        pass  # No new frames to process

# keep players moving smooth even when we skip frames
def applyContinuousMovement(app):
    # move fireboy if he's supposed to be moving
    if app.fireboyMovingDirection == "right":
        if app.fireboyx < app.width:
            app.fireboyx += 5
            app.fireboystatus = 'turn right'
    elif app.fireboyMovingDirection == "left":
        if app.fireboyx > 0:
            app.fireboyx -= 5
            app.fireboystatus = 'turn left'
    
    # move icegirl if she's supposed to be moving
    if app.icegirlMovingDirection == "right":
        if app.icegirlx < app.width:
            app.icegirlx += 5
            app.icegirlstatus = 'turn right'
    elif app.icegirlMovingDirection == "left":
        if app.icegirlx > 0:
            app.icegirlx -= 5
            app.icegirlstatus = 'turn left'

# Draw hand gesture indicators
def drawGestureIndicators(app):
    if not app.useHandGestures:
        return
    
    drawRect(50, 50, 100, 40, fill='black', opacity=70)
    
    gesture = gestureStatus.get("left_hand", None)
    if gesture == "jump":
        drawLabel("JUMP", 100, 70, fill='yellow', bold=True)
    elif gesture == "confirm":
        drawLabel("ACTION", 100, 70, fill='purple', bold=True)
    elif gesture == "point_left":
        drawLabel("LEFT", 100, 70, fill='red', bold=True)
    elif gesture == "point_right":
        drawLabel("RIGHT", 100, 70, fill='red', bold=True)
    else:
        drawLabel("IDLE", 100, 70, fill='white')
    
    drawRect(app.width - 150, 50, 100, 40, fill='black', opacity=70)
    
    gesture = gestureStatus.get("right_hand", None)
    if gesture == "jump":
        drawLabel("JUMP", app.width - 100, 70, fill='yellow', bold=True)
    elif gesture == "confirm":
        drawLabel("ACTION", app.width - 100, 70, fill='purple', bold=True)
    elif gesture == "point_left":
        drawLabel("LEFT", app.width - 100, 70, fill='red', bold=True)
    elif gesture == "point_right":
        drawLabel("RIGHT", app.width - 100, 70, fill='red', bold=True)
    else:
        drawLabel("IDLE", app.width - 100, 70, fill='white')
        
    if hasattr(app, 'lowPerformanceMode') and app.lowPerformanceMode:
        drawRect(app.width/2 - 100, 50, 200, 30, fill='black', opacity=70)
        drawLabel("LOW PERFORMANCE MODE", app.width/2,65,fill='green',bold=True)
        
    if hasattr(app, 'frameProcessingRate'):
        drawRect(app.width/2 - 100, 90, 200, 30, fill='black', opacity=70)
        drawLabel(f"Processing 1/{app.frameProcessingRate} frames", 
                  app.width/2, 105, fill='cyan')

# Helper function 
def calculateScore(app):
    score = 0
    if app.gamemode == 'level0':
        L = [app.blueDiamond1, app.blueDiamond2, 
             app.redDiamond2, app.redDiamond1]
        for x in L:
            if x == False:
                score +=25
        return score

def getAssetPath(path):
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(scriptDir, "Team project", "game it self", path)

def fireboynear(app, i):
    doorout = getAssetPath('doors/doorout.png')
    dO = Image.open(doorout)
    dowid, dohei = dO.size
    spacing = app.width / (app.totalLevel + 1)
    x = spacing * (i + 1) 
    return abs(app.fireboyx - (x - dowid/2-10)) < 40

def icegirlnear(app, i):
    doorout = getAssetPath('doors/doorout.png')
    dO = Image.open(doorout)
    dowid, dohei = dO.size
    spacing = app.width / (app.totalLevel + 1)
    x = spacing * (i + 1) 
    return abs(app.icegirlx - (x + dowid/2-10)) < 40

#main app
def onAppStart(app):
    app.levelUnlock = [0] 
    app.levelLocked = [1, 2]
    app.useHandGestures = True  # Flag to enable/disable hand gestures
    app.showInstructions = True  # Show instructions on startup
    app.instructionScreenActive = True
    app.stepsPerSecond = 30
    
    # Initialize hand detection
    if not initHandDetection(app):
        print('''Warning: Hand detection could not be initialized. Fallin
        g back to keyboard controls.''')
        app.useHandGestures = False
    
    initialstats(app)

def initialstats(app):
    app.ghostX = 20
    app.ghostY = 655
    app.ghostSpeed = 5
    app.ghostActive = False
    app.ghostActivationTime = 350  
    app.currentLevel = 0
    app.gamemode = 'desktopInitialize'
    if app.gamemode in[ "level0","level1"]:
        level1initialstat(app) 
    if app.gamemode == 'level2':  
        level2initialstat(app)  
    app.width = 1000
    app.height = 700
    app.frameCount = 0 
    app.levelselected = 0
    app.totalLevel = 3 
    app.gravity = 1
    app.jumpSpeed = -15
    app.lockedMessageTimer = 0
    app.lockedMessage = False
    app.gameFrozen = False
    app.icegirlground = app.fireboyground =  app.groundLevel = app.height / 2 
    
    app.platformY1 = 204
    app.platformY2 = 204
    
    fireboyinitialstat(app)
    icegirlinitialstat(app)
    
    
    app.platformX = 0
    app.platformY = 180
    app.switchX = 260
    app.switchY = 150
    app.blueDiamondX = 440
    app.blueDiamondY = 140
    app.redDiamondX = 640
    app.redDiamondY = 140
    app.icegirlSensorX = 560
    app.icegirlSensorY = 360
    app.fansX = 860
    app.fansY = 660
    app.poolX = 400
    app.poolY = app.lavaY = 680
    app.lavaX = 600
    app.acidX = app.acidY = 380
    app.trapW = 100
    app.trapH = 20
    app.platformW = 180
    app.diamondW = app.diamondH = 30
    app.level1Initialized = False
    app.level2Initialized = False
    app.blueDiamond1 = True
    app.redDiamond1 = True
    app.blueDiamond2 = True
    app.redDiamond2 = True
    app.levelscore1 = 0

def level1initialstat(app):
    app.level1Initialized = True  
    app.fireboyx = 50
    app.icegirlx = 80
    app.fireboyy = app.icegirly =  625
    app.fireboyVelY = 0
    app.icegirlVelY = 0
    app.fireboyground = app.icegirlground = app.groundLevel = 655
    app.fireboyCanJump = True
    app.icegirlCanJump = True
    app.blueDiamond1 = True
    app.redDiamond1 = True
    app.blueDiamond2 = True
    app.redDiamond2 = True
    app.fireboywin = 0
    app.icegirlwin = 0
    app.levelscore1 = 0

def level2initialstat(app):
    app.fireboywin = 0
    app.icegirlwin = 0

    app.level2Initialized = True
    app.fireboyx =  50
    app.icegirlx =  880
    app.fireboyy = app.icegirly = 645
    app.fireboyVelY = 0
    app.icegirlVelY = 0
    app.fireboyground = app.icegirlground = app.groundLevel = 645
    app.fireboyCanJump = True
    app.icegirlCanJump = True
    app.platformY2 = 204
    app.platformY1 = 204
    app.blueDia1 = True
    app.blueDia2 = True
    app.blueDia3 = True
    app.blueDia4 = True
    app.redDia1 = True
    app.redDia2 = True
    app.redDia3 = True
    app.redDia4 = True

def fireboyinitialstat(app):
    app.fireboyx = app.width/3
    app.fireboyy = app.height/2-15
    app.fireboystand = 0
    app.fireboystatus = 'stand'
    app.fireboybodywidth = 30
    app.fireboybodyheight = 30
    app.fireboyfacewidth = 45
    app.fireboyfaceheight = 75
    app.fbbodydiff = 47
    app.fireboyrun = 0
    app.fireboyVelY = 0
    app.fireboyCanJump = True
    app.fireoffset = 0
    app.firefaceoffset = 0
    app.fireboywin = 0

def fireboylevelselectstat(app):
    app.gamemode = 'levelSelection'
    app.fireboybodywidth = 20
    app.fireboybodyheight = 20
    app.fireboyfacewidth = 30
    app.fireboyfaceheight = 45
    app.fireboyx = app.width/3 -115
    app.fireboyy = app.height/2 - 15
    app.fbbodydiff = 25
    app.fireoffset = 5
    app.firefaceoffset = 5

def icegirlinitialstat(app):
    app.icegirlCanJump = True
    app.icegirlstand = 0
    app.icegirlx = app.width/3 *2
    app.icegirly = app.height/2
    app.icegirlstatus = 'stand'
    app.icegirlfacewidth = 55
    app.icegirlfaceheight =125
    app.icegirlbodywidth = 30
    app.icegirlbodyheight = 30
    app.igbodydiff = 30
    app.icegirlrun = 0
    app.icegirlVelY = 0
    app.icegirlwin = 0
    app.icegirlground = app.fireboyground =  app.groundLevel = app.height / 2 

def icegirllevelselectStat(app):
    app.icegirlfacewidth = 35
    app.icegirlfaceheight =80
    app.icegirlbodywidth = 20
    app.icegirlbodyheight = 20
    app.icegirlx = app.width/3 - 53
    app.icegirly = app.height/2 +5
    app.igbodydiff = 20

def onStep(app):
    if app.instructionScreenActive:
        return
        
    # Process hand gestures if enabled
    if app.useHandGestures and not app.gameFrozen:
        processHandGestures(app)
        
    if app.gameFrozen:  
        return
        
    if not app.gameFrozen:
        app.frameCount += 1
          
        if app.frameCount % 4 == 0:
            app.fireboystand = (app.fireboystand + 1) % 5
            app.icegirlstand = (app.icegirlstand + 1) % 11
            app.icegirlrun = (app.icegirlrun +1)%7
            app.fireboyrun = (app.fireboyrun +1)%7
        if app.lockedMessage:
            app.lockedMessageTimer -= 1
            if app.lockedMessageTimer <= 0:
                app.lockedMessage = False

        if app.gamemode in ['levelSelection', 'level0', 'level1', 'level2']:
            app.icegirly, app.icegirlVelY, ice_landed = advance_vertical(
                app.icegirly, app.icegirlVelY, app.gravity, app.icegirlground)
            app.fireboyy, app.fireboyVelY, fire_landed = advance_vertical(
                app.fireboyy, app.fireboyVelY, app.gravity, app.fireboyground)
            if app.fireboystatus == 'win':
                if app.frameCount % 4 == 0:
                    if app.fireboywin < 24:
                        app.fireboywin += 1
                    elif (app.icegirlwin and app.fireboywin) == 24:
                        app.gamemode = f'level{app.levelselected}'
                        if app.gamemode == 'levelSelection':
                            level1initialstat(app)

            
            if app.icegirlstatus =='win':
                if app.frameCount% 4 == 0:
                    if app.icegirlwin <24:
                        app.icegirlwin +=1

        if app.icegirly >= app.icegirlground:
            app.icegirly = app.icegirlground
            app.icegirlVelY = 0
            app.icegirlCanJump = True
            if app.icegirlstatus == 'up':
                app.icegirlstatus = 'stand'

        if app.fireboyy >= app.fireboyground:
            app.fireboyy = app.fireboyground
            app.fireboyVelY = 0
            app.fireboyCanJump = True
            if app.fireboystatus == 'up':
                app.fireboystatus = 'stand'
    if app.gamemode in ["level1", "level0"] and not app.level1Initialized:
        level1initialstat(app) 
    if app.gamemode == 'level2' and not app.level2Initialized:
        level2initialstat(app)              

    if app.gamemode in ['level0', 'level1', 'level2']:
        update_ground_levels(app)
        onFan(app)
        checkdead(app)
        moveTrap(app)
        checkDiamond(app)
        if app.gamemode == 'level1':
            ghostMove(app)

def ghostMove(app):
    if app.frameCount >= app.ghostActivationTime:
        app.ghostActive = True
    if app.ghostActive:
        if app.ghostX < app.fansX + 40 and app.ghostY > 350:
            app.ghostX += app.ghostSpeed
        elif app.ghostY > 350 and  app.platformX - 180 < app.ghostX:
            app.ghostY -= app.ghostSpeed
        elif app.ghostX > 90 and app.ghostY > 150:
            app.ghostX -= app.ghostSpeed
        elif app.ghostY > 150:    
            app.ghostY -= app.ghostSpeed
        elif app.ghostY <= 150 and app.ghostX < 800:
            app.ghostX += app.ghostSpeed

def checkDiamond(app):
  
    if 640 <= app.fireboyx <= 670:
        if 140<=app.fireboyy <= 200:
            app.redDiamond2 = False

            
        if 620 <= app.fireboyy <= 670:
            app.redDiamond1 = False

    if 440 <= app.icegirlx <= 470:
        if 140<=app.icegirly <= 170:
            app.blueDiamond2 = False
            
        if 620 <= app.icegirly <= 670:
            app.blueDiamond1 = False



def moveTrap(app):
    if app.gamemode == ('level0' or 'level1'):
        if ((560 <= app.fireboyx <= 620) and (318 <= app.fireboyy <= 400) or
            (560 <= app.icegirlx <= 620) and (318 <= app.icegirly <= 400)):
            if app.platformY <= 380:
                app.platformY += 5
        elif ((260 <= app.fireboyx <= 310) and (150 <= app.fireboyy <= 210) or
            (260 <= app.icegirlx <= 310 and 150 <= app.icegirly <=200)):
            if app.platformY <= 380:
                app.platformY += 5
        else:
            if app.platformY > 180:
                app.platformY -= 5

    if app.gamemode == 'level2':
        if (((210 <= app.fireboyx <= 260) and ((180 <= app.fireboyy <= 210) or 
            (400 <= app.fireboyy <= 470))) or ((210 <= app.icegirlx <= 260 )
            and ((180 <= app.icegirly <= 220) or 
                 (400 <= app.icegirly <= 500)))):
            if app.platformY2 <= 500:
                app.platformY2 += 5
        elif (((730 <= app.fireboyx <= 770) and ((180 <= app.fireboyy <= 210) or 
            (400 <= app.fireboyy <= 470))) or ((730 <= app.icegirlx <= 770 )
            and ((180 <= app.icegirly <= 220) or 
                 (400 <= app.icegirly <= 500)))):
            if app.platformY1 <= 500:
                app.platformY1 += 5
        else:
            if app.platformY1 > 210:
                app.platformY1 -= 5
            if app.platformY2 > 210:
                app.platformY2 -= 5

def onFanLevel2(app):
    if ((360 <= app.fireboyx <= 460 or 540 <= app.fireboyx <= 620) 
        and (650 >= app.fireboyy >= 400)):
        app.fireboyVelY = -5
    if ((360 <= app.icegirlx <= 460 or 540 <= app.icegirlx <= 620 ) and 
        (650 >= app.icegirly >= 400)):
        app.icegirlVelY = -5
    if ((210 <app.platformY1 <= 516) and 
        (0 <= app.fireboyx <= 152) and (app.fireboyy <= 516)
        and (app.fireboyy <= app.platformY1 +40)):
        app.fireboyy = app.platformY1 -30
    if ((210 < app.platformY1 <= 516) and 
        (0 <= app.icegirlx <= 152) and (app.icegirly <= 516)
        and (app.icegirly <= app.platformY1+ 40 )):
        app.icegirly = app.platformY1 -30

    
    if ((210 <app.platformY2 <= 516) and 
        (830 <= app.fireboyx <= 1000) and (app.fireboyy <= 516)
        and (app.fireboyy <= app.platformY2 +40)):
        app.fireboyy = app.platformY2 -30
    if ((210 < app.platformY2 <= 516) and 
        (830 <= app.icegirlx <= 1000) and (app.icegirly <= 516)
        and (app.icegirly <= app.platformY2+ 40 )):
        app.icegirly = app.platformY2 -30

def onFan(app):
    if app.gamemode == 'level0' or app.gamemode == 'level1':
        if (860 <= app.fireboyx <= 940 and 320 <= app.fireboyy <= 720):
            app.fireboyVelY = -5 
        if (860 <= app.icegirlx <= 960 and 370 <= app.icegirly <= 720):  
            app.icegirlVelY = -5  
        if ((app.platformY > 180 and app.platformY <= 380) and 
            (0 <= app.fireboyx <= 180) and (app.fireboyy <= 360)
            and (app.fireboyy <= app.platformY +20)):
            app.fireboyy = app.platformY -25
        if ((app.platformY > 180 and app.platformY <= 380) and 
            (0 <= app.icegirlx <= 180) and (app.icegirly <= 360)
            and (app.icegirly <= app.platformY+ 40 )):
            app.icegirly = app.platformY -25
    if app.gamemode == 'level2':
        onFanLevel2(app)

def checkdead(app):
    """Resolve lethal collisions using rectangular hitboxes, not point equality."""
    players = (
        ("fireboy", player_hitbox(app.fireboyx, app.fireboyy)),
        ("icegirl", player_hitbox(app.icegirlx, app.icegirly)),
    )
    for name, hitbox in players:
        for hazard in hazard_rectangles(app.gamemode, name):
            if overlaps(hitbox, hazard):
                app.gameFrozen = True
                return

        if app.gamemode == "level1" and app.ghostActive:
            if overlaps(hitbox, ghost_hitbox(app.ghostX, app.ghostY)):
                app.gameFrozen = True
                return


# def updateGround(app):  

def redrawAll(app):
    if app.gamemode == 'desktopInitialize' :
        desktopInitialize(app)
    elif app.gamemode == 'levelSelection':
        levelSelection(app)
    elif app.gamemode == 'level0':
        level1(app)
    elif app.gamemode == 'level1':
        level1(app) 
        ghost = getAssetPath('background/ghost.png')
        drawImage(ghost, app.ghostX, app.ghostY,width=app.fireboybodywidth *1.5,
                  height= 2* app.fireboybodyheight, align='center')
    elif app.gamemode == 'level2':
        level2(app)
        
    # Draw hand gesture indicators
    drawGestureIndicators(app)

def onKeyPress(app, keys):
    if app.instructionScreenActive:
        app.instructionScreenActive = False
        return
        
    if app.gameFrozen and keys == 'r':
        app.gameFrozen = False
        initialstats(app)
    
    if keys == 'h':
        app.useHandGestures = not app.useHandGestures
        if app.useHandGestures and not hasattr(app, 'cap'):
            if not initHandDetection(app):
                print('''Warning: Hand detection could not be initialized. 
                      Falling back to keyboard controls.''')
                app.useHandGestures = False
        elif not app.useHandGestures and hasattr(app, 'cap'):
            app.cap.release()
            if hasattr(app, 'showCameraWindow') and app.showCameraWindow:
                try:
                    cv2.destroyAllWindows()
                except:
                    pass
    
    if keys == 'c' and hasattr(app, 'cap'):
        app.showCameraWindow = not app.showCameraWindow
        print(f'''Camera window 
              {'enabled' if app.showCameraWindow else 'disabled'}''')
 
    if not app.gameFrozen:
        if app.gamemode == 'desktopInitialize':
            if keys == 'up':
                fireboylevelselectstat(app)
                icegirllevelselectStat(app)

        if app.gamemode in ['levelSelection', 'level0', 'level1','level2']: 
            if keys == 'down' and app.gamemode == 'levelSelection':
                initialstats(app)
            icegirlControl(app, keys)
            fireboyControl(app, keys)
            if app.icegirlwin and app.fireboywin == 24:
                if keys == 'r':
                    app.levelUnlock.append(app.levelselected+1)
                    if app.levelLocked != []:
                        app.levelLocked.pop(0)
                    initialstats(app)

            if app.gamemode in ['level0','level1']:
                dbwid, dbhei, dowid, dohei, spacing, \
                doorBoy, doorGirl, doorinside, doorout = doorInfo(app)
                if (770 <app.fireboyx < 830 and 
                    150 <= app.fireboyy < 150 + dbhei):
                    if keys =='z':
                        app.fireboystatus = 'win'
                if (850 <app.icegirlx < 910 and 
                    150 <= app.icegirly < 150 + dbhei):
                    if keys == 'space':
                        app.icegirlstatus = 'win'

            if app.gamemode == 'level2':
                if 870 <app.fireboyx < 930 and 640 <= app.fireboyy < 665:
                    if keys == 'z':
                        app.fireboystatus = 'win'
                if 70 <= app.icegirlx < 130 and 640 <= app.icegirly < 665:
                    if keys == 'space':
                        app.icegirlstatus = 'win'
            if app.gamemode == 'levelSelection':
                for i in range(app.totalLevel):
                    if fireboynear(app, i) and icegirlnear(app, i):
                        if i in app.levelUnlock:
                            if keys =='z':
                                app.fireboystatus = 'win'
                                app.levelselected = i
                            if keys == 'space':
                                app.icegirlstatus = 'win'
                        else:
                            if keys in ['z', 'space']:
                                app.lockedMessage = True
                                app.lockedMessageTimer = 60


def fireboyControl(app, keys):
    if keys == 'right':
        if app.gamemode == 'level2':
            if (app.fireboyx < 475 or 
                (app.fireboyx > 525 and app.fireboyx < app.width)):
                if app.fireboyx < app.width:
                    app.fireboyx += 5
                    app.fireboystatus = 'turn right'
        else:
            if app.fireboyx < app.width:
                app.fireboyx += 5
                app.fireboystatus = 'turn right'
        

    if keys == 'up' and app.fireboyCanJump:
        app.fireboyVelY = app.jumpSpeed
        app.fireboyCanJump = False
        app.fireboystatus = 'up'


    if keys == 'left':
        if app.gamemode == 'level2':
            if (app.fireboyx < 475 or 
                (app.fireboyx > 525 and app.fireboyx < app.width)):
                if app.fireboyx > 0:
                    app.fireboyx -= 5
                    app.fireboystatus = 'turn left'
        else:
            if app.fireboyx > 0:
                app.fireboyx -= 5
                app.fireboystatus = 'turn left'



def icegirlControl(app, keys):
    if keys == 'd':
        if app.gamemode == 'level2':
            if (app.icegirlx < 475 or 
                (app.icegirlx > 525 and app.icegirlx < app.width)):
                if app.icegirlx < app.width:
                    app.icegirlx += 5
                    app.icegirlstatus = 'turn right'
        else:
            if app.icegirlx < app.width:
                app.icegirlx += 5
                app.icegirlstatus = 'turn right'

    if keys == 'w' and app.icegirlCanJump:
        app.icegirlVelY = app.jumpSpeed
        app.icegirlCanJump = False
        app.icegirlstatus = 'up'

    if keys == 'a':
        if app.gamemode == 'level2':
            if app.icegirlx > 525 or (app.icegirlx > 0 and app.icegirlx < 475):
                if app.icegirlx > 0:
                    app.icegirlx -= 5
                    app.icegirlstatus = 'turn left'
        else:
            if app.icegirlx > 0:
                app.icegirlx -= 5
                app.icegirlstatus = 'turn left'

def onKeyRelease(app, keys):
    if app.gamemode in ['levelSelection', 'level0','level1', 'level2']:
        if keys in ['left', 'right', 'a', 'd']:
            app.fireboystatus = 'stand'
            app.icegirlstatus = 'stand'

def onKeyHold(app, keys):
    if not app.gameFrozen:
        if app.gamemode in ['levelSelection', 'level0','level1', 'level2']:
            if 'right' in keys:
                if app.fireboyx < app.width:
                    app.fireboyx += 5
                    app.fireboystatus = 'turn right'
            if 'd' in keys:
                if app.icegirlx < app.width:
                    app.icegirlx += 5
                    app.icegirlstatus = 'turn right'

            if 'left' in keys:
                if app.fireboyx > 0:
                    app.fireboyx -= 5
                    app.fireboystatus = 'turn left'
            if 'a' in keys:
                if app.icegirlx > 0:
                    app.icegirlx -= 5
                    app.icegirlstatus = 'turn left'



#character presentations:


def fireboystand(app):
    imagefireboybody = getAssetPath('fireboy/fireboy stand.png')
    drawImage(imagefireboybody, app.fireboyx, 
              app.fireboyy +app.fbbodydiff-app.fireoffset , 
                width = app.fireboybodywidth,height = app.fireboybodyheight, 
                align = 'center' ) 
 
    imagefireboy = getAssetPath(f"fireboy/fireboy stand {app.fireboystand}.png")
    drawImage(imagefireboy, app.fireboyx, 
              app.fireboyy -app.fireoffset-app.firefaceoffset , 
              width = app.fireboyfacewidth, height = app.fireboyfaceheight, 
              align ='center')  

def fireboyLeft(app):


    flippedBodyPath = getAssetPath(
        f"fireboy/fireboy run {app.fireboyrun}_flipped.png"
    )


    drawImage(flippedBodyPath, app.fireboyx, 
              app.fireboyy + app.fbbodydiff- app.fireoffset,
              width=app.fireboybodywidth, height=app.fireboybodyheight,
              align='center')



    flippedFacePath = getAssetPath(
        f"fireboy/fireboy_facerun_{app.fireboystand}_flipped.png"
    )


    drawImage(flippedFacePath, app.fireboyx+5, 
              app.fireboyy+5- app.fireoffset -app.firefaceoffset,
              width=45, height=35,
              align='center')



def fireboyRight(app):
    imagefireboy = getAssetPath(
        f"fireboy/fireboy_facerun_{app.fireboystand}.png"
    )
    drawImage(imagefireboy, app.fireboyx-5, 
              app.fireboyy+5- app.fireoffset - app.firefaceoffset, 
              width = 45, height = 35, 
              align ='center')  
    
    imagefireboyrun = getAssetPath(f'fireboy/fireboy run {app.fireboyrun}.png')
    drawImage(imagefireboyrun, app.fireboyx, 
              app.fireboyy + app.fbbodydiff- app.fireoffset, 
                width = app.fireboybodywidth,height = app.fireboybodyheight, 
                align = 'center' ) 
    

def fireboyUp(app):

    imagefireboyUp = getAssetPath(
        f'fireboy/fireboy_jump_{app.fireboystand}.png'
    )
    drawImage(imagefireboyUp, app.fireboyx, 
              app.fireboyy- app.fireoffset - app.firefaceoffset, 
              width = 35, height = app.fireboyfaceheight, 
              align ='center')

#def fireboyDown(app):
 #   imageicegirlDown = f'icegirl/icegirl_down_{app.icegirlstand}.png'
  #  drawImage(imageicegirlDown, app.icegirlx, app.icegirly, 
     #         width = 35, height = app.icegirlfaceheight-10, 
     #         align ='center')

def fireboyWin(app):
    imagefireboywin = getAssetPath(f'fireboy/fireboy_win_{app.fireboywin}.png')
    drawImage(imagefireboywin, app.fireboyx-30, app.fireboyy-40)


def icegirlstand(app):
    imageicegirlbody = getAssetPath('icegirl/icegirl stand.png')
    drawImage(imageicegirlbody, app.icegirlx-1, app.icegirly + app.igbodydiff, 
                width = app.icegirlbodywidth,height = app.icegirlbodyheight, 
                align = 'center' )   
 
    imageicegirl = getAssetPath(
        f"icegirl/watergirl_face_{app.icegirlstand}.png"
    )
    drawImage(imageicegirl, app.icegirlx, app.icegirly, 
              width = app.icegirlfacewidth, height = app.icegirlfaceheight, 
              align ='center') 

def icegirlLeft(app):


    flippedBodyPath = getAssetPath(
        f"icegirl/icegirlrun{app.icegirlrun}_flipped.png"
    )

    
    drawImage(flippedBodyPath, app.icegirlx - 10, app.icegirly + app.igbodydiff,
              width=app.icegirlbodywidth, height=app.icegirlbodyheight,
              align='center')


    flippedFacePath = getAssetPath(
        f"icegirl/watergirl_facerun_{app.icegirlstand}_flipped.png"
    )


    drawImage(flippedFacePath, app.icegirlx, app.icegirly,
              width=60, height=app.icegirlfaceheight,
              align='center')

def icegirlRight(app):

    imageicegirlbody = getAssetPath(f"icegirl/icegirlrun{app.icegirlrun}.png")
    drawImage(imageicegirlbody, app.icegirlx+10, app.icegirly + app.igbodydiff, 
                width = app.icegirlbodywidth,height = app.icegirlbodyheight, 
                align = 'center' )   
    
    imageicegirl = getAssetPath(
        f"icegirl/watergirl_facerun_{app.icegirlstand}.png"
    )
    drawImage(imageicegirl, app.icegirlx, app.icegirly, 
              width = 60, height = app.icegirlfaceheight, 
              align ='center') 

def icegirlUp(app):
    imageicegirlUp = getAssetPath(
        f'icegirl/icegirl_jump_{app.icegirlstand}.png'
    )
    drawImage(imageicegirlUp, app.icegirlx, app.icegirly, 
              width = 35, height = app.icegirlfaceheight-10, 
              align ='center')

def icegirlDown(app):
    imageicegirlDown = getAssetPath(
        f'icegirl/icegirl_down_{app.icegirlstand}.png'
    )
    drawImage(imageicegirlDown, app.icegirlx, app.icegirly, 
              width = 35, height = app.icegirlfaceheight-10, 
              align ='center')
    

def icegirlWin(app):
    imageicegirlwin = getAssetPath(f'icegirl/icegirl_win_{app.icegirlwin}.png')
    drawImage(imageicegirlwin, app.icegirlx-35, app.icegirly-40)


#screens     
def desktopInitialize(app):
    imaageoftitle = getAssetPath('desktopinitial/titlescreenbackground.png')
    drawImage(imaageoftitle, app.width/2, app.height/2, width=app.width, 
                height=app.height, align = 'center')
    title = getAssetPath('desktopinitial/FireboyIcegirlTitle.png')
    drawImage(title,app.width/2, app.height/3,width= app.width/3, 
                height =app.height / 8, align = 'center')
    start = getAssetPath('desktopinitial/Fist-Up-to-Start.png')
    drawImage(start,app.width/2, 2*app.height/3, width= app.width/3, 
                height =app.height / 8, align = 'center' )
    fireboystand(app)
    icegirlstand(app)

def levelSelection(app):

    drawRect(0, 0, app.width, app.height, fill = 'black')
    if app.lockedMessage:
        drawLabel("Locked", app.width/2, 50, size=30, fill='red', bold=True)
    
    #floor:

    floorImage = getAssetPath('levelSelection/floorblock.png')
    fi = Image.open(floorImage)
    fiwid, fihei = fi.size 


#door
    drawLevelDoors(app)
    #character presentation:
    if app.fireboystatus == 'stand':
        fireboystand(app)
    elif app.fireboystatus == 'turn left':
        fireboyLeft(app)
    elif app.fireboystatus == 'turn right':
        fireboyRight(app)
    elif app.fireboystatus == 'up':
        fireboyUp(app)
    #elif app.fireboystatus == 'down':
        #fireboyDown(app)
    elif app.fireboystatus == 'win':
        fireboyWin(app)

    if app.icegirlstatus == 'stand':
        icegirlstand(app)
    elif app.icegirlstatus == 'turn left':
        icegirlLeft(app)
    elif app.icegirlstatus == 'turn right':
        icegirlRight(app)
    elif app.icegirlstatus == 'up':
        icegirlUp(app)
    #elif app.icegirlstatus == 'down':
     #   icegirlDown(app)
    elif app.icegirlstatus == 'win':
        icegirlWin(app)
    
def level1(app):
    backgroundPath = getAssetPath(f"background/bricks.png")
    drawImage(backgroundPath, 0, 0, width=app.width, height=app.height)
    drawRect(180,180,app.width,20, fill=rgb(114,104,52), border = 'black',
             borderWidth = 4) # layer 3
    drawRect(0,380,800,20, fill=rgb(114,104,52),border ='black', borderWidth =4) 
    drawRect(0,680,app.width,20, fill=rgb(114,104,52), border = 'black',
             borderWidth = 4) 
    drawLabel(f"Level {app.levelselected+1}", app.width / 2, 30, font="Arial", 
              size=20, fill="white", bold=True)
    lavaPath = getAssetPath('background/lava.png')
    drawImage(lavaPath, app.lavaX, app.lavaY, width=app.trapW, height=app.trapH)
    acidPath = getAssetPath('background/acid.png')
    drawImage(acidPath, app.acidX, app.acidY, width=app.trapW, height=app.trapH)
    poolPath = getAssetPath('background/pool.png')
    drawImage(poolPath, app.poolX, app.poolY, width=app.trapW, height=app.trapH)
    platformPath = getAssetPath('background/platform.png')
    drawImage(platformPath, app.platformX, app.platformY, width=app.platformW, 
              height=app.trapH)
    switchPath = getAssetPath('background/switchOn.png')
    drawImage(switchPath, app.switchX, app.switchY, width=50,height=40)
    blueDiamondPath = getAssetPath('background/blueDiamond.png')
    if app.blueDiamond2:
        drawImage(blueDiamondPath, app.blueDiamondX, app.blueDiamondY, 
                  width=app.diamondW, height=app.diamondH)
    if app.blueDiamond1:
        drawImage(blueDiamondPath, app.blueDiamondX, app.blueDiamondY + 480, 
                  width=app.diamondW, height=app.diamondH)
    redDiamondPath = getAssetPath('background/redDiamond.png')
    if app.redDiamond2:
        drawImage(redDiamondPath, app.redDiamondX, app.redDiamondY, 
                  width=app.diamondW, height=app.diamondH)
    if app.redDiamond1:
        drawImage(redDiamondPath, app.redDiamondX, app.redDiamondY + 480,
                  width=app.diamondW, height=app.diamondH)
    icegirlSensorPath = getAssetPath('background/watergirlSensor2.png')
    drawImage(icegirlSensorPath, app.icegirlSensorX, app.icegirlSensorY,
              width=60, height=20)
    fansPath = getAssetPath('background/fan.png')
    drawImage(fansPath, app.fansX, app.fansY, width=80, height=20)

    drawLevelDoors(app)
 
    if app.fireboystatus == 'stand':
        fireboystand(app)
    elif app.fireboystatus == 'turn left':
        fireboyLeft(app)
    elif app.fireboystatus == 'turn right':
        fireboyRight(app)
    elif app.fireboystatus == 'up':
        fireboyUp(app)
    elif app.fireboystatus == 'win':
        fireboyWin(app)
    if app.icegirlwin and app.fireboywin == 24:
        score = calculateScore(app)
        drawLabel(f"You Win! Your score is {score} - Press R start page", 
                 app.width/2, 50, size=30, fill='red', bold=True)
    if app.gameFrozen:
        drawLabel("Game Over - Press R to restart", 
                 app.width/2, 50, size=30, fill='red', bold=True)

    # Icegirl drawing
    if app.icegirlstatus == 'stand' or app.fireboystatus == 'dead':
        icegirlstand(app)
    elif app.icegirlstatus == 'turn left':
        icegirlLeft(app)
    elif app.icegirlstatus == 'turn right':
        icegirlRight(app)
    elif app.icegirlstatus == 'up':
        icegirlUp(app)
    elif app.icegirlstatus == 'win':
        icegirlWin(app)  

def level2Stat(app):
    if app.icegirlstatus == 'stand' or app.fireboystatus == 'dead':
        icegirlstand(app)
    elif app.icegirlstatus == 'turn left':
        icegirlLeft(app)
    elif app.icegirlstatus == 'turn right':
        icegirlRight(app)
    elif app.icegirlstatus == 'up':
        icegirlUp(app)
    elif app.icegirlstatus == 'win':
        icegirlWin(app) 

    if app.fireboystatus == 'stand':
        fireboystand(app)
    elif app.fireboystatus == 'turn left':
        fireboyLeft(app)
    elif app.fireboystatus == 'turn right':
        fireboyRight(app)
    elif app.fireboystatus == 'up':
        fireboyUp(app)
    elif app.fireboystatus == 'win':
        fireboyWin(app)
    if app.icegirlwin and app.fireboywin == 24:
        score = calculateScore(app)
        drawLabel(f"You Win! Your score is {score} - Press R start page", 
                 app.width/2, 50, size=30, fill='red', bold=True)
    if app.gameFrozen:
        drawLabel("Game Over - Press R to restart", 
                 app.width/2, 50, size=30, fill='red', bold=True)

def level2(app):
    backgroundimage = getAssetPath('background/level2back.png')
    drawImage(backgroundimage, 0, 0, width = app.width, height = app.height)
    fansPath = getAssetPath('background/fan.png')
    drawImage(fansPath, 390, 650, width=80, height=20)
    drawImage(fansPath, 540, 650, width=80, height=20)
    chain = getAssetPath('background/chain.png')
    drawImage(chain, 475, 230, width=50, height=500)
    platform1 = getAssetPath('background/greenplatform.png')
    drawImage(platform1, 30, app.platformY1, width=140, height=30)
    platform2 = getAssetPath('background/blueplatform.png')
    drawImage(platform2, 833, app.platformY2, width=140, height=30)
    drawLevelDoors(app)
    level2Stat(app)



    
def doorInfo(app):
    doorBoy = getAssetPath('doors/doorboy.png')
    dB = Image.open(doorBoy)
    dbwid, dbhei = dB.size

    doorGirl = getAssetPath('doors/doorgirl.png')

    doorinside = getAssetPath('doors/doorinside.png')
    doorout = getAssetPath('doors/doorout.png')
    dO = Image.open(doorout)
    dowid, dohei = dO.size

    spacing = app.width / (app.totalLevel + 1)
    return (dbwid, dbhei, dowid, dohei, spacing, 
            doorBoy, doorGirl, doorinside, doorout)

def drawLevel2Doors(app):
    dbwid, dbhei, dowid, dohei, spacing, \
    doorBoy, doorGirl, doorinside, doorout = doorInfo(app)
    if 870 <app.fireboyx < 930 and 640 <= app.fireboyy < 665:
        drawImage(doorinside, 900, 640, align='center')
    else:
        drawImage(doorBoy, 900, 640, align = 'center')
    drawImage(doorout, 900, 640, align='center')

    if 70 <= app.icegirlx < 130 and 640 <= app.icegirly < 665:
        drawImage(doorinside, 100, 640, align='center')
    else:
        drawImage(doorGirl, 100, 640, align = 'center')
    drawImage(doorout, 100, 640, align='center')

def drawLevelDoors(app):
    dbwid, dbhei, dowid, dohei, spacing, \
    doorBoy, doorGirl, doorinside, doorout = doorInfo(app)

    if app.gamemode in ['level0','level1']: 
        if 770 <app.fireboyx < 830 and 150 <= app.fireboyy < 150 + dbhei:
            drawImage(doorinside, 800, 150, align='center')
        else:
            drawImage(doorBoy, 800, 150, align = 'center')
        drawImage(doorout, 800, 150, align='center')

        if 850 <app.icegirlx < 910 and 150 <= app.icegirly < 150 + dbhei:
            drawImage(doorinside, 880, 150, align='center')
        else:
            drawImage(doorGirl, 880, 150, align = 'center')
        drawImage(doorout, 880, 150, align='center')

    if app.gamemode == 'level2':
        drawLevel2Doors(app)
    elif app.gamemode == 'levelSelection':    
        for i in range(app.totalLevel):
            x = spacing * (i + 1) 
            drawImage(doorBoy, x - dbwid/2-10, 
                app.height/2+5, align = 'center')

            drawImage(doorGirl, x + dbwid/2 + 10, app.height/2 +5, 
                    align = 'center')

            if fireboynear(app, i):
                drawImage(doorinside, x - dowid/2, app.height/2, align='center')
            else:
                drawImage(doorout, x - dowid/2, app.height/2, align='center')

            if icegirlnear(app, i):
                drawImage(doorinside, x + dowid/2, app.height/2, align='center')
            else:
                drawImage(doorout, x + dowid/2, app.height/2, align='center')

# Clean up 🧹
def onAppStop(app):
    # Clean up 🛀
    if hasattr(app, 'handGestureThread'):
        app.handGestureThread.stop()
        app.handGestureThread.join()
    
    if hasattr(app, 'cap') and app.cap.isOpened():
        app.cap.release()
    
    if hasattr(app, 'showCameraWindow') and app.showCameraWindow:
        try:
            cv2.destroyAllWindows()
        except:
            pass
    
    if hasattr(app, 'hands'):
        app.hands.close()

runApp()