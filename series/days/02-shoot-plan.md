# Day 2 — Shoot & Production Plan

Companion to `02-script.md`. Lists the selfie takes to record, b-roll
to capture, Remotion components to build, and intermediate artifacts
to generate so the script can be assembled.

---

## Selfie takes

All written to `raw/day_02/selfie_take_NN.mov` per `CONVENTIONS.md`.
Phone selfie mode, 9:16 vertical, plain background or current set, no
HDR (Settings → Camera → Record Video → HDR Video off — that fixes
the Day 1 disaster at the source).

Recommended approach: read the entire script through 3–4 times so we
have take options per shot. Tighten will pick the best read per beat.

| File | Shots covered | Notes |
|---|---|---|
| `selfie_take_01.mov` | Full read, takes A/B/C | Three full reads back to back; ~3 min raw |
| `selfie_take_02.mov` | SHOT 1 isolation | 5–6 takes of just "Day 2... [pause] ...of teaching AI to be my video editor. And day one almost didn't happen." for the graphic-flinch timing |

The flinch in SHOT 1 is the highest-risk delivery moment — worth
rehearsing 8–10 times to find a take where it reads natural-startled
rather than performed-startled. Eyes widen, head dips ~20 degrees,
recovery in <300ms, slight smile on recovery.

**Wardrobe:** plain solid shirt — no graphic, no text. Day 1's
TrafficJunky shirt competed with the lower-third caption real estate
(see Day 1 review findings).

---

## B-roll captures

All written to `raw/day_02/screen_take_NN.mov`.

### `screen_take_01.mov` — Build the review skill

For SHOT 7. Screen-record this sequence on your laptop:

1. Open Claude Code in the ContentCopilot project (3s)
2. Type / paste a prompt like *"build a video review skill that
   samples frames and detects cuts"* (3s)
3. Cut to terminal:
   `python plugins/day-02-video-review/skills/review-video/senses/cuts.py edits/day_01/final.mp4`
   show the JSON output scroll (3s)
4. Cut to the same terminal, run:
   `python plugins/day-02-video-review/skills/review-video/senses/frames.py edits/day_01/final.mp4`
   show the JPEGs being written (2s)

Total ~12s; we'll trim to fit the 8s window.

### `screen_take_02.mov` — Artifacts review

For SHOT 8. Open `review/day_01/` and pan / cut through:

