# Day 1 — Shoot Plan

> **Open this on shoot day.** Self-contained operational guide: setup, script, shots, media, takes, edit, post. Everything for filming, editing, and shipping Day 1.
>
> Sister docs: [`01.md`](01.md) (hub/lineage tracker) · [`01-script.md`](01-script.md) (script with iteration history) · [`01-brainstorm.md`](01-brainstorm.md) (the planning conversation).

```
═════════════════════════════════════════════
  Day 1 of teaching an AI to be my video editor
─────────────────────────────────────────────
  Runtime:    ~49 sec
  Aspect:     9:16 vertical (1080×1920)
  Primary:    Instagram Reels
  Cross:      TikTok
  CTA:        Comment 'DAY1' → DM
  Plugin:     day-01-series-planner
  Status:     ready to shoot
═════════════════════════════════════════════
```

---

## 1. Pre-shoot setup

Run this checklist before you pick up the phone. Everything below is independent of takes — set it up once.

### Phone (selfie shots)

- [ ] iPhone, vertical orientation, **default camera app** in Video mode
- [ ] Resolution: 1080p or 4K @ 30fps (4K is fine; we crop to 1080 in pipeline)
- [ ] Phone propped at **eye level** (book stack works; tripod better). Camera ~18 inches from your face.
- [ ] Tap-to-focus on your face, then **lock AE/AF** (long-press the focus point until "AE/AF Lock" appears) so the exposure doesn't drift between takes
- [ ] Airplane mode + Do Not Disturb so notifications don't appear

### Lighting

- [ ] Natural window light **in front of you**, not behind. Window between 10am and 3pm is ideal.
- [ ] No overhead light directly above (creates raccoon eyes)
- [ ] Background has some depth — not a flat white wall right behind your head. A few feet of distance to anything textured works.

### Audio

- [ ] **Don't use AirPods.** Phone mic is fine and matches the raw aesthetic.
- [ ] Quiet room. Close windows, AC off if possible. Listen for fridge hum, fan, traffic.
- [ ] Don't move the phone while talking — handling noise will show up in the audio.

### Screen recording (Shot 2)

- [ ] **Terminal**: full-screen, dark theme, font size **≥ 20pt**. Test by sending `printf '\e[8;30;100t'` if you want a known-good window size.
- [ ] **Editor** (VS Code / Cursor / Zed): `series/SERIES_PLAN.md` open at the top, dark theme, font size **≥ 18pt**, word wrap on
- [ ] Hide your dock and menu bar if you can (auto-hide both)
- [ ] Close every other app + tab. The shot needs to be clean.
- [ ] Test `Cmd+Shift+5` once to make sure it launches and saves to a known location

### Environment / infrastructure

