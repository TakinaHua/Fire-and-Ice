"""Executable CMU Graphics entrypoint. Run: python src/Game.py."""
from engine.runtime import onAppStart, onStep
from input.keyboard import onKeyPress, onKeyRelease, onKeyHold
from input.gestures import onAppStop
from rendering.screens import redrawAll


if __name__ == '__main__':
    # CMU runApp expects its initial app binding in the executable namespace.
    from cmu_graphics import app, runApp
    runApp()
