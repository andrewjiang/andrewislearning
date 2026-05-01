# Day 02 Brief

## Angle

Day 1 proved the pipeline can publish. Day 2 proves it can catch problems before publishing.

The story should start with the reason the series exists, then introduce the new drama: the first automated upload almost shipped as a black video. That failure makes the review skill feel necessary instead of abstract.

## Hook

Primary:

> Day 2 of teaching an AI to be my video editor. My video got almost a million views on X, then someone reposted it to Instagram and got thousands of comments. So I'm building the editor I should have had. Yesterday it posted the first Reel, and it almost shipped a totally black video.

Shorter alternate:

> Day 2 of teaching an AI to be my video editor. Yesterday it posted the first Reel, and it almost shipped a totally black video.

Use the primary if delivery is fast. Use the shorter alternate if the first take feels slow.

## Story

1. Re-establish why the series exists: high-performing content got reposted elsewhere and captured the attention.
2. Show the Day 1 post went live.
3. Introduce the failure: the automation almost shipped a black video.
4. Reframe the failure: publishing is not enough; an AI editor needs a review step.
5. Show the Claude prompt: build a skill that reviews my video before it publishes.
6. Show what the skill actually does:
   - `ffprobe` reads specs.
   - `ffmpeg` extracts stills.
   - caption timing JSON samples subtitle frames.
   - audio check reads loudness.
7. Show the review artifacts: hook sheet, contact sheet, caption sheet, cover, scorecard.
8. Show the two findings:
   - captions should be cleaner.
   - the hook needs to get to the point faster.
9. End with the loop: publish -> inspect -> fix -> repeat.

## Shot List

| Time | Visual | Line |
|---:|---|---|
| 0-10s | Selfie + quick X/IG proof flashes | "Day 2 of teaching an AI to be my video editor. Quick reminder why I'm doing this..." |
| 10-16s | Published Reel / receipt | "Yesterday the AI posted its first Reel. And it almost shipped a totally black video." |
| 16-22s | Black-video graphic | "The automation worked. The video did not." |
| 22-27s | Selfie or graphic | "Before this thing publishes anything, it needs to review the video like an editor." |
| 27-31s | Remotion Claude prompt modal | "So I asked Claude: build a skill that reviews my video." |
| 31-40s | Terminal running review pack | "It uses ffprobe, ffmpeg, caption timing, and an audio check." |
| 40-47s | Hook/contact/caption/cover sheets | "Then it gives me a hook sheet, pacing map, caption frames, cover, and scorecard." |
| 47-55s | Review markdown / findings cards | "Two fixes: cleaner captions, and get to the point faster." |
| 55-58s | Loop card | "Publish, inspect, fix, repeat." |
| 58-63s | Selfie / plugin path | "Comment REVIEW and I'll send you the skill." |

## Pipeline Build

- Plugin: `plugins/day-02-video-review`
- Skills: `review-script`, `spoken-reveal-captions`, `instagram-remotion-overlay`, `claude-remotion-overlay`, `ffmpeg-remotion-overlay`, `voice-enhance-reel`
- Review senses: `plugins/day-02-video-review/skills/review-video/senses/frames.py` and `cuts.py`
- Review output: `.context/reviews/day_01/`
- Written outputs:
  - `series/days/01-review.md`
  - `series/days/02-brief.md`
  - `series/days/02-script.md`

## Visual Inserts To Build Later

- Black-video failure card.
- Claude prompt modal.
- Tool-stack labels over terminal.
- Two finding cards: `Captions: cleaner`, `Hook: faster`.
- Loop card: `publish -> inspect -> fix -> repeat`.

## Caption Notes

- Keep pages to 1-3 words.
- No underline.
- Red highlight on the active word only.
- Use big centered single-word treatment for `review`, `faster`, and `repeat`.
- Avoid punctuation unless it changes meaning.
- Let the black-video beat sit for a moment; do not rush the first caption of the next sentence onto the black frame.

## CTA

Primary:

> Comment REVIEW and I'll send you the skill.

Secondary:

> I'm packaging the whole 30-day system as I build it.

## Success Criteria

- The first 15 seconds contain a reason, proof, and a failure.
- The black-video problem makes the review skill feel necessary.
- At least one code/tool detail is visible enough that the build feels real.
- The generated contact sheets are visible on screen, not just described.
- The two findings are understandable without reading the whole review doc.
