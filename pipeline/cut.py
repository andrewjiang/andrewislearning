#!/usr/bin/env python3
"""
Stage 2: Apply a cut list to a raw video.

DAY 1 STATUS: stub. Pass-through copy via ffmpeg stream-copy so no re-encode.
On Day 4: Claude reads the transcript, decides which segments to keep / drop
(silence, filler words, retakes), emits a cut list, and this script executes it.

Usage:
    python pipeline/cut.py raw/day_01/selfie_take_01.mp4
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
EDITS_DIR = REPO / "edits"


def cut(input_path: Path) -> Path:
    """Apply a cut list to the input. STUB: stream-copy passthrough."""
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    # Outputs mirror the input's day_NN/ subfolder.
    day_dir = input_path.parent.name
    out_dir = EDITS_DIR / day_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{input_path.stem}.cut.mp4"

    if shutil.which("ffmpeg") is None:
        # Fallback for environments without ffmpeg — straight file copy.
        shutil.copy2(input_path, out_path)
        print(f"[cut] (no ffmpeg) copied → {out_path.relative_to(REPO)}")
        return out_path

    # Stream-copy passthrough for Day 1. Day 4 will replace this with a real
    # cut list driven by transcript timestamps.
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(input_path),
            "-c", "copy",
            str(out_path),
        ],
        check=True,
    )
    print(f"[cut] wrote {out_path.relative_to(REPO)}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python pipeline/cut.py <raw/video.mp4>", file=sys.stderr)
        sys.exit(2)
    cut(Path(sys.argv[1]).resolve())
