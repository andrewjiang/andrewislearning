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
    ▼  caption.py       (Day 5 — Remotion captions, ASS fallback)
edits/day_01/selfie_take_01.captioned.mp4
    │
    ▼  enhance_audio.py (optional — API voice cleanup / isolation)
edits/day_01/selfie_take_01.voice.mp4
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

## Caption renderer

`caption.py` now defaults to the local Remotion renderer in `../captioner/`.
Python still owns transcript timestamp mapping; it writes a canonical
`*.captions.json` payload, then Remotion renders the source video with dynamic
caption pages, active-word styling, safer vertical placement, and Google Fonts.

Install once:

```bash
cd captioner
npm install
```

Use the ASS/libass fallback if Remotion is not installed:

```bash
python3 pipeline/caption.py --config series/days/01-caption.json --engine ass
```

## Proxy workflow

Use proxies for fast iteration on iPhone/4K/HEVC footage:

```bash
python3 pipeline/proxy.py raw/day_02/*.MOV raw/day_01/broll_take_01.mp4
```

This writes normalized H.264 edit proxies to `proxies/day_NN/`, preserving the
raw originals in `raw/`. The proxy files are lower-resolution, real vertical
MP4s with rotation metadata baked in, so concat/tighten/assembly iterations are
fast and avoid the HEVC rotation glitches that can appear when raw iPhone clips
are concatenated directly.

Workflow:

1. Ingest camera originals into `raw/day_NN/`.
2. Generate proxies into `proxies/day_NN/`.
3. Build timing, tighten, and rough assemblies against proxies.
4. Reuse the same clip order and in/out timings against `raw/` for the final
   high-quality export.

For shot-to-shot joins, use `pipeline/sequence.py` instead of raw
concat/tighten. It accepts explicit clip windows, optional silence/pause
segments, and optional `xfade`/`acrossfade` joins. Default to direct cuts for the
talking-head series style; add transitions only when the edit specifically
needs them.

## Export quality

Video-producing stages use the shared profile in `ffmpeg_quality.py`: H.264 high
profile, `yuv420p`, BT.709 color tags, CRF 16, slow preset, AAC 256k, and
faststart. This keeps the final upload master high-bitrate enough for social
platform recompression instead of letting ffmpeg's defaults crush detail.

## Voice enhancement

`enhance_audio.py` is the optional API-backed voice cleanup stage for IG Reels.
It extracts the spoken track, enhances that audio, then muxes it back onto the
same video stream so visual edits and caption timing stay intact.

Recommended defaults:

```bash
# Auto picks Cleanvoice, then ElevenLabs, then Resemble if the matching API key
# exists; otherwise it falls back to local ffmpeg cleanup.
python3 pipeline/enhance_audio.py edits/day_02/final_captioned.mp4 \
  --provider auto \
  --out edits/day_02/final_captioned.voice.mp4

# Final pass still does the social master: -14 LUFS, light compression, color,
# and speedup.
python3 pipeline/finish.py edits/day_02/final_captioned.voice.mp4 \
  --out edits/day_02/final.mp4
```

Provider guide:

- **Cleanvoice** (`CLEANVOICE_API_KEY`) — first choice for normal phone/selfie
  clips; uses `remove_noise`, `studio_sound`, `normalize`, and `target_lufs=-14`
  without filler/silence removal so timing is preserved.
- **ElevenLabs** (`ELEVENLABS_API_KEY`) — use when a clip has heavy background
  noise, music, street noise, or ambience and needs voice isolation first.
- **Resemble** (`RESEMBLE_API_KEY`) — alternate async studio-sound provider.
- **local** — offline ffmpeg high-pass, denoise, compression, and loudnorm.

## Conventions

- **Filenames are the source of truth.** A file flows through every stage with the same stem and a suffix per stage (`.cut`, `.captioned`, `.final`). No renaming, no metadata DB — the filename tells you the lineage.
- **Shot-type prefix.** Raw stems are `<shot_type>_take_NN` where `shot_type ∈ {selfie, screen, broll}`. `cut.py` will use this on Day 4 to distinguish A-roll from B-roll without watching the file.
- **Day-keyed subfolders.** Every stage folder mirrors the input's `day_NN/` subdirectory. Outputs are written to `<stage>/day_NN/<stem>.<suffix>`. Pipeline code reads `input_path.parent.name` to derive the day.
- **Each stage is idempotent.** Re-running on the same input either skips or overwrites cleanly.
- **No state outside files.** The pipeline is a directory walk; nothing in memory between stages.
