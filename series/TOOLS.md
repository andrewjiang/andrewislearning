# Tool Rollout

The principle: prefer **programmable / agentic** tools over GUI apps. ffmpeg + APIs orchestrated by Claude Code, not Premiere with an AI button.

Each tool is introduced on a specific day so we don't pile the whole stack on Day 2.

## Editing

| Tool | Purpose | First used |
|------|---------|-----------|
| Claude Code | Orchestrator. Reads transcripts, writes cut lists, runs ffmpeg. | Day 1 |
| ffmpeg | The actual cuts, concats, captions, reformats. | Day 4 |
| Whisper (local or API) | Transcription with word-level timestamps. | Day 3 |
| Remotion | Code-based motion graphics — intros, outros, animated captions. | Day 8 |
| Submagic API (optional) | Viral-style word-by-word captions if Remotion is too much work. | Day 10 |
| Replicate / Runway API | AI B-roll from transcript keywords. | Day 12 |
| ElevenLabs API | Voice cleanup, fix flubs without re-recording, eventually dubs. | Day 26 |

## Publishing

| Tool | Purpose | First used |
|------|---------|-----------|
| Ayrshare API | One request → IG + TikTok + X. | Day 15 |
| Buffer API | Boring fallback if Ayrshare doesn't cover something. | (only if needed) |
| Computer-use agent | When an API doesn't exist for a feature, agent clicks the app. | Day 25 |

## Capture (manual — only stage where the rules let me touch things)

- iPhone, vertical orientation, default camera app.
- AirDrop or iCloud Drive into `raw/` on the laptop.
- macOS screen recording (Cmd+Shift+5) for laptop B-roll.

## Not using (and why)

- **CapCut / Descript / Premiere with AI features.** GUI-first; defeats the agentic-pipeline premise. (One exception: Day 1 on-screen cards in CapCut, because we haven't built the Remotion templates yet. We'll narrate that tension.)
- **Buffer / Hootsuite as the primary publisher.** Not really AI; just schedulers with a UI.
- **Sora / Veo for full-video generation.** Not the point of the series — we're automating the *pipeline* around real talking-head footage, not replacing the footage.

## Cost ceiling

Rough monthly when fully scaled (post Day 21):

- Whisper API: ~$5
- Remotion: free (self-hosted) / ~$15 cloud
- Replicate / Runway: ~$30 budget for B-roll generation
- Ayrshare: ~$30
- ElevenLabs: ~$22
- Claude API (if not using Code subscription): ~$30

Target: under $150/mo for the whole stack at full bore. Will track and report on Day 30.
