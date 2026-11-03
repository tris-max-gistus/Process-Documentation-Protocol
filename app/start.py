"""Launcher for Process Log. Standard library only, so it runs on any Python 3.9+.

First run builds app/venv and installs Flask; after that it just starts the server
and opens the browser. Run it from VS Code (Run button), a terminal, or one of the
launcher scripts next to this folder.
"""
import os
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
VENV_DIR = APP_DIR / "venv"
LOG_FILE = APP_DIR / "launch_log.txt"
DEFAULT_PORT = 5173  # not 5000: macOS reserves it for AirPlay Receiver
PY_URL = "https://www.python.org/downloads/"
IS_WIN = sys.platform == "win32"

# Decide before any redirect: no console means a windowless launch.
INTERACTIVE = bool(sys.stdout and sys.stdout.isatty())
if sys.stdout is None or sys.stderr is None:
    _log = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = _log


def say(msg):
    print(msg, flush=True)


def fatal(msg):
    """Print the problem, and show a dialog when there is no console to read it in."""
    say(f"\nProcess Log could not start:\n{msg}\n")
    if not INTERACTIVE:
        try:
            if IS_WIN:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, msg, "Process Log", 0x10)
            elif sys.platform == "darwin":
                text = msg.replace("\\", "\\\\").replace('"', '\\"')
                subprocess.run(["osascript", "-e",
                                f'display dialog "{text}" with title "Process Log" buttons {{"OK"}}'],
                               check=False)
        except Exception:
            pass
    sys.exit(1)


def venv_python():
    return VENV_DIR / ("Scripts/python.exe" if IS_WIN else "bin/python")


def run(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, **kw)


def venv_works():
    py = venv_python()
    if not py.exists():
        return False
    try:
        return run([str(py), "-c", "import flask"]).returncode == 0
    except OSError:
        return False


def ensure_venv():
    if venv_works():
        return
    py = venv_python()
    # A venv copied from another machine or folder is not portable; rebuild it.
    broken = VENV_DIR.exists()
    if broken:
        try:
            ok = py.exists() and run([str(py), "-c", "pass"]).returncode == 0
        except OSError:
            ok = False
        if not ok:
            say("Existing app/venv does not work on this computer; rebuilding it.")
            shutil.rmtree(VENV_DIR, ignore_errors=True)
    if not py.exists():
        say("First run: setting up (this takes about a minute, needs internet once)...")
        r = run([sys.executable, "-m", "venv", str(VENV_DIR)])
        if r.returncode != 0 or not py.exists():
            fatal("Could not create the app's Python environment.\n\n" + r.stdout[-800:])
    say("Installing Flask...")
    r = run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check", "flask"])
    if r.returncode != 0:
        fatal("Could not install Flask. Check your internet connection and run this again.\n\n"
              + r.stdout[-800:])


def pick_port():
    pref = int(os.environ.get("UI2_PORT", DEFAULT_PORT))
    for port in (pref, 0):
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", port))
            return s.getsockname()[1]
        except OSError:
            continue
        finally:
            s.close()
    fatal("No free network port was available on this computer.")


def wait_for(port, proc, timeout=20):
    end = time.time() + timeout
    while time.time() < end and proc.poll() is None:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def main():
    if sys.version_info < (3, 9):
        fatal(f"Python 3.9 or newer is needed (this is {sys.version.split()[0]}).\n"
              f"Install it from {PY_URL} and try again.")
    ensure_venv()
    port = pick_port()
    env = dict(os.environ, UI2_PORT=str(port))
    if not INTERACTIVE:
        env["UI2_WATCHDOG"] = "1"  # no console to close, so quit when the tab is gone
    kw = {}
    if IS_WIN and not INTERACTIVE:
        kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    out = sys.stdout if INTERACTIVE else open(LOG_FILE, "a", encoding="utf-8")
    proc = subprocess.Popen([str(venv_python()), str(APP_DIR / "app.py")],
                            cwd=str(APP_DIR), env=env, stdout=out, stderr=subprocess.STDOUT, **kw)
    if not wait_for(port, proc):
        fatal("The app did not start. Details are in app/launch_log.txt "
              "(or above, if you ran this in a terminal).")
    url = f"http://127.0.0.1:{port}/"
    say(f"Process Log is running at {url}\nClose this window or press Ctrl+C to stop it.")
    if not os.environ.get("UI2_NO_BROWSER"):
        webbrowser.open(url)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
    sys.exit(0)


if __name__ == "__main__":
    main()
