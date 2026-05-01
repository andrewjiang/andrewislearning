# Instagram Overlay Config

Source component: `captioner/src/SocialOverlays.jsx`

## Floating Proof Card

Overlay type: `instagram_float`

```json
{
  "type": "instagram_float",
  "start": 0.25,
  "end": 3.75,
  "headline": "Reposted on Instagram",
  "subhead": "My video got a second life on someone else's account.",
  "handle": "@ohmo.ai",
  "metric": "2,000+ comments",
  "note": "demo link in comments",
  "anchor": "lower_center",
  "bottomPercent": 0.25
}
```

Common fields: `headline`, `subhead`, `handle`, `source`, `metric`, `note`, `accent`, `anchor`, `width`, `bottomPercent`, `bottom`.

## Mini Reel Mock

Overlay type: `instagram_reel_mock`

```json
{
  "type": "instagram_reel_mock",
  "start": 0.15,
  "end": 3.85,
  "username": "andrewislearning",
  "audio": "Original audio",
  "caption": "Day 1 of training AI to be my video editor. Written, edited, captioned, and published by AI. Follow + comment \"DAY 1\" for the guide + plugin.",
  "captionPreview": "Day 1 of training AI to be my video editor. Written, edited...",
  "likeCount": "0",
  "commentCount": "0",
  "shareCount": "0",
  "videoLabel": "",
  "avatar": ".context/attachments/fc3795ea-adaa-44df-a3d1-ff4c932af794.png",
  "verified": true,
  "anchor": "lower_center",
  "width": 500,
  "bottomPercent": 0.07
}
```

Common fields: `username`, `audio`, `caption`, `captionPreview`, `likeCount`, `commentCount`, `shareCount`, `videoLabel`, `avatar`, `verified`, `width`, `bottomPercent`.

Asset handling:

- `render-captioned.mjs` copies `avatar` into Remotion's temporary public dir automatically.
- Keep avatar paths local and stable under `.context/attachments/` or a checked-in asset folder.
