#!/bin/bash
cd "$(dirname "$0")"

# One-time convenience: plant a Desktop alias so future launches don't
# require opening this folder at all. Tracked by a marker file in app/ so
# it only happens once per clone; delete the marker to redo it. Best-effort
# -- if this fails for any reason it's silently skipped and the app still
# launches normally below.
MARKER="app/.shortcut_created"
if [ -d "app" ] && [ ! -f "$MARKER" ]; then
    SCRIPT_PATH="$(pwd)/start.command"
    osascript \
        -e "tell application \"Finder\" to make alias file to POSIX file \"$SCRIPT_PATH\" at desktop" \
        -e "set name of result to \"Process Logger\"" \
        > /dev/null 2>&1 && touch "$MARKER"
fi

python3 app/start.py
