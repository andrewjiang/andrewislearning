#!/usr/bin/env python3
"""
Stage 6: Finish pass — audio enhancement + light color grade + speedup.

Single ffmpeg call applies all polish in one pass. Replaces the inline speedup
that was happening at the end of the pipeline.

Audio chain:
    highpass=80      remove low-frequency rumble
    afftdn=nr=10     FFT noise reduction (~10 dB on residual hiss)
    acompressor      gentle 3:1 compression, evens out volume
    loudnorm         normalize to -14 LUFS (IG/TikTok platform target)
    atempo=N         speedup with pitch preservation

Color chain:
    eq               +5% contrast, +10% saturation (subtle pop)
    colortemperature 5800K (default 6500K → slightly warmer whites)
    setpts=PTS/N     speedup (synced with atempo)

Usage:
    python pipeline/finish.py edits/day_01/final_captioned.mp4 \\
        --out edits/day_01/final.mp4 --speed 1.08

    # disable individual stages with flags:
    python pipeline/finish.py input.mp4 --out output.mp4 --no-color
    python pipeline/finish.py input.mp4 --out output.mp4 --no-audio-polish
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from ffmpeg_quality import aac_quality_args, h264_quality_args


REPO = Path(__file__).resolve().parent.parent

# Audio polish defaults — tuned for phone-recorded talking-head selfie
HIGHPASS_HZ = 80
AFFTDN_NR = 10            # noise reduction in dB
COMP_THRESH = "-20dB"
COMP_RATIO = 3
COMP_ATTACK = 20
COMP_RELEASE = 250
LOUDNORM_I = -14          # target loudness, -14 LUFS = IG/TikTok standard
LOUDNORM_LRA = 11
LOUDNORM_TP = -1.5

# Color grade defaults — restored some pop after dialing back too far.
# Previous (1.05/1.10/5800K) pushed too yellow-red.
# Then went too flat (1.02/1.04/6500K).
# Sweet spot: light contrast/sat bump, slight warmth (6300K instead of 5800K).
EQ_CONTRAST = 1.04
EQ_SATURATION = 1.07
COLOR_TEMP_K = 6300       # subtle warmth (between neutral 6500K and previous 5800K)


def build_video_filter(speed: float, color: bool) -> str:
    parts = []
    if color:
        parts.append(f"eq=contrast={EQ_CONTRAST}:saturation={EQ_SATURATION}")
        parts.append(f"colortemperature=temperature={COLOR_TEMP_K}")
    if speed != 1.0:
        parts.append(f"setpts=PTS/{speed}")
    return ",".join(parts) if parts else "null"


def build_audio_filter(speed: float, audio_polish: bool) -> str:
    parts = []
    if audio_polish:
        parts.append(f"highpass=f={HIGHPASS_HZ}")
        parts.append(f"afftdn=nr={AFFTDN_NR}")
        parts.append(
            f"acompressor=threshold={COMP_THRESH}:ratio={COMP_RATIO}:"
            f"attack={COMP_ATTACK}:release={COMP_RELEASE}"
        )
        parts.append(f"loudnorm=I={LOUDNORM_I}:LRA={LOUDNORM_LRA}:TP={LOUDNORM_TP}")
    if speed != 1.0:
        # atempo accepts 0.5–2.0; chain multiple if outside that range
        parts.append(f"atempo={speed}")
    return ",".join(parts) if parts else "anull"


def finish(input_path: Path, output_path: Path, speed: float = 1.08,
           audio_polish: bool = True, color_grade: bool = True) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    vf = build_video_filter(speed, color_grade)
    af = build_audio_filter(speed, audio_polish)

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(input_path),
        "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]",
        "-map", "[v]", "-map", "[a]",
        *h264_quality_args(),
        *aac_quality_args(),
        str(output_path),
    ]

    sys.stderr.write(
        f"[finish] speed={speed}× · "
        f"audio_polish={audio_polish} · color_grade={color_grade}\n"
    )
    if audio_polish:
        sys.stderr.write(
            f"[finish]   audio: highpass {HIGHPASS_HZ}Hz → afftdn nr={AFFTDN_NR}dB "
            f"→ comp 3:1 → loudnorm I={LOUDNORM_I} LUFS\n"
        )
    if color_grade:
        sys.stderr.write(
            f"[finish]   color: contrast +{int((EQ_CONTRAST - 1) * 100)}% "
            f"saturation +{int((EQ_SATURATION - 1) * 100)}% temp {COLOR_TEMP_K}K\n"
        )

    subprocess.run(cmd, check=True)

    rel = output_path.relative_to(REPO) if output_path.is_relative_to(REPO) else output_path
    sys.stderr.write(f"[finish] wrote {rel}\n")
    return output_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--speed", type=float, default=1.08,
                        help="Playback speed multiplier (default: 1.08)")
    parser.add_argument("--no-audio-polish", action="store_true",
                        help="Skip audio enhancement chain")
    parser.add_argument("--no-color", action="store_true",
                        help="Skip color grade")
    args = parser.parse_args(argv)

    finish(
        args.input.resolve(), args.out.resolve(),
        speed=args.speed,
        audio_polish=not args.no_audio_polish,
        color_grade=not args.no_color,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
