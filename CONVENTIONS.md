# Conventions

Rules another agent (or future-Andrew) needs to follow when dropping files into the project.

## Folder layout

Every main folder uses **per-day subfolders**, zero-padded to two digits:

```
raw/day_01/         transcripts/day_01/      edits/day_01/        published/day_01/
raw/day_02/         transcripts/day_02/      edits/day_02/        published/day_02/
…
raw/day_30/         transcripts/day_30/      edits/day_30/        published/day_30/
```

Symmetry across folders is the rule. If a file exists at `raw/day_07/foo.mov`, its derivatives live at `transcripts/day_07/foo.json`, `edits/day_07/foo.cut.mp4`, etc.

## Filenames in `raw/`

Pattern: `{shot_type}_take_{NN}.{ext}`

- **shot_type**: one of `selfie`, `screen`, `broll`
- **NN**: take number, zero-padded (`01`, `02`, …)
- **ext**: original extension, lowercase (`mov` for iPhone footage, `mp4` for screen recordings, `mov` for QuickTime)

Examples:

```
raw/day_01/selfie_take_01.mov
raw/day_01/selfie_take_02.mov
raw/day_01/screen_take_01.mp4
raw/day_05/broll_take_01.mov
```

## Why this matters

The pipeline (`pipeline/edit.py` and downstream) uses the day folder name to route outputs and the shot prefix to decide how to handle a file (selfie = A-roll, screen = inset, broll = cutaway). Get the naming wrong and the pipeline silently does the wrong thing.

## Instruction prompt for another agent

Paste this verbatim if another agent (e.g., a phone-side agent that handles AirDrop) needs to drop raw files in:

> Save raw video files to `<repo>/raw/day_NN/` where `NN` is the current day number, zero-padded (`01` through `30`). Filenames must be `{shot_type}_take_{MM}.{ext}` where `shot_type` is one of `selfie`, `screen`, or `broll`, `MM` is the take number zero-padded, and `ext` is the original file extension lowercased (`mov` for iPhone footage, `mp4` for screen recordings). Create the day folder if it doesn't exist. Do not modify file contents — only move/rename.

## Other folders, briefly

- **`plugins/day-NN-<slug>/`** — the daily takeaway packaged as a Claude Code plugin. One per day. Slug is short kebab-case (`series-planner`, `cut-filler`, `auto-captions`).
- **`series/days/NN.md`** — the public writeup for the day, source for the website's day page.
- **`web/days/NN.html`** — generated from the markdown; deployed to andrewislearning.com.
- **`.claude-plugin/marketplace.json`** — the marketplace manifest. Append a new entry every day.

## What never changes

- Day numbers are zero-padded to 2 digits everywhere (`day_01`, not `day_1`).
- Plugin names use kebab-case with a `day-NN-` prefix.
- Every artifact produced on a given day lives under that day's folder. No cross-day pollution.
