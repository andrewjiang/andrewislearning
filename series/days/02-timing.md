# Day 2 - Transcript & Timing Map

Generated from the raw Day 2 clips in `raw/day_02/` using:

```bash
.venv-whisper/bin/python pipeline/transcribe.py raw/day_02/IMG_####.MOV --model small
```

All transcript outputs are in `transcripts/day_02/` and include word-level timing in `segments[].words[]`.

## Clip Inventory

| Clip | Dur | Res | Words | Transcript excerpt | Match | Role | In-Out |
|---|---:|---|---:|---|---|---|---|
| `IMG_0196.MOV` | 4.77s | 1920x1080 | 12 | Play around with remotion to get these cool little on-screen graphics | Reserve / not selected | Production note | - |
| `IMG_0204.MOV` | 10.63s | 1920x1080 | 34 | Quick recap my video on X got nearly a million views someone else reposted it to Instagram and got 2,000 comments... | SHOT 2 - recap proof | A-roll audio + Day 1 repost b-roll visual | 0.00-10.05s |
| `IMG_0206.MOV` | 6.10s | 1920x1080 | 16 | Day 2 of teaching my AI to be a video editor. Day 1 almost didn't happen. | SHOT 1 - Day 2 reveal | A-roll | 0.00-5.45s |
| `IMG_0207.MOV` | 2.80s | 1920x1080 | 6 | So day one almost didn't happen | Reserve / not selected | Alternate hook tail | - |
| `IMG_0210.MOV` | 4.33s | 1920x1080 | 13 | Shout out to Kevin for being the one like on that black video | SHOT 4 - Kevin beat | A-roll + notification overlay | 0.05-3.20s |
| `IMG_0211.MOV` | 8.23s | 1920x1080 | 22 | So the lesson is obvious. Before this thing publishes a video, it has to actually watch the video just like an editor. | SHOT 5 - lesson | A-roll | 0.00-7.50s |
| `IMG_0220.MOV` | 7.93s | 1920x1080 | 23 | So I asked Claude to build me a review agent. Sample the frames, read the transcript, and do a full check before publishing. | SHOT 6 - review agent prompt | A-roll + Claude/terminal b-roll | 0.00-6.62s |
| `IMG_0235.MOV` | 14.93s | 3840x2160 | 36 | It gives me a scorecard and areas to improve. Like for day one it suggested better captions, better on-screen visuals... | SHOTS 7-8 - scorecard + fixes | A-roll + scorecard/fixes visuals | 0.00-12.78s |
| `IMG_0236.MOV` | 6.27s | 3840x2160 | 17 | Day 2 is the review agent. Comment review and I'll send you the plugin and full guide. | SHOT 9 - CTA | A-roll | 0.11-5.16s |
| `IMG_0247.MOV` | 10.03s | 3840x2160 | 22 | Yesterday my AI agent automatically posted day one. The audio worked, but the video was completely black. It was a formatting issue. | SHOT 3 - black video reveal | A-roll + black Reel mockup | 0.00-8.62s |
| `IMG_0253.MOV` | 13.50s | 3840x2160 | 37 | Quick recap my video on x got nearly a million views someone else reposted a better edited version to Instagram... | SHOT 2 - improved recap | A-roll selfie + short b-roll insert | 0.18-12.85s |
| `IMG_0253-v1.MOV` | 13.50s | 3840x2160 | 37 | Quick recap my video on x got nearly a million views someone else reposted a better edited version to Instagram... | SHOT 2 - improved recap v2 | A-roll selfie + short b-roll insert; preferred tail because eyes are on camera | 0.18-12.85s |
| `IMG_0260-v1.MOV` | 3.30s | 3840x2160 | 10 | So I'm training AI to be the video editor I never had. | SHOT 2 - training pickup | A-roll replacement for the post-b-roll tail | 0.00-2.70s |
| `IMG_0270.MOV` | 12.67s | 1920x1080 | 36 | Quick recap, my video on X got nearly a million views. Somebody else reposted it to Instagram... | SHOT 2 - cleaner recap | A-roll with Instagram b-roll over "Somebody else..." | 0.00-11.60s |
| `IMG_0271.MOV` | 4.00s | 1920x1080 | 13 | Shout out to Kevin for being the one comment on that video. | SHOT 4 - Kevin pickup | A-roll replacement | 0.12-3.25s |
| `IMG_0274.mov` | 5.29s | 1920x1080 | 13 | Day two of teaching AI to be my video editor and day one almost didn't happen. | SHOT 1 - cleaner opener | A-roll replacement | 0.00-4.95s |
| `screen_review_agent.mov` | 19.30s | 1524x2570 | - | Claude review UI showing sampling frames, scorecard, and review output. | SHOTS 6-7 - review UI proof | B-roll insert | 5.50-12.20s |

## Selected Spine Order

Use the selected clips in this order to build the proxy audio/visual spine:

