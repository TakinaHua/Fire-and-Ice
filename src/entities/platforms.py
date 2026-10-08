"""entities / platforms extracted from the original game."""



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
