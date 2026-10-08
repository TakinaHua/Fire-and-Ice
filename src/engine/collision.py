"""Reusable axis-aligned hitbox primitives and level hazard definitions.

Coordinates are screen pixels. Objects have an x/y center and rectangular extent.
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


# Deliberately smaller than the animated artwork: forgiving gameplay hitbox.
PLAYER_WIDTH = 22
PLAYER_HEIGHT = 26
GHOST_WIDTH = 35
GHOST_HEIGHT = 35


def player_hitbox(x, y):
    return Rect.centered(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)


def ghost_hitbox(x, y):
    return Rect.centered(x, y, GHOST_WIDTH, GHOST_HEIGHT)


def hazard_rectangles(level, player):
    """Static lethal regions. Fireboy and Icegirl have different pool immunity.

    Other platforms/sensors remain handled by the existing level logic.
    """
    if level in ("level0", "level1"):
        pool = Rect(400, 650, 100, 60) if player == "fireboy" else Rect(600, 650, 100, 60)
        return (pool, Rect(380, 350, 100, 20))
    if level == "level2":
        pool = Rect(185, 645, 70, 60) if player == "fireboy" else Rect(725, 645, 85, 60)
        return (pool, Rect(450, 175, 90, 25), Rect(475, 230, 50, 420))
    return ()
