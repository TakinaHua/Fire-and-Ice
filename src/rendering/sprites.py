"""rendering / sprites extracted from the original game."""
from rendering.assets import getAssetPath
from rendering.backend import drawImage


def fireboystand(app):
    imagefireboybody = getAssetPath('fireboy/fireboy stand.png')
    drawImage(imagefireboybody, app.fireboyx,
              app.fireboyy +app.fbbodydiff-app.fireoffset ,
                width = app.fireboybodywidth,height = app.fireboybodyheight,
                align = 'center' )

    imagefireboy = getAssetPath(f"fireboy/fireboy stand {app.fireboystand}.png")
    drawImage(imagefireboy, app.fireboyx,
              app.fireboyy -app.fireoffset-app.firefaceoffset ,
              width = app.fireboyfacewidth, height = app.fireboyfaceheight,
              align ='center')


def fireboyLeft(app):


    flippedBodyPath = getAssetPath(
        f"fireboy/fireboy run {app.fireboyrun}_flipped.png"
    )


    drawImage(flippedBodyPath, app.fireboyx,
              app.fireboyy + app.fbbodydiff- app.fireoffset,
              width=app.fireboybodywidth, height=app.fireboybodyheight,
              align='center')



    flippedFacePath = getAssetPath(
        f"fireboy/fireboy_facerun_{app.fireboystand}_flipped.png"
    )


    drawImage(flippedFacePath, app.fireboyx+5,
              app.fireboyy+5- app.fireoffset -app.firefaceoffset,
              width=45, height=35,
              align='center')


def fireboyRight(app):
    imagefireboy = getAssetPath(
        f"fireboy/fireboy_facerun_{app.fireboystand}.png"
    )
    drawImage(imagefireboy, app.fireboyx-5,
              app.fireboyy+5- app.fireoffset - app.firefaceoffset,
              width = 45, height = 35,
              align ='center')

    imagefireboyrun = getAssetPath(f'fireboy/fireboy run {app.fireboyrun}.png')
    drawImage(imagefireboyrun, app.fireboyx,
              app.fireboyy + app.fbbodydiff- app.fireoffset,
                width = app.fireboybodywidth,height = app.fireboybodyheight,
                align = 'center' )


def fireboyUp(app):

    imagefireboyUp = getAssetPath(
        f'fireboy/fireboy_jump_{app.fireboystand}.png'
    )
    drawImage(imagefireboyUp, app.fireboyx,
              app.fireboyy- app.fireoffset - app.firefaceoffset,
              width = 35, height = app.fireboyfaceheight,
              align ='center')


def fireboyWin(app):
    imagefireboywin = getAssetPath(f'fireboy/fireboy_win_{app.fireboywin}.png')
    drawImage(imagefireboywin, app.fireboyx-30, app.fireboyy-40)


def icegirlstand(app):
    imageicegirlbody = getAssetPath('icegirl/icegirl stand.png')
    drawImage(imageicegirlbody, app.icegirlx-1, app.icegirly + app.igbodydiff,
                width = app.icegirlbodywidth,height = app.icegirlbodyheight,
                align = 'center' )

    imageicegirl = getAssetPath(
        f"icegirl/watergirl_face_{app.icegirlstand}.png"
    )
    drawImage(imageicegirl, app.icegirlx, app.icegirly,
              width = app.icegirlfacewidth, height = app.icegirlfaceheight,
              align ='center')


def icegirlLeft(app):


    flippedBodyPath = getAssetPath(
        f"icegirl/icegirlrun{app.icegirlrun}_flipped.png"
    )


    drawImage(flippedBodyPath, app.icegirlx - 10, app.icegirly + app.igbodydiff,
              width=app.icegirlbodywidth, height=app.icegirlbodyheight,
              align='center')


    flippedFacePath = getAssetPath(
        f"icegirl/watergirl_facerun_{app.icegirlstand}_flipped.png"
    )


    drawImage(flippedFacePath, app.icegirlx, app.icegirly,
              width=60, height=app.icegirlfaceheight,
              align='center')


def icegirlRight(app):

    imageicegirlbody = getAssetPath(f"icegirl/icegirlrun{app.icegirlrun}.png")
    drawImage(imageicegirlbody, app.icegirlx+10, app.icegirly + app.igbodydiff,
                width = app.icegirlbodywidth,height = app.icegirlbodyheight,
                align = 'center' )

    imageicegirl = getAssetPath(
        f"icegirl/watergirl_facerun_{app.icegirlstand}.png"
    )
    drawImage(imageicegirl, app.icegirlx, app.icegirly,
              width = 60, height = app.icegirlfaceheight,
              align ='center')


def icegirlUp(app):
    imageicegirlUp = getAssetPath(
        f'icegirl/icegirl_jump_{app.icegirlstand}.png'
    )
    drawImage(imageicegirlUp, app.icegirlx, app.icegirly,
              width = 35, height = app.icegirlfaceheight-10,
              align ='center')


def icegirlDown(app):
    imageicegirlDown = getAssetPath(
        f'icegirl/icegirl_down_{app.icegirlstand}.png'
    )
    drawImage(imageicegirlDown, app.icegirlx, app.icegirly,
              width = 35, height = app.icegirlfaceheight-10,
              align ='center')


def icegirlWin(app):
    imageicegirlwin = getAssetPath(f'icegirl/icegirl_win_{app.icegirlwin}.png')
    drawImage(imageicegirlwin, app.icegirlx-35, app.icegirly-40)
