"""levels / selection extracted from the original game."""
from rendering.assets import imageSize
from rendering.assets import getAssetPath


def fireboynear(app, i):
    doorout = getAssetPath('doors/doorout.png')
    dowid, dohei = imageSize(doorout)
    spacing = app.width / (app.totalLevel + 1)
    x = spacing * (i + 1)
    return abs(app.fireboyx - (x - dowid/2-10)) < 40


def icegirlnear(app, i):
    doorout = getAssetPath('doors/doorout.png')
    dowid, dohei = imageSize(doorout)
    spacing = app.width / (app.totalLevel + 1)
    x = spacing * (i + 1)
    return abs(app.icegirlx - (x + dowid/2-10)) < 40
