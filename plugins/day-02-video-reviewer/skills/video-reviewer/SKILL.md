---
name: video-reviewer
description: Review a previous short-form vertical video and plan the next episode. Use when the user asks to review yesterday's video, critique a Reel/TikTok/Short, build a video review pack, extract stills/contact sheets, analyze captions/pacing/cover/CTA, or turn prior post performance into a next-day shoot plan.
---

# Video Reviewer

Review the previous episode as evidence, not vibes. Build a review pack first, inspect the generated artifacts, then write a critique and a next-episode brief.

## Core workflow

1. Identify the day to review.
   - If the user says "yesterday" or "previous day", infer the latest completed `edits/day_NN/final.mp4`.
   - Use repo paths first: `edits/day_NN/final.mp4`, `edits/day_NN/final_captioned.captions.json`, `published/day_NN/receipt*.json`, and `series/days/NN-*.md`.
2. Run the review pack script:

   ```bash
   python3 plugins/day-02-video-reviewer/skills/video-reviewer/scripts/build_review_pack.py NN
   ```

3. Inspect the artifacts in `.context/reviews/day_NN/`.
   - Open `hook_sheet.jpg`, `contact_sheet.jpg`, `caption_sheet.png`, and any cover frame.
   - Read `review_pack.json` for specs, caption page counts, receipt URLs, and audio levels.
   - Read the script/transcript/caption files when available.
4. Write `series/days/NN-review.md`.
5. Write `series/days/MM-brief.md` for the next day.

Do not publish or delete posts during review. If a live post has a serious issue, recommend the action and wait for explicit approval.

## Review rubric

Use timestamped evidence wherever possible.

- **Hook:** Does the first 3 seconds establish format, tension, and stakes?
- **Proof:** Are claims supported visually instead of only asserted?
- **Pace:** Are there pauses, confusing transitions, or overly fast reads?
- **Captions:** Are captions readable on mobile, short enough, timed to speech, and clear of faces/platform UI?
- **Visual variety:** Is there enough movement between selfie, screen, b-roll, and proof?
- **Audio:** Is loudness clear, clipped, too quiet, or noisy?
- **Cover:** Does the cover read at feed size and make a viewer want to tap?
- **CTA:** Is the comment/DM action specific and worth doing?
- **Series continuity:** Does the episode set up tomorrow?
- **Pipeline learning:** What should become more automated next?

## Output format

For `NN-review.md`:

```markdown
# Day NN Review

## Verdict
- Overall: N/10
- Keep:
- Fix next:

## Evidence
| Area | Timestamp | Observation | Decision |
|---|---:|---|---|

## Scorecard
| Dimension | Score | Notes |
|---|---:|---|

## Pipeline Improvements

## Metrics To Add Later
```

For `MM-brief.md`:

```markdown
# Day MM Brief

## Angle

## Hook

## Story

## Shot List

## Pipeline Build

## CTA

## Success Criteria
```

## Judgment rules

- Prefer concrete fixes over broad advice.
- Preserve what worked before changing style.
- Make tomorrow's episode a visible build step, not just a status update.
- If metrics are missing, produce a creative review anyway and list the metrics to backfill.
- If the video is already live, treat deletion/repost as a last resort.
