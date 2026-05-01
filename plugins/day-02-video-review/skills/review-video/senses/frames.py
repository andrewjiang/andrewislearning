#!/usr/bin/env python3
"""
Sense: frames

Sample frames at a fixed FPS from a video, write JPEGs to disk, and print
a JSON manifest to stdout. This is the perception layer — the script gives
Claude something to *see* (via vision) when reviewing a video.

Default is 1 fps (one frame per second), dense enough that no short-form
b-roll under a second can fall between samples. Bump --fps higher (e.g.
2.0) for tighter resolution; lower (e.g. 0.25) for hour-long content.

Usage:
    python frames.py edits/day_01/final.mp4
    python frames.py edits/day_01/final.mp4 --fps 2.0
    python frames.py edits/day_01/final.mp4 --out review/day_01/frames/

Output (stdout):
    {
      "video": "edits/day_01/final.mp4",
      "duration_s": 55.767,
      "fps": 1.0,
      "frame_count": 56,
      "frames": [
        {"index": 1, "t": 0.0, "path": "review/day_01/frames/frame_001.jpg"},
        {"index": 2, "t": 1.0, "path": "review/day_01/frames/frame_002.jpg"},
        ...
      ]
    }

Files written to <out>/frame_NNN.jpg, three-digit zero-padded.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


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


def find_repo_and_day(video: Path) -> tuple[Path | None, str | None]:
    """If the video lives under .../day_NN/..., return (repo_root, "day_NN").

    Repo root is the parent of the day folder's category folder
    (e.g., edits/day_01 → repo is parent of edits/).
    """
    video = video.resolve()
    for parent in video.parents:
        if re.match(r"day_\d{2}$", parent.name):
            return parent.parent.parent, parent.name
    return None, None


def derive_default_out(video: Path) -> Path:
    """Default output dir: <repo>/review/day_NN/frames/ if we can detect day,
    otherwise <video_parent>/frames/."""
    repo, day = find_repo_and_day(video)
    if repo and day:
        return repo / "review" / day / "frames"
    return video.parent / "frames"


def extract_frames_at_fps(video: Path, fps: float, out_dir: Path) -> None:
    """Extract all frames at the given fps in a single ffmpeg pass.

    Outputs <out_dir>/frame_NNN.jpg starting at 001. Frame N corresponds to
    timestamp (N-1) / fps seconds (ffmpeg's fps filter samples at 0, 1/fps,
    2/fps, ... by default).
    """
    # Clean any prior frames so stale output doesn't confuse the manifest.
    # Best-effort — sandboxed filesystems may not allow deletion; ffmpeg will
    # overwrite same-named files, and the manifest only enumerates frame_NNN
    # (three-digit) which won't collide with older two-digit patterns.
    for old in out_dir.glob("frame_[0-9][0-9][0-9].jpg"):
        try:
            old.unlink()
        except (PermissionError, OSError):
            pass

    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(video),
            "-vf", f"fps={fps}",
            "-q:v", "3",  # JPEG quality 2-31, lower=better. 3 ≈ visually lossless.
            "-start_number", "1",
            str(out_dir / "frame_%03d.jpg"),
        ],
        check=True,
    )


def relpath_or_str(path: Path, base: Path | None) -> str:
    """Render path relative to base if possible, else as-is."""
    if base is None:
        return str(path)
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sample frames at a fixed fps from a video.")
    ap.add_argument("video", type=Path, help="Path to input video")
    ap.add_argument("--fps", type=float, default=1.0, help="Frames per second to sample (default: 1.0)")
    ap.add_argument("--out", type=Path, default=None, help="Output dir (default: review/day_NN/frames/)")
    args = ap.parse_args()

    if not args.video.exists():
        print(f"frames: input not found: {args.video}", file=sys.stderr)
        return 2

    if args.fps <= 0:
        print(f"frames: --fps must be positive, got {args.fps}", file=sys.stderr)
        return 2

    out_dir = args.out or derive_default_out(args.video)
    out_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(args.video)
    if duration <= 0:
        print(f"frames: zero-length video: {args.video}", file=sys.stderr)
        return 2

    extract_frames_at_fps(args.video, args.fps, out_dir)

    repo, _day = find_repo_and_day(args.video)
    files = sorted(out_dir.glob("frame_[0-9][0-9][0-9].jpg"))

    frames = [
        {
            "index": i + 1,
            "t": round(i / args.fps, 3),
            "path": relpath_or_str(f, repo),
        }
        for i, f in enumerate(files)
    ]

    manifest = {
        "video": relpath_or_str(args.video, repo),
        "duration_s": round(duration, 3),
        "fps": args.fps,
        "frame_count": len(frames),
        "frames": frames,
    }
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
