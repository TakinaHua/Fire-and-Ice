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
