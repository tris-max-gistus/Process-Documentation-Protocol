# Iterating On This Tool's Design

If you're curious about changing this tool for your own purposes (a different kind of process log, a new feature, a different set of fields), this file gives an LLM assistant enough context to help you design it. Fill in your ideas below, then paste this **whole file** into an LLM chat (like Claude) to start ideating.

**Before you fork and start changing things:** see `versioning_with_github.md` in this folder for how to make and track your own copy.

**Submissions use the provided version.** Whatever you build here is for your own exploration; it is not what you turn in for the class. What you share for a course always comes from the unmodified version your instructor gave you. Treat this as a personal sandbox, not a replacement for your official logs.

------------------------------------------------------------
MY IDEAS (fill this in)

What do you want to change or add?


Why does this matter to you? What would make this tool more useful for your own work?


Is this about what an entry records, how logs are organized or reopened, the Reflect flow, how outputs and tags work, or something else entirely?


------------------------------------------------------------
CONTEXT FOR THE LLM HELPING ME (leave this part as-is)

This is a local Flask web app (version 2) for logging a student's study and LLM-use process. It is fully local: no network calls, no LLM integration beyond what the student pastes in manually, nothing leaves the student's machine. The previous version (check-in / process log / check-out with a YAML question bank and a zip export) is preserved at the git tag `v1.0`.

**Folder structure:**
```
/               launchers (Start.vbs, start.command), README, help/, artifacts/, logs/
/app            app.py (Flask server and the whole single-page UI), start.py (launcher), start.bat, venv/
/logs           one JSON file per log: <first-tag>_<YYYYMMDD-HHMM>.json
/artifacts      optional: free-form files students add themselves
```

**Design principles:**
- One screen. Capture on the left (Input, Note, tags), recent logs on the right. "Log LLM output" and "Reflect" are buttons that open small dialogs.
- One log = one append-only JSON file. Reopening a log appends; entries are never edited or deleted.
- The first tag the student types becomes the log's title and filename. Other tags populate a tag bank (computed from all logs on request) that suggests tags when tagging entries. Tags are free text.
- Entry kinds: `input`, `note`, `output` (pasted partial LLM output, optional summary), `pre`, `post`. Pre and post are paired by a student-chosen `topic` string; a topic is "open" while it has a pre without a later post. Post is never required.
- Entry ids are `<log id>:<position>` so later tools (a labeling layer, a review UI) can reference entries stably.
- No identity fields. Writes are atomic (temp file, then replace).
- Dependencies: Flask only, installed into app/venv by app/start.py (standard library only). No frontend framework, no CDN, no build step; the page is a single HTML string inside app.py.
- Cross-platform launch matters: Windows (Start.vbs / start.bat), macOS (start.command, with VS Code "Run start.py" as the most reliable path), default port 5173 because macOS uses 5000 for AirPlay.

**API (all JSON):** `GET /api/logs`, `POST /api/logs`, `GET /api/logs/<id>`, `POST /api/logs/<id>/entries`, `GET /api/tags`, `POST /api/heartbeat`.

**Not built yet:** export, a review/search UI across logs, any automated labeling or suggestion of tags, a built-in LLM chat.

------------------------------------------------------------
Copy this whole file (with your ideas filled in above) and paste it into an LLM chat to start designing your change.
