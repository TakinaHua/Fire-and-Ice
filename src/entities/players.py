"""entities / players extracted from the original game."""



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


def icegirllevelselectStat(app):
    app.icegirlfacewidth = 35
    app.icegirlfaceheight =80
    app.icegirlbodywidth = 20
    app.icegirlbodyheight = 20
    app.icegirlx = app.width/3 - 53
    app.icegirly = app.height/2 +5
    app.igbodydiff = 20


def applyContinuousMovement(app):
    from engine.world import move_horizontal
    for name in ('fireboy', 'icegirl'):
        direction = getattr(app, name+'MovingDirection', None)
        if direction in ('left', 'right'):
            move_horizontal(app, name, 5 if direction == 'right' else -5)
