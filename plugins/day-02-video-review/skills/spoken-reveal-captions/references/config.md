# Spoken Reveal Caption Config

Source components:

- `pipeline/caption.py` emits `style.wordRevealMode` and `style.wordRevealFadeFrames`.
- `captioner/src/CaptionedVideo.jsx` keeps every word in the layout and fades each word opacity from `0` to `1` at its timestamp.

## Fields

- `style.wordRevealMode`: set to `"spoken"` to enable stable-position reveal.
- `style.wordRevealFadeFrames`: reveal fade length in frames. Default to `2`.
- `maxWordsPerPage`: use `2` or `3`.
- `maxCharsPerPage`: use `17-26`, lower for more rhythmic captions.
- `sceneOverrides`: use when captions need to move to `upper_safe` during overlays or screen recordings.

## Minimal Example

```json
{
  "engine": "remotion",
  "captionVariant": "founder_clean",
  "input": "edits/day_02/day_02_proxy_assembled_v4.mp4",
  "output": "edits/day_02/day_02_proxy_captioned_reveal.mp4",
  "width": 540,
  "height": 960,
  "fps": 30,
  "maxWordsPerPage": 3,
  "maxCharsPerPage": 24,
  "anchor": "lower_safe",
  "style": {
    "size": 54,
    "color": "FFFFFF",
    "activeColor": "FF5A4F",
    "activeScale": 1.035,
    "pageEnterFrames": 5,
    "wordRevealMode": "spoken",
    "wordRevealFadeFrames": 2,
    "emphasis_color": "FFA395",
    "outline_color": "0A0A0A",
    "remotion_box_alpha": 0.0
  }
}
```

The config still needs normal `transcripts` entries with `combined_offset`, `leading_trim`, and `max_original` for the target assembled timeline.
