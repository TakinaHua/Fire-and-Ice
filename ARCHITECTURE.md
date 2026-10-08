# Stage 2: modular game architecture

**Runtime update:** This moved copy now uses Python 3.13 and MediaPipe Tasks.
See [PYTHON_SETUP.md](PYTHON_SETUP.md) for current setup and verification commands.
The original extraction record below describes the pre-upgrade branch.

This local branch, `refactor/stage-2-architecture`, starts at
`ca02fca8c6433113bfd0906659ac82894ae1a7eb` from
`refactor/collision-physics-engine`. It reorganizes the game before any further
collision or mechanics work. The course history, assets, and bundled libraries
are unchanged.

## Module map

```text
src/
  Game.py                 Executable entrypoint and CMU callback exports
  engine/
    runtime.py            Startup and ordered per-frame orchestration
    state.py              Shared game reset, scoring, lethal collision dispatch
    collision.py          Existing AABB helpers (unchanged)
    physics.py            Existing vertical integration (unchanged)
    terrain.py            Existing ground calculations (unchanged)
  entities/
    players.py            Player initialization, selection poses, gesture movement
    enemies.py            Ghost activation and movement
    platforms.py          Moving platforms, sensors, fans, platform carrying
  input/
    keyboard.py           Key press/hold/release and character key mappings
    gestures.py           MediaPipe recognition, camera worker, queue, cleanup
  levels/
    config.py             Legacy pixel layout initialization
    state.py              Level resets and collectible state
    selection.py          Level-door proximity checks
  rendering/
    assets.py             Stable asset paths and image dimensions
    backend.py            Lazy CMU drawing adapters
    screens.py            Menu, selection, levels, doors, gesture indicators
    sprites.py            Character sprite drawing
  tests/
    test_engine.py        Original ten collision/physics tests
    test_architecture.py  Headless integration and resource tests
```

`Game.py` exposes the same seven CMU callbacks at the executable module's top
level. CMU Graphics discovers these through `__main__`; launching the file still
works. Importing `Game` does not launch the application, load graphics libraries,
or open a camera. Drawing loads CMU Graphics on demand; camera operations load
OpenCV and MediaPipe when used. This does not make those packages optional for
the normal camera-enabled startup.

The existing `app` object remains the shared mutable state interface. Modules
receive it explicitly. Entities and level configuration do not depend on the
renderer. Input calls player and level helpers; `engine/runtime.py` coordinates
input and simulation. Rendering reads state; asset metadata is shared with door
selection to preserve the original image-derived dimensions. No module imports
`Game.py`, and there are no circular imports.

The frame sequence remains: instructions gate, gestures, frozen gate, animation
and vertical motion, landing, level initialization, terrain, fans, death checks,
platform switches, collectibles, then ghost movement. Rendering dispatch and
keyboard/gesture bindings retain their original behavior.

## Run and verify

Use a Python environment compatible with the repository's existing CMU Graphics
and MediaPipe versions. The inherited requirements are minimum versions, not a
reproducible lockfile; installing the latest versions has not been validated.
The rendering integration tests need Pillow, but never open a window or camera.

From the repository root:

```sh
python -m pip install -r requirements.txt Pillow
python src/Game.py
```

The original `cd src && python Game.py` command also works. Asset paths resolve
from the source location even when launched from another working directory.

```sh
cd src
python -m unittest discover -s tests -v
python -m compileall -q Game.py engine entities input levels rendering tests
cd ..
python tools/check_architecture.py
git diff --check
```

The architecture checker checks global name references in the active modules,
then reads the fixed baseline from local Git history and compares 2,500 frame
states across all five screen modes using a deterministic keyboard sequence.
It never executes the baseline's startup or camera code. This supplements unit
tests; it is not an exhaustive equivalence proof or a general-purpose linter.

## Compatibility changes and limits

- Only `src/Game.py` is the supported executable entrypoint. Earlier course
  snapshots remain untouched.
- Moving the asset helper required anchoring paths to `src` explicitly.
- Image metadata reads now close files immediately, eliminating resource warnings.
- The gesture module now imports `queue` explicitly for the existing
  `queue.Empty` handler, fixing a previously unresolved name.
- Shared state field names, timing, numeric constants, gesture thresholds,
  scoring, collision behavior, and update order are retained. This is a module
  extraction, not a new entity object model or a redesigned physics engine.
- Existing quirks are deliberately retained, including the level-0-only effect
  of `('level0' or 'level1')`, different key-press/key-hold movement constraints,
  and the camera toggle/worker queue lifecycle. The blocking producer queue and
  camera reopen behavior merit a separate lifecycle fix and real webcam testing.
- Headless drawing spies verify asset references and dispatch, not rendered
  appearance. Camera mocks verify initialization, queue handling, and cleanup,
  not hardware access or real hand recognition.

## Verification on this branch

Python 3.12.10: 27 tests pass (10 existing, 17 new). Compilation, static global
name checks, the 2,500-frame comparison, and whitespace checks pass. Live graphical
play and webcam gesture recognition have not been verified. Before merging,
play all levels with keyboard and gestures, test H/C toggles, restart/unlock,
and quit with the camera running. No changes have been pushed or merged.
