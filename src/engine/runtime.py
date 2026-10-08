"""Frame orchestration for continuous collision-based movement."""
from engine.state import initialstats, checkdead
from engine.world import step_players, carry_players, ghost_collisions, refresh_support
from engine.collision import ghost_hitbox
from entities.enemies import ghostMove
from entities.platforms import moveTrap, onFan
from input.gestures import initHandDetection, processHandGestures
from levels.geometry import moving_platforms
from levels.state import level1initialstat, level2initialstat, checkDiamond


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


def initialize_level(app):
    if app.gamemode in ('level0', 'level1') and not app.level1Initialized:
        level1initialstat(app)
    elif app.gamemode == 'level2' and not app.level2Initialized:
        level2initialstat(app)


def onStep(app):
    if app.instructionScreenActive or app.gameFrozen:
        return
    initialize_level(app)
    if app.gamemode != 'desktopInitialize':
        for name in ('fireboy', 'icegirl'):
            refresh_support(app, name)
    if app.useHandGestures:
        processHandGestures(app)
    if app.gameFrozen:
        return
    app.frameCount += 1
    if app.frameCount % 4 == 0:
        app.fireboystand = (app.fireboystand + 1) % 5
        app.icegirlstand = (app.icegirlstand + 1) % 11
        app.icegirlrun = (app.icegirlrun + 1) % 7
        app.fireboyrun = (app.fireboyrun + 1) % 7
    if app.lockedMessage:
        app.lockedMessageTimer -= 1
        if app.lockedMessageTimer <= 0:
            app.lockedMessage = False
    if app.gamemode in ('levelSelection', 'level0', 'level1', 'level2'):
        previous = moving_platforms(app)
        moveTrap(app)
        carry_players(app, previous)
        if app.gameFrozen:
            return
        onFan(app)
        step_players(app)
        if app.frameCount % 4 == 0:
            if app.fireboystatus == 'win':
                if app.fireboywin < 24:
                    app.fireboywin += 1
                elif (app.icegirlwin and app.fireboywin) == 24:
                    app.gamemode = f'level{app.levelselected}'
                    initialize_level(app)
            if app.icegirlstatus == 'win' and app.icegirlwin < 24:
                app.icegirlwin += 1
    if app.gamemode in ('level0', 'level1', 'level2'):
        checkdead(app)
        checkDiamond(app)
        if app.gamemode == 'level1':
            previous = ghost_hitbox(app.ghostX, app.ghostY)
            ghostMove(app)
            ghost_collisions(app, previous)
