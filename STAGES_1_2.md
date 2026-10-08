# Collision and physics refactor (Stages 1–2)

This branch preserves the 15-112 course version on `main`. Changes to the
newer `src/Game.py` extract reusable **engine modules**:

- `engine/collision.py`: typed AABB rectangles, player/ghost hitboxes,
  level-specific hazard definitions.
- `engine/physics.py`: independently testable gravity and vertical integration.
- `engine/terrain.py`: extracted level-dependent ground logic, retained for
  gameplay compatibility while we migrate toward geometric platform resolution.
- `tests/test_engine.py`: headless unit tests with no graphics/camera dependency.

Run checks from `src/`:

```bash
cd src
python -m unittest discover -s tests -v
```

Launch the game using the existing instructions in the repository README.

## Important limitations and follow-up work

This is an **incremental** refactor. Legacy terrain heights, fan and moving
platform repositioning, and horizontal movement constraints still use the
original coordinate-based implementations. The physics helper preserves the
original ground-clamp mechanics rather than pretending to be a complete rigid
body solver. Geometry hitboxes can alter the timing of some deaths near pools
and ghost edges; playtest both levels before merging.

Next: unify static and moving platforms using collision resolution with
previous-position checks; move all level geometry to data-driven definitions;
extract entities, controls and rendering in small behavior-preserving steps.

## Stage 2 architecture follow-up

The module extraction is now implemented on the local architecture branch. See
[ARCHITECTURE.md](ARCHITECTURE.md) for the current folder map and verification.
Further collision resolution changes remain deferred.
