"""Pure vertical movement step; no dependency on rendering or game input."""


def advance_vertical(y, velocity_y, gravity, ground_y):
    """Integrate one frame and clamp at the current ground.

    Returns (new_y, new_velocity_y, grounded). Y increases down the screen.
    The caller owns the ground-height calculation and jump state.
    """
    next_velocity = velocity_y + gravity
    next_y = y + next_velocity
    if next_y >= ground_y:
        return ground_y, 0, True
    return next_y, next_velocity, False


from dataclasses import dataclass
from engine.collision import Rect, overlaps, translated, sweep, PLAYERS

EPSILON = 1e-7


@dataclass(frozen=True)
class Motion:
    rect: Rect
    contacts: tuple
    segments: tuple
    crushed: bool = False

    @property
    def grounded(self):
        return any(normal_y == -1 for _, _, normal_y in self.contacts)


def move_body(body, dx, dy, colliders, layer=PLAYERS):
    """Sweep, slide, and resolve initial penetration against solid AABBs.

    Each contact removes the velocity component entering that face. Remaining
    tangential movement is swept again, so thin walls/floors cannot be skipped.
    One-way surfaces only catch bodies crossing their top while descending.
    """
    solids = [c for c in colliders if c.mask & layer]
    contacts, segments = [], []
    for _ in range(12):
        intersecting = [c for c in solids if not c.one_way and overlaps(body, c.rect)]
        if not intersecting:
            break
        candidates = []
        for c in intersecting:
            r = c.rect
            candidates.extend([
                (abs(r.x-body.x-body.width), r.x-body.x-body.width, 0, c, -1, 0),
                (abs(r.x+r.width-body.x), r.x+r.width-body.x, 0, c, 1, 0),
                (abs(r.y-body.y-body.height), 0, r.y-body.y-body.height, c, 0, -1),
                (abs(r.y+r.height-body.y), 0, r.y+r.height-body.y, c, 0, 1),
            ])
        _, push_x, push_y, collider, nx, ny = min(candidates, key=lambda v: v[0])
        old = body; body = translated(body, push_x, push_y)
        segments.append((old, body)); contacts.append((collider.key, nx, ny))
    for _ in range(8):
        if abs(dx) < EPSILON and abs(dy) < EPSILON:
            break
        hits = []
        for collider in solids:
            if collider.one_way and (dy <= 0 or body.y+body.height > collider.rect.y+EPSILON):
                continue
            hit = sweep(body, dx, dy, collider.rect)
            if hit is not None and (not collider.one_way or hit.normal_y == -1):
                hits.append((hit, collider))
        if not hits:
            end = translated(body, dx, dy); segments.append((body, end)); body = end
            break
        earliest = min(hit.time for hit, _ in hits)
        end = translated(body, dx*earliest, dy*earliest)
        segments.append((body, end)); body = end
        dx *= 1-earliest; dy *= 1-earliest
        for hit, collider in hits:
            if abs(hit.time-earliest) <= EPSILON:
                contacts.append((collider.key, hit.normal_x, hit.normal_y))
                if hit.normal_x: dx = 0
                if hit.normal_y: dy = 0
    crushed = any(not c.one_way and overlaps(body, c.rect) for c in solids)
    return Motion(body, tuple(contacts), tuple(segments), crushed)


def supporting_platform(body, colliders):
    return next((c for c in colliders
                 if abs(body.y+body.height-c.rect.y) <= EPSILON
                 and body.x < c.rect.x+c.rect.width
                 and body.x+body.width > c.rect.x), None)


def platform_motion(body, previous, current, other_solids, layer=PLAYERS):
    """Carry riders and push bodies contacted by a moving platform.

    Resolve against other solids before checking for crushing. The platform's
    previous position determines support; proximity alone never teleports a body.
    """
    dx, dy = current.rect.x-previous.rect.x, current.rect.y-previous.rect.y
    rider = supporting_platform(body, [previous]) is not None
    hit = sweep(previous.rect, dx, dy, body)
    if not rider and hit is None:
        return Motion(body, (), ())
    if rider:
        push_x, push_y = dx, dy
    else:
        push_x = dx*(1-hit.time) if hit.normal_x else 0
        push_y = dy*(1-hit.time) if hit.normal_y else 0
    result = move_body(body, push_x, push_y, other_solids, layer)
    crushed = result.crushed or overlaps(result.rect, current.rect)
    return Motion(result.rect, result.contacts, result.segments, crushed)
