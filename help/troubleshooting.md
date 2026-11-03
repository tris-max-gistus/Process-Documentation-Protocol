# Troubleshooting

Known issues and fixes, newest additions at the top. Each entry follows
the same format — see "Adding a new entry" at the bottom.

---

## Frequently Asked Questions

**Can I use this on multiple devices?**
The tool is designed for one student on one device. If you work on
different computers, you'll have separate logs. Note which device each one
came from.

**What if I make a mistake in a log?**
Entries are never edited once saved, on purpose: the log is an honest trace
of your thinking, mistakes included. Add a new Note saying what was wrong.

**What if I want to start fresh?**
Click **New log**. If you really want a clean slate, move the `logs/` folder
somewhere safe (rather than deleting it) and the tool creates a new one on
next run. The `artifacts/` folder is for you to manage.

**Is this tool open source?**
Yes, you're welcome to explore the code and modify it for your own needs
after the course.

---

## Folder still won't move, even though no python process is running

**Symptom:** `Get-Process python,pythonw` (see the entry below) shows
nothing, but moving/renaming the folder still fails with "The process
cannot access the file because it is being used by another process."

**Cause:** A freshly-created `app/venv/` contains real executables
(`python.exe`, DLLs). Something else — usually antivirus scanning those
new binaries, sometimes the search indexer — can hold a brief lock on
them that has nothing to do with the app itself. See
`venv_architecture.md` for why this folder structure makes that possible
and how to avoid it.

**Fix:** Delete the `app/venv/` subfolder (it's disposable — the launcher
rebuilds it automatically), then move the folder. Don't try to move a
`venv/` folder directly even if you do get it unstuck — it embeds
absolute paths and isn't portable anyway.

---

## "It says the app is already running" / can't move or delete the folder

**Symptom:** You get an error like "The action can't be completed because
the file is open in another program" when trying to move, rename, or
delete the project folder. (If an old copy is still holding the app's
port, the new one quietly picks a different free port, so you can end up
with two copies running.)

**Cause:** Closing the browser tab doesn't always fully stop the local
server right away. With `Start.vbs` it exits by itself a couple of minutes
after the tab is closed; in a terminal or VS Code, closing that window or
pressing Ctrl+C stops it. Until then the app's Python process keeps
running in the background, which locks the folder (Windows won't let you
move/rename a folder that contains a currently-running program).

**Fix:** find that process and stop it.

**Windows (PowerShell)** — recommended, shows exactly which folder each
process belongs to, so you can be sure you're stopping the right one:
```
Get-Process python,pythonw -ErrorAction SilentlyContinue | Select-Object Id, Path
```
Find the row whose Path is inside this project's folder, then:
```
Stop-Process -Id <id> -Force
```

**Windows (Command Prompt)** — alternative, based on the port instead:
```
netstat -ano | findstr :5173
taskkill /PID <pid> /F
```

**Mac/Linux:**
```
lsof -i :5173
kill -9 <pid>
```

Then try the original action again.

---

## Adding a new entry

Copy this template and fill it in:

```
## Short description of the error

**Symptom:** What you see (exact error text if possible).

**Cause:** Why it happens, if known.

**Fix:** Steps to resolve it.
```

Add new entries above this section, so the newest is always closest to
the top.
