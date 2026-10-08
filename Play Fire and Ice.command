#!/bin/zsh
PROJECT_DIR="${0:A:h}"
cd "$PROJECT_DIR" || exit 1
"$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/src/Game.py"
status_code=$?
if (( status_code != 0 )); then
    echo "The game stopped with an error. See the message above."
    read "?Press Return to close."
fi
exit "$status_code"
