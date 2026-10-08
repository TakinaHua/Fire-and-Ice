"""engine / runtime extracted from the original game."""
from engine.physics import advance_vertical
from engine.terrain import update_ground_levels
from engine.state import checkdead, initialstats
from entities.enemies import ghostMove
from entities.platforms import moveTrap, onFan
from input.gestures import initHandDetection, processHandGestures
from levels.state import checkDiamond, level1initialstat, level2initialstat


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
