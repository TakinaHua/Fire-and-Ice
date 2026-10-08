"""entities / platforms extracted from the original game."""



def moveTrap(app):
    if app.gamemode in ('level0', 'level1'):
        if ((560 <= app.fireboyx <= 620) and (318 <= app.fireboyy <= 400) or
            (560 <= app.icegirlx <= 620) and (318 <= app.icegirly <= 400)):
            if app.platformY < 380:
                app.platformY += 5
        elif ((260 <= app.fireboyx <= 310) and (150 <= app.fireboyy <= 210) or
            (260 <= app.icegirlx <= 310 and 150 <= app.icegirly <=200)):
            if app.platformY < 380:
                app.platformY += 5
        else:
            if app.platformY > 180:
                app.platformY -= 5

    if app.gamemode == 'level2':
        if (((210 <= app.fireboyx <= 260) and ((180 <= app.fireboyy <= 210) or
            (400 <= app.fireboyy <= 470))) or ((210 <= app.icegirlx <= 260 )
            and ((180 <= app.icegirly <= 220) or
                 (400 <= app.icegirly <= 500)))):
            if app.platformY2 < 500:
                app.platformY2 = min(500, app.platformY2 + 5)
        elif (((730 <= app.fireboyx <= 770) and ((180 <= app.fireboyy <= 210) or
            (400 <= app.fireboyy <= 470))) or ((730 <= app.icegirlx <= 770 )
            and ((180 <= app.icegirly <= 220) or
                 (400 <= app.icegirly <= 500)))):
            if app.platformY1 < 500:
                app.platformY1 = min(500, app.platformY1 + 5)
        else:
            if app.platformY1 > 204:
                app.platformY1 = max(204, app.platformY1 - 5)
            if app.platformY2 > 204:
                app.platformY2 = max(204, app.platformY2 - 5)


def onFanLevel2(app):
    for name in ('fireboy', 'icegirl'):
        x, y = getattr(app, name+'x'), getattr(app, name+'y')
        if (360 <= x <= 460 or 540 <= x <= 620) and 160 <= y <= 650:
            setattr(app, name+'VelY', -5)


def onFan(app):
    # Lift shafts extend through one-way upper ledges so the route is traversable
    # without the legacy ability to jump again while already airborne.
    if app.gamemode in ('level0', 'level1'):
        for name in ('fireboy', 'icegirl'):
            x, y = getattr(app, name+'x'), getattr(app, name+'y')
            if 860 <= x <= 940 and 130 <= y <= 720:
                setattr(app, name+'VelY', -5)
    elif app.gamemode == 'level2':
        onFanLevel2(app)
