# Day 2 — Video Review

The Day 2 plugin from [@andrewislearning](https://andrewislearning.com) — a 30-day series on automating content creation with AI.

## What it does

Installs a bundle of skills for reviewing and improving a short-form video before it publishes. It gives Claude practical senses for the final artifact: frame sampling, cut metrics, script review, spoken-reveal captions, Remotion overlays, and voice cleanup.

## Install

```text
/plugin marketplace add andrewjiang/andrewislearning
/plugin install day-02-video-review@andrewislearning
```

## Use

In any Claude Code session inside a video project, say:

> Review my final Reel before I publish it.

For direct evidence extraction:

```bash
python plugins/day-02-video-review/skills/review-video/senses/frames.py edits/day_02/final.mp4 --fps 1
python plugins/day-02-video-review/skills/review-video/senses/cuts.py edits/day_02/final.mp4
```

Then ask Claude for a scorecard, timestamped issues, and exact edit or config changes.

## Included skills

- `review-script` — reviews a Reel/TikTok/Short script against the short-form rubric.
- `spoken-reveal-captions` — builds stable captions where each word appears when spoken.
- `instagram-remotion-overlay` — adds Instagram proof cards and black Reel mockups.
- `claude-remotion-overlay` — adds a typed Claude prompt modal.
- `ffmpeg-remotion-overlay` — adds a video-cutting modal with filmstrip frames.
- `voice-enhance-reel` — cleans and masters phone voice audio.

## What it's based on

Day 1 almost shipped as a black video. Day 2 turns that failure into a review loop: sample the final video, read the transcript, score the edit, and catch obvious issues before publishing.

Watch the episode and read the guide on [Day 2](https://andrewislearning.com/days/02).

## License

MIT.
