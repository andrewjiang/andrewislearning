# Day 1 — Video Review

**Subject:** `edits/day_01/final.mp4`
**Reviewed:** 2026-04-29 16:33 PDT
**Reviewer:** `video-review` skill, perception layer v0.1
**Reference rubric:** `references/SHORT_FORM_REELS.md`

---

## Scorecard

| Axis | Score | Notes |
|---|---|---|
| Hook (0–3s) | **C+** | Strong concrete numbers, no visual pattern interrupt |
| Pacing | **D+** | One shot is 24.2s long — half the video |
| Captions | **B−** | Density and emphasis good; animation flat |
| Audio | **A** | -14.2 LUFS, dynamic range 8.4 LU, no clipping |
| B-roll | **A−** | Concrete, well-timed, real-world proof |
| Color | **F** | HDR metadata leaked through entire chain |
| Length | **A** | 55.8s, inside the 45–60s sweet spot |
| CTA | **A** | Single keyword, short, comment-to-DM |
| **Overall** | **C+** | Ship-blocker on color; everything else is polish |

---

## Mechanical metrics

```
duration_s         : 55.767
width × height     : 1080 × 1920
frame_rate         : 30 fps
bit_rate           : 1.60 Mbps    ⚠ low for 1080p
codec              : h264 / yuv420p
color_transfer     : arib-std-b67  🚨 HDR (HLG) — see finding F-01
color_primaries    : bt2020        🚨 HDR — see finding F-01
integrated_lufs    : -14.2         ✓ on target
loudness_range_lu  : 8.4           ✓ healthy dynamic range
true_peak_db       : -1.1          ✓ headroom OK
silence_ratio      : 0.04          ✓
shot_count         : 5
avg_shot_length_s  : 11.15
longest_static_s   : 24.20         ⚠ at 0:12.43 — see finding P-01
cut_timestamps     : [7.17, 12.43, 36.63, 48.80]
caption_chunks     : 78
chunks_per_second  : 1.30          ✓ within target
emphasis_ratio     : 0.18          ✓ within target
```

---

## Shot-by-shot

| # | Range | Duration | Content | Verdict |
|---|---|---|---|---|
| 1 | 0:00 – 0:07 | 7.2s | Selfie, hook ("Day 1...million views") | OK |
| 2 | 0:07 – 0:12 | 5.3s | **IG repost b-roll** (ohmo.ai screen recording) | Strong |
| 3 | 0:12 – 0:37 | **24.2s** | Selfie, the rules / challenge declaration | **🚨 RETENTION RISK** |
| 4 | 0:37 – 0:49 | 12.2s | **Claude planning b-roll** (project setup, transcript run) | Strong |
| 5 | 0:49 – 0:56 | 7.0s | Selfie, CTA | OK |

---

## Findings

### 🚨 [BLOCKER] F-01 — HDR metadata on every file in the chain

**Diagnosis:** Source iPhone footage is HEVC HLG (HDR). Every re-encode in
the pipeline carried `color_transfer=arib-std-b67`, `color_primaries=bt2020`,
`color_space=bt2020nc` forward in the metadata while the pixels were
downconverted to 8-bit SDR. Result: SDR pixels with HDR tags. IG mobile
players that respect the tags attempt to tone-map and **render the video
as black**. Audio is unaffected, so the post ships with sound but no
picture.

**Where it broke:** every output from `selfie_combined.mp4` onward through
`final.mp4`. ffprobe confirms the leak at every stage.

**Fix:** Add explicit SDR color flags to every ffmpeg encode + tone-map
HDR sources at ingest:

```diff
- "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
+ "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
+ "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
```

Plus an HLG → SDR tone-map filter on the source pass:
```
zscale=tin=arib-std-b67:t=linear:npl=100,format=gbrpf32le,
zscale=primaries=bt709:transfer=linear:matrix=bt709,
tonemap=tonemap=hable:desat=0,
zscale=transfer=bt709:matrix=bt709:primaries=bt709:range=tv,
format=yuv420p
```

Status: applied 2026-04-29. Final.mp4 now 6.0 Mbps bt709 SDR.

---

### 🚨 [BLOCKER] P-01 — Shot 3 is 24.2 seconds of unbroken selfie

**Diagnosis:** The "30 days, every edit through an AI agent, every post
through an AI agent, just my phone and a laptop" beat sits on a single
selfie composition for 24.2 seconds — **43% of the total runtime**. Per
`SHORT_FORM_REELS §6`, average shot length should be 1.5–3s; static
stretches over 8s are retention killers. This shot lands directly on the
challenge-declaration beat, which is the highest-stakes section.

