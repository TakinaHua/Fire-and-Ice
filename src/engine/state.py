"""engine / state extracted from the original game."""
from levels.config import initialize_layout
from engine.collision import overlaps, player_hitbox, ghost_hitbox, hazard_rectangles
from entities.players import fireboyinitialstat, icegirlinitialstat
from levels.state import level1initialstat, level2initialstat


def initialstats(app):
    app.debugColliders = False
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


    initialize_layout(app)
    app.level1Initialized = False
    app.level2Initialized = False
    app.blueDiamond1 = True
    app.redDiamond1 = True
    app.blueDiamond2 = True
    app.redDiamond2 = True
    app.levelscore1 = 0


def calculateScore(app):
    score = 0
    if app.gamemode == 'level0':
        L = [app.blueDiamond1, app.blueDiamond2,
             app.redDiamond2, app.redDiamond1]
        for x in L:
            if x == False:
                score +=25
        return score


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
