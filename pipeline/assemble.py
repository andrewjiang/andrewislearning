#!/usr/bin/env python3
"""
Stage: Assemble a final video from a base track (audio spine) + b-roll inserts.

The base track provides BOTH the audio spine and the default visual. Inserts
replace the *visual* during specified time windows; the *audio* (the spoken
script) comes from the base throughout. This is the canonical b-roll-over-a-roll
pattern. No timeline UI involved — every cut is described in JSON, executed by
ffmpeg, called from a Python script Claude wrote.

Usage:
    # JSON config (recommended for committed shoot plans):
    python pipeline/assemble.py series/days/01-assembly.json

    # Inline args (quick iterations):
    python pipeline/assemble.py \\
        --base raw/day_01/selfie_take_01.mp4 \\
        --insert 30:7:raw/day_01/screen_take_01.mp4 \\
        --insert 37:6:edits/day_01/cards.mp4 \\
        --out edits/day_01/final.mp4

JSON config shape:
{
  "base":   "raw/day_01/selfie_take_01.mp4",
  "inserts": [
    {"at": 30.0, "duration": 7.0, "video": "raw/day_01/screen_take_01.mp4"},
    {"at": 37.0, "duration": 6.0, "video": "edits/day_01/cards.mp4"}
  ],
  "output": "edits/day_01/final.mp4",
  "width":  1080,
  "height": 1920,
  "fps":    30
}
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parent.parent

# Defaults — match the rest of the pipeline (vertical, 30fps, h264).
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
DEFAULT_FPS = 30


@dataclass
class Insert:
    at: float           # start time in the base track (seconds)
    duration: float     # how long the insert occupies (seconds)
    video: Path         # the b-roll clip to show during this window


@dataclass
class Plan:
    base: Path
    inserts: list[Insert]
    output: Path
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    fps: int = DEFAULT_FPS


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def load_plan_from_json(json_path: Path) -> Plan:
    cfg = json.loads(json_path.read_text())
    base_dir = json_path.parent if not Path(cfg["base"]).is_absolute() else Path("/")

    def resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else (REPO / path)

    return Plan(
        base=resolve(cfg["base"]),
        inserts=[
            Insert(at=float(i["at"]), duration=float(i["duration"]),
                   video=resolve(i["video"]))
            for i in cfg["inserts"]
        ],
        output=resolve(cfg["output"]),
        width=int(cfg.get("width", DEFAULT_WIDTH)),
        height=int(cfg.get("height", DEFAULT_HEIGHT)),
        fps=int(cfg.get("fps", DEFAULT_FPS)),
    )


def validate_plan(plan: Plan) -> None:
    if not plan.base.exists():
        raise FileNotFoundError(f"base not found: {plan.base}")
    base_dur = probe_duration(plan.base)

    sorted_inserts = sorted(plan.inserts, key=lambda i: i.at)
    cursor = 0.0
    for ins in sorted_inserts:
        if not ins.video.exists():
            raise FileNotFoundError(f"insert video not found: {ins.video}")
        if ins.at < cursor:
            raise ValueError(
                f"insert at {ins.at}s overlaps with prior insert ending at {cursor}s"
            )
        if ins.at + ins.duration > base_dur + 0.05:
            raise ValueError(
                f"insert at {ins.at}s + {ins.duration}s ({ins.at + ins.duration}s) "
                f"runs past base duration ({base_dur:.2f}s)"
            )
        ins_dur = probe_duration(ins.video)
        if ins.duration > ins_dur + 0.05:
            raise ValueError(
                f"insert {ins.video.name} is only {ins_dur:.2f}s long but plan "
                f"asks for {ins.duration}s"
            )
        cursor = ins.at + ins.duration


def normalize_segment(
    source: Path, start: float, duration: float,
    width: int, height: int, fps: int,
    out_path: Path,
) -> None:
    """Trim [start, start+duration] from source, scale-and-letterbox to WxH @ fps,
    drop audio (we mux the spine's audio at the very end)."""
    # The scale=...:force_original_aspect_ratio=decrease + pad combination
    # letterboxes when the source aspect doesn't match (e.g. 16:9 screen rec
    # into 9:16 vertical), preserving content. setsar=1 normalizes pixel ratio
    # so the concat demuxer doesn't complain across heterogeneous sources.
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,fps={fps}"
    )
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", f"{start}",
        "-i", str(source),
        "-t", f"{duration}",
        "-an",
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)


