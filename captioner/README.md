# Captioner

Local Remotion renderer for dynamic short-form captions.

The Python pipeline remains the main entrypoint:

```bash
python3 pipeline/caption.py --config series/days/01-caption.json
```

Install once:

```bash
cd captioner
npm install
```

`pipeline/caption.py` writes `edits/day_NN/*.captions.json` and invokes
`render-captioned.mjs`, which renders the source video with a React/CSS caption
overlay. Use `--engine ass` on the Python command to fall back to the old
ffmpeg/libass renderer.

## Sound effects

Reusable audio lives in `.context/sfx/`.

- Use `.context/sfx/catalog.json` when an agent needs machine-readable effect
  choices, default volumes, and overlay fields.
- Use `.context/sfx/README.md` for the intensity scale and copy-paste examples.
- Use `.context/sfx/SOURCES.md` for source/license/edit notes.

Keep the approved palette tight: real typing, knife cut, and hard metal slam.
Retire scratch sounds quickly when they start to feel generic or distracting.

## Timed social overlays

Caption configs can include an `overlays` array. Supported overlay types:

- `instagram_float`: floating proof card.
- `instagram_reel_mock`: mini Reel UI with a black video area and native-style
  action rail.
- `claude_prompt_modal`: Claude Desktop-style prompt modal with typed ask.
- `ffmpeg_cut_modal`: FFmpeg process modal with logs and a cutting filmstrip.
- `slam_title`: oversized title caption that slams into frame with optional
  impact audio.

Floating proof card:

```json
{
  "overlays": [
    {
      "type": "instagram_float",
      "start": 8.8,
      "end": 14.2,
      "headline": "Reposted on Instagram",
      "subhead": "Someone used my video and got the attention.",
      "handle": "@ohmo.ai",
      "metric": "2,000+ comments",
      "note": "demo link in comments",
      "anchor": "lower_center"
    }
  ]
}
```

Use `sceneOverrides` to move captions to `upper_safe` or `mid_safe` during the
same window if the overlay is sharing the lower part of the frame.

Mini black Reel mock:

```json
{
  "overlays": [
    {
      "type": "instagram_reel_mock",
      "start": 10.2,
      "end": 16.0,
      "username": "andrewislearning",
      "caption": "Day 1 of training AI to be my video editor. Written, edited, captioned, and published by AI. Follow + comment \"DAY 1\" for the guide + plugin.",
      "captionPreview": "Day 1 of training AI to be my video editor. Written, edited...",
      "likeCount": "0",
      "commentCount": "0",
      "shareCount": "0",
      "avatar": ".context/attachments/fc3795ea-adaa-44df-a3d1-ff4c932af794.png",
      "anchor": "lower_center"
    }
  ]
}
```

Claude prompt modal:

```json
{
  "overlays": [
    {
      "type": "claude_prompt_modal",
      "start": 20.0,
      "end": 25.2,
      "greeting": "",
      "placeholder": "How can I help you?",
      "ask": "help me edit my video",
      "typingTrack": ".context/sfx/mixkit_fast_laptop_typing_short.wav",
      "typingVolume": 1
    }
  ]
}
```

FFmpeg cutting modal:

```json
{
  "overlays": [
    {
      "type": "ffmpeg_cut_modal",
      "start": 30.0,
      "end": 36.0,
      "command": "ffmpeg -i raw.mov -ss 00:12 -to 00:18 -c copy clip.mp4",
      "frames": [
        ".context/previews/ffmpeg_frames/frame_01.png",
        ".context/previews/ffmpeg_frames/frame_02.png",
        ".context/previews/ffmpeg_frames/frame_03.png",
        ".context/previews/ffmpeg_frames/frame_04.png",
        ".context/previews/ffmpeg_frames/frame_05.png",
        ".context/previews/ffmpeg_frames/frame_06.png"
      ],
      "cutSound": ".context/sfx/sumaga_knife_cut_short.wav",
      "cutSoundVolume": 0.72,
      "cutSoundFrames": [12, 20]
    }
  ]
}
```

Slam title:

```json
{
  "overlays": [
    {
      "type": "slam_title",
      "start": 0.15,
      "end": 2.6,
      "text": "DAY TWO",
      "topPercent": 0.022,
      "fontFamily": "Slam Antonio",
      "fontWeight": 700,
      "fontFile": ".context/fonts/Antonio-Bold.ttf",
      "fontSize": 356,
      "accentLastWord": true,
      "slamSound": ".context/sfx/soundreality_metal_door_slam_short.wav",
      "slamVolume": 0.9,
      "soundOffsetFrame": 5
    }
  ]
}
```
