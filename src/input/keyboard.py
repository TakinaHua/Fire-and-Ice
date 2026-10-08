"""input / keyboard extracted from the original game."""
from engine.world import move_horizontal, jump
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

    if keys == 'b':
        app.debugColliders = not getattr(app, 'debugColliders', False)

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
    if keys == 'right': move_horizontal(app, 'fireboy', 5)
    elif keys == 'left': move_horizontal(app, 'fireboy', -5)
    elif keys == 'up': jump(app, 'fireboy')


def icegirlControl(app, keys):
    if keys == 'd': move_horizontal(app, 'icegirl', 5)
    elif keys == 'a': move_horizontal(app, 'icegirl', -5)
    elif keys == 'w': jump(app, 'icegirl')


def onKeyRelease(app, keys):
    if app.gamemode in ['levelSelection', 'level0','level1', 'level2']:
        if keys in ['left', 'right', 'a', 'd']:
            app.fireboystatus = 'stand'
            app.icegirlstatus = 'stand'


def onKeyHold(app, keys):
    if not app.gameFrozen and app.gamemode in ('levelSelection', 'level0', 'level1', 'level2'):
        for key in ('right', 'left', 'd', 'a'):
            if key in keys:
                if key in ('right', 'left'): fireboyControl(app, key)
                else: icegirlControl(app, key)