1. The 56-frame contact sheet (need to generate — see "Artifacts to
   create" below)
2. The pacing map / timeline visualization (need to generate)
3. A caption-frame composite (need to generate)
4. The scorecard markdown rendered (need to generate)

If the artifacts don't yet exist as polished images, mock them in
Remotion as a `<ContactSheetReveal>` component and skip the screen
recording. See "Remotion components" below.

### `screen_take_03.mov` — Side-by-side fixes

For SHOT 9. Two splits:

1. **Captions split.** Left: Day 1 caption appearing flat (color swap,
   no motion). Right: Day 2 same beat with scale-pop animation. ~3s.
2. **Zoom split.** Left: Day 1 static stretch (the 24-second selfie
   from 0:12 to 0:37). Right: same stretch with zoom-punches at the
   emphasis beats. ~3s.

These are easier to render programmatically (run `pipeline/finish.py`
twice with different configs, capture both outputs side-by-side via
ffmpeg `hstack`) than to screen-record. See "Artifacts to create".

---

## Remotion components

Create under `remotion/src/components/` (assumes a Remotion project
scaffolded at the repo root or under `remotion/`).

### 1. `<DayTitleReveal />`

**For:** SHOT 1.

**Props:**
- `dayNumber: number` (e.g., 2)
- `label?: string` (default `"DAY ${dayNumber}"`)
- `position?: "above-speaker" | "center"` (default `"above-speaker"`)

**Animation:**
- 0–200ms: text scales from 0 to 110%, drops from above with overshoot
- 200–350ms: settles to 100% with bounce
- 350ms–end: holds, optional subtle drift
- Total animation 350ms; rest of shot duration (~3.5s) holds steady

**Style:** Poppins Black (or Bold) at ~280pt, white with 12px black
outline, casts soft drop shadow. Reusable across all 30 days.

### 2. `<PhoneReelMockup />`

**For:** SHOT 4.

**Props:**
- `contentSrc: string | "black"` (URL to video clip or solid color)
- `audioWaveform: boolean` (animate waveform overlay if true)
- `caption?: string` (caption rendered inside the Reel screen)
- `username?: string` (header username)
- `placement: "split" | "lower-third"` (how it sits relative to speaker)

**Visual:** iPhone frame (rounded corners, dynamic island, front-facing
camera dot). Inner area is a 9:16 Reel UI:
- Top header with username and "..." button
- Right side stack: like, comment, share, audio attribution
- Bottom: caption text + audio name
- Center: video content area

When `contentSrc === "black"`, render solid black with optional
audio-waveform overlay across the middle (proves the audio is working
when picture isn't).

### 3. `<CommentNotification />`

**For:** SHOT 4 (Kevin shoutout).

**Props:**
- `username: string` (e.g., "Kevin")
- `commentText?: string` (optional — if you want the actual comment shown, e.g., "?" or empty)
- `avatarSrc?: string`
- `delay?: number` (ms before triggering)

**Animation:**
- Speech-bubble icon (rounded rectangle with tail, IG comment style)
  pops out of bottom of `<PhoneReelMockup />` (use as child element)
- Scales 0 → 120% → 100% over 250ms
- Drifts upward 80px over 1s while fading from opacity 1 → 0.7
- "Kevin commented on your reel" text floats from below, fades in at
  bubble's peak
- If `commentText` is provided, render the comment text inside the
  bubble — short ones land best ("?", "👀", "lol")

### 4. `<ContactSheetReveal />`

**For:** SHOT 8.

**Props:**
- `items: { src: string, label: string }[]`
- `staggerMs?: number` (default 200)

**Animation:** Each item fades + slides in from below with stagger.
Background: dark grid backdrop. Each item has a small label below it.

For Day 2's run, four items:
1. Contact sheet (12-frame grid PNG)
2. Pacing map (timeline visualization)
3. Caption frames (4-up grid)
4. Scorecard (text panel)

### 5. `<ComparisonSplit />`

**For:** SHOT 9.

**Props:**
- `leftSrc: string` (image or video)
- `rightSrc: string`
- `leftLabel: string` (e.g., "DAY 1")
- `rightLabel: string` (e.g., "DAY 2")
- `divider?: "fixed" | "wipe"` (default "fixed")

**Visual:** Vertical 50/50 split, label chip in top-left of each side.
If `divider === "wipe"`, animate divider sliding right at 50% mark.

### Optional: `<EmphasisChip />`

A reusable salmon-pill text chip for popping numbers / facts onto the
screen during selfie shots ("950k VIEWS", "TWO THOUSAND COMMENTS",
"LOOK MA NO HANDS"). Replaces some of the dialog burden — show, don't say.

---

## Artifacts to create

These are *outputs of the perception layer* — Day 2's b-roll depends
on them existing as visible images. Build them as a script in the
`review-video` skill so they auto-generate every time the perception
layer runs.

### `senses/contact_sheet.py` (new sense / utility)

Combines the N JPEGs from `frames.py` into a single grid PNG. Default
4 columns × 3 rows for a 12-frame sample, or 8 × 7 for a 56-frame 1fps
sample. Outputs `review/day_NN/contact_sheet.png`.

### `senses/pacing_map.py` (new utility)

Renders the output of `cuts.py` as a horizontal timeline image.
Each shot is a colored band proportional to its duration. The
longest-static stretch is highlighted with a red overlay and a label.
Output `review/day_NN/pacing_map.png`.

### `senses/caption_frames.py` (new utility)

Reads transcript timestamps and the caption config; for each caption
emphasis beat, extracts the corresponding frame and composites it
into a 2×2 grid showing what the audience sees at the load-bearing
moments. Output `review/day_NN/caption_frames.png`.

### `senses/scorecard.py` (new utility)

Synthesizes the JSON outputs from `frames`, `cuts`, `audio`, and
`captions` into a single markdown / image scorecard with the metrics
that matter for retention. Renders as PNG via headless browser or
`pillow`. Output `review/day_NN/scorecard.png`.

---

## Day-2-specific pipeline upgrades

These are the *actual fixes* the script claims were applied — they
need to exist in code by the time you record:

### `pipeline/caption.py` — animated emphasis

Add ASS animation tags to emphasis events:
```
{\t(0,150,\fscx140\fscy140\1c&H8C95FF&)\t(150,300,\fscx100\fscy100)}
```
- 0–150ms: scale to 140%, color swap to salmon
- 150–300ms: scale back to 100%, hold salmon

Configurable via `series/days/02-caption.json`:
```json
"emphasis_animation": "scale_pop"
```

### `pipeline/finish.py` — zoom-punch effect

Add a `zoompunch` filter built on ffmpeg's `zoompan`:
- 100% → 106% over 250ms, hold 100ms, return to 100% over 250ms
- Triggered at timestamps specified in a new config field

Example `series/days/02-finish.json`:
```json
"effects": [
  {"type": "zoompunch", "t": 22.5, "scale": 1.06, "duration": 0.6},
  {"type": "zoompunch", "t": 25.1, "scale": 1.07, "duration": 0.6}
]
```

---

## Order of operations

1. **Record selfie takes** (15 minutes, including SHOT 1 flinch reps).
2. **Build pipeline upgrades** — animated captions + zoom-punches.
3. **Build perception-layer utilities** — contact sheet, pacing map,
   caption frames, scorecard generators.
4. **Run the full pipeline through Day 1** to generate the b-roll
   artifacts (re-using Day 1's video as the "reviewed" subject).
5. **Build Remotion components** — the 5 listed above.
6. **Render Remotion compositions** for SHOTS 1, 4, 5, 8, 9.
7. **Capture screen recordings** for SHOTS 7, 8 if not handled by
   Remotion.
8. **Run the standard pipeline** (transcribe → tighten → assemble →
   caption → finish) on the Day 2 selfie takes + b-roll + Remotion.
9. **Run the review skill on the Day 2 video** before publishing —
   per the entire premise of the episode, do not publish without
   the review.
10. **Publish via Post for Me** with a custom cover image (use the
    `<DayTitleReveal />` Remotion render against a clean selfie frame).
