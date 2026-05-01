---
name: voice-enhance-reel
description: Enhance spoken voice audio for Instagram Reels/TikTok clips using the ContentCopilot pipeline. Use when the user asks to clean up, polish, isolate, denoise, normalize, or make phone/selfie voice audio sound production-quality.
---

# Voice Enhance Reel

Use `pipeline/enhance_audio.py` to clean the spoken voice track while preserving the existing video stream and caption timing.

## When to trigger

- "Clean up the voice audio"
- "Make this Reel sound production quality"
- "Enhance the spoken audio"
- "Use Cleanvoice / ElevenLabs voice isolator"
- "Denoise this clip"
- "Normalize the audio for IG Reels"

## Provider choice

Default to `--provider auto`.

Selection rules:

1. Use **Cleanvoice** when `CLEANVOICE_API_KEY` is present and the clip is normal phone/selfie speech that needs studio polish.
2. Use **ElevenLabs Voice Isolator** when the clip has heavy background noise, music, street noise, or room ambience.
3. Use **Resemble** only when `RESEMBLE_API_KEY` is present and Cleanvoice is unavailable.
4. Use **local** when no provider key is configured or when testing the pipeline offline.

Never run filler-word removal, silence removal, or timing-changing cleanup for final video exports unless the user explicitly asks. Caption timing and visual edits must stay stable.

## Workflow

1. Pick the input clip. Prefer the latest captioned or assembled day artifact:

   ```bash
   ls -lh edits/day_*/**/*.mp4 2>/dev/null || find edits -name '*.mp4' -print
   ```

2. Run the enhancement stage:

   ```bash
   python3 pipeline/enhance_audio.py INPUT.mp4 \
     --provider auto \
     --out OUTPUT.voice.mp4
   ```

3. If using a specific provider:

   ```bash
   python3 pipeline/enhance_audio.py INPUT.mp4 \
     --provider cleanvoice \
     --out OUTPUT.voice.mp4
   ```

   ```bash
   python3 pipeline/enhance_audio.py INPUT.mp4 \
     --provider elevenlabs \
     --out OUTPUT.voice.mp4
   ```

4. Run the finish/mastering pass after external voice cleanup:

   ```bash
   python3 pipeline/finish.py OUTPUT.voice.mp4 \
     --out edits/day_NN/final.mp4
   ```

5. Verify the output has one video stream and one audio stream:

   ```bash
   ffprobe -v error \
     -show_entries stream=index,codec_type,codec_name:format=duration \
     -of json edits/day_NN/final.mp4
   ```

## Environment

Keys are read from the local shell environment:

- `CLEANVOICE_API_KEY`
- `ELEVENLABS_API_KEY`
- `RESEMBLE_API_KEY`

Do not write API keys into repo files, committed configs, skill files, captions JSON, or series docs.

For a temporary one-command run:

```bash
CLEANVOICE_API_KEY="..." python3 pipeline/enhance_audio.py INPUT.mp4 \
  --provider cleanvoice \
  --out OUTPUT.voice.mp4
```

For normal local use, store the export in `~/.zshrc`, then open a new shell or run `source ~/.zshrc`.

## Output naming

Use a `.voice.mp4` suffix before the final finish pass:

- `edits/day_02/final_captioned.voice.mp4`
- `edits/day_02/final.mp4`

Keep throwaway tests under `.context/previews/`.

## Quality bar

- Voice is clearer and more present than the source.
- Output duration matches the input within normal encoder tolerance.
- No clipping or obvious pumping.
- No words are removed or shifted.
- The final upload master still goes through `pipeline/finish.py`.
