#!/usr/bin/env python3
"""
Tighten a video by keeping only specified time windows and concatenating them.

Removes dead air, long pauses, retakes — anything outside the keep list. Audio
and video stay in sync. Useful as a manual-edit pass before the transcript-driven
cutter (Day 4 of the series) takes over.

Usage:
    # Inline windows (start:end pairs in seconds, space-separated):
    python pipeline/tighten.py raw/day_01/selfie_combined.mp4 \\
        --keep 0:17.9 19.2:23.45 23.51:30.10 \\
        --out raw/day_01/selfie_combined_tight.mp4

    # Or load windows from a JSON config:
    python pipeline/tighten.py --config series/days/01-tighten.json

JSON config shape:
    {
      "input":  "raw/day_01/selfie_combined.mp4",
      "output": "raw/day_01/selfie_combined_tight.mp4",
      "keep": [
        {"start": 0.0,   "end": 17.9,  "label": "opener"},
        {"start": 19.2,  "end": 23.45, "label": "its-on-me"},
        ...
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


@dataclass
class Window:
    start: float
    end: float
    label: str = ""

    @property
    def duration(self) -> float:
        return self.end - self.start


def parse_inline(arg: str) -> Window:
    if ":" not in arg:
        raise argparse.ArgumentTypeError(f"keep window expects start:end, got {arg!r}")
    a, b = arg.split(":", 1)
    return Window(start=float(a), end=float(b))


def tighten(input_path: Path, windows: list[Window], out_path: Path) -> Path:
    """Concat the kept windows from input → out, preserving A/V sync."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found")
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if not windows:
        raise ValueError("at least one keep window required")
    for w in windows:
        if w.duration <= 0:
            raise ValueError(f"window {w} has non-positive duration")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build a filter_complex that trims each window from input, then concats.
    parts = []
    streams = []
    for i, w in enumerate(windows):
        parts.append(
            f"[0:v]trim={w.start}:{w.end},setpts=PTS-STARTPTS[v{i}];"
            f"[0:a]atrim={w.start}:{w.end},asetpts=PTS-STARTPTS[a{i}]"
        )
        streams.append(f"[v{i}][a{i}]")
    concat = "".join(streams) + f"concat=n={len(windows)}:v=1:a=1[v][a]"
    filter_complex = ";".join(parts + [concat])

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(input_path),
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path


def load_config(config_path: Path) -> tuple[Path, list[Window], Path]:
    cfg = json.loads(config_path.read_text())

    def resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else (REPO / path)

    return (
        resolve(cfg["input"]),
        [Window(float(w["start"]), float(w["end"]), w.get("label", ""))
         for w in cfg["keep"]],
        resolve(cfg["output"]),
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", nargs="?", type=Path, help="Input video")
    parser.add_argument("--keep", nargs="+", type=parse_inline,
                        help="Keep windows: start:end pairs in seconds")
    parser.add_argument("--out", type=Path, help="Output video path")
    parser.add_argument("--config", type=Path, help="JSON config (overrides positional args)")
    args = parser.parse_args(argv)

    if args.config:
        in_path, windows, out_path = load_config(args.config)
    else:
        if not (args.input and args.keep and args.out):
            parser.error("provide a JSON --config OR positional input + --keep + --out")
        in_path, windows, out_path = args.input.resolve(), args.keep, args.out.resolve()

    tighten(in_path, windows, out_path)
    total = sum(w.duration for w in windows)
    rel = out_path.relative_to(REPO) if out_path.is_relative_to(REPO) else out_path
    sys.stderr.write(
        f"[tighten] wrote {rel} — {len(windows)} windows, "
        f"{total:.2f}s kept\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
