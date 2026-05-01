# FFmpeg Overlay Config

Source component: `captioner/src/WorkflowOverlays.jsx`

Overlay type: `ffmpeg_cut_modal`

```json
{
  "type": "ffmpeg_cut_modal",
  "start": 0.2,
  "end": 4.55,
  "command": "ffmpeg -i raw.mov -ss 00:12 -to 00:18 -c copy clip.mp4",
  "frames": [
    ".context/previews/img0196_ffmpeg_frames/frame_01.png",
    ".context/previews/img0196_ffmpeg_frames/frame_02.png",
    ".context/previews/img0196_ffmpeg_frames/frame_03.png",
    ".context/previews/img0196_ffmpeg_frames/frame_04.png",
    ".context/previews/img0196_ffmpeg_frames/frame_05.png",
    ".context/previews/img0196_ffmpeg_frames/frame_06.png",
    ".context/previews/img0196_ffmpeg_frames/frame_07.png",
    ".context/previews/img0196_ffmpeg_frames/frame_08.png"
  ],
  "cutSound": ".context/sfx/sumaga_knife_cut_short.wav",
  "cutSoundVolume": 0.72,
  "cutSoundFrames": [12, 20],
  "bottomPercent": 0.22
}
```

Common fields:

- `command`: terminal command shown at top of log box.
- `frames`: array of local image paths, copied into Remotion's public dir automatically.
- `cutSound`, `cutSoundVolume`, `cutSoundFrames`: optional knife-cut audio hits for cut markers.
- `title`: defaults to `ffmpeg`.
- `subtitle`: defaults to `cutting video`.
- `anchor`, `bottomPercent`, `bottom`, `width`, `sidePad`: placement controls.

Frame extraction pattern:

```bash
ffmpeg -y -loglevel error -i <source-video> -vf "fps=2,scale=120:80:force_original_aspect_ratio=increase,crop=120:80" -frames:v 8 <out-dir>/frame_%02d.png
```

If the source is shorter than 4 seconds, keep `duration` and overlay `end` inside the source duration.
