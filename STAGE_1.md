# Stage 1: continuous collision and physics

This work is on `feature/stage-1-collision`. The architecture and Python 3.13
version was separately pushed as commit `cd8c445ec86772954e76d371bfc2f1b8c15d1f7f`
on `refactor/stage-2-python313` at https://github.com/TakinaHua/Fire-and-Ice.

## Implemented

- `engine/collision.py`: continuous AABB sweeps return first impact time and normal;
  explicit Fireboy, Icegirl, solid, hazard, and enemy categories; swept trigger
  tests cover fast players and ghosts. Edge touching alone is not lethal overlap.
- `engine/physics.py`: reusable swept movement with sliding, floor/ceiling/side
  resolution, initial penetration correction, one-way ledges, support queries,
  moving-platform carrying/pushing, and crush detection. The original
  `advance_vertical` helper remains for compatibility but no longer drives play.
- `levels/geometry.py`: explicit colliders for all three levels and the selection
  screen. Hazard masks encode water/lava immunity and shared acid/chain lethality.
- `engine/world.py`: bridges pure geometry to the existing shared app state.
  Keyboard press, held keys, and continuous gesture movement use this same path.
- `engine/runtime.py`: updates moving platforms and carries riders, applies fans,
  integrates players, then checks collectibles and moving ghosts. Ground height
  comes from actual support; walking off an edge clears jump permission.
- `entities/platforms.py`: sensor movement works in both level0 and level1; lifts
  stay within their endpoints. Position-based rider teleportation is removed.
- `rendering/screens.py`: **B** toggles collider outlines for playtesting: yellow
  solids, cyan one-way surfaces, red hazards, and green player bodies.

Players deliberately remain non-solid to each other, preserving cooperative play.
This is deterministic rectangular collision, not a general rigid-body simulation.

## Deliberate gameplay differences

Player colliders are now 22 by 50 pixels centered on the existing player anchor,
with logical feet 25 pixels below it. Art remains unchanged and is larger than the
collider. Floors/ledges use explicit screen coordinates: level0/1 floor 680,
middle 380, upper 180; level2 floor 675, middle 495, upper 210. Some resting anchor
positions therefore differ from the former guessed ground heights by 5–10 pixels.

Upper walkways and the two level2 middle ledges are one-way. The existing fan/lift
routes require passage upward through those surfaces. Other solids resolve on all
sides. Fan shafts extend to above the upper landing, replacing the old accidental
ability to jump again while already airborne. Jumping now requires real support;
leaving a lift by jumping detaches the rider immediately.

Liquid colliders follow the rendered surface with a one-pixel lip above the floor,
so standing on a harmful liquid registers contact. The level2 chain includes a
one-pixel margin in front of its solid column. Fast movement is tested along the
actual resolved path, rather than a single final position or an enclosing box.
A platform that traps a player against a solid freezes the game as a crush death.

## Verification and local playtest

From the project root:

```sh
(cd src && ../.venv/bin/python -m unittest discover -s tests -v)
./.venv/bin/python tools/check_architecture.py --static-only
./.venv/bin/python -m compileall -q src/Game.py src/engine src/entities src/input src/levels src/rendering src/tests
./.venv/bin/python tools/smoke_graphics.py
./.venv/bin/python src/Game.py
```

63 tests pass, including 26 Stage 1 tests and three camera-resource regression tests. Coverage includes all contact sides,
edge landings, thin-obstacle tunneling, diagonal sliding, initial overlaps, layers,
one-way surfaces, platform carrying/pushing/crushing, jumping off lifts, both fan
routes, character immunities, fast ghost/hazard crossings, and input consistency.
The original jump tests now place players on a floor before requesting a jump.
The legacy behavior-equality comparison is intentionally inapplicable to this
physics change; `--static-only` checks module references without that comparison.

Real CMU offscreen rendering and compilation also pass. Live playtesting is still
needed for timing and difficulty: use B to inspect colliders, try edges/ceilings,
ride both lift directions, exit each fan onto the upper walkway, test both player
immunities, restart after death, and confirm keyboard and webcam controls. The new
geometry is explicit, but level2 art is a baked background rather than generated
from collider data; the overlay helps inspect that alignment.

Stage 1 is maintained on its feature branch for review and playtesting; it has not
been merged into main. The prior version stays available on its separate branch.