1. `IMG_0274.mov` - SHOT 1, cleaner Day 2 opener in one take
2. `IMG_0270.MOV` - SHOT 2, cleaner recap in one take
3. `IMG_0247.MOV` - SHOT 3, black video / format issue
4. `IMG_0271.MOV` - SHOT 4, cleaner Kevin one-comment pickup
5. `IMG_0211.MOV` - SHOT 5, lesson
6. `IMG_0220.MOV` - SHOT 6, review agent
7. `IMG_0235.MOV` - SHOTS 7-8, scorecard + fixes
8. `IMG_0236.MOV` - SHOT 9, CTA

Generate normalized proxies first:

```bash
python3 pipeline/proxy.py raw/day_02/*.MOV raw/day_01/broll_take_01.mp4
```

Then create the untrimmed proxy spine with:

```bash
python3 pipeline/sequence.py --config series/days/02-proxy-sequence.json
```

Then run:

```bash
python3 pipeline/assemble.py series/days/02-proxy-assembly-v2.json
```

Current v6 direct-cut command:

```bash
python3 pipeline/sequence.py --config series/days/02-proxy-sequence-v6.json
python3 pipeline/assemble.py series/days/02-proxy-assembly-v6.json
```

## Tightened Timeline

These are the expected post-tighten timeline positions before the final 1.08x finish speedup.

| Shot | Source | Tightened timeline | Duration | Visual treatment |
|---|---|---:|---:|---|
| SHOT 1 | `IMG_0274.mov` | 0.00-4.95s | 4.95s | Clean one-take opener; no black pause or extra hook pickup cut |
| SHOT 2 | `IMG_0270.MOV` | 4.95-16.55s | 11.60s | Single recap take; Instagram b-roll from 8.27-13.17s over "Somebody else..." through comments, then face returns for "So I'm training..." |
| SHOT 3 | `IMG_0247.MOV` | 16.55-25.17s | 8.62s | Black Reel mockup + format-error flash |
| SHOT 4 | `IMG_0271.MOV` | 25.17-28.30s | 3.13s | New "one comment" Kevin pickup |
| SHOT 5 | `IMG_0211.MOV` | 28.30-35.80s | 7.50s | Selfie, original proxy framing |
| SHOT 6 | `IMG_0220.MOV` | 35.80-42.42s | 6.62s | Review-agent A-roll; Claude review screen B-roll starts at 38.50s on "Sample..." using the screen recording from 5.50s in |
| SHOTS 7-8 | `IMG_0235.MOV` | 42.42-55.20s | 12.78s | Claude review screen continues through 45.20s, then returns to camera for "Like for day one"; scorecard/fixes visuals after |
| SHOT 9 | `IMG_0236.MOV` | 55.20-60.33s | 5.13s | Selfie CTA |

Pre-speedup runtime target from selected windows: about 60.33s.
Post-speedup at 1.08x: about 55.86s.

## Current V7 Timing

V7 removes the Kevin shoutout section entirely. Later timings shift 3.13s earlier.

| Shot | Source | Timeline | Length | Notes |
| --- | --- | ---: | ---: | --- |
| SHOT 1 | `IMG_0274.mov` | 0.00-4.95s | 4.95s | Clean one-take opener; visual black-frame repair applied at ~2.07s in the assembled proxy |
| SHOT 2 | `IMG_0270.MOV` | 4.95-16.55s | 11.60s | Quick recap; Instagram repost b-roll remains 8.27-13.17s |
| SHOT 3 | `IMG_0247.MOV` | 16.55-25.17s | 8.62s | Black-video / formatting issue beat with Instagram Reel mock overlay at 20.45-25.12s |
| SHOT 5 | `IMG_0211.MOV` | 25.17-32.67s | 7.50s | Lesson beat after Kevin cut |
| SHOT 6 | `IMG_0220.MOV` | 32.67-39.29s | 6.62s | Claude prompt modal at 32.77-35.32s; review screen b-roll starts at 35.37s |
| SHOTS 7-8 | `IMG_0235.MOV` | 39.29-52.07s | 12.78s | FFmpeg modal at 45.42-50.27s with air-slice cut SFX |
| SHOT 9 | `IMG_0236.MOV` | 52.07-57.13s | 5.05s | Selfie CTA |

## Notes