def concat_segments(segments: list[Path], out_path: Path) -> None:
    """Concat normalized segments via the concat demuxer (lossless, no re-encode)."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for s in segments:
            f.write(f"file '{s.resolve()}'\n")
        list_file = f.name
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-f", "concat", "-safe", "0",
             "-i", list_file,
             "-c", "copy",
             str(out_path)],
            check=True,
        )
    finally:
        Path(list_file).unlink(missing_ok=True)


def extract_audio(base: Path, out_path: Path) -> None:
    """Extract full audio from the base track, re-encoded to AAC for mux compatibility."""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(base),
         "-vn", "-c:a", "aac", "-b:a", "192k",
         str(out_path)],
        check=True,
    )


def mux(video_only: Path, audio: Path, out_path: Path) -> None:
    """Mux a video-only mp4 with an audio track, no re-encode."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(video_only),
         "-i", str(audio),
         "-c:v", "copy", "-c:a", "copy",
         "-map", "0:v:0", "-map", "1:a:0",
         "-shortest",
         str(out_path)],
        check=True,
    )


def assemble(plan: Plan) -> Path:
    """Run the assembly. Returns the output path."""
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("ffmpeg/ffprobe not found on PATH")

    validate_plan(plan)
    base_dur = probe_duration(plan.base)
    sorted_inserts = sorted(plan.inserts, key=lambda i: i.at)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # Walk the timeline and produce a normalized segment per slice.
        segments: list[Path] = []
        cursor = 0.0
        seg_idx = 0

        for ins in sorted_inserts:
            # Base footage runs from `cursor` up to the insert's start.
            if ins.at > cursor + 0.01:
                seg_path = tmp_dir / f"seg_{seg_idx:02d}_base.mp4"
                normalize_segment(
                    plan.base, cursor, ins.at - cursor,
                    plan.width, plan.height, plan.fps, seg_path,
                )
                segments.append(seg_path)
                seg_idx += 1
            # The insert occupies `ins.duration` seconds, sourced from the
            # start of the b-roll clip. (If you want a specific in-point
            # within the insert clip, extend the JSON with an "in" field.)
            seg_path = tmp_dir / f"seg_{seg_idx:02d}_insert.mp4"
            normalize_segment(
                ins.video, 0.0, ins.duration,
                plan.width, plan.height, plan.fps, seg_path,
            )
            segments.append(seg_path)
            seg_idx += 1
            cursor = ins.at + ins.duration

        # Tail: base footage from `cursor` to end.
        if cursor < base_dur - 0.01:
            seg_path = tmp_dir / f"seg_{seg_idx:02d}_base.mp4"
            normalize_segment(
                plan.base, cursor, base_dur - cursor,
                plan.width, plan.height, plan.fps, seg_path,
            )
            segments.append(seg_path)

        # Stitch video, then mux the spine's audio over the whole thing.
        video_only = tmp_dir / "video_only.mp4"
        audio_track = tmp_dir / "audio.m4a"
        concat_segments(segments, video_only)
        extract_audio(plan.base, audio_track)
        mux(video_only, audio_track, plan.output)

    return plan.output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_insert_arg(s: str) -> Insert:
    """Parse 'AT:DURATION:VIDEO' (e.g., '30:7:raw/day_01/screen_take_01.mp4')."""
    parts = s.split(":", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"--insert expects AT:DURATION:VIDEO, got: {s}"
        )
    at, dur, video = parts
    return Insert(at=float(at), duration=float(dur), video=Path(video).resolve())


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble a final video from a base track + b-roll inserts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("config", nargs="?", type=Path,
                        help="JSON config file. If omitted, use --base/--insert/--out flags.")
    parser.add_argument("--base", type=Path, help="Base track (audio spine).")
    parser.add_argument("--insert", action="append", type=parse_insert_arg, default=[],
                        help="Repeat. Format: AT:DURATION:VIDEO_PATH")
    parser.add_argument("--out", type=Path, help="Output mp4 path.")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    args = parser.parse_args(argv)

    if args.config:
        plan = load_plan_from_json(args.config)
    else:
        if not (args.base and args.out):
            parser.error("either pass a JSON config OR --base/--insert/--out")
        plan = Plan(
            base=args.base.resolve(),
            inserts=args.insert,
            output=args.out.resolve(),
            width=args.width, height=args.height, fps=args.fps,
        )

    out = assemble(plan)
    dur = probe_duration(out)
    print(f"[assemble] wrote {out.relative_to(REPO)} — {dur:.2f}s, "
          f"{plan.width}×{plan.height} @ {plan.fps}fps")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
