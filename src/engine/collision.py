"""Reusable axis-aligned hitbox primitives and level hazard definitions.

Rect coordinates are top-left screen pixels; player/ghost helpers accept centers.
These pure helpers are independent of CMU Graphics and webcam input.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self):
        if self.width < 0 or self.height < 0:
            raise ValueError("Collider dimensions must be nonnegative")

    @classmethod
    def centered(cls, cx, cy, width, height):
        return cls(cx - width / 2, cy - height / 2, width, height)


def overlaps(a: Rect, b: Rect) -> bool:
    """True when positive-area intersection exists (edge-touch is not overlap)."""
    return (a.x < b.x + b.width and
            a.x + a.width > b.x and
            a.y < b.y + b.height and
            a.y + a.height > b.y)


# A narrow collision body with feet 25px below the existing sprite anchor.
PLAYER_WIDTH = 22
PLAYER_HEIGHT = 50
GHOST_WIDTH = 35
GHOST_HEIGHT = 35


def player_hitbox(x, y):
    return Rect.centered(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)


def ghost_hitbox(x, y):
    return Rect.centered(x, y, GHOST_WIDTH, GHOST_HEIGHT)


def hazard_rectangles(level, player):
    """Static lethal regions. Fireboy and Icegirl have different pool immunity.

    Compatibility query backed by the level collision layers.
    """
    from levels.geometry import hazards
    layer = Layer.FIRE if player == 'fireboy' else Layer.ICE
    return tuple(c.rect for c in hazards(level) if c.mask & layer)


# Collision categories allow geometry to opt into Fireboy/Icegirl independently.
from enum import IntFlag


class Layer(IntFlag):
    FIRE = 1
    ICE = 2
    SOLID = 4
    HAZARD = 8
    ENEMY = 16


PLAYERS = Layer.FIRE | Layer.ICE


@dataclass(frozen=True)
class Collider:
    rect: Rect
    key: str = ''
    layer: Layer = Layer.SOLID
    mask: Layer = PLAYERS
    one_way: bool = False


@dataclass(frozen=True)
class Hit:
    time: float
    normal_x: int
    normal_y: int


def translated(rect, dx, dy):
    return Rect(rect.x + dx, rect.y + dy, rect.width, rect.height)


def sweep(a, dx, dy, b):
    """Continuous AABB time of first contact in [0, 1], excluding grazing.

    Initial penetration is handled separately by the resolver. Merely resting
    against a face and moving away or parallel to it is not a new impact.
    """
    entries, exits = [], []
    for start, size, speed, other, extent in (
        (a.x, a.width, dx, b.x, b.width),
        (a.y, a.height, dy, b.y, b.height),
    ):
        if abs(speed) < 1e-12:
            if start + size <= other or start >= other + extent:
                return None
            entries.append(float('-inf')); exits.append(float('inf'))
        else:
            t1 = (other - start - size) / speed
            t2 = (other + extent - start) / speed
            entries.append(min(t1, t2)); exits.append(max(t1, t2))
    enter, leave = max(entries), min(exits)
    if enter < -1e-9 or enter > 1 or enter >= leave or leave <= 0:
        return None
    if entries[0] > entries[1]:
        return Hit(max(0, enter), -1 if dx > 0 else 1, 0)
    return Hit(max(0, enter), 0, -1 if dy > 0 else 1)


def swept_overlap(start, end, target):
    if overlaps(start, target) or overlaps(end, target):
        return True
    hit = sweep(start, end.x-start.x, end.y-start.y, target)
    return hit is not None and hit.time < 1