- [ ] Domain `andrewislearning.com` registered ✓ (you confirmed)
- [ ] GitHub repo `andrewjiang/andrewislearning` created and **pushed** (`/plugin marketplace add` won't work otherwise)
- [ ] ManyChat configured: keyword `DAY1` → auto-DM with the install snippet + one-line "drop this into Claude Code" explainer
- [ ] Test the install command on your own machine first. If it fails, the launch fails.

---

## 2. The script (v3, locked)

For full alternates, delivery notes, and version history, see [`01-script.md`](01-script.md). The script reproduced inline here so you don't have to switch tabs:

> **[SHOT 1 — selfie, phone, vertical]**
>
> "Day 1 of teaching an AI to be my video editor.
>
> My video on X got nearly a million views. Someone reposted it on Instagram, gave away my repo link, and got two thousand comments. They're getting more out of my content than I am.
>
> I just got out-edited on my own work — and that's on me.
>
> So I'm challenging myself: thirty days, every edit through an AI agent, every post through an AI agent. Just my phone and a laptop.
>
> **[SHOT 2 — laptop, Claude Code, SERIES_PLAN.md scrolling]**
>
> Day 1, no edits yet. I asked Claude to plan the whole series. Three phases.
>
> **[SHOT 3 — 3 cards, ~2s each]**
>
> Build it. Polish it. Automate it.
>
> **[SHOT 4 — back to selfie]**
>
> I packaged today into a free plugin. Comment 'DAY1' and I'll DM you everything. Tomorrow we build the pipeline."

### Lines that need extra attention

- **The opener.** *"Day 1 of teaching an AI to be my video editor."* Say it like a fact, not an announcement. No upspeak. This line repeats every episode for series identity — it has to feel natural now.
- **The credential.** *"My video on X got nearly a million views."* Sell with confidence. Not a humble-brag, not a flex, just a fact.
- **The ownership beat.** *"and that's on me."* This is the emotional flip. Shoot **all three alternates** below; pick best in edit.
  1. *"…and that's on me."* — sincere
  2. *"…and that's embarrassing."* — self-deprecating
  3. *"…so something's clearly broken with my setup."* — deflects to tools

---

## 3. Shot list

| # | Type | Source | What | Length | Status |
|---|------|--------|------|--------|--------|
| 1 | Selfie A-roll | Phone | Cold open + rules | ~30s | ⏳ to shoot |
| 2 | Screen recording | Laptop (`Cmd+Shift+5`) | Two-beat: live Claude + scroll | ~7s | ⏳ to shoot |
| 3 | Title cards | `pipeline/cards.py` | "Build it. Polish it. Automate it." | 6s | ✅ generated |
| 4 | Selfie A-roll | Phone | CTA + outro | ~6s | ⏳ to shoot (same setup as #1) |

### Shot 1 & 4 — Selfie

- Same setup, same lighting, same framing. Shoot 4 either as a separate take or tail-end of the main monologue.
- Frame: head + shoulders, eyes ~⅔ up the frame ("rule of thirds upper line"), some headroom but not a lot.
- Look directly at the lens. If using rear camera (better quality), tape a sticky note next to the lens so you know where to look.
- **Take 3–5 full takes back-to-back. Do not review between takes.** The next-take you remember the previous take is the worst version of the script. First takes are usually best because nerves are real but self-criticism hasn't kicked in.

### Shot 2 — Screen recording

Two beats, ~7 seconds total:

**Beat 1 (~3s) — live Claude.** Terminal foreground. In Claude Code, type:

> Plan a 30-day series for me on automating content creation with AI.

Hit return. Let Claude stream for ~3 seconds. The streaming text + appearing markdown headings IS the visual. Don't try to recreate this conversation exactly — Claude will produce something coherent, and the *act* of planning is the point.

**Beat 2 (~4s) — the rendered plan.** Cut to your editor with `series/SERIES_PLAN.md` open at the top. Two-finger trackpad scroll, smooth, until you reach the bottom of Week 1. Stop scrolling at the "Week 1 — The Bare Pipeline" section header so it sits visible at the end.

Save as `raw/day_01/screen_take_01.mp4`.

### Shot 3 — Cards (already generated)

- File: `edits/day_01/cards.mp4` (1080×1920, 6 sec, three cards × 2 sec, hard cuts)
- White DejaVu Sans Bold on black, centered
- Re-run anytime: `python3 pipeline/cards.py`

---

## 4. Media manifest

Everything that ends up in the final video.

| Asset | Where | Made by | Status |
|---|---|---|---|
| Selfie A-roll | `raw/day_01/selfie_take_NN.mov` | iPhone | ⏳ to shoot |
| Screen recording | `raw/day_01/screen_take_01.mp4` | macOS `Cmd+Shift+5` | ⏳ to record |
| Title cards | `edits/day_01/cards.mp4` | `pipeline/cards.py` | ✅ generated |
| (optional) static screenshots | `web/assets/day_01/*.png` | request from Claude | offered, not used by default |

**Optional inserts I can generate on request:**

- Screenshot of the `web/index.html` landing page (white, single folder card)
- Screenshot of the marketplace listing rendered in your editor
- Screenshot of the plugin's `SKILL.md`

These are **second-or-two static cuts** if you want extra texture. None are required to ship Day 1. Let me know which you want.

---

## 5. Take strategy

- **3–5 selfie takes back-to-back, no review between.** Rolling full 30-second monologue each time.
- **3 alternates of the ownership beat.** Either as separate clips or by re-recording just the second sentence three times. Tag them in your head as "on me / embarrassing / setup" so you can find them later.
- **Screen recording: 2 takes max.** It's not a performance.
- **Cards: already done.** No takes.

After all takes, you should have:

```
raw/day_01/selfie_take_01.mov   # full monologue, take 1
raw/day_01/selfie_take_02.mov   # full monologue, take 2
raw/day_01/selfie_take_03.mov   # full monologue, take 3
raw/day_01/selfie_take_04.mov   # (optional) ownership-beat alts as a separate clip
raw/day_01/screen_take_01.mp4   # screen rec, two beats
```

---

## 6. Post-shoot pipeline

In order. Run from the repo root.

### 6a. Drop files (per `CONVENTIONS.md`)

AirDrop selfie clips from phone → laptop → into `raw/day_01/`. Rename to the convention as you go (or batch rename after).

### 6b. Pick the best selfie take (manual, just for Day 1)

Day 11 is when hook detection lands. For Day 1, watch your takes once and pick the one where the opener felt most natural. Move on; don't agonize.

### 6c. Run the (stubbed) pipeline to produce a `.final.mp4`

```bash
python3 pipeline/edit.py raw/day_01/selfie_take_NN.mp4
```

Today this is mostly a passthrough — real cuts/captions/reformatting land Days 4–6. But running it confirms the plumbing for the day.

### 6d. Edit the assembly plan with your actual timestamps

The selfie should be one **continuous** take covering the whole 49-second script — including the parts where the final video will show b-roll instead of you. Speak the entire script through; the assembler swaps the *visual* during the b-roll windows but keeps your *audio* throughout.

Open [`series/days/01-assembly.json`](01-assembly.json). The two `at` values are estimates from the v3 script; you'll likely deliver slightly faster or slower than estimated. Watch your chosen selfie take, note when you start each b-roll moment, and edit:

```jsonc
{
  "base": "raw/day_01/selfie_take_NN.mp4",   // ← the take you picked
  "inserts": [
    {"at": 30.0, "duration": 7.0, "video": "raw/day_01/screen_take_01.mp4"},
    //         ↑ adjust to where you say "Day 1, no edits yet…"
    {"at": 37.0, "duration": 6.0, "video": "edits/day_01/cards.mp4"}
    //         ↑ adjust to where you say "Three phases."
  ],
  "output": "edits/day_01/final.mp4"
}
```

**Tip for finding timestamps fast.** macOS QuickTime → open the selfie clip → arrow keys advance frame-by-frame. The current time appears in the title bar. Note the second value where you naturally pause before "Day 1, no edits yet" — that's `at` for insert 1. The next pause before "Build it." is `at + duration` of insert 1, which gives you `at` for insert 2.

### 6e. Run the assembler — produces the final video

```bash
python3 pipeline/assemble.py series/days/01-assembly.json
```

Output: `edits/day_01/final.mp4` — 1080×1920, H.264, the right length, with selfie audio across the whole thing and the inserts replacing visuals at the timestamps you set.

> **Why this beats iMovie.** Every cut, every letterbox, every mux is described in JSON and executed by ffmpeg. The "edit" is reading the JSON; Claude could do that for you next time. **No timeline UI was opened.** This keeps Day 1 honest to the rule: every edit through an AI agent.

### 6f. Eyeball-check the output

Watch the final once before posting. What you're checking:
- Are the b-roll cuts at the right moments? If the screen recording starts a half-second before "Day 1, no edits yet…" → bump `at` of insert 1 by 0.5 and re-run.
- Is the audio continuous? (Should be — the assembler muxes the spine's audio over the whole timeline.)
- Are the inserts visible with sufficient contrast? If the screen recording is too dark, brighten it before re-running.

Re-running takes ~10 seconds; iterate until it's right.

### 6e. Save metadata

Update the lineage table in [`01.md`](01.md) — mark which selfie take you picked, which version of the ownership beat you used, final file path.

---

## 7. Posting checklist

- [ ] Final video is 1080×1920, < 60 sec, MP4, H.264
- [ ] Caption written. Suggested template:

  > Day 1 of teaching an AI to be my video editor.
  >
  > Got out-edited on my own content by a random account. Spending the next 30 days fixing it — every edit and every post through an AI agent. Phone + laptop only.
  >
  > Comment 'DAY1' and I'll DM you the plugin I built today. Plan your own 30-day series with Claude.

- [ ] Hashtags (don't overdo it — 5–8 max for IG): `#aitools #contentcreation #automation #buildinpublic #claudeai #aieditor #shorts #reels`
- [ ] **Test ManyChat once before posting** with a comment from a friend's account
- [ ] Post to IG Reels at the time your audience is on
- [ ] Cross-post to TikTok with the same caption (or trim — TikTok captions tend to be shorter)
- [ ] Update [`01.md`](01.md) with both URLs

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/plugin marketplace add` fails | Repo not pushed yet, or marketplace.json malformed | Push the repo. Verify with `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"` |
| Cards.mp4 plays but text is tiny | Font size in `pipeline/cards.py` is too small | Increase `FONT_SIZE` in cards.py and re-run |
| Screen recording is too dark to read | Editor / terminal theme is too low contrast | Switch to a high-contrast dark theme; bump font sizes |
| ManyChat doesn't send DM | Keyword case-sensitivity, or DM permission revoked | Test with a comment containing exactly `DAY1` (and lowercase `day1`); reauth ManyChat to your IG |
| Audio sounds boomy | Recorded too close, or in a hard-walled room | Move 6–12 inches further; add soft surfaces (rug, bedding) for retake |

---

## 9. After Day 1 ships

- [ ] Mark Day 1 status as `posted` in [`01.md`](01.md)
- [ ] Capture early metrics: comments, DM replies, follower delta — feed these to Day 2 hub
- [ ] Day 2 = wire up the actual pipeline (transcription + cut). Plugin: `day-02-capture-loop`. Drafting starts when Day 1 hits its first 50 comments.
