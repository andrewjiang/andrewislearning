# Day 2 Caption Experiments

## Research Notes

- TikTok's current in-feed specs recommend vertical 9:16 creative and safe-zone checks so text is not covered by platform UI: https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads
- Meta's Reels guidance emphasizes 9:16 video with audio and key messages inside the safe zone: https://www.facebook.com/business/ads/facebook-instagram-reels-ads
- TikTok's creative tips recommend direct-to-camera or voiceover, concise text overlays, and closed captions: https://ads.tiktok.com/business/library/7TopCreativeTips.pdf
- Remotion's caption docs support the implementation shape used here: page timing with `Sequence`, per-token highlighting, `fitText()`, and frame-derived animation: https://www.remotion.dev/docs/captions/displaying
- Remotion `spring()` and `interpolate()` are the right primitives for deterministic render-time motion: https://www.remotion.dev/docs/spring and https://www.remotion.dev/docs/interpolate
- Market references such as Remotion Pro animated captions, ZapCap, and Submagic converge on active-word color, active-word scaling, keyword emphasis, and optional emojis. Emoji is intentionally skipped for this technical/founder series.
- The current reference direction is darker video, bright white uppercase captions, selective pink emphasis, and a modern heavy sans. This reads more native to current mobile editors than the older salmon/subtitle look.

## Caption System Direction

- Treat caption design as presets composed from independent controls: font family, weight, page size, reveal behavior, active/emphasis color, stroke, shadow, dim overlay, lane, and optional impact layers.
- Keep a curated display-font registry in Remotion rather than relying on browser fallback. Current registry includes `TikTok Sans`, `Montserrat`, `Inter Tight`, `Poppins`, `Archivo Black`, `Anton`, `Barlow Condensed`, `Oswald`, `Teko`, `League Gothic`, `Bebas Neue`, `Kalam`, and `Permanent Marker`.
- Prefer stable-position spoken reveal for founder/video-review clips: page layout is visible as a single phrase, but each word fades in only when said. This avoids the old flashing-card feel while preserving speech lock.
- Use video dimming as a preset-level choice. The modern dark preset uses a black overlay so white captions stay readable without a large caption box.
- Reserve large impact words for proof beats or chapter beats. If used, they should linger longer than a single spoken word and use a separate lane/font from base captions.
- Page grouping needs editorial rules, not only word counts. The current modern preset treats punctuation and transcript segment ends as hard boundaries, prefers one-line pages up to medium caption lengths, and uses phrase groups to avoid dangling words like `a`, `to`, `and`, or the first word of a new sentence.
- Screen-recording sections should use lower, smaller captions when the source video already contains readable UI text. The caption should support the narration without covering the proof on screen.

## Variants

- `founder_clean` uses the current readable style: 1-3 word pages, salmon active word, subtle scale, strong shadow, no extra stroke.
- `kinetic_pop` uses shorter 1-2 word pages, faster entry, stronger active-word scale/lift, and a light stroke for higher TikTok-style energy.
- `proof_impact` keeps the clean base style but turns proof beats into large centered impact words: `MILLION`, `BLACK`, `WATCH`, `SCORECARD`, `FFMPEG`, `FASTER`, and `REVIEW`.
- `modern_dark` uses a lightly dimmed video base, `TikTok Sans` 900, uppercase white captions, spoken reveal, compact shadow/stroke, one-line-biased sizing, and pink only for emphasis terms.

## Render Commands

```bash
python3 pipeline/caption.py --config series/days/02-caption-proxy-clean.json
python3 pipeline/caption.py --config series/days/02-caption-proxy-pop.json
python3 pipeline/caption.py --config series/days/02-caption-proxy-impact.json
python3 pipeline/caption.py --config series/days/02-caption-proxy-modern-dark.json
```

Outputs:

- `edits/day_02/day_02_proxy_captioned_clean.mp4`
- `edits/day_02/day_02_proxy_captioned_pop.mp4`
- `edits/day_02/day_02_proxy_captioned_impact.mp4`
- `edits/day_02/day_02_proxy_captioned_modern_dark.mp4`

QA sheet:

- `.context/caption-experiments/day_02_proxy/modern_dark_sheet.jpg`

## Next Experiments

- `modern_white`: same dimmed video and font registry, but all-white captions with emphasis conveyed by scale/weight only.
- `editorial_day`: title-card style for chapter beats like `DAY 2`, using cinematic serif or condensed display type separately from spoken captions.
- `commentary_callout`: small anchored labels/arrows for UI proof moments, independent from spoken captions.
- `impact_linger`: large handwritten/italic proof words above the face, held for 0.6-0.9 seconds after the spoken word.
- `karaoke_stack`: 2-line stable phrase with unsaid words at 0 opacity, said words white, and emphasis terms pink.

## Winner Checklist

- Text stays inside the safe zone and clears lower platform UI.
- Captions do not cover faces or important screen details for more than a beat.
- Active-word timing feels locked to speech.
- The first 5 seconds communicate the premise faster than Day 1.
- The proof beats are readable without sound.
- The winner feels native to a founder/build-in-public video, not like a generic subtitle template.
