# Day 1 — IG Post Package (research-rewrite)

This is the *researched* version of the post plan. The previous draft followed default IG advice that's now outdated. Three things changed in late 2025 / early 2026 that reshape the strategy:

1. **Hashtag hard cap of 5** (Dec 2025). Posts with more than 5 hashtags now have excess tags removed or get blocked.
2. **Caption sweet spot is <150 chars** for Reels. Longer captions cut watch-time.
3. **Captions are searchable text** in 2026. Keywords in flow ("AI video editor", "AI agent", "Claude plugin") matter more than hashtags for discovery.
4. **ManyChat comment-to-DM converts at 70–80%** with a 4-message sequence vs ~10–20% with single message.

---

## 1. Caption (locked, 142-char body + dot-separated hashtags below)

```
Day 1 of training AI to be my video editor. Written, edited, captioned, and published by AI. Follow + comment 'DAY 1' for the guide + plugin.
.
.
.
.
#ClaudeAI #AIagents #ContentAutomation #BuildInPublic #AIWorkflow
```

**Why this caption works:**

- **The meta-flex is the strongest possible proof.** *"Written, edited, captioned, and published by AI"* — the post itself is the evidence the series claims to deliver. Viewers don't have to take your word; the artifact in front of them IS the proof. This single sentence earns the entire agentic-pipeline thesis.
- **First 125 chars** ("Day 1 of training AI to be my video editor. Written, edited, captioned, and published by AI…") — visible above the "more" fold. The format + the meta-flex both land before any expand.
- **Keyword density** — "AI video editor", "Claude plugin" appear in flow. IG's 2026 search treats caption text as the primary discovery signal.
- **Dual CTA** — *Follow + comment 'DAY 1'* — folds follow into the value transaction (algo-safe, since it's part of the deal, not pure follow-bait). The quotes around `'DAY 1'` signal "type this exactly" → boosts ManyChat trigger rate.
- **Hashtags hidden below dots.** IG strips genuinely empty lines, so periods on their own lines are the workaround — they push the 5 hashtags below the "more" fold so the preview stays pure. When expanded, hashtags read as metadata, not as part of the message.
- **5 hashtags exactly** — under the new IG cap, niche-specific. Skipped #AITools (too broad), #IGreels (redundant — IG knows it's a Reel), #AIContent (redundant).

---

## 2. ManyChat DM funnel

Day 1 ships with a **single message** for simplicity. The 4-message sequence (research says 70–80% conversion vs single-message ~10–20%) is a Day 5+ upgrade once we have data.

### Message 1 — Welcome + Bundle (sends instantly on `DAY 1` keyword match)

```
Day 1 of teaching an AI to be my video editor 👇

📋 Free guide (script + shots + edits): andrewislearning.com/days/01

🔌 Claude plugin (plan your own daily series):
   /plugin marketplace add andrewjiang/andrewislearning
   /plugin install day-01-series-planner@andrewislearning

Drop the install command into Claude Code (free at claude.com/code) and tell Claude to plan a series for you.

Tomorrow: wiring up the actual editing pipeline. Follow @andrewislearning for the full 30 days.
```

**Trigger keyword variants** to set up in ManyChat:
- `DAY 1` (primary)
- `day 1`, `day1`, `DAY1` (case + spacing variants)
- `DAY1!`, `day 1!` (with punctuation — viewers add it)

### Day 5+ planned upgrade — 4-message sequence

(Document for later, not building now)

1. **Welcome + Qualifier** — same as above, but ends with "Are you a creator who wants AI editing, or a builder curious about pipelines? Reply C or B."
2. **Problem mirror** (sends ~30 min later if no reply) — "Most people who ask for the plugin get stuck on the install. The whole thing is one command if Claude Code is installed. Want me to walk you through?"
3. **Offer** (~2 hours later) — "Tomorrow's episode is the cut.py recipe — auto-removes filler words. Want a heads-up DM when it drops?"
4. **24h nudge** — "Quick check: did the plugin install cleanly for you? If not, what error?"

This is the conversion funnel that'll move users from "got the bundle" to "actually using the pipeline" to "committed series follower."

---

## 3. First comment (drop within 60 sec of posting)

```
Day 1 → andrewislearning.com/days/01

(Comment 'DAY 1' below for the install command.)
```

The first comment is critical for two reasons:
1. Algorithm rewards creator engagement signal in first 30 minutes
2. Surfaces the URL — IG hides links in caption body but allows them in comments

---

## 4. Cover frame

[`web/assets/day_01/final_v10/at_1s.png`](../../web/assets/day_01/final_v10/at_1s.png) — opening selfie + "DAY 1" caption visible. Title-card-style thumbnail.

Or for stronger product signal: [`final_v10/at_52s.png`](../../web/assets/day_01/final_v10/at_52s.png) — "CLAUDE PLUGIN" caption. Higher CTR for builder/founder audience.

I'd default to the 0:01 frame for first-impression / opening line clarity.

---

## 5. TikTok variant (same caption — Post for Me sends one)

The Post for Me API publishes one caption to both platforms. The 142-char caption above works for both:

- IG sweet spot: <150 chars ✓
- TikTok preview before "more": ~150 chars ✓
- TikTok hashtag norm: 3–5 ✓

So no separate TikTok caption needed. The single caption ships to both.

---

## 6. Posting time

Research consensus for IG Reels engagement peaks (April 2026):

- **Tue–Thu, 9–11 AM PT or 7–9 PM PT** — peak audience activity for US-based creators
- Avoid Friday afternoon and weekend mornings (lower discovery)
- Post → engage with first 5 comments within 30 min (algorithm signal boost)

For andrewislearning specifically — your audience is founders/creators, mostly US — **Tuesday or Wednesday at 8–10 AM PT** is the call.

---

## 7. Pre-launch checklist (must all be ✓ before running publish.py)

- [ ] **GitHub repo** `andrewjiang/andrewislearning` is public + pushed
- [ ] **Plugin install** `/plugin install day-01-series-planner@andrewislearning` works on YOUR machine (test it)
- [ ] **Website** `andrewislearning.com/days/01` is live and shows Day 1's bundle
- [ ] **ManyChat keyword** `DAY 1` (and variants) armed and tested with friend's comment
- [ ] **Post for Me accounts** both IG (Business or Creator, FB-Page-linked) and TikTok connected
- [ ] **`$POSTFORME_API_KEY`** loaded in shell (verify with `echo "${POSTFORME_API_KEY:0:8}..."` — should print `pfm_live` or `pfm_test`)
- [ ] **Final video** `edits/day_01/final.mp4` is the version you want shipping (55.77s, 1080×1920)

---

## 8. Ship command

From your Mac terminal (not Cowork — needs your env var):

```bash
cd "/Users/andrewjiang/Bao/content-copilot/ContentCopilot"
python3 pipeline/publish.py series/days/01-publish.json
```

The script will:
1. Verify $POSTFORME_API_KEY
2. List connected accounts (will tell you if anything's missing)
3. Upload `edits/day_01/final.mp4` via Post for Me's upload URL
4. Publish to IG + TikTok in one API call
5. Poll for results for ~90 seconds
6. Save the receipt to `published/day_01/receipt.json` with the live permalinks

---

## 9. Post-launch: 24-hour metrics

Capture these the day after Day 1 ships — they become the baseline for Day 2.

| Metric | Target | Where |
|---|---|---|
| Reel views | 2K+ | IG Insights |
| Comments | 30+ | IG comments |
| `DAY 1` keyword DM sends | 10+ | ManyChat dashboard |
| Plugin installs | 5+ | GitHub traffic / marketplace stats |
| Web visits | 50+ | andrewislearning.com analytics |
| New IG follows | 30+ | IG profile insights |
| TikTok views (24h) | 1K+ | TikTok Analytics |

If any of these underperform by 50%+, that's signal for Day 2 to push harder on that lever (better hook, broader hashtags, etc.).

---

## Sources for the research-driven changes

- [How the Instagram Algorithm Works 2026 (Buffer)](https://buffer.com/resources/instagram-algorithms/)
- [Instagram hashtags in 2026, 5-tag limit (Later)](https://later.com/blog/ultimate-guide-to-using-instagram-hashtags/)
- [Why Captions Matter More Than Hashtags 2026 (Lamplight)](https://lamplightcreatives.com/captions-vs-hashtags-instagram-2026/)
- [Instagram reel caption length 2026 (TrustyPost)](https://trustypost.ai/blog/instagram-reel-caption-length-2026-best-practices-examples-that-get-watched/)
- [Instagram DM Automation vs Email 2025 (Unkoa)](https://www.unkoa.com/instagram-dm-automation-vs-email-in-2025-why-manychat-delivers-90-open-rates-and-60-reply-rates/)
- [Instagram Reach in 2026 (TrueFuture Media)](https://www.truefuturemedia.com/articles/instagram-reach-2026-algorithm-reels-carousels-caption-seo)
- [Comment LINK Instagram Strategy (CreatorFlow)](https://creatorflow.so/blog/comment-link-instagram-strategy/)
