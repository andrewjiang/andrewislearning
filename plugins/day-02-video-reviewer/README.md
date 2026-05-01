# Day 2 — Video Reviewer

The Day 2 plugin from [@andrewislearning](https://andrewislearning.com) — a 30-day series on automating content creation with AI.

## What it does

Installs a `video-reviewer` skill that helps Claude review a previous short-form video, generate contact sheets and frame evidence, score what worked, and turn the findings into the next episode plan.

## Install

```
/plugin marketplace add andrewjiang/andrewislearning
/plugin install day-02-video-reviewer@andrewislearning
```

## Use

In any Claude Code session inside a video project, say:

> Review Day 1 and plan Day 2.

The skill builds a review pack from the previous day's exported video and writes a timestamped critique plus the next-day brief.

## What it's based on

This is the review loop added after Day 1 shipped: the pipeline does not stop at publishing. It watches the artifact, critiques the hook, captions, pacing, cover, and CTA, then feeds the next episode.

## License

MIT.
