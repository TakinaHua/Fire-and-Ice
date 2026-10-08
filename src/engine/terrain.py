"""Ground support comes from collider geometry, never coordinate range guesses."""
from engine.world import refresh_support


def update_ground_levels(app):
    for name in ('fireboy', 'icegirl'):
        refresh_support(app, name)
