---
name: spoken-reveal-captions
description: Build or refine stable-position Remotion captions where the full caption phrase keeps its layout but each word appears only when spoken. Use when the user asks for word reveal captions, words appearing when said, no caption layout shift, karaoke-style captions without moving text, or wants to add `wordRevealMode: "spoken"` to a ContentCopilot caption config.
---

# Spoken Reveal Captions

Create Remotion captions where each caption page reserves the full phrase layout, but future words remain invisible until their word timestamp. This is for cleaner short-form captions that feel timed to speech without the text jumping around.

The behavior lives in `captioner/src/CaptionedVideo.jsx` and is enabled through the Remotion caption payload style fields emitted by `pipeline/caption.py`.

## Workflow

1. Start from an existing caption config for the target video, or copy `series/days/02-caption-proxy-reveal.json` for a working example.
2. Keep the regular caption style. This treatment works best as a clean caption variant, not as a giant impact-word layer.
3. In the config `style`, set:

   ```json
   {
     "wordRevealMode": "spoken",
     "wordRevealFadeFrames": 2
   }
   ```

4. Use normal caption chunking first:
   - `maxWordsPerPage`: `2` or `3`
   - `maxCharsPerPage`: around `17-26`
   - `min_chunk_duration`: around `0.40-0.55`

5. Render through the Python pipeline:

   ```bash
   python3 pipeline/caption.py --config series/days/02-caption-proxy-reveal.json
   ```

6. Generate a contact sheet at representative timestamps:

   ```bash
   /opt/homebrew/bin/ffmpeg -y -loglevel error \
     -i edits/day_02/day_02_proxy_captioned_reveal.mp4 \
     -vf "select='eq(n,30)+eq(n,120)+eq(n,270)+eq(n,540)+eq(n,810)+eq(n,1194)+eq(n,1389)+eq(n,1710)',scale=270:480,tile=4x2:padding=8:margin=8:color=black" \
     -frames:v 1 .context/caption-experiments/day_02_proxy/reveal_sheet.jpg
   ```

7. Open the video and sheet for review:

   ```bash
   open edits/day_02/day_02_proxy_captioned_reveal.mp4 \
     .context/caption-experiments/day_02_proxy/reveal_sheet.jpg
   ```

## Taste Rules

- The line should not jump when words appear. If it jumps, the renderer is hiding words by removing them instead of fading their opacity.
- Keep future words fully invisible, not greyed out, unless the user explicitly wants a teleprompter/read-ahead look.
- Use a short fade, usually `1-3` frames. Longer fades feel mushy and laggy.
- Avoid using this on huge impact words. It is meant for sentence captions where stable layout matters.
- If too much empty space feels awkward before the final word appears, reduce `maxWordsPerPage` or `maxCharsPerPage`.
- Move the caption lane with `sceneOverrides` when b-roll or screen recordings need the lower third.

## Reference

Read `references/config.md` for the exact config fields and a compact JSON example.
