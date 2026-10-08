"""input / keyboard extracted from the original game."""
from input.gestures import stopHandDetection
from engine.state import initialstats
from entities.players import fireboylevelselectstat, icegirllevelselectStat
from input.gestures import initHandDetection
from levels.selection import fireboynear, icegirlnear
from rendering.assets import doorInfo


def onKeyPress(app, keys):
    if app.instructionScreenActive:
        app.instructionScreenActive = False
        return

    if app.gameFrozen and keys == 'r':
        app.gameFrozen = False
        initialstats(app)

    if keys == 'h':
        if app.useHandGestures:
            stopHandDetection(app)
        else:
            initHandDetection(app)

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
