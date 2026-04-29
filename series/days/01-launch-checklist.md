# Day 1 — Launch Checklist

> Open this on launch morning (Wed Apr 29, 8 AM PT). Walk top-to-bottom. Every box must be ✓ before running `pipeline/publish.py`. After publish, follow the post-launch sequence.

**Target launch:** Wednesday, April 29, 2026 · 8:00 AM PT
**Cadence locked:** 8 AM PT daily for Days 2–30

---

## T-12 hours (Tuesday evening)

These take the longest and are the most likely to fail. Do them tonight.

### Infrastructure

- [ ] **GitHub repo public** — go to https://github.com/andrewjiang/andrewislearning · confirm "Public" badge
- [ ] **Repo pushed clean** — `git status` returns "nothing to commit, working tree clean"
- [ ] **Marketplace JSON valid** — `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"` returns no error
- [ ] **Plugin manifest valid** — `python3 -c "import json; json.load(open('plugins/day-01-series-planner/.claude-plugin/plugin.json'))"`
- [ ] **Plugin installs end-to-end on YOUR machine** — `/plugin marketplace add andrewjiang/andrewislearning` then `/plugin install day-01-series-planner@andrewislearning`. Activate Claude Code, type "plan a 30 day series for me," confirm the skill triggers.

### Website

- [ ] **andrewislearning.com domain points to your hosting** (Vercel/Netlify/CDN) — `dig andrewislearning.com` returns the right IP
- [ ] **Index page live** — visit https://andrewislearning.com — see the white-page-with-folders home
- [ ] **Day 1 page live** — visit https://andrewislearning.com/days/01 — confirms the guide content renders
- [ ] **Day 1 page video embed plays** — embed must work on mobile (where most DM clicks land)
- [ ] **Install command on the page is copy-able** — the dark code block with the two `/plugin` lines

### ManyChat (the auto-DM funnel)

- [ ] **ManyChat IG account connected** — your `@andrewislearning` IG is auth'd
- [ ] **Keyword routing active** for `DAY 1` — the automation is set to "Active" not "Paused"
- [ ] **Keyword variants armed**: `DAY 1`, `day 1`, `DAY1`, `day1` (people will type all four)
- [ ] **DM body matches** the message in [`01-post.md`](01-post.md) §2
- [ ] **Test fired with friend's comment** — post a placeholder somewhere, have a friend leave the DAY 1 comment, confirm the DM arrives within 60 sec
- [ ] **DM links work** — friend confirms the andrewislearning.com URL and `/plugin install` command in the DM are valid (URL loads, install instructions readable)

### Post for Me / Publishing

- [ ] **`$POSTFORME_API_KEY` loaded** — `echo "${POSTFORME_API_KEY:0:8}..."` prints `pfm_live` or `pfm_test`
- [ ] **IG account connected** — `curl -s https://api.postforme.dev/v1/social-accounts -H "Authorization: Bearer $POSTFORME_API_KEY" | jq '.data[] | select(.platform == "instagram")'` returns your account
- [ ] **TikTok account connected** — same query for TikTok
- [ ] **IG account is Business or Creator** linked to a Facebook Page (Personal IGs cannot publish via API)
- [ ] **Test publish to a draft** OR a private test account — verify upload + publish flow works end-to-end with a placeholder video before using the real one

### Final video

- [ ] **`edits/day_01/final.mp4` is the version you want shipping** — watch it once on your phone with sound on. If anything looks/sounds off, do NOT push.
- [ ] **Specs check** — 1080×1920, h264 + aac, ≤90 seconds, ≤500 MB. Verify with `ffprobe edits/day_01/final.mp4`.
- [ ] **Captions readable** — text doesn't get cut off, salmon emphasis pops, no typos in burned-in text
- [ ] **First frame works as cover** — when you scrub to t=0, what you see is presentable as a thumbnail

---

## T-30 minutes (Wed 7:30 AM PT)

Final pre-flight on launch morning.

- [ ] **Coffee ☕** — you'll be replying to comments for the next 30 min
- [ ] **Re-check `$POSTFORME_API_KEY`** is in env in this shell session
- [ ] **`cd "/Users/andrewjiang/Bao/content-copilot/ContentCopilot"`**
- [ ] **`git pull`** if you've been editing on another machine — make sure local matches the public repo
- [ ] **Open IG app on phone** — be ready to engage with comments immediately

---

## T-0 — Launch (Wed 8:00 AM PT)

### Step 1 — Publish via API

