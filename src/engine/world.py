"""Adapt reusable physics to the existing CMU app state, without graphics imports."""
from engine.collision import (Layer, player_hitbox, ghost_hitbox, swept_overlap,
                              PLAYER_WIDTH, PLAYER_HEIGHT)
from engine.physics import move_body, supporting_platform, platform_motion
from levels.geometry import solids, hazards, moving_platforms

PLAYERS = ('fireboy', 'icegirl')


def player_layer(name):
    return Layer.FIRE if name == 'fireboy' else Layer.ICE


def body(app, name):
    return player_hitbox(getattr(app, name+'x'), getattr(app, name+'y'))


def store_body(app, name, rect):
    setattr(app, name+'x', rect.x+PLAYER_WIDTH/2)
    setattr(app, name+'y', rect.y+PLAYER_HEIGHT/2)


def check_segments(app, name, segments):
    targets = [c.rect for c in hazards(app.gamemode) if c.mask & player_layer(name)]
    if app.gamemode == 'level1' and app.ghostActive:
        targets.append(ghost_hitbox(app.ghostX, app.ghostY))
    if any(swept_overlap(start, end, target)
           for start, end in segments for target in targets):
        app.gameFrozen = True


def move_player(app, name, dx=0, dy=0):
    start = body(app, name)
    result = move_body(start, dx, dy, solids(app), player_layer(name))
    store_body(app, name, result.rect)
    check_segments(app, name, result.segments or ((start, result.rect),))
    if result.crushed:
        app.gameFrozen = True
    return result


def refresh_support(app, name):
    support = supporting_platform(body(app, name), solids(app))
    if getattr(app, name+'VelY') < 0:
        support = None
    setattr(app, name+'CanJump', support is not None)
    setattr(app, name+'ground', support.rect.y-PLAYER_HEIGHT/2 if support else float('inf'))
    if support is not None and getattr(app, name+'status') == 'up':
        setattr(app, name+'status', 'stand')
    return support


def move_horizontal(app, name, distance):
    if app.gameFrozen:
        return
    move_player(app, name, dx=distance)
    refresh_support(app, name)
    setattr(app, name+'status', 'turn right' if distance > 0 else 'turn left')


def jump(app, name):
    if not app.gameFrozen and refresh_support(app, name) is not None:
        setattr(app, name+'VelY', app.jumpSpeed)
        setattr(app, name+'CanJump', False)
        setattr(app, name+'status', 'up')


def step_players(app):
    for name in PLAYERS:
        velocity = getattr(app, name+'VelY') + app.gravity
        result = move_player(app, name, dy=velocity)
        if any(ny for _, _, ny in result.contacts):
            velocity = 0
        setattr(app, name+'VelY', velocity)
        refresh_support(app, name)


def carry_players(app, previous):
    current = {c.key: c for c in moving_platforms(app)}
    for old in previous:
        new = current[old.key]
        others = [c for c in solids(app) if c.key != old.key]
        for name in PLAYERS:
            if getattr(app, name+'VelY') < 0 and supporting_platform(body(app, name), [old]):
                continue
            result = platform_motion(body(app, name), old, new, others, player_layer(name))
            store_body(app, name, result.rect)
            check_segments(app, name, result.segments)
            if result.crushed:
                app.gameFrozen = True


def ghost_collisions(app, previous):
    if app.gamemode == 'level1' and app.ghostActive:
        current = ghost_hitbox(app.ghostX, app.ghostY)
        if any(swept_overlap(previous, current, body(app, name)) for name in PLAYERS):
            app.gameFrozen = True
