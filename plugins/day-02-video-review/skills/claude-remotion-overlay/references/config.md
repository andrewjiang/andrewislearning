# Claude Overlay Config

Source component: `captioner/src/WorkflowOverlays.jsx`

Overlay type: `claude_prompt_modal`

Common fields:

```json
{
  "type": "claude_prompt_modal",
  "start": 0.2,
  "end": 4.55,
  "ask": "help me edit my video",
  "greeting": "",
  "placeholder": "How can I help you?",
  "typingTrack": ".context/sfx/mixkit_fast_laptop_typing_short.wav",
  "typingVolume": 1,
  "typeStartFrame": 12,
  "typeFramesPerChar": 1.55,
  "bottomPercent": 0.28
}
```

Supported placement fields:

- `anchor`: `lower_center`, `lower_left`, or `lower_right`.
- `bottomPercent`: fraction of frame height from bottom.
- `bottom`: absolute pixel override.
- `width`: card width in pixels.
- `sidePad`: left/right inset for side anchors.

Audio notes:

- Source typing clip: `.context/sfx/source/mixkit-fast-laptop-keyboard-typing-1392.wav`
- Edited preview clip: `.context/sfx/mixkit_fast_laptop_typing_short.wav`
- Source/license note: `.context/sfx/SOURCES.md`
