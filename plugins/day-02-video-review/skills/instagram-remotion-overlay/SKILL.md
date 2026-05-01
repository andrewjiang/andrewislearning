---
name: instagram-remotion-overlay
description: Build or refine local Remotion Instagram overlays for short-form videos. Use when the user asks for an Instagram proof card, floating Instagram component, mini Reel mock, black Reel preview, action rail, profile avatar, counts, caption preview, or wants to add `instagram_float` or `instagram_reel_mock` to a ContentCopilot caption config.
---

# Instagram Remotion Overlay

Create Instagram-style proof overlays rendered by the local Remotion captioner. The components live in `captioner/src/SocialOverlays.jsx`.

## Overlay Choices

- Use `instagram_float` for a compact proof card about reposts, comments, links, or social proof.
- Use `instagram_reel_mock` for a mini Reel UI, especially the black-video failure beat.

## Workflow

1. Start from `.context/instagram_overlay_preview.json` for proof cards or `.context/instagram_reel_mock_preview.json` for Reel mocks.
2. Set `sourceVideo` to the user's requested clip and keep output under `.context/previews/`.
3. Add one social overlay in the `overlays` array.
4. If the overlay shares lower-screen space with captions, move captions with `sceneOverrides` to `upper_safe` or `mid_safe`.
5. Render:

   ```bash
   node captioner/render-captioned.mjs --config .context/instagram_reel_mock_preview.json
   ```

6. Extract a still for review:

   ```bash
   ffmpeg -y -loglevel error -ss 1.5 -i .context/previews/instagram_reel_mock_preview.mp4 -frames:v 1 .context/previews/instagram_reel_mock_preview.png
   ```

## Taste Rules

- Do not use fake engagement unless the story calls for it. For the black Reel preview, keep likes/comments/shares at `0`.
- The mini Reel should feel native: black video area, action rail, bottom nav, small caption preview, and real avatar.
- Keep caption previews short; show only the first line or two like Instagram does.
- Avoid big labels like `BLACK VIDEO`; the black media area should communicate the failure.
- Keep the card small enough that the underlying face and body language remain visible.

## Reference

Read `references/config.md` for field lists and complete JSON snippets.
