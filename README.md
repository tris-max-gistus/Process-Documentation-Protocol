# Process Documentation Tool

A demonstration of the value of having a consistent process-documentation protocol.

This tool logs your process while you study and work with LLMs: what you
asked, what came back, what you thought, and what you expected versus what
actually happened. It exists to make your own process visible *to you*, not
to feed a research dataset that only benefits someone else. The record is
yours: a legible trace of your own thinking that you can look back on, learn
from, and build judgment from over time.

That's the actual premise here. Not "track LLM usage," but **make your
own process visible to yourself.** Held consistently, it becomes closer to
a systems-thinking practice than a usage log: a way of seeing your own
work as a process with structure, not a series of disconnected sessions.

> **Version 2.** This is a ground-up simplification of the original
> check-in / process-log / check-out tool. The original is preserved as the
> `v1.0` tag (`git checkout v1.0`).

## Not evaluated, not policed

Your usage of LLM tools is **not** judged or graded based on the patterns
in this log. This is a research study on how students engage with LLMs to
understand learning processes, not a compliance tool. Be honest about
your process.

- **No personal identifying information** is collected (no name, ID, email).
- **All data stays on your computer** until you choose to send a log file to someone.
- **Linkage to your identity** happens through your course's existing
  submission portal, not through this tool.

## A note on language

This tool says "LLM" (large language model) rather than "AI," and "input"
rather than "prompt." That's deliberate. "AI" is a marketing category: it
implies intelligence, intention, understanding. An LLM is a specific,
well-understood technology: a statistical model that predicts likely text
given prior text. Precise language keeps you clear-eyed about what you're
actually using, and whose work (yours) is doing the thinking.

This distinction is rooted in the work of [Dr. Emily Bender](https://linguistics.washington.edu/people/emily-m-bender).

## Start it

You need Python 3.9 or newer from [python.org](https://www.python.org/downloads/),
and (recommended) [VS Code](https://code.visualstudio.com/).

| Where | How |
|---|---|
| **Any OS, easiest** | Open this folder in VS Code, open `app/start.py`, press the Run (play) button. |
| **Windows** | Double-click `Start.vbs`. |
| **macOS** | Double-click `start.command`. The first time, right-click it and choose **Open**, then **Open** again. If macOS refuses, use the VS Code way above. |

The first launch sets itself up (about a minute, needs internet once). After
that it opens in your browser right away. On Mac or in VS Code, close the
terminal window or press Ctrl+C to stop it. On Windows with `Start.vbs` it
stops by itself a couple of minutes after you close the browser tab.

## Using it

- **New log:** type tags and press Enter after each. The **first tag becomes
  the log's title and the file name**. Other tags go into your tag bank, which
  suggests tags later.
- **Continue a log:** pick it from *Recent logs*. New entries are added to the
  end; nothing already written is changed.
- **Input / Note:** type and press Add (or Ctrl/⌘+Enter).
- **Log LLM output:** paste only the part that matters; add an optional short
  summary and tags.
- **Reflect:** name a *topic*. **Pre** = what you expect or plan before working
  on it. **Post** = what happened and what surprised you. Come back to the
  same topic for the Post whenever you are ready; it is never required.

Your logs are plain JSON files in `logs/`, one per log. To share one, send the
file. The `artifacts/` folder is optional: drop notes, PDFs or system maps
there if you want them kept next to your logs.

See [`help/`](help/) for troubleshooting, the file format, and how to get
help from an LLM if something won't start.

---

**Questions?** Check with your instructor. This tool is here to help you
reflect on your process, not police your LLM use.
