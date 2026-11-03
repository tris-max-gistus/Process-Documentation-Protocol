# How This Tool Stores Your Process as JSON

A reference for what's inside the files in `/logs`, and why they're shaped the way they are. It's written for anyone curious about the back end, not just how to use the app.

## The core idea

One **log** is one JSON file. Everything you add (an input, a note, a pasted LLM output, a reflection) becomes an **entry** appended to the end of that file. Nothing is inferred or summarized when it's written: the file is a literal record of what you typed, in the order you typed it. The list of entries *is* the trace of your process.

JSON is just a text format of nested `"key": value` pairs, easy for the app to read back and easy for a person to open.

## File name

`<first-tag>_<YYYYMMDD-HHMM>.json`, for example `heat-exchangers_20261031-1304.json`. The first tag you typed when you started the log becomes the title and the start of the name. If two logs would get the same name, the second gets `-2` added.

## The log

```json
{
  "schema": "ui2-1",
  "id": "heat-exchangers_20261031-1304",
  "title": "Heat Exchangers",
  "created": "2026-10-31T13:04:30",
  "tags": ["Heat Exchangers", "thermo", "LMTD"],
  "entries": [ ... ]
}
```

| field | meaning |
|---|---|
| `schema` | format version, so later tools know what shape to expect |
| `id` | the file name without `.json` |
| `title` | the first tag, as you typed it |
| `created` | when the log was started (local time, ISO 8601) |
| `tags` | every tag used in the log, first tag first (this is where your tag bank comes from) |
| `entries` | the chronological list, below |

## Entries

```json
{
  "id": "heat-exchangers_20261031-1304:2",
  "kind": "output",
  "text": "Counterflow keeps a more uniform temperature difference...",
  "summary": "explains dT uniformity",
  "tags": ["llm-claim", "thermo"],
  "topic": null,
  "ts": "2026-10-31T13:04:38"
}
```

| field | meaning |
|---|---|
| `id` | `<log id>:<position>`. Stable forever because entries are only appended, so other tools can point at one entry |
| `kind` | `input` (what you typed to an LLM), `note` (your own thought), `output` (pasted LLM output), `pre` (expectation before working on a topic), `post` (what happened afterwards) |
| `text` | what you wrote or pasted |
| `summary` | optional one-liner, mainly used on outputs |
| `tags` | tags you attached to this entry |
| `topic` | required for `pre` and `post`; the short name that pairs them. `null` otherwise |
| `ts` | when it was saved |

A topic is **open** while it has a `pre` entry and no later `post` with the same topic name. Open topics are just the ones the Reflect dialog offers you under Post; nothing enforces them.

## Why this design

- **Append, don't rewrite.** Entries are never edited or deleted by the app, so the file is an honest, order-preserving trace, not a cleaned-up final draft. Your prediction (`pre`) can't be quietly revised after you see the result (`post`).
- **One file per thread.** A log is one line of inquiry you can pick up again days later. You choose where it begins by choosing its first tag.
- **Saves can't half-finish.** Each save writes a temporary file and swaps it into place, so a crash or closed laptop leaves the previous version intact.
- **Free tags, not fixed categories.** What matters to you is yours to name; the tag bank only suggests from your own past use.
- **No identity.** Nothing in the file says who you are.
