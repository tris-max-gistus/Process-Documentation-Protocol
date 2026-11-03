#!/bin/bash
# macOS launcher. Double-click (first time: right-click > Open).
# Never calls the stock /usr/bin/python3 stub, which would start a multi-GB
# Xcode Command Line Tools install prompt on a Mac that has no real Python.
cd "$(dirname "$0")" || exit 1

PY=""
for c in /Library/Frameworks/Python.framework/Versions/Current/bin/python3 \
         /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  [ -x "$c" ] && PY="$c" && break
done
if [ -z "$PY" ] && [ -x /usr/bin/python3 ] && xcode-select -p >/dev/null 2>&1; then
  PY=/usr/bin/python3
fi
if [ -z "$PY" ]; then
  echo "Python was not found."
  echo "Install the macOS installer from https://www.python.org/downloads/ then run this again."
  open "https://www.python.org/downloads/"
  read -r -p "Press Enter to close."
  exit 1
fi

"$PY" app/start.py
status=$?
[ $status -ne 0 ] && read -r -p "Something went wrong (see above). Press Enter to close."
exit $status
