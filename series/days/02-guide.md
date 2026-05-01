# Day 2 Guide — Give Your AI Editor Eyes

Day 1 proved the pipeline could publish. Day 2 adds the missing safety loop: before the agent posts, it needs to look at the final video and explain what might hurt retention.

## Install

```text
/plugin marketplace add andrewjiang/andrewislearning
/plugin install day-02-video-review@andrewislearning
```

## Use It

In Claude Code, ask:

```text
Review my final Reel before I publish it.
```

Then point Claude at the video you want reviewed, usually:

```text
edits/day_02/final.mp4
```

The plugin includes small review senses:

```bash
python plugins/day-02-video-review/skills/review-video/senses/frames.py edits/day_02/final.mp4 --fps 1
python plugins/day-02-video-review/skills/review-video/senses/cuts.py edits/day_02/final.mp4
```

`frames.py` writes stills so Claude can inspect the actual video. `cuts.py` reports scene changes, shot count, average shot length, and the longest static stretch.

## What To Ask Claude For

Use a concrete prompt:

```text
Review this Reel as if you are the editor before publish.

Check:
- first 3 seconds
- black frames or format issues
- caption readability
- whether captions match the spoken sentence
- long static stretches
- confusing cuts
- audio clarity
- CTA clarity

Return:
- a 1-10 scorecard
- timestamped issues
- exact config or edit changes
- whether this is safe to publish
```

## What Good Output Looks Like

The useful review is not vague. It should say things like:

- `0:00.10` has a black flicker before the first frame; trim or replace with the first good frame.
- `0:21.0` has a short decode flash; inspect the source transition and rerender that segment.
- Caption page `Day 1 almost didn't happen` is too dense; split it into two phrases and highlight `didn't happen`.
- The longest static stretch starts at `0:32`; insert Claude or ffmpeg B-roll there.

## Skills Included

- `review-script` checks a short-form script before recording.
- `spoken-reveal-captions` keeps caption layout stable while words appear when spoken.
- `instagram-remotion-overlay` adds Instagram proof cards and black Reel mocks.
- `claude-remotion-overlay` adds the typed Claude prompt modal.
- `ffmpeg-remotion-overlay` adds the cutting/filmstrip modal.
- `voice-enhance-reel` cleans and masters phone voice audio.

## Day 2 Lesson

Publishing is not the finish line for an AI editor. The next capability is review: the agent needs enough perception to catch obvious failures before a human does.
