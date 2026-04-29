# Day 1 — Vercel Deploy Guide

One-time setup, then `python pipeline/deploy.py NN` per day.

---

## One-time setup (do once, never again)

### 1. Install Vercel CLI

```bash
npm i -g vercel
```

(Or use `pnpm i -g vercel` / `bun i -g vercel` — same outcome.)

### 2. Link the repo to a Vercel project

```bash
cd "/Users/andrewjiang/Bao/content-copilot/ContentCopilot"
vercel link
```

It'll ask:
- **Set up and deploy?** → Y
- **Which scope?** → your personal account (or org)
- **Link to existing project?** → N (this is a new one)
- **Project name?** → `andrewislearning` (this becomes part of the preview URL)
- **In which directory is your code?** → `./` (root — `vercel.json` already says `outputDirectory: web`)
- **Override settings?** → N

This creates `.vercel/` in the repo (already gitignored by Vercel CLI). You're now linked.

### 3. First deploy — confirm it works

```bash
vercel --prod
```

Should output a deploy URL like `https://andrewislearning-xyz.vercel.app`. Visit it; verify:
- Index page renders (white-page-with-folders)
- `/days/01` renders (Day 1 guide)
- The video at `/cdn/day_01/final.mp4` plays
- Cover image loads at `/cdn/day_01/cover.jpg`

### 4. Add the custom domain

In Vercel dashboard → your project → Settings → Domains → Add `andrewislearning.com`.

Vercel gives you DNS records (an A record for `@` and a CNAME for `www`). Update your domain registrar's DNS settings:
- A record: `@` → `76.76.21.21`
- CNAME: `www` → `cname.vercel-dns.com`

Propagation: 5 min – 24 hours. Verify with `dig andrewislearning.com` until it returns Vercel's IP.

### 5. Enable HTTPS

Automatic — Vercel provisions a Let's Encrypt cert as soon as DNS resolves. No action needed.

---

## Daily deploy (every shipping day)

After `pipeline/finish.py` produces `edits/day_NN/final.mp4`:

```bash
python pipeline/deploy.py 01
```

This script:
1. Copies `edits/day_01/final.mp4` → `web/cdn/day_01/final.mp4`
2. Extracts `cover.jpg` from t=0.5s
3. Runs `vercel --prod` to push the new assets live

In ~30 seconds the new video is on andrewislearning.com.

**Skip the deploy step** (just stage assets, deploy manually):

```bash
python pipeline/deploy.py 01 --no-vercel
```

**Custom cover frame:**

```bash
python pipeline/deploy.py 01 --cover-at 22  # frame at 22 seconds (e.g. the AI AGENT caption)
```

---

## What's deployed

```
web/
├── index.html              # the white-page-with-folders home
├── days/
│   └── 01.html             # Day 1 guide (with video embed + plugin install)
└── cdn/
    └── day_01/
        ├── final.mp4       # 12.5 MB, 55.77s, 1080×1920
        └── cover.jpg       # 143 KB, frame from t=0.5s
```

`vercel.json` at the repo root tells Vercel:
- `outputDirectory: web` — that's the static site root
- `cleanUrls: true` — `/days/01` resolves to `/days/01.html`
- Long-lived cache headers on `/cdn/*` (immutable assets, 1 year cache)
- Standard cache + stale-while-revalidate on HTML

---

## After Day 1 ships

The site grows organically: each day adds one entry. Day 2 needs:

1. `web/days/02.html` — the Day 2 guide (use Day 1 as template)
2. Update `web/index.html` — add a second folder card pointing to `/days/02`
3. Run `python pipeline/deploy.py 02` to stage assets + deploy

Eventually we automate the index page itself (Day 22-ish — the watch-folder episode would auto-generate `index.html` from the day pages that exist). For now, manual edits per day.

---

## Troubleshooting

### `vercel: command not found`

Vercel CLI isn't installed or your shell doesn't see it. `which vercel` should return something like `/usr/local/bin/vercel`. If empty, re-install: `npm i -g vercel`.

### Deploy succeeds but video 404s

Check `web/cdn/day_01/final.mp4` actually exists in your local checkout. Vercel only deploys what's in the directory — empty paths → 404.

### Custom domain not resolving

DNS propagation is the usual culprit. Check `dig andrewislearning.com`; until it returns `76.76.21.21`, Vercel can't serve from that domain.

### Video plays choppy on mobile

Vercel's edge cache should serve smoothly. If choppy, the source MP4 might have a high bitrate. Re-encode with: `ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -maxrate 2.5M -bufsize 4M -c:a aac -b:a 128k output.mp4`. 2 Mbps video is plenty for 1080×1920 60-sec content.

### Hit Vercel free tier bandwidth (100 GB/month)

If/when you exceed, move `/cdn/*` to Cloudflare R2 ($0.015/GB) or Bunny.net ($0.005/GB). Update `web/days/01.html` `<source>` paths to point at the CDN. Day 22-ish concern.
