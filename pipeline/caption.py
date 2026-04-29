#!/usr/bin/env python3
"""
Stage 5: Burn captions into a video using transcript word timing.

Reads transcripts (with original word timestamps), applies the same timestamp
transforms that tighten + assemble apply, generates an ASS subtitle file with
chunked captions in our cream-on-dark / orange-accent palette, and burns them
into the video via ffmpeg's subtitles filter.

Usage:
    python pipeline/caption.py --config series/days/01-caption.json

Pipeline order:
    tighten → assemble → caption → speedup → final

Captioning runs BEFORE speedup so timestamp math stays simple. The speedup at
the end speeds up the burned-in captions naturally.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


REPO = Path(__file__).resolve().parent.parent


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class Chunk:
    words: list[Word]

    @property
    def start(self) -> float:
        return self.words[0].start

    @property
    def end(self) -> float:
        return max(w.end for w in self.words)

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)


# ---- timestamp transforms -------------------------------------------------

def map_to_combined(
    word_time: float,
    combined_offset: float,
    leading_trim: float = 0.0,
    max_original: Optional[float] = None,
) -> Optional[float]:
    """Map a word's time in a transcript to the combined-selfie timeline."""
    if word_time < leading_trim:
        return None
    if max_original is not None and word_time > max_original:
        return None
    return combined_offset + (word_time - leading_trim)


def map_to_tightened(
    combined_time: float,
    keep_windows: list[tuple[float, float]],
) -> Optional[float]:
    """Map a combined-time to the tightened timeline. None if in a removed gap."""
    cum = 0.0
    for start, end in keep_windows:
        if start <= combined_time <= end:
            return cum + (combined_time - start)
        cum += end - start
    return None


# ---- chunking -------------------------------------------------------------

def chunkify(
    words: list[Word],
    max_words: int = 3,
    emphasis_predicate=None,
    phrases: list[str] | None = None,
) -> list[Chunk]:
    """Group words into chunks.

    Phrase matching first — if upcoming words match a phrase from the `phrases`
    list (case/punct-insensitive), emit them as a single atomic chunk. This is
    how 'Claude plugin' / 'follow and comment' / 'free guide' stay together
    rather than getting split by max_words or punct.

    Otherwise: a single word that matches the emphasis_predicate gets its own
    chunk; remaining words flow into chunks bounded by punctuation or max_words.
    """
    if phrases is None:
        phrases = []

    # Longer phrases tried first — so "follow and comment" matches before "follow".
    sorted_phrases = sorted(
        [p.lower().split() for p in phrases],
        key=lambda p: -len(p),
    )

    chunks: list[Chunk] = []
    current: list[Word] = []

    def flush():
        nonlocal current
        if current:
            chunks.append(Chunk(current))
            current = []

    def normalize(text: str) -> str:
        return text.lower().strip(".,!?;:'\" ")

    i = 0
    while i < len(words):
        # Try to match a phrase starting at words[i].
        phrase_n = 0
        for phrase_words in sorted_phrases:
            n = len(phrase_words)
            if i + n > len(words):
                continue
            if [normalize(words[i + j].text) for j in range(n)] == phrase_words:
                phrase_n = n
                break

        if phrase_n > 0:
            flush()
            chunks.append(Chunk(words[i:i + phrase_n]))
            i += phrase_n
            continue

        w = words[i]
        is_single_emph = emphasis_predicate(w.text) if emphasis_predicate else False
        ends_with_punct = bool(re.search(r"[.,!?;:]$", w.text))

        if is_single_emph:
            flush()
            chunks.append(Chunk([w]))
        else:
            current.append(w)
            if ends_with_punct or len(current) >= max_words:
                flush()
        i += 1

    flush()
    return chunks


# ---- ASS generation -------------------------------------------------------

def hex_to_ass(rgb_hex: str) -> str:
    """Convert RRGGBB to ASS &H00BBGGRR."""
    rgb_hex = rgb_hex.lstrip("#").lower()
    r, g, b = rgb_hex[0:2], rgb_hex[2:4], rgb_hex[4:6]
    return f"&H00{b}{g}{r}".upper()


def fmt_ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def resolve_font(declared: str) -> str:
    """If the user dropped fonts/main-bold.ttf into the repo, prefer that.
    Otherwise use the declared font name (rendered via fontconfig)."""
    user_font = REPO / "fonts" / "main-bold.ttf"
    if user_font.exists():
        return str(user_font)
    return declared


