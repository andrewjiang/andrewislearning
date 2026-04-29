# Pipeline

The agentic editing + publishing pipeline. Currently scaffolded with stubs — real implementations roll in over Days 2–28 per `../series/SERIES_PLAN.md`.

## Stages

Every stage preserves the input's `day_NN/` subfolder so artifacts stay grouped by day across all stage folders.

```
raw/day_01/selfie_take_01.mp4
    │
    ▼  transcribe.py    (Day 3 — Whisper)
transcripts/day_01/selfie_take_01.json
    │
    ▼  cut.py           (Day 4 — Claude picks cuts, ffmpeg executes)
edits/day_01/selfie_take_01.cut.mp4
    │
    ▼  caption.py       (Day 5 — burn-in captions)
edits/day_01/selfie_take_01.captioned.mp4
    │
    ▼  reformat.py      (Day 6 — 9:16 + smart crop)
edits/day_01/selfie_take_01.final.mp4
    │
    ▼  publish.py       (Day 15 — Ayrshare API)
published/day_01/selfie_take_01.json     (post metadata + URLs)
```

## Today's stubs

Every stage today is a placeholder that copies the input through and writes a marker file. This lets us test the *plumbing* end-to-end on Day 1 before any real logic is in place.

```bash
# from repo root
python pipeline/edit.py raw/day_01/selfie_take_01.mp4
```

Should produce `edits/day_01/selfie_take_01.final.mp4` and a per-stage record in `transcripts/day_01/` and `edits/day_01/`.

## Conventions

- **Filenames are the source of truth.** A file flows through every stage with the same stem and a suffix per stage (`.cut`, `.captioned`, `.final`). No renaming, no metadata DB — the filename tells you the lineage.
- **Shot-type prefix.** Raw stems are `<shot_type>_take_NN` where `shot_type ∈ {selfie, screen, broll}`. `cut.py` will use this on Day 4 to distinguish A-roll from B-roll without watching the file.
- **Day-keyed subfolders.** Every stage folder mirrors the input's `day_NN/` subdirectory. Outputs are written to `<stage>/day_NN/<stem>.<suffix>`. Pipeline code reads `input_path.parent.name` to derive the day.
- **Each stage is idempotent.** Re-running on the same input either skips or overwrites cleanly.
- **No state outside files.** The pipeline is a directory walk; nothing in memory between stages.