- `series/days/02-script.md` already matches the updated script attachment exactly.
- V7 cuts the Kevin shoutout section because it slows down the video.
- The raw Kevin clip says "one like", while the updated script says "one comment". If the "one comment" wording is required, record a short pickup for SHOT 4. Otherwise the natural spoken take is usable and the overlay can avoid contradicting it.
- `IMG_0196.MOV` is useful as a production-note reference for Remotion graphics but should not go into the main spine.
- `IMG_0207.MOV` is now used as the tighter "day one almost didn't happen" pickup after the Remotion title reveal.
- `IMG_0253.MOV` replaces `IMG_0204.MOV` for the recap. This keeps the "my video on X..." beat on selfie, uses b-roll only for the Instagram repost proof, then returns to selfie for "so I'm training..."
- `IMG_0253-v1.MOV` replaces `IMG_0253.MOV` in v3 because the tail returns to eye contact after the b-roll.
- `IMG_0260-v1.MOV` replaces the post-b-roll "So I'm training AI..." tail in v5.
- `IMG_0274.mov`, `IMG_0270.MOV`, and `IMG_0271.MOV` replace the opener, recap, and Kevin beats in v6 to reduce A-roll cuts.
- v6 uses the original uncropped proxy framing. Do not crop or zoom A-roll unless explicitly requested.
- `screen_review_agent.mov` is the Claude review UI B-roll used from "Sample..." until just before "Like for day one"; v6 starts this source 5.50s in to skip the preamble text.
- `series/days/02-caption-v6-overlays.json` is the first Remotion overlay + caption pass for v6:
  - `instagram_reel_mock` at 20.45-25.12s over the black-video / formatting issue beat.
  - `claude_prompt_modal` at 35.90-38.45s over "So I asked Claude...".
  - `ffmpeg_cut_modal` at 48.55-53.40s over the onscreen-tools / ffmpeg beat.
  - Captions use the v6 transcript timing and the existing Remotion caption pipeline from Day 1.
- `series/days/02-caption-v7-overlays.json` switches to spoken reveal captions, keeps Instagram captions in the top lane, lets the Claude caption sit below the modal, and adds `sumaga_knife_cut_short.wav` to the FFmpeg cut markers.
- Do not concatenate raw iPhone HEVC clips directly for iteration. Generate proxies first; each raw clip gets independently decoded, autorotated, scaled, and re-encoded before concat.
- v2 tested a 0.10s `xfade`/`acrossfade`, but it felt too much like an effect. v3 returned to direct cuts but used a generated black/silent pause. v5 removes that synthetic pause and uses extra real footage at the cut instead.

## Validation

- 14 Day 2 `.mov`/`.MOV` raw clips found in `raw/day_02/`, including the screen review recording.
- 13 transcript JSON files written in `transcripts/day_02/` for the spoken camera clips.
- Every transcript includes at least one `segments[].words[]` entry.
- Selected spoken windows cover SHOTS 1-9 and support the target runtime.
- `raw/day_02/selfie_spine_raw.mp4` generated from the selected clip order: 68.49s, 1080x1920.
- `raw/day_02/selfie_spine_tight.mp4` generated by `pipeline/tighten.py`: 59.30s, 1080x1920.
- `edits/day_02/day_02_assembled.mp4` generated by `pipeline/assemble.py`: 59.30s, 1080x1920, with the Day 1 repost b-roll inserted over the recap.
- `proxies/day_02/*.proxy.mp4` generated by `pipeline/proxy.py`: 540x960 H.264 edit proxies.
- `edits/day_02/day_02_proxy_assembled.mp4` generated from proxy media: 59.43s, 540x960, no right-edge HEVC corruption in sampled frames.
- `edits/day_02/day_02_proxy_assembled_v2.mp4` generated from the new recap proxy sequence: 60.43s, 540x960, shorter b-roll window, subtle crossfades between A-roll segments, clean ffmpeg decode.
- `edits/day_02/day_02_proxy_assembled_v3.mp4` generated from the v3 direct-cut sequence: 61.50s, 540x960, `IMG_0253-v1` recap tail, 0.25s hook pause, no crossfades, clean ffmpeg decode.
- `edits/day_02/day_02_proxy_assembled_v5.mp4` generated from the v5 direct-cut sequence: 60.33s, 540x960, real-footage hook pause, shortened Instagram b-roll, `IMG_0260-v1` training pickup, Claude review screen B-roll, clean ffmpeg decode.
- `edits/day_02/day_02_proxy_assembled_v6.mp4` generated from the v6 direct-cut sequence: 60.27s, 540x960, cleaner opener/recap/Kevin takes, 8 A-roll segments instead of 10, original uncropped proxy framing, clean ffmpeg decode.
- `edits/day_02/day_02_proxy_captioned_v6_overlays.mp4` generated from the v6 overlay/caption pass: Instagram black-Reel mock, Claude prompt modal, ffmpeg tools modal, Remotion captions, clean ffmpeg decode.
- `edits/day_02/day_02_proxy_assembled_v7_noflicker.mp4` generated from the v7 no-Kevin sequence: 57.13s, 540x960, with the opener black-frame blip repaired by freezing the prior good visual frame while preserving audio/timing.
- `edits/day_02/day_02_proxy_captioned_v7_noflicker_overlays_1080.mp4` generated from the v7 no-flicker assembly: 57.13s, 1080x1920, spoken reveal captions, Instagram/Claude/FFmpeg overlays, FFmpeg cut SFX, no `blackdetect` full-frame intervals.
