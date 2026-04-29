# Day 1 — Script & Shot List (v3.2, current)

**Working title:** Day 1 of teaching an AI to be my video editor
**Length target:** ~52 seconds
**Aspect:** 9:16 (1080×1920)
**Primary platform:** Instagram Reels (cross-post to TikTok)
**CTA keyword:** `DAY1`
**Series-format opener:** *"Day N of teaching an AI to be my video editor."* — used on every episode for series identity.

Prior versions: [`versions/01-script.v1.md`](versions/01-script.v1.md) · [`versions/01-script.v2.md`](versions/01-script.v2.md) · [`versions/01-script.v3.md`](versions/01-script.v3.md).

---

## Script (v3.2 — locked for shoot)

> **[SHOT 1A — selfie, phone, vertical, raw]**
>
> "Day 1 of teaching an AI to be my video editor.
>
> My video on X got nearly a million views."
>
> **[SHOT 1B — IG repost b-roll, `raw/day_01/broll_take_01.mp4`]**
>
> "Someone reposted it on Instagram, gave away my demo link, and got two thousand comments."
>
> **[SHOT 1C — selfie]**
>
> "I got out-edited on my own work — and that's on me.
>
> So instead of becoming an editor, I'm gonna teach an AI to be one.
>
> Thirty days. Every edit through an AI agent. Every post through an AI agent. Just my phone and a laptop."
>
> **[SHOT 2 — Cowork screen clip, `edits/day_01/screen_clip.mp4`]**
>
> "Step one wasn't recording. It was opening Claude. I asked it to plan the whole thirty days."
>
> **[SHOT 3 — 4 cards, narrated, `edits/day_01/cards.mp4`]**
>
> "Build. *(card 1, 1.0s)* Polish. *(card 2, 1.0s)* Automate. *(card 3, 1.0s)* Every day. *(card 4, 1.0s)*"
>
> **[SHOT 4 — selfie outro]**
>
> "I'm packaging everything into a free guide. Follow and comment 'DAY1' and I'll DM you everything."
>
> *Optional tail (4 more words):* "Tomorrow we build the pipeline."

### Three alternates for the ownership beat

The line "and that's on me" is the ownership flip. Shoot all three, pick in edit:

1. *"…and that's on me."* — direct, sincere
2. *"…and that's embarrassing."* — self-deprecating, more relatable
3. *"…so something's clearly broken with my setup."* — deflects to tools, slightly weaker

---

## Shot list & timing

| # | Type | Source | Audio (what you say) | Window | Length |
|---|------|--------|----------------------|--------|--------|
| 1A | Selfie | `raw/day_01/selfie_take_NN.mp4` | "Day 1 of teaching… got nearly a million views." | 0:00–0:08 | 8s |
| 1B | IG repost b-roll | `raw/day_01/broll_take_01.mp4` | "Someone reposted it on Instagram… two thousand comments." | 0:08–0:14 | 6s |
| 1C | Selfie | (same selfie clip) | "I got out-edited… just my phone and a laptop." | 0:14–0:35 | 21s |
| 2 | Cowork screen clip | `edits/day_01/screen_clip.mp4` | "Step one wasn't recording… plan the whole thirty days." | 0:35–0:42 | 7s |
| 3 | Cards | `edits/day_01/cards.mp4` | "Build. Polish. Automate. Every day." (1:1 sync, 1.0s/card) | 0:42–0:46 | 4s |
| 4 | Selfie | (same selfie clip) | "I'm packaging everything… DM you everything." | 0:46–0:52 | 6s |

**Total:** ~52s. ✓ within target.

The selfie should be **one continuous take** covering the whole 52-second script. The assembler swaps the *visual* during the b-roll windows but keeps the *audio* (you speaking) throughout.

---

## Production notes

**Lighting/audio (selfie).** Window light to your front. Phone propped at eye level (book stack works). Mic source is the phone — speak clearly, don't move the phone. We are NOT optimizing the raw take. The *AI does the polish* is the entire premise. Good-enough raw is the brand.

**Delivery — load-bearing lines:**

