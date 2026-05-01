#!/usr/bin/env python3
"""
Sense: cuts

Detect scene cuts in a video using ffmpeg's scene-change filter, then derive
shot metrics — count, average length, longest static stretch (and where it
starts). The output is JSON on stdout, no files written.

Why these metrics: in short-form vertical video, the longest static stretch is
the #1 retention killer. A 60s Reel with one 25s static shot loses viewers
right where attention dips. Surfacing that number — and the timestamp it
starts at — lets Claude propose targeted fixes (zoom-punches, b-roll inserts)
at the exact moment they're needed, not as generic advice.

Usage:
    python cuts.py edits/day_01/final.mp4
    python cuts.py edits/day_01/final.mp4 --threshold 0.3

Output (stdout):
    {
      "video": "edits/day_01/final.mp4",
      "duration_s": 55.767,
      "threshold": 0.3,
      "shot_count": 5,
      "avg_shot_length_s": 11.15,
      "longest_static_s": 24.2,
      "longest_static_at": 12.43,
      "cuts": [
        {"t": 7.167},
        {"t": 12.433},
        {"t": 36.633},
        {"t": 48.8}
      ],
      "shots": [
        {"index": 0, "start": 0.0,    "end": 7.167,  "duration_s": 7.167},
        {"index": 1, "start": 7.167,  "end": 12.433, "duration_s": 5.266},
        {"index": 2, "start": 12.433, "end": 36.633, "duration_s": 24.2},
        {"index": 3, "start": 36.633, "end": 48.8,   "duration_s": 12.167},
        {"index": 4, "start": 48.8,   "end": 55.767, "duration_s": 6.967}
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


# Pulled from frames.py-style helpers — duplicated here to keep each sense
# self-contained (no cross-import between senses). Trades a few duplicated
# lines for clean independent invocation.

def probe_duration(video: Path) -> float:
    """Return duration in seconds via ffprobe."""
    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(out.stdout.strip())


def find_repo(video: Path) -> Path | None:
    """Walk up from the video's path looking for a day_NN folder; return the
    repo root (parent of edits/, raw/, etc.)."""
    for parent in video.resolve().parents:
        if re.match(r"day_\d{2}$", parent.name):
            return parent.parent.parent
    return None


def relpath_or_str(path: Path, base: Path | None) -> str:
    if base is None:
        return str(path)
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path)


def detect_cuts(video: Path, threshold: float) -> list[float]:
    """Return scene-change timestamps in seconds.

    Uses ffmpeg's scene filter: any frame whose scene-change score exceeds
    `threshold` (0.0–1.0) is reported as a cut. 0.3 is a tested-good default
    for short-form video — catches hard cuts without flagging fast motion or
    caption changes within a shot.
    """
    proc = subprocess.run(
        [
            "ffmpeg", "-i", str(video),
            "-vf", f"select='gt(scene,{threshold})',showinfo",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
    )
    # showinfo writes lines like:
    #   [Parsed_showinfo_1 @ 0x...] n:3 pts:... pts_time:7.16667 ...
    pattern = re.compile(r"pts_time:([0-9]+\.?[0-9]*)")
    return [float(m.group(1)) for m in pattern.finditer(proc.stderr)]


def main() -> int:
    ap = argparse.ArgumentParser(description="Detect scene cuts and shot metrics.")
    ap.add_argument("video", type=Path, help="Path to input video")
    ap.add_argument(
        "--threshold", type=float, default=0.3,
        help="Scene-change score threshold (0.0–1.0). Default 0.3.",
    )
    args = ap.parse_args()

    if not args.video.exists():
        print(f"cuts: input not found: {args.video}", file=sys.stderr)
        return 2

    duration = probe_duration(args.video)
    if duration <= 0:
        print(f"cuts: zero-length video: {args.video}", file=sys.stderr)
        return 2

    cut_times = detect_cuts(args.video, args.threshold)

    # Build shot list: a shot runs from one cut to the next. Shot 0 starts
    # at t=0, the last shot ends at duration.
    boundaries = [0.0] + cut_times + [duration]
    shots = []
    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        shots.append({
            "index": i,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration_s": round(end - start, 3),
        })

    longest = max(shots, key=lambda s: s["duration_s"]) if shots else None
    avg_len = (
        round(sum(s["duration_s"] for s in shots) / len(shots), 3)
        if shots else 0.0
    )

    repo = find_repo(args.video)
    manifest = {
        "video": relpath_or_str(args.video, repo),
        "duration_s": round(duration, 3),
        "threshold": args.threshold,
        "shot_count": len(shots),
        "avg_shot_length_s": avg_len,
        "longest_static_s": longest["duration_s"] if longest else 0.0,
        "longest_static_at": longest["start"] if longest else 0.0,
        "cuts": [{"t": round(t, 3)} for t in cut_times],
        "shots": shots,
    }
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
