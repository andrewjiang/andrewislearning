# ContentCopilot

A 30-day series: noob to AI-automated content creator.

**The premise.** Someone reposted my video on Instagram and got more views than the original. I'm a founder/investor — I've raised >$60M and shipped AI projects with millions of views — and I just got out-edited on my own content by a random account. So I'm spending 30 days teaching an AI to be my video editor.

**The rules.**

1. Every edit is done by an AI agent (Claude Code, Codex, ffmpeg-driven scripts, APIs). No timeline scrubbing.
2. Every post is published by an AI agent (API or computer-use). No tapping through the IG app.
3. Capture only — phone and laptop. No camera crew, no outside help.

**The arc.**

- **Week 1 — The Bare Pipeline.** Phone → folder → one command that transcribes, cuts, captions, and exports.
- **Week 2 — Polish.** Remotion templates, AI B-roll, hook detection, thumbnails.
- **Week 3 — Distribution.** One source → IG Reel + TikTok + carousel + tweet, captions per platform, posted via API.
- **Week 4 — Glue.** Watch folder, approval gate, scheduling, and the season finale: an episode shipped *by* the pipeline it describes.

## Layout

Per-day subfolders inside every stage. The day number is the join key — the same `day_NN/` segment shows up in `raw/`, `transcripts/`, `edits/`, `published/`, `series/days/`, and `plugins/day-NN-*/`. That makes "everything for Day 5" a clean unit (backups, reshoots, `./ship.sh day_05`).

```
ContentCopilot/
├── raw/                         # phone + laptop captures (AirDrop / iCloud / screen-rec)
│   └── day_01/
│       ├── selfie_take_NN.mp4   # talking-head, vertical, phone
│       ├── screen_take_NN.mp4   # laptop screen recording
│       └── broll_*.mp4          # (added later)
├── transcripts/                 # whisper output, word-level JSON
│   └── day_01/
├── edits/                       # pipeline outputs: .cut.mp4 → .final.mp4
│   └── day_01/
├── published/                   # archive of what went out, with post metadata
│   └── day_01/
├── pipeline/                    # the code (Python + ffmpeg + Claude Code)
├── plugins/                     # one Claude Code plugin per day's recipe
│   └── day-01-series-planner/
└── series/
    ├── SERIES_PLAN.md           # the 30-day arc
    ├── TOOLS.md                 # rolling tool list
    └── days/
        ├── 01.md                # Day 1 hub: status + file lineage tracker (READ FIRST)
        ├── 01-shoot-plan.md     # operational doc for shoot day (setup, script, shots, post)
        ├── 01-script.md         # current locked script + alternates + iteration log
        ├── 01-brainstorm.md     # raw planning notes from the AI brainstorm
        └── versions/            # archived prior script versions (v1, v2, ...)
```

**Filename convention.** `<shot_type>_take_NN.mp4` — `shot_type` is `selfie`, `screen`, or `broll`. The prefix lets `cut.py` (Day 4) tell A-roll from B-roll without watching the file.

## Day 1

Two entry points depending on what you're doing:

- **Coming back to plan/edit?** Open [`series/days/01.md`](series/days/01.md) — the hub with status, file lineage, and links to everything.
- **About to shoot?** Open [`series/days/01-shoot-plan.md`](series/days/01-shoot-plan.md) — self-contained operational doc: setup, script inline, per-shot details, post-shoot pipeline, posting checklist.

The whole series plan is in `series/SERIES_PLAN.md`. The tool rollout is in `series/TOOLS.md`.
