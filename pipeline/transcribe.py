#!/usr/bin/env python3
"""
Stage 1: Transcribe a raw video to word-level JSON using faster-whisper.

This script needs faster-whisper installed locally — it's not in the Cowork
sandbox (network-restricted). Install once on your Mac, then run as needed.

Setup (one-time, ~30 seconds):
    pip3 install --user --break-system-packages faster-whisper

Usage:
    python3 pipeline/transcribe.py raw/day_01/selfie_part_a.mov
    python3 pipeline/transcribe.py raw/day_01/selfie_part_a.mov --model small

First run also downloads the model (~250 MB for 'small', ~75 MB for 'base').
Subsequent runs are local-only.

Output:
    transcripts/day_NN/<stem>.json — segments + word-level timestamps.

Model sizes:
    tiny    ~75 MB   fastest, lowest accuracy
    base    ~75 MB   slightly better — recommended for quick iterations
    small   ~250 MB  best balance — recommended for shipping (default)
    medium  ~770 MB  high accuracy, slower
    large-v3 ~1.5 GB highest accuracy, slowest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
TRANSCRIPTS_DIR = REPO / "transcripts"


def transcribe(input_path: Path, model_size: str = "small") -> Path:
    """Transcribe a video file → JSON with word-level timestamps."""
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.stderr.write(
            "\nERROR: faster-whisper is not installed.\n"
            "Install it on your Mac (not in the Cowork sandbox):\n\n"
            "    pip3 install --user --break-system-packages faster-whisper\n\n"
        )
        sys.exit(2)

    # Mirror the input's day_NN/ subfolder so transcripts stay symmetric with
    # raw/, edits/, published/.
    day_dir = input_path.parent.name
    out_dir = TRANSCRIPTS_DIR / day_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{input_path.stem}.json"

    sys.stderr.write(
        f"[transcribe] loading model '{model_size}' "
        f"(first run downloads from Hugging Face)…\n"
    )
    # CPU + int8 is the fastest path on Mac without a GPU. For Apple Silicon
    # you can experiment with compute_type='int8_float32' but int8 is fine.
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    sys.stderr.write(f"[transcribe] running on {input_path.name}…\n")
    segments_iter, info = model.transcribe(
        str(input_path),
        word_timestamps=True,
        vad_filter=True,        # cuts down on hallucinated text in silence
        vad_parameters={"min_silence_duration_ms": 350},
    )

    # Materialize the iterator and shape the output JSON.
    try:
        rel_source = str(input_path.relative_to(REPO))
    except ValueError:
        rel_source = str(input_path)

    out = {
        "source": rel_source,
        "engine": f"faster-whisper:{model_size}",
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "duration": round(info.duration, 3),
        "segments": [],
    }
    for seg in segments_iter:
        out["segments"].append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": [
                {
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "word": w.word.strip(),
                }
                for w in (seg.words or [])
            ],
        })

    out_path.write_text(json.dumps(out, indent=2))
    rel_out = out_path.relative_to(REPO) if out_path.is_relative_to(REPO) else out_path
    sys.stderr.write(
        f"[transcribe] wrote {rel_out} — "
        f"{len(out['segments'])} segments, "
        f"{info.duration:.1f}s, language={info.language}\n"
    )
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="Path to a video or audio file")
    parser.add_argument(
        "--model", default="small",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: small)",
    )
    args = parser.parse_args()
    transcribe(args.input.resolve(), args.model)
