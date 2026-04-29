# 30-Day Series Plan

Each day = one specific, copyable automation. Recipes, not vibes.

## Week 1 — The Bare Pipeline
> Goal: by Day 7, one command turns a raw phone take into a postable vertical video.

- **Day 1 — Plan & scaffold.** Brainstorm with Claude, set up folders, commit empty stubs. *(this episode)*
- **Day 2 — Capture loop.** AirDrop / iCloud Drive into `raw/`. ffmpeg + Python deps installed.
- **Day 3 — Transcribe.** Whisper (local or API) → word-level JSON in `transcripts/`.
- **Day 4 — Cut filler.** Claude reads the transcript, writes a cut list, ffmpeg executes. Silence + "um/uh/like" gone.
- **Day 5 — Burn-in captions.** Transcript → SRT → ffmpeg overlay.
- **Day 6 — Vertical reformat.** 9:16 export, smart-crop centered on speaker.
- **Day 7 — End-to-end run.** `pipeline/edit.py raw/take.mp4` → postable file. The pipeline works.

## Week 2 — Polish
> Goal: same Day 7 input, dramatically better output.

- **Day 8 — Remotion intro template.** Code-defined opener, branded.
- **Day 9 — Remotion outro / end card.** CTA + episode counter.
- **Day 10 — Animated captions.** Word-by-word highlight, viral-style.
- **Day 11 — Hook detection.** Claude scans the transcript and picks the strongest 3-second opener.
- **Day 12 — AI B-roll.** Replicate / Runway API; Claude maps transcript keywords → generated clips.
- **Day 13 — Thumbnails / cover frame.** First-frame generator, episode-numbered.
- **Day 14 — Polish pass.** Re-run Day 7's video through the full Week 2 pipeline. Show the diff.

## Week 3 — Distribution
> Goal: one source video → 5 outputs across platforms, automated.

- **Day 15 — Ayrshare setup.** Account, API key, first programmatic post.
- **Day 16 — Per-platform captions.** Claude writes IG vs TikTok vs X variants from the transcript.
- **Day 17 — Hashtag generator.** Per-platform, per-topic. Avoids the obvious.
- **Day 18 — TikTok-native cut.** Different pacing, different hook style — same source.
- **Day 19 — IG carousel.** Slice into stills + key quotes from the transcript.
- **Day 20 — Tweet thread.** Transcript → 5-tweet thread, written by Claude.
- **Day 21 — Five-platform ship.** One command, five places, automated.

## Week 4 — Glue
> Goal: pipeline runs itself.

- **Day 22 — Watch folder.** Drop a file in `raw/`, pipeline triggers.
- **Day 23 — Approval gate.** Human-in-the-loop check before publish.
- **Day 24 — Scheduling.** Best-time-to-post heuristic. Queue, don't fire.
- **Day 25 — Computer-use fallback.** When an API doesn't exist, agent clicks the app for me.
- **Day 26 — ElevenLabs voice fix / dub.** Re-record a flubbed line without re-recording.
- **Day 27 — Analytics loop.** Pull views back. Claude reads what worked.
- **Day 28 — One-command ship.** `./ship.sh raw/take.mp4` — the whole thing.
- **Day 29 — Pipeline ships itself.** Today's episode is edited and posted by the pipeline.
- **Day 30 — Recap + open-source.** Numbers, lessons, repo public.