- *"Day 1 of teaching an AI to be my video editor."* — say it like a fact, not an announcement. No upspeak. Repeats every episode for series identity.
- *"My video on X got nearly a million views."* — the credential. Sell with confidence. Not a humble-brag, not a flex, just a fact.
- *"…and that's on me."* — the emotional flip. Practice the three alternates; pick in edit.
- *"Build. Polish. Automate. Every day."* — narrate in 1.0-second beats; each phrase synced 1:1 with a card. Snappy, not slow.

**B-roll cues for shoot day:**

- **Shot 1B (IG repost):** the file `raw/day_01/broll_take_01.mp4` is already in place. Plays under your voice during "Someone reposted it on Instagram…"
- **Shot 2 (Cowork):** the file `edits/day_01/screen_clip.mp4` is already in place — clipped 0:02–0:12 from your raw recording, sped up 1.5×. Plays under "Step one wasn't recording…"
- **Shot 3 (cards):** the file `edits/day_01/cards.mp4` is already in place — 4 cards × 1.0s = 4 sec total, Liberation Sans Bold, orange kicker numbers (matches Cowork submit-button color), warm cream-on-dark palette, hard cuts (no fades). Plays under your narration. Drop a custom font at `fonts/main-bold.ttf` to override.

**Take strategy.** Shoot the selfie monologue 3–5 times back-to-back, no reviewing between takes. Save them per `CONVENTIONS.md`:

```
raw/day_01/selfie_take_01.mov
raw/day_01/selfie_take_02.mov
raw/day_01/selfie_take_03.mov
```

Pipeline picks the best selfie automatically once hook detection lands on Day 11. For Day 1, you pick.

---

## What ships at the end of Day 1

The plugin at `plugins/day-01-series-planner/` — installable via:

```
/plugin marketplace add andrewjiang/andrewislearning
/plugin install day-01-series-planner@andrewislearning
```

Anyone can use it to plan their own daily content series with Claude. The CTA in the video drives DMs that hand them this exact install command + a one-line "drop this into Claude Code" instruction (presented as a "free guide" for the entrepreneur audience).

---

## Iteration log

### v3.1 → v3.2 patch (current)

- **Viral-video b-roll on the cold open.** The IG repost (`broll_take_01.mp4`) cuts in during "Someone reposted it on Instagram… two thousand comments." Converts the credential from a *claim* into a *receipt*.
- **Thesis bridge inserted (Option B).** "I got out-edited" → *"So instead of becoming an editor, I'm gonna teach an AI to be one."* → rules. Surfaces the contrarian move that's the show's actual thesis. Drops the redundant "They're getting more out of my content than I am" line (the b-roll already proved it).
- **Cowork shot rebuilt.** New b-roll `edits/day_01/screen_clip.mp4` (clipped 0:02–0:12 from raw, sped up 1.5×, ~6.7s). Replaces the placeholder. Native vertical (1348×2140), shows "AI Content Series" project + the planning prompt being typed.
- **"Day 1, no edits yet" replaced.** Too clever. Now: *"Step one wasn't recording. It was opening Claude. I asked it to plan the whole thirty days."* — concrete, sequential, no inside-baseball.
- **Cards: 3 → 4, narrated, no wordmark.** *"Build. Polish. Automate. Every day."* The fourth card breaks the phase reading and surfaces the daily-compounding thesis. Narrated 1:1 with the visual (1.0s per card). Liberation Sans Bold; warm cream-on-dark palette (Cowork-orange kicker); hard cuts.
- **CTA: "free plugin" → "free guide", "comment" → "follow and comment".** Accessible framing for the entrepreneur audience; the "follow" is part of the value transaction (algo-safe).

### v3 → v3.1 patch

- **Cards generated by ffmpeg, not CapCut.** `pipeline/cards.py` introduced. Reason: hand-rolling in CapCut violates the "every edit through an AI agent" rule on episode one.

### v2 → v3 changes

See [`versions/01-script.v3.md`](versions/01-script.v3.md) for v3 → why-it-was-replaced notes.

### Open questions for shoot day

- Test all three alternates for the ownership beat; pick in edit.
- ManyChat: confirm `DAY1` keyword routes to the right auto-DM (containing install lines + brief explainer) before posting.
- Practice the opener line until it sounds matter-of-fact, not announcerly.
- Decide whether to include the optional "Tomorrow we build the pipeline" tail (~2 more sec).
