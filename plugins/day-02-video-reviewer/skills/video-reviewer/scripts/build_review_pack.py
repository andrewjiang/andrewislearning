#!/usr/bin/env python3
"""Build a review pack for a short-form video day."""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def die(message: str) -> None:
    print(f"[review-pack] ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "series").exists() and (candidate / "pipeline").exists():
            return candidate
    return start.resolve()


def day_token(raw: str) -> str:
    match = re.search(r"\d+", raw)
    if not match:
        die(f"could not parse day number from {raw!r}")
    return f"{int(match.group()):02d}"


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        capture_output=capture,
        text=True,
    )


def find_binary(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    for candidate in [
        Path.home() / ".nix-profile" / "bin" / name,
        Path("/opt/homebrew/bin") / name,
        Path("/usr/local/bin") / name,
        Path("/usr/bin") / name,
    ]:
        if candidate.exists():
            return str(candidate)
    die(f"{name} not found")
    raise AssertionError("unreachable")


def ffprobe_json(ffprobe: str, video: Path) -> dict[str, Any]:
    proc = run([
        ffprobe,
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json",
        str(video),
    ], capture=True)
    return json.loads(proc.stdout)


def video_duration(specs: dict[str, Any]) -> float:
    duration = specs.get("format", {}).get("duration")
    if duration:
        return float(duration)
    for stream in specs.get("streams", []):
        if stream.get("codec_type") == "video" and stream.get("duration"):
            return float(stream["duration"])
    return 0.0


def video_stream(specs: dict[str, Any]) -> dict[str, Any]:
    for stream in specs.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return {}


def make_sheet(
    ffmpeg: str,
    video: Path,
    out: Path,
    *,
    start: float | None = None,
    duration: float | None = None,
    fps: str,
    tile: str,
    scale: str = "270:480",
) -> None:
    command = [ffmpeg, "-y", "-loglevel", "error"]
    if start is not None:
        command.extend(["-ss", f"{start:.3f}"])
    command.extend(["-i", str(video)])
    if duration is not None:
        command.extend(["-t", f"{duration:.3f}"])
    command.extend([
        "-vf", f"fps={fps},scale={scale}:force_original_aspect_ratio=decrease,pad={scale}:(ow-iw)/2:(oh-ih)/2,tile={tile}",
        "-frames:v", "1",
        str(out),
    ])
    run(command)


def extract_frame(ffmpeg: str, video: Path, timestamp: float, out: Path, duration: float | None = None) -> None:
    if duration is not None and duration > 0:
        timestamp = min(max(timestamp, 0.0), max(duration - 0.10, 0.0))
    run([
        ffmpeg,
        "-y", "-loglevel", "error",
        "-ss", f"{timestamp:.3f}",
        "-i", str(video),
        "-frames:v", "1",
        str(out),
    ])


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def find_receipt(root: Path, day: str) -> Path | None:
    receipt_dir = root / "published" / f"day_{day}"
    candidates = sorted(receipt_dir.glob("receipt*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def caption_midpoints(caption_payload: dict[str, Any] | None, duration: float) -> list[float]:
    if not caption_payload:
        return [duration * i / 10 for i in range(1, 10)]
    pages = caption_payload.get("pages", [])
    if not pages:
        return [duration * i / 10 for i in range(1, 10)]
    if len(pages) <= 16:
        selected = pages
    else:
        step = (len(pages) - 1) / 15
        selected = [pages[round(i * step)] for i in range(16)]
    payload_duration = float(caption_payload.get("duration") or duration or 0)
    scale = duration / payload_duration if payload_duration > duration + 0.5 else 1.0
    return [
        min(max(
            ((float(page["start"]) + float(page["end"])) / 2) * scale,
            0.0,
        ), max(duration - 0.10, 0.0))
        for page in selected
        if "start" in page and "end" in page
    ]


def extract_caption_frames(ffmpeg: str, video: Path, times: list[float], frame_dir: Path, duration: float) -> list[Path]:
    frame_dir.mkdir(parents=True, exist_ok=True)
    frames: list[Path] = []
    for idx, timestamp in enumerate(times):
        timestamp = min(max(timestamp, 0.0), max(duration - 0.10, 0.0))
        out = frame_dir / f"caption_{idx:02d}_{timestamp:06.2f}.png"
        extract_frame(ffmpeg, video, timestamp, out, duration)
        frames.append(out)
    return frames


def caption_sample_details(caption_payload: dict[str, Any] | None, duration: float) -> list[dict[str, Any]]:
    if not caption_payload:
        return []
    pages = caption_payload.get("pages", [])
    if len(pages) <= 16:
        selected = pages
    else:
        step = (len(pages) - 1) / 15
        selected = [pages[round(i * step)] for i in range(16)]
    payload_duration = float(caption_payload.get("duration") or duration or 0)
    scale = duration / payload_duration if payload_duration > duration + 0.5 else 1.0
    details = []
    for page in selected:
        if "start" not in page or "end" not in page:
            continue
        raw_mid = (float(page["start"]) + float(page["end"])) / 2
        details.append({
            "text": page.get("text"),
            "payload_time": round(raw_mid, 3),
            "video_time": round(min(max(raw_mid * scale, 0.0), max(duration - 0.10, 0.0)), 3),
        })
    return details


def make_image_sheet(ffmpeg: str, frames: list[Path], out: Path) -> None:
    if not frames:
        return
    pattern = str(frames[0].parent / "caption_*.png")
    run([
        ffmpeg,
        "-y", "-loglevel", "error",
        "-pattern_type", "glob",
        "-framerate", "1",
        "-i", pattern,
        "-vf", "scale=270:480:force_original_aspect_ratio=decrease,pad=270:480:(ow-iw)/2:(oh-ih)/2,tile=4x4",
        "-frames:v", "1",
        str(out),
    ])


def audio_levels(ffmpeg: str, video: Path) -> dict[str, str]:
    proc = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-i", str(video),
            "-vn",
            "-af", "volumedetect",
            "-f", "null",
            "-",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    text = proc.stderr
    levels: dict[str, str] = {}
    for key in ["mean_volume", "max_volume"]:
        match = re.search(rf"{key}:\s*([^\n]+)", text)
        if match:
            levels[key] = match.group(1).strip()
    return levels


def receipt_summary(receipt: dict[str, Any] | None) -> dict[str, Any] | None:
    if not receipt:
        return None
    results = receipt.get("results") or []
    urls = []
    for result in results:
        url = result.get("platform_data", {}).get("url") or result.get("permalink") or result.get("link")
        if url:
            urls.append(url)
    return {
        "post_id": receipt.get("post_id"),
        "platforms": receipt.get("platforms"),
        "published_at": receipt.get("published_at"),
        "urls": urls,
        "cover": receipt.get("cover"),
    }


def write_review_prompt(out_dir: Path, day: str, next_day: str) -> None:
    prompt = f"""# Review Pack Prompt

Use this review pack to write:

- `series/days/{day}-review.md`
- `series/days/{next_day}-brief.md`

Inspect:

- `contact_sheet.jpg` for whole-video pacing
- `hook_sheet.jpg` for the first 5 seconds
- `caption_sheet.png` for caption readability
- `review_pack.json` for specs, caption counts, audio levels, and publish receipt

Review the video with timestamped evidence. Convert the critique into concrete Day {int(next_day)} decisions.
"""
    (out_dir / "PROMPT.md").write_text(prompt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("day", help="Day number to review, e.g. 01 or day_01")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--video", type=Path)
    parser.add_argument("--captions", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    root = repo_root(args.repo)
    day = day_token(args.day)
    next_day = f"{int(day) + 1:02d}"
    video = args.video or (root / "edits" / f"day_{day}" / "final.mp4")
    captions = args.captions or (root / "edits" / f"day_{day}" / "final_captioned.captions.json")
    receipt_path = args.receipt or find_receipt(root, day)
    out_dir = args.out or (root / ".context" / "reviews" / f"day_{day}")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not video.exists():
        die(f"video not found: {video}")

    ffmpeg = find_binary("ffmpeg")
    ffprobe = find_binary("ffprobe")
    specs = ffprobe_json(ffprobe, video)
    duration = video_duration(specs)
    stream = video_stream(specs)
    contact_cols = 5
    contact_rows = max(1, math.ceil(max(duration, 1) / 3 / contact_cols))

    contact_sheet = out_dir / "contact_sheet.jpg"
    hook_sheet = out_dir / "hook_sheet.jpg"
    caption_sheet = out_dir / "caption_sheet.png"
    frame_dir = out_dir / "caption_frames"

    make_sheet(
        ffmpeg,
        video,
        contact_sheet,
        fps="1/3",
        tile=f"{contact_cols}x{contact_rows}",
    )
    make_sheet(
        ffmpeg,
        video,
        hook_sheet,
        start=0,
        duration=min(5.0, duration),
        fps="2",
        tile="5x2",
    )

    caption_payload = load_json(captions)
    caption_frames = extract_caption_frames(ffmpeg, video, caption_midpoints(caption_payload, duration), frame_dir, duration)
    make_image_sheet(ffmpeg, caption_frames, caption_sheet)

    cover_path: str | None = None
    receipt = load_json(receipt_path) if receipt_path else None
    if receipt and receipt.get("cover"):
        candidate = Path(str(receipt["cover"]))
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.exists():
            cover_out = out_dir / "cover.png"
            shutil.copyfile(candidate, cover_out)
            cover_path = rel(cover_out, root)

    pack = {
        "day": day,
        "next_day": next_day,
        "video": rel(video, root),
        "captions": rel(captions, root) if captions.exists() else None,
        "receipt": rel(receipt_path, root) if receipt_path else None,
        "outputs": {
            "contact_sheet": rel(contact_sheet, root),
            "hook_sheet": rel(hook_sheet, root),
            "caption_sheet": rel(caption_sheet, root),
            "caption_frames": rel(frame_dir, root),
            "cover": cover_path,
        },
        "specs": {
            "duration": duration,
            "width": stream.get("width"),
            "height": stream.get("height"),
            "codec": stream.get("codec_name"),
            "bit_rate": stream.get("bit_rate") or specs.get("format", {}).get("bit_rate"),
            "size_bytes": int(specs.get("format", {}).get("size", 0) or 0),
        },
        "audio": audio_levels(ffmpeg, video),
        "captions_summary": {
            "pages": len(caption_payload.get("pages", [])) if caption_payload else None,
            "words": len(caption_payload.get("words", [])) if caption_payload else None,
            "style": caption_payload.get("style") if caption_payload else None,
            "samples": caption_sample_details(caption_payload, duration),
        },
        "publish": receipt_summary(receipt),
    }

    (out_dir / "review_pack.json").write_text(json.dumps(pack, indent=2))
    write_review_prompt(out_dir, day, next_day)

    print(f"[review-pack] wrote {rel(out_dir, root)}")
    print(f"[review-pack] contact sheet: {rel(contact_sheet, root)}")
    print(f"[review-pack] hook sheet: {rel(hook_sheet, root)}")
    print(f"[review-pack] caption sheet: {rel(caption_sheet, root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
