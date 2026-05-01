#!/usr/bin/env python3
"""
Create lightweight edit proxies from camera originals.

Proxy workflow:
  1. Keep `raw/day_NN/*` untouched as camera originals.
  2. Generate normalized, low-res H.264 proxies in `proxies/day_NN/`.
  3. Do timing and rough assembly against proxies for fast iteration.
  4. Reuse the same clip order / in-out windows against raw files for final export.

Usage:
    python3 pipeline/proxy.py raw/day_02/*.MOV
    python3 pipeline/proxy.py raw/day_02/*.MOV --height 1280 --force
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PROXIES_DIR = REPO / "proxies"


def tool(name: str) -> str:
    """Return a working ffmpeg tool path, avoiding stale shim binaries."""
    candidates = [
        shutil.which(name),
        f"/usr/local/bin/{name}",
        f"/opt/homebrew/bin/{name}",
        f"/Users/andrewjiang/.nix-profile/bin/{name}",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            subprocess.run(
                [candidate, "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return candidate
        except (OSError, subprocess.CalledProcessError):
            continue
    raise RuntimeError(f"{name} not found on PATH")


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        [
            tool("ffprobe"), "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(out.stdout.strip())


def proxy_path_for(input_path: Path) -> Path:
    try:
        rel = input_path.resolve().relative_to(REPO)
    except ValueError:
        rel = Path(input_path.name)

    if rel.parts and rel.parts[0] == "raw" and len(rel.parts) >= 2:
        day_dir = rel.parts[1]
    else:
        day_dir = input_path.parent.name

    return PROXIES_DIR / day_dir / f"{input_path.stem}.proxy.mp4"


def make_proxy(input_path: Path, output_path: Path, height: int, force: bool) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not force and output_path.stat().st_mtime >= input_path.stat().st_mtime:
        print(f"[proxy] up to date {output_path.relative_to(REPO)}")
        return output_path

    width = int(round(height * 9 / 16))
    # ffmpeg autorotates iPhone MOVs by default before filters. This turns the
    # HEVC+rotation source into a real vertical H.264 file with no rotation tag.
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        "setsar=1,fps=30"
    )

    cmd = [
        tool("ffmpeg"), "-y", "-loglevel", "error",
        "-i", str(input_path),
        "-map", "0:v:0", "-map", "0:a:0?",
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "28",
        "-profile:v", "main", "-level:v", "3.1",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    print(
        f"[proxy] {input_path.relative_to(REPO)} -> "
        f"{output_path.relative_to(REPO)} ({probe_duration(output_path):.2f}s)"
    )
    return output_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--height", type=int, default=960, help="proxy frame height; width is 9:16 (default: 960)")
    parser.add_argument("--force", action="store_true", help="regenerate existing proxies")
    parser.add_argument("--manifest", type=Path, help="optional JSON manifest output path")
    args = parser.parse_args(argv)

    outputs = []
    for raw in args.inputs:
        input_path = raw.resolve()
        output_path = proxy_path_for(input_path)
        proxy = make_proxy(input_path, output_path, args.height, args.force)
        outputs.append({
            "raw": str(input_path.relative_to(REPO)) if input_path.is_relative_to(REPO) else str(input_path),
            "proxy": str(proxy.relative_to(REPO)),
            "duration": round(probe_duration(proxy), 3),
        })

    if args.manifest:
        manifest_path = args.manifest if args.manifest.is_absolute() else REPO / args.manifest
    else:
        day_dirs = {Path(item["proxy"]).parent for item in outputs}
        manifest_path = REPO / sorted(day_dirs)[0] / "proxy_manifest.json" if len(day_dirs) == 1 else PROXIES_DIR / "proxy_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({"proxies": outputs}, indent=2) + "\n")
    print(f"[proxy] wrote {manifest_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
