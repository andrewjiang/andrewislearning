# Day 1 — Series Planner

The Day 1 plugin from [@andrewislearning](https://andrewislearning.com) — a 30-day series on automating content creation with AI.

## What it does

Installs a `series-planner` skill that helps you plan a daily content series with Claude. You describe the topic, rules, audience, and inciting incident; it produces a 30-day arc, a Day 1 script, and a tool rollout plan.

## Install

```
/plugin marketplace add andrewjiang/andrewislearning
/plugin install day-01-series-planner@andrewislearning
```

## Use

In any Claude Code session, just say:

> Help me plan a 30-day series about [your topic].

The skill activates, asks the right questions, and produces three files in your project: `SERIES_PLAN.md`, `DAY_01_SCRIPT.md`, and `TOOLS.md`.

## What it's based on

This is the actual skill used to plan @andrewislearning's own series. The reasoning behind the questions, the arc structure, and the script template comes from the planning session that opens the series. You can watch that on [Day 1](https://andrewislearning.com/days/01).

## License

MIT.