**Captions cycle every ~1–2s and carry the section, but the underlying
visual is identical from 0:12 to 0:37.**

**Fix:** Add zoom-punches at the emphasis beats inside shot 3. Targets:

```json
"effects": [
  {"type": "zoompunch", "t": 22.5, "scale": 1.06, "duration": 0.30},
  {"type": "zoompunch", "t": 25.1, "scale": 1.07, "duration": 0.30},
  {"type": "zoompunch", "t": 30.3, "scale": 1.06, "duration": 0.30},
  {"type": "zoompunch", "t": 36.0, "scale": 1.07, "duration": 0.30}
]
```

Four micro-zooms at "TEACH AN AI", "30 DAYS", "AI AGENT", "MY PHONE"
break the static feel without re-shooting.

---

### ⚠ [IMPROVEMENT] C-01 — Caption animation is flat

**Diagnosis:** Frame analysis at 1fps confirms captions appear with
color-only emphasis (white → salmon). No scale change, no motion on
entry. Per `SHORT_FORM_REELS §4`, animated captions yield 15–40% higher
retention than static.

**Fix:** Add ASS scale-pop tags on emphasis events in `pipeline/caption.py`:

```
{\t(0,150,\fscx140\fscy140\1c&H8C95FF&)\t(150,300,\fscx100\fscy100)}
```

0–150ms: scale to 140%, color-swap to salmon. 150–300ms: scale back to
100%, hold salmon. Same emphasis word list, just animated.

---

### ⚠ [IMPROVEMENT] W-01 — Wardrobe competes with caption real estate

**Diagnosis:** The "TRAFFICJUNKY · EST 2008 · MONTREAL" shirt text reads
clearly in the lower-third of frames 4, 6, 7, 11, and most of shot 3.
Captions land in the same lower-third zone. The eye re-parses both,
fragmenting attention.

**Fix:** Plain solid shirt for Day 2 onward. No graphic, no text. Free
fix; no re-shoot needed for Day 1.

---

### ⚠ [IMPROVEMENT] H-01 — Hook lacks visual pattern interrupt

**Diagnosis:** First 3 seconds hold a single selfie composition with one
caption ("DAY 1"). Per `SHORT_FORM_REELS §1`, Reels with a storytelling
hook *or* jump cut in the first 3s are 72% more likely to go viral. The
audio is strong (specific number, concrete claim), but the visual is
static.

**Fix:** Day 2 onward — open with a Remotion title-reveal graphic that
punches in inside the first second. Visual pattern interrupt + visceral
on-screen text. The DAY-N reveal can become a series-format opener
signature.

---

### ⓘ [NIT] B-01 — B-roll quality is excellent, keep doing this

**Note:** Shot 2 (IG repost screen recording with comment count visible)
and shot 4 (Claude planning UI with real terminal output) are concrete,
recognizable, and timed well. Both b-rolls match the spoken claim with
real artifacts, not stock footage. Per `SHORT_FORM_REELS §6`, this is
the gold standard. Reuse pattern for every future day.

---

### ⓘ [NIT] L-01 — Loudness target hit cleanly

**Note:** Integrated -14.2 LUFS, loudness range 8.4 LU, true peak
-1.1 dB. All within IG/TikTok delivery spec. Audio chain (highpass →
afftdn → acompressor → loudnorm) is well-tuned. No action.

---

### ⓘ [NIT] CTA-01 — CTA is single, keyword, short

**Note:** "Comment 'DAY 1' for the link" is the highest-converting CTA
shape per `SHORT_FORM_REELS §5`. Single goal, short keyword, comment-to-DM
funnel. Keep this template; vary keyword per episode.

---

## Verdict

**Ship-blocker resolved.** F-01 (HDR) and P-01 (shot 3 monotony) were
the two findings that would have cost the post real reach. F-01 is fixed
in the rebuilt pipeline; P-01 needs the zoom-punch effect to land before
Day 2 publishes. C-01, W-01, H-01 are quality lifts for Day 2 onward.

**Day 1 verdict:** ship as-is for the historical record, but note that
the live `final.mp4` was re-rendered post-incident with HDR metadata
fixed and bitrate restored. Future days inherit the patched pipeline by
default.

**For the review agent on Day 2:** the pattern is clear — every video
should be reviewed by this skill *before* `publish.py` runs. The black-
post incident only happened because nothing in the pipeline ever looked
at the output. Today, that step is mandatory.

---

*Generated by `plugins/day-02-video-review/skills/review-video` —
frames sampled at 1 fps, cuts detected at scene-threshold 0.3, audio
profiled via ffmpeg loudnorm pass-1, captions analyzed against
`series/days/01-caption.json` rendered output.*
