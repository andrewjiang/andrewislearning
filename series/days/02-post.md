# Day 2 — IG Post Package

## 1. Caption

```
Day 2 of training AI to be my video editor. I built a review agent that watches before posting. Follow + comment 'REVIEW' for the guide + plugin.
.
.
.
.
#ClaudeAI #AIagents #ContentAutomation #BuildInPublic #AIWorkflow
```

## 2. ManyChat DM Funnel

Trigger keyword variants:
- `REVIEW`
- `review`
- `Review`
- `REVIEW!`

Message:

```
Day 2 of teaching an AI to be my video editor 👇

Today’s plugin is the video review agent: it samples frames, checks captions, checks audio, and gives the edit a scorecard before publishing.

📋 Guide + script: andrewislearning.com/days/02

🔌 Claude plugin:
   /plugin marketplace add andrewjiang/andrewislearning
   /plugin install day-02-video-review@andrewislearning

Tomorrow: making the editor faster and more automatic. Follow @andrewislearning for the full 30 days.
```

## 3. First Comment

```
Day 2 → andrewislearning.com/days/02

(Comment 'REVIEW' below for the review-agent guide + plugin.)
```

## 4. Cover Frame

`.context/reel_cover_custom/day_02_claude_day_two_cover.png`

Claude prompt filled in, with the overhead DAY TWO title treatment.

## 5. Ship Command

```bash
python3 pipeline/publish.py series/days/02-publish-instagram.json
```

Published Instagram Reel: https://www.instagram.com/reel/DXx0j_njUPu/

TikTok was skipped at publish time because the TikTok account was not connected in Post For Me.
