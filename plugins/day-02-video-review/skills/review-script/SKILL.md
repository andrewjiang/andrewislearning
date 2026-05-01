---
name: review-script
description: Review a short-form video script (Instagram Reel, TikTok, YouTube Short) against a research-backed rubric. Use when the user has a draft script and wants structured feedback before recording — checks the hook, length, three-act structure, recap discipline, CTA, captions plan, pacing, specificity, and resolves open loops. Triggers on phrases like "review my script", "check this script", "is this Reel script good", "rubric for short-form".
---

# Script Review

You apply a research-backed rubric to a short-form video script and produce
**actionable, specific feedback** — not a vague vibe check.

## When to trigger

- "Review this script"
- "Check my Reel / TikTok / Short script"
- "Is this hook strong enough?"
- "How long should this run?"
- "Workshop my Day N script"

If the user has a script in their working files (e.g.,
`series/days/NN-script.md`), default to reviewing that. Otherwise, ask
for the script as text.

## Step 1 — Read the rubric

Read `references/SHORT_FORM_REELS.md` in this skill's directory. That
file is the source of truth for what counts as good. Do **not** invent
rules from memory — every claim in your review should trace to a
specific rubric section.

## Step 2 — Mechanical metrics first

Before opinions, measure:

1. **Word count.** Count spoken words (not shot directions, not
   captions, not parenthetical notes). Multiply by 0.34 to estimate
   pre-speedup duration in seconds (typical conversational pace ≈ 2.9
   words/sec). Multiply by 0.31 for post-1.08×-speedup duration.
2. **Hook word count.** Count the words spoken in the first 3 seconds
   of the script (≈ first 8–10 words). Verify these are scripted, not
   filler.
3. **Recap length.** If the script has a recap section, measure how
   many seconds it occupies and where it lands.
4. **Shot count and average shot length.** Count distinct shots from
   the shot list; divide total target length by shot count.
5. **CTA presence and shape.** Does the script have exactly one CTA?
   Is it keyword-based? Is the keyword short and specific?

Surface these as a small table at the top of your review.

## Step 3 — Apply the rubric checklist

Go through the 10-item checklist in `references/SHORT_FORM_REELS.md §8`.
For each item, decide: pass / improvement / blocker, and write one
sentence of diagnosis.

## Step 4 — Findings

Output each finding in this shape:

```
### [SEVERITY] Shot or timestamp · Short title

Diagnosis: one sentence.

Fix: the proposed concrete change — a rewritten line, a cut, a move,
or a config tweak. Make it copy-pasteable; don't write "consider
making this stronger."
```

Severities:
- **BLOCKER** — would meaningfully hurt retention or the post's primary
  goal. Must fix.
- **IMPROVEMENT** — measurable upside if changed. Should fix.
- **NIT** — minor polish. Optional.

## Step 5 — Summary line

Close the review with a single line judgment:

> Verdict: ship as-is / one round of fixes / structural rewrite needed.

## Step 6 — Save

Write the review to `series/days/NN-script-review.md` (or the
appropriate per-day path), so the user has a durable record they can
diff against future revisions.

## What this skill does NOT do

- It does not rewrite the entire script. It surfaces findings and
  proposes specific edits; the human keeps creative control.
- It does not check video files. For that, use the sibling
  `review-video` skill in this same plugin.
- It does not invent best-practice rules. Every claim cites a section
  of `SHORT_FORM_REELS.md`.

## Tone

Direct, specific, kind. Skip hedging language ("you might want to
consider…"). Lead with the rule that's at stake, then the diagnosis,
then the fix. Treat the writer as a capable adult who wants real
feedback, not encouragement.
