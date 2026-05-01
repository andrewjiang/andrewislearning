---
name: claude-remotion-overlay
description: Build or refine the local Remotion Claude prompt modal overlay for short-form videos. Use when the user asks for a Claude Desktop-style modal, a typed Claude prompt, keyboard typing audio, send-button press/loading animation, or wants to add the `claude_prompt_modal` overlay to a ContentCopilot caption config.
---

# Claude Remotion Overlay

Create a clean Claude-style prompt card rendered by the local Remotion captioner. The overlay lives in `captioner/src/WorkflowOverlays.jsx` and is selected with `type: "claude_prompt_modal"`.

## Workflow

1. Start from the current preview config at `.context/claude_modal_preview.json` when iterating the design.
2. Use `sourceVideo` from the user's requested clip. Keep `width: 1080`, `height: 1920`, `fps: 30`, and trim `duration` to the source clip length.
3. Configure a single overlay with:
   - `placeholder`: faint input-box text, usually `How can I help you?`.
   - `ask`: the typed prompt, e.g. `help me edit my video`.
   - `greeting`: keep empty unless the user explicitly wants a greeting line.
   - `typingTrack`: prefer `.context/sfx/mixkit_fast_laptop_typing_short.wav`.
   - `typingVolume`: use `1` for preview audibility, lower only if it fights voiceover.
4. Render:

   ```bash
   node captioner/render-captioned.mjs --config .context/claude_modal_preview.json
   ```

5. Extract review stills:

   ```bash
   ffmpeg -y -loglevel error -ss 0.35 -i .context/previews/claude_modal_preview.mp4 -frames:v 1 .context/previews/claude_modal_preview_placeholder.png
   ffmpeg -y -loglevel error -ss 2.75 -i .context/previews/claude_modal_preview.mp4 -frames:v 1 .context/previews/claude_modal_preview_loading.png
   ```

6. Inspect the stills and the MP4. The user should see: placeholder only before typing, typed ask as the focal point, send-button press, then a spinning Claude mark.

## Taste Rules

- Keep the card visually quiet. Do not add explanatory labels or feature text.
- Keep the input text larger and heavier than any header text.
- Do not let the card cover the user's face; default to lower-middle over chest.
- The placeholder should disappear immediately once typing starts.
- The loading state should be visible in motion, not just as a static icon.

## Reference

Read `references/config.md` for the field list and a complete config snippet.
