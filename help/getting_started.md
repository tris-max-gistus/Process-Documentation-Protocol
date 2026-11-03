# Getting Started

## First time

1. Install Python 3.9 or newer from [python.org](https://www.python.org/downloads/) if you don't have it. On a Mac, use the python.org installer; don't accept a prompt to install Xcode command line tools just for this.
2. Unzip (or clone) this folder somewhere you'll find it again.
3. Start the app. **Easiest on any computer:** open the folder in VS Code, open `app/start.py`, press the Run (play) button.
   - **Windows:** double-click `Start.vbs` (no console window; a small message appears only if something goes wrong).
   - **Mac:** double-click `start.command`. The first time, right-click it and choose **Open**, then **Open** again. If macOS still refuses, use the VS Code way.
4. The first launch sets itself up (about a minute, internet needed once). A browser tab then opens on your own computer, at an address like `http://127.0.0.1:5173/`.

If something seems stuck, run `app/start.bat` (Windows) or `python3 app/start.py` in a terminal (Mac) once: the visible output usually explains what's wrong. `Start.vbs` also writes to `app/launch_log.txt`. See `ask_for_help.txt` if you want an LLM to help you troubleshoot.

## During your work

The screen has two parts.

**Left: your current log.** Pick tags for the next entry, then write in either box:
- **Input**: what you typed or asked an LLM.
- **Note**: your own thought, an aside, a decision.

Press Add, or Ctrl/⌘+Enter. Below the boxes is the log so far, newest first.

**Right: recent logs.** Click one to open it and keep adding. Nothing already written is ever edited.

Two buttons in the top bar:
- **Log LLM output**: paste the part of an LLM's answer that matters, with an optional one-line summary and tags. You don't need to paste everything.
- **Reflect**: choose **Pre** to name a topic and write what you expect or plan before working on it; choose **Post** (later, whenever you're ready) to say what happened and what surprised you. Post offers your topics that are still open. It is never required.

## Starting a log and tagging

Press **New log** and type tags, pressing Enter after each. The **first tag is the log's title** and the start of its file name (`heat-exchangers_20261031-1304.json`). Every other tag joins your tag bank, so the app can suggest it next time you tag an input or an output. Tags are free text; there are no required categories.

## Folders

```
/logs        → your logs (JSON), one per log. This is your data. Don't delete it.
/artifacts   → optional: drop notes, PDFs, system maps you want kept alongside
/help        → this folder
/app         → internals (server, launcher, and venv/); you shouldn't need to open it
Start.vbs        → Windows double-click launcher
start.command    → Mac double-click launcher
```

## Sharing your work

Send the log file(s) you were asked to share. They are plain text; open one in any editor to see exactly what would be shared. See `json_schema_reference.md` for what's inside.
