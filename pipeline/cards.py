#!/usr/bin/env python3
"""
Generate a card-stack video — title cards with kicker numbers, footer wordmark,
and per-card fade in/out. Vertical 1080x1920, white-on-black.

Usage:
    # Default Day 1 cards (4 cards × 1.5s each = 6s):
    python pipeline/cards.py

    # Custom cards / output / per-card duration:
    python pipeline/cards.py "Build." "Polish." "Automate." "Every day." \
        --out edits/day_01/cards.mp4 --duration 1.5

This is the agentic replacement for hand-rolled CapCut title cards. Day 8 will
add Remotion for animated/word-by-word styles; until then ffmpeg drawtext +
Liberation Sans Bold is the honest minimum.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "edits" / "day_01" / "cards.mp4"
DEFAULT_TEXT = ["Build.", "Polish.", "Automate.", "Every day."]
DEFAULT_DURATION = 1.0  # seconds per card — matches natural spoken pace

# Vertical 1080x1920 to match the rest of the pipeline.
WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Typography. Drop a .ttf into `fonts/` at the repo root to override
# (e.g., Inter-Bold.ttf or Geist-Bold.ttf). Otherwise we use Liberation Sans
# Bold from the system — closest-to-Helvetica face that ships by default.
_USER_FONT = REPO / "fonts" / "main-bold.ttf"
FONT_MAIN = (
    str(_USER_FONT) if _USER_FONT.exists()
    else "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
)
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

FONT_SIZE_MAIN = 170
FONT_SIZE_KICKER = 38

# Color palette — visible warmth, not pure b/w. Background is a deep warm
# brown-black (not just "near black"); text is a cream/parchment tone; the
# kicker number gets the Cowork submit-button orange as a brand tie. Adjust
# the hexes here to retune the whole stack.
COLOR_MAIN = "0xF4EAD5"        # cream/parchment — warm off-white
COLOR_KICKER = "0xD97757"      # warm orange — Cowork accent
COLOR_BG = "0x100E0B"          # warm dark brown-black


def shrink_to_fit(text: str, base_size: int = FONT_SIZE_MAIN, max_chars: int = 8) -> int:
    """Shrink the main font for longer phrases so they don't overflow.
    'Build.' (6) → base. 'Every day.' (10) → smaller. Heuristic, not exact metrics."""
    if len(text) <= max_chars:
        return base_size
    # Linear shrink by character count above the threshold.
    ratio = max_chars / len(text)
    # Cap the shrink at 70% so the text doesn't get too small.
    return max(int(base_size * 0.7), int(base_size * ratio))


def render_card(
    text: str,
    index: int,
    total: int,
    duration: float,
    out_path: Path,
) -> None:
    """Render one card as a silent vertical mp4 with kicker + footer + fades."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    main_size = shrink_to_fit(text)
    kicker = f"{index:02d} / {total:02d}"

    def esc(t: str) -> str:
        # Escape colons and apostrophes for the drawtext filter.
        return t.replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")

    main = (
        f"drawtext=fontfile={FONT_MAIN}:"
        f"text='{esc(text)}':"
        f"fontsize={main_size}:"
        f"fontcolor={COLOR_MAIN}:"
        f"x=(w-text_w)/2:y=(h-text_h)/2"
    )
    kicker_layer = (
        f"drawtext=fontfile={FONT_MONO}:"
        f"text='{esc(kicker)}':"
        f"fontsize={FONT_SIZE_KICKER}:"
        f"fontcolor={COLOR_KICKER}:"
        f"x=(w-text_w)/2:y=h*0.20"
    )

    # No fades — hard cuts between cards. Synced 1:1 with spoken word.
    vf = ",".join([kicker_layer, main])

    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi",
            "-i", f"color=c={COLOR_BG}:s={WIDTH}x{HEIGHT}:r={FPS}:d={duration}",
            "-vf", vf,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-t", str(duration),
            str(out_path),
        ],
        check=True,
    )


def concat_mp4s(parts: list[Path], out_path: Path) -> None:
    """Concat with hard cuts (each card already has its own fade in/out)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for p in parts:
            f.write(f"file '{p.resolve()}'\n")
        list_file = f.name
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-f", "concat", "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                str(out_path),
            ],
            check=True,
        )
    finally:
        Path(list_file).unlink(missing_ok=True)


def cards(
    texts: list[str],
    out_path: Path,
    duration: float = DEFAULT_DURATION,
    durations: list[float] | None = None,
) -> Path:
    """Build a card-stack video. Returns the output path.

    If `durations` is provided, it must be the same length as `texts` and is
    used per-card. Otherwise, every card uses `duration`.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH")
    if durations is not None and len(durations) != len(texts):
        raise ValueError(
            f"durations ({len(durations)}) must match texts ({len(texts)})"
        )

    total = len(texts)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        parts: list[Path] = []
        for i, text in enumerate(texts, start=1):
            d = durations[i - 1] if durations is not None else duration
            part = tmp_dir / f"card_{i:02d}.mp4"
            render_card(text, i, total, d, part)
            parts.append(part)
        concat_mp4s(parts, out_path)
    return out_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("texts", nargs="*", default=DEFAULT_TEXT,
                        help="Card texts in order. Defaults to the Day 1 cards.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), type=Path,
                        help=f"Output mp4 path (default: {DEFAULT_OUT.relative_to(REPO)})")
    parser.add_argument("--duration", default=DEFAULT_DURATION, type=float,
                        help=f"Seconds per card (default: {DEFAULT_DURATION}). "
                             f"Ignored if --durations is set.")
    parser.add_argument("--durations", type=str, default=None,
                        help="Comma-separated per-card durations (one per text), "
                             "e.g. '1.04,1.24,0.70,0.88'. Overrides --duration.")
    args = parser.parse_args(argv)

    durations = None
    if args.durations:
        durations = [float(x) for x in args.durations.split(",")]

    out = cards(args.texts, args.out, args.duration, durations)
    if durations:
        total_dur = sum(durations)
        per_card = ", ".join(f"{d:.2f}s" for d in durations)
        print(f"[cards] wrote {out.relative_to(REPO)} — "
              f"{len(args.texts)} cards [{per_card}] = {total_dur:.2f}s total")
    else:
        total_dur = args.duration * len(args.texts)
        print(f"[cards] wrote {out.relative_to(REPO)} — "
              f"{len(args.texts)} cards × {args.duration:.1f}s = {total_dur:.1f}s total")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
