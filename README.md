# Fire and Ice Game — 15-112 Team Project

The latest team-project version is in [`src/Game.py`](src/Game.py). This snapshot was synchronized from [15-112-s25/prelim-group-28-tp](https://github.com/15-112-s25/prelim-group-28-tp), commit `6a619ad95c6f3f46f35dce56d68774a84e092e9f` (April 24, 2025).

## Project

A Python platform game with keyboard and camera-based hand controls, built with CMU Graphics, OpenCV, and MediaPipe.

- [Latest source and assets](src/)
- [Team member contributions](contributions.txt)
- [Citations](citations.txt)
- [Video demo](video-demo.txt)
- [Original dependency list](requirements.txt)

The original course repository may require course access. The synchronized files here are available to view publicly.

## Running the latest version

This folder now uses an isolated Python 3.13 environment with updated CMU Graphics
and MediaPipe Tasks. Double-click **Play Fire and Ice.command**, or run:

```sh
./.venv/bin/python src/Game.py
```

See [PYTHON_SETUP.md](PYTHON_SETUP.md) for editor setup, pinned dependencies,
camera controls, verification, and restoring the saved original files.

## Stage 2 architecture

The current local refactor keeps `src/Game.py` as the entrypoint and splits logic
into `engine`, `entities`, `input`, `levels`, and `rendering` packages.
See [ARCHITECTURE.md](ARCHITECTURE.md) for module responsibilities, launch and
headless test commands, compatibility decisions, and verification limits.
Assets also resolve when launched from the repository root with `python src/Game.py`.

## Earlier work

The root `Team project/` folder and other pre-existing root files are retained as earlier development versions. For the final team version, use `src/Game.py` above.

Team attribution and external-source citations are preserved in the original files linked above.