def make_ass(
    chunks: list[Chunk],
    emphasis_predicate,
    style: dict,
    width: int,
    height: int,
) -> str:
    declared_font = style.get("font", "Liberation Sans Bold")
    font = resolve_font(declared_font)
    size = style.get("size", 92)
    emph_mult = float(style.get("emphasis_size_multiplier", 1.0))
    emphasis_size = int(round(size * emph_mult))
    color = hex_to_ass(style.get("color", "F4EAD5"))
    emphasis_color = hex_to_ass(style.get("emphasis_color", "F2A03A"))
    outline_color = hex_to_ass(style.get("outline_color", "100E0B"))
    back_color = hex_to_ass(style.get("back_color", "100E0B"))
    outline_w = style.get("outline", 4)
    shadow = style.get("shadow", 0)
    y_pos = style.get("y_position", 0.78)
    margin_v = int(height * (1 - y_pos))
    # BorderStyle: 1 = outline+shadow, 3 = opaque box (pill behind text).
    border_style = style.get("border_style", 3)
    # ASS spec: alpha 00 = opaque, FF = transparent. We want ~85% opaque pill.
    box_alpha = style.get("box_alpha", "26")  # 0x26 ≈ 15% transparent

    # When BorderStyle=3, OutlineColour becomes the box fill color.
    # Add alpha override for the box.
    box_fill = f"&H{box_alpha}{back_color[4:]}"  # splice alpha into &H00BBGGRR

    header = (
        f"[Script Info]\n"
        f"ScriptType: v4.00+\n"
        f"PlayResX: {width}\n"
        f"PlayResY: {height}\n"
        f"WrapStyle: 0\n"
        f"ScaledBorderAndShadow: yes\n\n"
        f"[V4+ Styles]\n"
        f"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        f"OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
        f"ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        f"MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font},{size},{color},&H000000FF,{box_fill},"
        f"&H00000000,-1,0,0,0,100,100,0,0,{border_style},{outline_w},{shadow},2,40,40,{margin_v},1\n"
        f"Style: Emphasis,{font},{emphasis_size},{emphasis_color},&H000000FF,{box_fill},"
        f"&H00000000,-1,0,0,0,100,100,0,0,{border_style},{outline_w},{shadow},2,40,40,{margin_v},1\n\n"
        f"[Events]\n"
        f"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    replacements = style.get("text_replacements", {})

    lines = [header]
    for c in chunks:
        text = c.text.upper()
        text = re.sub(r"[,.;:]+$", "", text)  # drop trailing punctuation
        text = text.replace("\n", " ")
        # Apply text replacements (e.g. "DAY ONE" → "DAY 1")
        for old, new in replacements.items():
            text = text.replace(old.upper(), new)
        is_emph = emphasis_predicate(c.text)
        style_name = "Emphasis" if is_emph else "Default"
        lines.append(
            f"Dialogue: 0,{fmt_ass_time(c.start)},{fmt_ass_time(c.end)},"
            f"{style_name},,0,0,0,,{text}"
        )
    return "\n".join(lines) + "\n"


# ---- driver ---------------------------------------------------------------

def caption(config_path: Path) -> Path:
    cfg = json.loads(config_path.read_text())

    def resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else (REPO / path)

    input_path = resolve(cfg["input"])
    output_path = resolve(cfg["output"])
    tighten_cfg = json.loads(resolve(cfg["tighten_config"]).read_text())
    keep_windows = [(float(w["start"]), float(w["end"])) for w in tighten_cfg["keep"]]

    emphasis_terms = [t.lower() for t in cfg.get("emphasis_words", [])]

    def is_emphasized(text: str) -> bool:
        lower = text.lower().strip(".,!?;:'\" ")
        for term in emphasis_terms:
            if term in lower:
                return True
        return False

    # Collect all words in tightened timeline.
    all_words: list[Word] = []
    for tcfg in cfg["transcripts"]:
        trans = json.loads(resolve(tcfg["path"]).read_text())
        offset = float(tcfg.get("combined_offset", 0.0))
        leading_trim = float(tcfg.get("leading_trim", 0.0))
        max_original = tcfg.get("max_original")
        if max_original is not None:
            max_original = float(max_original)

        for seg in trans["segments"]:
            for w in seg.get("words", []):
                start_c = map_to_combined(w["start"], offset, leading_trim, max_original)
                end_c = map_to_combined(w["end"], offset, leading_trim, max_original)
                if start_c is None or end_c is None:
                    continue
                start_t = map_to_tightened(start_c, keep_windows)
                end_t = map_to_tightened(end_c, keep_windows)
                if start_t is None or end_t is None:
                    continue
                # Skip very short words (artifacts of whisper)
                if end_t - start_t < 0.05:
                    end_t = start_t + 0.15
                all_words.append(Word(text=w["word"].strip(), start=start_t, end=end_t))

    all_words.sort(key=lambda w: w.start)
    print(f"[caption] mapped {len(all_words)} words to tightened timeline")

    # Phrases that must stay together as a chunk: any multi-word emphasis
    # term, plus any explicitly listed group_phrases (e.g. "follow and comment"
    # which we want grouped but not emphasized).
    multi_word_emph = [t for t in cfg.get("emphasis_words", []) if " " in t]
    group_phrases = cfg.get("group_phrases", [])
    all_phrases = list(set(multi_word_emph + group_phrases))

    chunks = chunkify(
        all_words,
        max_words=cfg.get("max_words_per_chunk", 3),
        emphasis_predicate=is_emphasized,
        phrases=all_phrases,
    )
    print(f"[caption] chunked into {len(chunks)} caption groups "
          f"(phrases: {len(all_phrases)} configured)")

    # Extend short chunks so they're readable (min 0.4s display time)
    min_display = float(cfg.get("min_chunk_duration", 0.40))
    for i, c in enumerate(chunks):
        target_end = c.start + min_display
        if c.end < target_end:
            # Don't overlap with next chunk
            if i + 1 < len(chunks):
                target_end = min(target_end, chunks[i + 1].start - 0.02)
            if target_end > c.end:
                c.words[-1].end = target_end

    style = cfg.get("style", {})
    width = int(cfg.get("width", 1080))
    height = int(cfg.get("height", 1920))
    ass_content = make_ass(chunks, is_emphasized, style, width, height)

    ass_path = output_path.parent / (output_path.stem + ".ass")
    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text(ass_content)
    print(f"[caption] wrote {ass_path.relative_to(REPO)}")

    # Burn captions via ffmpeg subtitles filter.
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(input_path),
            "-vf", f"subtitles={ass_path}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-c:a", "copy",
            str(output_path),
        ],
        check=True,
    )
    print(f"[caption] wrote {output_path.relative_to(REPO)}")
    return output_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args(argv)
    caption(args.config.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