```bash
cd "/Users/andrewjiang/Bao/content-copilot/ContentCopilot"
python3 pipeline/publish.py series/days/01-publish.json
```

Watch the output. Expected:

```
[publish] checking connected accounts...
[publish]   instagram: andrewislearning  (sa_xxx)
[publish]   tiktok:    andrewislearning  (sa_yyy)
[publish] PUT final.mp4 (X.X MB)...
[publish] uploaded → https://...
[publish] publishing to instagram, tiktok...
[publish] post_id: pst_xxx
[publish]   instagram: published  https://www.instagram.com/reel/...
[publish]   tiktok:    published  https://www.tiktok.com/@.../...
[publish] wrote receipt → published/day_01/receipt.json
```

If anything errors, jump to **Emergency aborts** below.

### Step 2 — First comment (within 60 sec of post going live)

Open the IG post on your phone. Drop this as the first comment:

```
Day 1 → andrewislearning.com/days/01

(Comment 'DAY 1' below for the install command.)
```

Why immediately: algorithm rewards creator activity in the first 30 minutes. Plus it surfaces the URL since IG hides links in caption body.

### Step 3 — Engage 8:00–8:30 AM PT

- Reply to first 5 comments within 30 minutes (algo signal boost)
- Like every comment as it lands
- DM-fire spot-check: when a real viewer comments DAY 1, confirm the auto-DM lands within 60 sec
- Post a 24-hour story with "Day 1 is live" + sticker → swipe up link

### Step 4 — Verify ManyChat is firing on real comments

- Open ManyChat dashboard
- Watch the "Recent activity" feed — you should see DM sends piling up
- If after 10 minutes there are comments but zero DM sends, the keyword routing broke — pause, debug, re-enable

---

## T+12 hours / 8 PM PT

- [ ] **Capture half-day metrics** — views, comments, DM sends, plugin installs (GitHub traffic)
- [ ] **Reply to all comments** that came in during the day
- [ ] **Plan Day 2 hook** based on what worked — was it the meta-flex? the salmon CLAUDE PLUGIN? the agentic b-roll? Day 2 should lean into whatever popped.

---

## T+24 hours (Thu 8 AM PT)

Capture the metrics that become Day 2's baseline:

| Metric | Target | Where |
|---|---|---|
| Reel views | 2K+ | IG Insights |
| Comments | 30+ | IG comments |
| `DAY 1` keyword DMs | 10+ | ManyChat dashboard |
| Plugin installs | 5+ | `gh api /repos/andrewjiang/andrewislearning/traffic/clones` |
| Web visits | 50+ | andrewislearning.com analytics |
| New IG follows | 30+ | IG profile insights |
| TikTok views | 1K+ | TikTok Analytics |

Save these to [`series/days/01.md`](01.md) under "post-launch metrics" so Day 2 has a comparison anchor.

---

## Emergency aborts

### If `publish.py` fails with `Instagram account is not Business/Creator`

Convert IG → Professional in the IG app: Settings → Account → Switch to Professional → link a Facebook Page. Re-run.

### If `publish.py` fails with `media url not accessible`

Probably a transient Post for Me upload issue. Re-run `publish.py` — it'll re-upload.

### If TikTok 403s with `unaudited_client`

Project is in Quickstart audit-pending mode. Either:
- Wait for audit (~24h), OR
- Edit `01-publish.json` to drop `tiktok` from `platforms` array, ship to IG only, queue TikTok for manual upload

### If the post goes live but the DM never fires

ManyChat keyword routing broke. Open ManyChat → Automation → confirm the rule is Active. Test with a fresh comment from a friend's account. If still broken, manually DM the first 10 commenters with the install link until ManyChat is fixed.

### If something looks visibly wrong in the live post

Don't panic-delete. Two options:
1. **If it's small** (typo in caption, etc.) — IG lets you edit captions. Edit, don't delete.
2. **If the video itself is broken** — delete the IG post (NOT the TikTok), re-encode, re-publish via `publish.py`. Reset the day's metrics and note the timeline shift in `01.md`.

---

## Sign-off

When you're back at your desk Thursday morning, fill this in and you're done with Day 1:

| Field | Value |
|---|---|
| Posted at | __:__ AM PT |
| IG Reel URL | https://www.instagram.com/reel/______ |
| TikTok URL | https://www.tiktok.com/@andrewislearning/______ |
| 24h views | _____ |
| 24h comments | _____ |
| 24h DM sends | _____ |
| 24h follows | _____ |
| Notes for Day 2 | _________________________________ |

Day 1 shipped. 30 to go.
