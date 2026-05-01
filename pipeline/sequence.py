#!/usr/bin/env python3
"""
Build a spoken-video spine from explicit source clip windows.

This is the proxy-era replacement for "concat raw clips, then tighten": each
selected window is decoded on its own, normalized to one frame size, then joined
with an optional micro crossfade. The same config shape can later be conformed
back to `raw/` for a full-quality export.

Usage:
    python3 pipeline/sequence.py --config series/days/02-proxy-sequence.json
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
from typing import Literal

from ffmpeg_quality import h264_quality_args


REPO = Path(__file__).resolve().parent.parent


@dataclass
class Segment:
    source: Path | None = None
    start: float = 0.0
    end: float = 0.0
    label: str = ""
    type: Literal["clip", "silence"] = "clip"
    duration_override: float | None = None

    @property
    def duration(self) -> float:
        if self.type == "silence":
            if self.duration_override is None:
                raise ValueError("silence segment needs duration")
            return self.duration_override
        return self.end - self.start


@dataclass
class SequencePlan:
    segments: list[Segment]
    output: Path
    width: int
    height: int
    fps: int
    transition: float
    crf: int
    preset: str


def tool(name: str) -> str:
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
            subprocess.run([candidate, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return candidate
        except (OSError, subprocess.CalledProcessError):
            continue
    raise RuntimeError(f"{name} not found")


def resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else REPO / p


def load_config(path: Path) -> SequencePlan:
    cfg = json.loads(path.read_text())
    return SequencePlan(
        segments=[
            Segment(
                source=resolve(s["source"]) if s.get("source") else None,
                start=float(s.get("start", 0.0)),
                end=float(s.get("end", 0.0)),
                label=s.get("label", ""),
                type=s.get("type", "clip"),
                duration_override=float(s["duration"]) if "duration" in s else None,
            )
            for s in cfg["segments"]
        ],
        output=resolve(cfg["output"]),
        width=int(cfg.get("width", 540)),
        height=int(cfg.get("height", 960)),
        fps=int(cfg.get("fps", 30)),
        transition=float(cfg.get("transition", 0.0)),
        crf=int(cfg.get("crf", 16)),
        preset=str(cfg.get("preset", "slow")),
    )


def render_segment(
    seg: Segment,
    out_path: Path,
    width: int,
    height: int,
    fps: int,
    crf: int,
    preset: str,
) -> None:
    if seg.type == "silence":
        subprocess.run(
            [
                tool("ffmpeg"), "-y", "-loglevel", "error",
                "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:r={fps}:d={seg.duration}",
                "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000:d={seg.duration}",
            *h264_quality_args(
                crf=crf,
                preset=preset,
                level="5.2" if max(width, height) >= 2160 else "4.2",
            ),
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(out_path),
            ],
            check=True,
        )
        return

    if seg.source is None:
        raise ValueError(f"clip segment missing source: {seg}")
    if not seg.source.exists():
        raise FileNotFoundError(seg.source)
    if seg.duration <= 0:
        raise ValueError(f"non-positive segment duration: {seg}")

    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,fps={fps},format=yuv420p"
    )
    subprocess.run(
        [
            tool("ffmpeg"), "-y", "-loglevel", "error",
            "-ss", f"{seg.start}",
            "-i", str(seg.source),
            "-t", f"{seg.duration}",
            "-vf", vf,
            "-af", "aresample=async=1:first_pts=0",
            *h264_quality_args(
                crf=crf,
                preset=preset,
                level="5.2" if max(width, height) >= 2160 else "4.2",
            ),
            "-c:a", "aac", "-b:a", "128k",
            str(out_path),
        ],
        check=True,
    )


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


def concat_no_transition(files: list[Path], out_path: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for file in files:
            f.write(f"file '{file.resolve()}'\n")
        list_path = Path(f.name)
    try:
        subprocess.run(
            [
                tool("ffmpeg"), "-y", "-loglevel", "error",
                "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c", "copy", "-movflags", "+faststart",
                str(out_path),
            ],
            check=True,
        )
    finally:
        list_path.unlink(missing_ok=True)


def concat_with_crossfades(files: list[Path], out_path: Path, transition: float) -> None:
    durations = [probe_duration(f) for f in files]
    inputs: list[str] = []
    for f in files:
        inputs.extend(["-i", str(f)])

    parts: list[str] = []
    for i in range(len(files)):
        parts.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[{i}:a]asetpts=PTS-STARTPTS[a{i}]")

    video_label = "v0"
    audio_label = "a0"
    output_duration = durations[0]
    for i in range(1, len(files)):
        vout = f"vx{i}"
        aout = f"ax{i}"
        offset = max(0.0, output_duration - transition)
        parts.append(
            f"[{video_label}][v{i}]"
            f"xfade=transition=fade:duration={transition}:offset={offset:.6f}"
            f"[{vout}]"
        )
        parts.append(
            f"[{audio_label}][a{i}]"
            f"acrossfade=d={transition}:c1=tri:c2=tri"
            f"[{aout}]"
        )
        video_label = vout
        audio_label = aout
        output_duration += durations[i] - transition

    subprocess.run(
        [
            tool("ffmpeg"), "-y", "-loglevel", "error",
            *inputs,
            "-filter_complex", ";".join(parts),
            "-map", f"[{video_label}]",
            "-map", f"[{audio_label}]",
            *h264_quality_args(
                crf=20,
                preset="medium",
                level="5.2",
            ),
            "-c:a", "aac", "-b:a", "128k",
            str(out_path),
        ],
        check=True,
    )


def build_sequence(plan: SequencePlan) -> Path:
    if not plan.segments:
        raise ValueError("sequence needs at least one segment")
    plan.output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        rendered: list[Path] = []
        for idx, seg in enumerate(plan.segments):
            out = tmp_dir / f"seg_{idx:02d}.mp4"
            render_segment(seg, out, plan.width, plan.height, plan.fps, plan.crf, plan.preset)
            rendered.append(out)

        if plan.transition > 0 and len(rendered) > 1:
            concat_with_crossfades(rendered, plan.output, plan.transition)
        else:
            concat_no_transition(rendered, plan.output)

    print(
        f"[sequence] wrote {plan.output.relative_to(REPO)} — "
        f"{len(plan.segments)} segments, {probe_duration(plan.output):.2f}s"
    )
    return plan.output


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args(argv)
    build_sequence(load_config(args.config.resolve()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
