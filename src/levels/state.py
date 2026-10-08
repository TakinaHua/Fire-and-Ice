"""levels / state extracted from the original game."""



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
