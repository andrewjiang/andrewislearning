# Day 1 — Brainstorm

> Source: opening conversation with the AI on 2026-04-28. This *is* the Day 1 episode — the meta angle is "I'm a noob, so I asked an AI to help me plan a series about automating content creation with AI."
>
> **Status:** partial transcription from a screenshot. The AI response is cut off at the CapCut bullet; the rest of the brainstorm needs to be pasted in below the marker.

---

## My prompt

I'm on a mission to start a 30 day series where I go from a content creation noob to creating beautiful and informative content about creating, editing, and shipping content on AI.

The series is a "Day _ of making automating content creation", I'd imagine there are some rules.

1. all editing needs to be done using AI tools
2. all publishing needs to be done using AI tools
3. limited to using my phone and laptop for content recording, with no outside help

Help me brainstorm. We're going to do a full brainstorm on how to do this, what the initial setup might be and what the content script might be. This is part of the series!

## AI response (partial — see truncation marker)

Love this. And here's the move I want to lock in before we even start: **this conversation is Day 1.** The single best thing about your series concept is that the most authentic possible opening is "I'm a noob, so I asked an AI to help me plan a series about automating content creation with AI." Day 1 is meta and free. Don't waste it.

Let me throw out a bunch of stuff and then we narrow.

### The pipeline you're really designing (3 stages)

*Capture* is the only stage your rules say must be human/manual: phone for talking-head + B-roll, laptop for screen recordings (QuickTime or OBS — not AI, just the source of truth). The AI rules kick in after.

*Edit* is where you have the most options and they vary wildly in vibe:

- **Descript** — edit video by editing the transcript. Great for talking-head + tutorial. AI fills word gaps, removes "ums," even clones your voice for fixes.
- **Submagic / Captions / Opus Clip** — vertical-first, viral-style auto captions, hook detection, auto-zoom on faces. Best for short-form feel.
- **CapCut** (now with AI features) — phone-native, free, Gen Z polish.

<!-- TRUNCATION: screenshot cut off here. Paste the rest of the brainstorm below this marker. -->

## To paste in next session

- [ ] Rest of the *Edit* stage options (after CapCut bullet)
- [ ] *Publish* stage discussion
- [ ] Initial setup recommendations
- [ ] Day 1 content script suggestions
- [ ] Anything else from the brainstorm

## Decisions we've already locked in from this conversation

- This conversation IS Day 1 (the meta angle is the hook).
- Stage-first folder layout *with* per-day subfolders inside each stage. Every stage mirrors `day_NN/` so the day number is the join key.
- Filename convention for raw: `<shot_type>_take_NN.mp4` where shot_type ∈ {selfie, screen, broll}.
- Each day gets a Claude Code plugin under `plugins/day-NN-<slug>/` — Day 1's plugin is `day-01-series-planner`.
