"""rendering / screens extracted from the original game."""
from rendering.assets import imageSize
from input.gestures import gestureStatus
from engine.state import calculateScore
from levels.selection import fireboynear, icegirlnear
from rendering.assets import doorInfo, getAssetPath
from rendering.sprites import fireboyLeft, fireboyRight, fireboyUp, fireboyWin, fireboystand, icegirlLeft, icegirlRight, icegirlUp, icegirlWin, icegirlstand
from rendering.backend import drawImage, drawLabel, drawRect, rgb


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
    if getattr(app, "debugColliders", False):
        drawColliders(app)


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
    fiwid, fihei = imageSize(floorImage)


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


def drawColliders(app):
    from levels.geometry import solids, hazards
    from engine.world import body
    for collider in solids(app) + hazards(app.gamemode):
        rect = collider.rect
        if collider.key.endswith('bound'): continue
        color = 'red' if collider in hazards(app.gamemode) else ('cyan' if collider.one_way else 'yellow')
        drawRect(rect.x, rect.y, rect.width, rect.height, fill=None, border=color)
    for name in ('fireboy', 'icegirl'):
        rect = body(app, name)
        drawRect(rect.x, rect.y, rect.width, rect.height, fill=None, border='lime')
