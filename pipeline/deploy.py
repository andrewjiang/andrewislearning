#!/usr/bin/env python3
"""
Stage 8: Prepare CDN assets for a day, then trigger Vercel deploy.

Daily-cadence helper. Copies the day's final.mp4 + extracts a cover image into
web/cdn/day_NN/, then optionally runs `vercel --prod` (requires the Vercel CLI
to be installed and the project linked).

Usage:
    python pipeline/deploy.py 01
    python pipeline/deploy.py 01 --no-vercel   # just stage assets, don't deploy
    python pipeline/deploy.py 01 --cover-at 1.5  # cover image from t=1.5s
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


def stage_cdn_assets(day_str: str, cover_at: float = 0.5) -> tuple[Path, Path]:
    """Copy final.mp4 + extract cover.jpg into web/cdn/day_NN/."""
    final_src = REPO / "edits" / f"day_{day_str}" / "final.mp4"
    if not final_src.exists():
        sys.exit(f"[deploy] ERROR: {final_src.relative_to(REPO)} not found — "
                 f"run the pipeline first")

    cdn_dir = REPO / "web" / "cdn" / f"day_{day_str}"
    cdn_dir.mkdir(parents=True, exist_ok=True)

    final_dst = cdn_dir / "final.mp4"
    shutil.copy2(final_src, final_dst)
    sys.stderr.write(
        f"[deploy] copied {final_src.relative_to(REPO)} → "
        f"{final_dst.relative_to(REPO)} ({final_dst.stat().st_size / 1024 / 1024:.1f} MB)\n"
    )

    cover_dst = cdn_dir / "cover.jpg"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-ss", str(cover_at), "-i", str(final_src),
         "-vframes", "1", "-q:v", "2",
         str(cover_dst)],
        check=True,
    )
    sys.stderr.write(
        f"[deploy] extracted cover @ t={cover_at}s → "
        f"{cover_dst.relative_to(REPO)} ({cover_dst.stat().st_size / 1024:.1f} KB)\n"
    )
    return final_dst, cover_dst


def vercel_deploy() -> None:
    if shutil.which("vercel") is None:
        sys.exit(
            "[deploy] vercel CLI not found. Install with:\n"
            "    npm i -g vercel\n"
            "Then run `vercel link` once in this repo to associate it with the project."
        )
    sys.stderr.write("[deploy] running `vercel --prod` ...\n")
    proc = subprocess.run(["vercel", "--prod", "--yes"], cwd=REPO)
    if proc.returncode != 0:
        sys.exit(f"[deploy] vercel deploy failed (exit {proc.returncode})")
    sys.stderr.write("[deploy] vercel deploy complete\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("day", help="Two-digit day number, e.g. '01'")
    parser.add_argument("--cover-at", type=float, default=0.5,
                        help="Timestamp (sec) to extract cover image from (default 0.5)")
    parser.add_argument("--no-vercel", action="store_true",
                        help="Just stage assets, skip the vercel deploy")
    args = parser.parse_args()

    day_str = args.day.zfill(2)
    stage_cdn_assets(day_str, cover_at=args.cover_at)

    if not args.no_vercel:
        vercel_deploy()
    else:
        sys.stderr.write("[deploy] skipped vercel deploy (--no-vercel)\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
