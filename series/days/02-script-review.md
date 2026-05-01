# Day 2 — Script Review

Applied: `plugins/day-02-video-review/skills/review-script` rubric
(see `references/SHORT_FORM_REELS.md` for the source claims).

## Mechanical metrics

| Metric | Value | Target | Status |
|---|---|---|---|
| Spoken word count | 166 | — | — |
| Pre-speedup duration (est.) | 56s | 60s ±10 | ✓ |
| Post-1.08×-speedup (est.) | 52s | 45–60s | ✓ |
| Hook word count (first 3s) | ~9 (split by graphic) | scripted, ≤ 10 | ⚠ verbal weak |
| Recap section | 6s @ 0:08–0:14 | ≤ 6s | ✓ at limit |
| Shot count | 10 | — | — |
| Avg shot length | 5.8s | < 6s | ✓ |
| Longest shot | 8s (SHOTS 7, 9) | < 8s | ✓ at limit |
| CTAs | 1 (`REVIEW`) | exactly 1 | ✓ |
| CTA shape | comment-keyword | comment-keyword | ✓ |
| Open loops set up | 2 | ≥ 1 | ✓ |
| Open loops resolved | 2/2 | 100% | ✓ |

## Findings

### [IMPROVEMENT] SHOT 1 + 2 · Verbal hook is weaker than the visual hook

**Diagnosis:** The first 3 seconds rely entirely on the Remotion graphic
to do hook work. The audio in SHOTS 1–2 is *"Day 2 of teaching AI to be
my video editor. Day one almost didn't happen."* — but the open loop
("almost didn't happen") doesn't arrive until ~5 seconds in. Per
SHORT_FORM_REELS §1, storytelling hooks landing inside the first 3s are
72% more likely to go viral; up to 50% of viewers drop off in those
3 seconds.

**Fix:** Merge SHOTS 1 and 2 into a single 5-second cold open with the
open loop arriving inside the first 4 seconds:

> *[Calm]* "Day 2…"
> *[BAM — graphic + flinch]*
> "…of teaching AI to be my video editor. **And day one almost didn't happen.**"

Same pieces, repacked so the graphic punches in on "Day 2" and the
disaster setup lands at ~3.5s instead of ~5s. The flinch becomes a beat
*inside* the hook rather than a separator between two beats.

---

### [IMPROVEMENT] SHOT 3 · Recap could be more specific

**Diagnosis:** *"My X video went viral"* and *"got thousands of
comments"* are vaguer than the Day 1 page's versions ("nearly a million
views", "nearly two thousand comments"). Per §7, specificity is
correlated with retention and shares, and the costs are ~2 extra words.

**Fix:** Restore the specific numbers from the Day 1 record:

> "My X video got nearly a million views. Someone reposted it to
> Instagram, got two thousand comments. So I'm training AI to be the
> editor I never had."

Saves no time, lifts the credibility floor, and creates two
caption-emphasis chips ("MILLION", "TWO THOUSAND") for the caption pass.

---

### [IMPROVEMENT] SHOT 7 · Tool list is dense for the time budget

**Diagnosis:** *"Frame samples, cut detection, caption timing, loudness
check. Plus a Remotion layer for the graphics you're seeing right now."*
That's five distinct tools/techniques in 8 seconds of audio — viewers
will not retain all five (per §6, average shot length ≤ 6s and
information density follows). The b-roll already shows the senses
running on screen, so the audio doesn't need to enumerate them.

**Fix:** Cut the list to two named deliverables; let the b-roll carry
the technical detail visually:

> "So I asked Claude to build two things — a review skill that watches
> my videos, and the Remotion graphics you're seeing right now."

Saves ~2 seconds. Reclaim those for breathing room or extend SHOT 8.

---

### [NIT] SHOT 6 · "Yesterday's lesson?" reads slightly clinical

**Diagnosis:** Question framing pivots the speaker from narrator to
presenter. Minor tonal nit; not load-bearing.

**Fix:**
> "So the lesson is obvious. Before this thing publishes anything, it
> has to actually watch what it made. Like an editor."

---

### [NIT] SHOT 3 · "Quick context:" is meta-textual

**Diagnosis:** Telling the viewer you're recapping signals "skip this
section." Just dive in.

**Fix:** Drop "Quick context:" — open with the recap directly. Combined
with the previous fix:

> "My X video got nearly a million views…"

---

### [PASS] Items the rubric checks

- **Length** — 52s post-speedup is in the 45–60s sweet spot (§2).
- **Three-act structure** — clear hook (0–8s), tension (8–45s), payoff (45–58s) (§3).
- **CTA** — single, keyword-based, short, specific to the deliverable (§5).
- **Captions plan** — burned-in, animated, emphasis chips, salmon brand color (§4).
- **Open loops resolved** — both setups paid off (§7, §8 #10).
- **Self-deprecation budget** — exactly one beat ("Day one almost didn't happen"), within the rubric limit (§7).
- **Pacing** — average shot 5.8s, no stretch over 8s (§6).

---

## Verdict

**One round of fixes.** The bones are right — three-act structure
holds, length is on target, hook visually strong, CTA clean. The
tightening is mechanical: merge SHOTS 1+2 to land the open loop
inside the first 3 seconds, restore the specific numbers in the
recap, trim the tool list in SHOT 7. ~3 minutes of script edits, no
re-shoot needed.

After fixes: ship as-is.

## Diff to apply

```diff
- SHOT 1: "Day 2... of teaching AI to be my video editor."
- SHOT 2: "Day one almost didn't happen."
+ SHOT 1+2 (merged, 0–5s):
+   "Day 2..." [graphic+flinch] "...of teaching AI to be my video editor.
+   And day one almost didn't happen."

- SHOT 3: "Quick context: my X video went viral, someone reposted it to
-   Instagram and got thousands of comments. So I'm training AI to be
-   the editor I never had."
+ SHOT 3: "My X video got nearly a million views. Someone reposted it to
+   Instagram, got two thousand comments. So I'm training AI to be the
+   editor I never had."

- SHOT 6: "Yesterday's lesson? Before this thing publishes anything, it
-   has to actually watch what it made. Like an editor."
+ SHOT 6: "So the lesson is obvious. Before this thing publishes
+   anything, it has to actually watch what it made. Like an editor."

- SHOT 7: "So I asked Claude to build a review skill — frame samples,
-   cut detection, caption timing, loudness check. Plus a Remotion layer
-   for the graphics you're seeing right now."
+ SHOT 7: "So I asked Claude to build two things — a review skill that
+   watches my videos, and the Remotion graphics you're seeing right
+   now."
```
