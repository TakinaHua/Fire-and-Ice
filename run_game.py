"""Launch using the project's isolated Python, regardless of shell environment."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
python = root / '.venv' / 'bin' / 'python'
if not python.is_file():
    raise SystemExit('Project environment missing. Follow PYTHON_SETUP.md to recreate it.')
raise SystemExit(subprocess.call([str(python), str(root / 'src' / 'Game.py')], cwd=root))
