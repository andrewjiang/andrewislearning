#!/usr/bin/env python3
"""
Top-level orchestrator. Runs the full pipeline on one raw take.

DAY 1 STATUS: only the first two stages exist as stubs. Caption / reformat /
publish stages will be added on the days called out in series/SERIES_PLAN.md.

Usage:
    python pipeline/edit.py raw/day_01/selfie_take_01.mp4
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from cut import cut
from transcribe import transcribe


REPO = Path(__file__).resolve().parent.parent
EDITS_DIR = REPO / "edits"


def edit(input_path: Path) -> Path:
    """Run all pipeline stages and return the final edit path."""
    print(f"[edit] starting pipeline on {input_path.relative_to(REPO)}")
    transcribe(input_path)
    cut_out = cut(input_path)

    # Stages below are placeholders for Days 5/6/15. Today, just copy the
    # cut.mp4 to a `.final.mp4` so the pipeline produces a recognizable end
    # artifact and we can prove the plumbing works end-to-end.
    day_dir = input_path.parent.name
    out_dir = EDITS_DIR / day_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    final = out_dir / f"{input_path.stem}.final.mp4"
    shutil.copy2(cut_out, final)
    print(f"[edit] wrote {final.relative_to(REPO)}")
    print(f"[edit] done")
    return final


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python pipeline/edit.py <raw/video.mp4>", file=sys.stderr)
        sys.exit(2)
    edit(Path(sys.argv[1]).resolve())
