"""World geometry in screen pixels, shared by collision and platform rendering.

Upper ledges are one-way so the existing fan/lift routes can pass through them.
Floors, the center column, world bounds, and moving platforms are solid.
"""
from engine.collision import Rect, Collider, Layer, PLAYERS


def static_platforms(level, width=1000, height=700):
    bounds = (
        Collider(Rect(-1000, -1000, 1000, height+2000), 'left-bound'),
        Collider(Rect(width, -1000, 1000, height+2000), 'right-bound'),
        Collider(Rect(0, -1000, width, 1000), 'ceiling-bound'),
    )
    if level in ('level0', 'level1'):
        return bounds + (
            Collider(Rect(0, 680, width, 20), 'floor'),
            Collider(Rect(0, 380, 800, 20), 'middle'),
            Collider(Rect(180, 180, width-180, 20), 'upper', one_way=True),
        )
    if level == 'level2':
        return bounds + (
            Collider(Rect(0, 675, width, 25), 'floor'),
            Collider(Rect(0, 495, 315, 22), 'middle-left', one_way=True),
            Collider(Rect(685, 495, width-685, 22), 'middle-right', one_way=True),
            Collider(Rect(152, 210, 681, 20), 'upper', one_way=True),
            Collider(Rect(475, 230, 50, 445), 'column'),
        )
    return bounds + (Collider(Rect(0, height/2+25, width, height), 'menu-floor'),)


def moving_platforms(app):
    if app.gamemode in ('level0', 'level1'):
        return (Collider(Rect(app.platformX, app.platformY, 180, 20), 'lift'),)
    if app.gamemode == 'level2':
        return (
            Collider(Rect(30, app.platformY1, 140, 30), 'lift-left'),
            Collider(Rect(833, app.platformY2, 140, 30), 'lift-right'),
        )
    return ()


def solids(app):
    return static_platforms(app.gamemode, app.width, app.height) + moving_platforms(app)


def hazards(level):
    # A one-pixel lip above the solid floor detects standing contact with liquids.
    if level in ('level0', 'level1'):
        return (
            Collider(Rect(400, 679, 100, 21), 'water', Layer.HAZARD, Layer.FIRE),
            Collider(Rect(600, 679, 100, 21), 'lava', Layer.HAZARD, Layer.ICE),
            Collider(Rect(380, 379, 100, 21), 'acid', Layer.HAZARD, PLAYERS),
        )
    if level == 'level2':
        return (
            Collider(Rect(185, 674, 80, 26), 'water', Layer.HAZARD, Layer.FIRE),
            Collider(Rect(725, 674, 85, 26), 'lava', Layer.HAZARD, Layer.ICE),
            Collider(Rect(450, 209, 100, 21), 'acid', Layer.HAZARD, PLAYERS),
            Collider(Rect(474, 230, 52, 420), 'chain', Layer.HAZARD, PLAYERS),
        )
    return ()
