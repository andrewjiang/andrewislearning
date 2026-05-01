---
name: ffmpeg-remotion-overlay
description: Build or refine the local Remotion FFmpeg cutting modal overlay for short-form videos. Use when the user asks for an ffmpeg process card, command-line video edit visualization, filmstrip, cut-cut animation, removed middle segment, rejoined clip, or wants to add `ffmpeg_cut_modal` to a ContentCopilot caption config.
---

# FFmpeg Remotion Overlay

Create a dark FFmpeg process modal with command logs and a real-video filmstrip cut animation. The overlay lives in `captioner/src/WorkflowOverlays.jsx` and is selected with `type: "ffmpeg_cut_modal"`.

## Workflow

1. Start from `.context/ffmpeg_modal_preview.json`.
2. Set `sourceVideo` to the user's requested clip.
3. Generate fresh filmstrip frames from the same source clip:

   ```bash
   mkdir -p .context/previews/img0196_ffmpeg_frames
   ffmpeg -y -loglevel error -i .context/attachments/IMG_0196.MOV -vf "fps=2,scale=120:80:force_original_aspect_ratio=increase,crop=120:80" -frames:v 8 .context/previews/img0196_ffmpeg_frames/frame_%02d.png
   ```

   Change the output folder name for different source clips so stale stills do not leak into the preview.

4. Put those frame paths in the overlay `frames` array.
5. Render:

   ```bash
   node captioner/render-captioned.mjs --config .context/ffmpeg_modal_preview.json
   ```

6. Extract review stills:

   ```bash
   ffmpeg -y -loglevel error -ss 1.7 -i .context/previews/ffmpeg_modal_preview.mp4 -frames:v 1 .context/previews/ffmpeg_modal_preview_cut1.png
   ffmpeg -y -loglevel error -ss 3.4 -i .context/previews/ffmpeg_modal_preview.mp4 -frames:v 1 .context/previews/ffmpeg_modal_preview.png
   ```

## Taste Rules

- Use real stills from the same source video whenever possible.
- Keep the animation fast: cut, cut, middle drops out, sides snap together.
- Keep command text plausible but short. Do not let terminal copy become the focal point.
- Use this as a visual metaphor for editing, not as a literal tutorial.
- Keep the card low enough to read but clear of the user's face.

## Reference

Read `references/config.md` for the field list and a complete config snippet.
