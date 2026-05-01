#!/usr/bin/env python3
"""
Stage 5: Burn captions into a video using transcript word timing.

Default engine: Remotion. Python maps the transcript from original word timing
into the tightened/assembled timeline, writes a canonical caption payload, then
asks the local Remotion sidecar in `captioner/` to render dynamic captions.

Fallback engine: ASS/libass via ffmpeg. This keeps the Day 1 renderer available
for machines that do not have Node/Remotion installed yet.

Usage:
    python pipeline/caption.py --config series/days/01-caption.json
    python pipeline/caption.py --config series/days/01-caption.json --engine ass

Pipeline order:
    tighten -> assemble -> caption -> speedup -> final

Captioning runs BEFORE speedup so timestamp math stays simple. The speedup at
the end speeds up the burned-in captions naturally.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ffmpeg_quality import h264_quality_args


REPO = Path(__file__).resolve().parent.parent
CAPTIONER_DIR = REPO / "captioner"


@dataclass
class Word:
    text: str
    start: float
    end: float
    display: str = ""
    role: str = "word"
    emphasis: bool = False
    phrase_id: str | None = None
    break_after: bool = False
    hidden: bool = False


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


@dataclass
class CaptionPage:
    words: list[Word]
    anchor: str
    style_preset: str

    @property
    def start(self) -> float:
        return self.words[0].start

    @property
    def end(self) -> float:
        return max(w.end for w in self.words)

    @property
    def text(self) -> str:
        return " ".join(w.display or w.text for w in self.words if not w.hidden and (w.display or w.text))


# ---- timeline transforms --------------------------------------------------

def map_to_combined(
    word_time: float,
    combined_offset: float,
    leading_trim: float = 0.0,
    max_original: Optional[float] = None,
    speed: float = 1.0,
) -> Optional[float]:
    """Map a word's time in a transcript to the combined-selfie timeline."""
    if word_time < leading_trim:
        return None
    if max_original is not None and word_time > max_original:
        return None
    if speed <= 0:
        raise ValueError(f"transcript speed must be positive, got {speed}")
    return combined_offset + ((word_time - leading_trim) / speed)


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


# ---- shared utilities -----------------------------------------------------

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def resolve_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else (REPO / path)


def css_color(value: Any, default: str) -> str:
    if not value:
        return default
    text = str(value).strip()
    if text.startswith("#") or text.startswith("rgb"):
        return text
    if re.fullmatch(r"[0-9a-fA-F]{6}", text):
        return f"#{text}"
    return default


def normalize_token(text: str) -> str:
    return text.lower().strip(".,!?;:'\"()[]{}<>“”‘’‐‑‒–—-")


def text_len(words: list[Word]) -> int:
    return len(" ".join(w.display or w.text for w in words if not w.hidden and (w.display or w.text)))


def visible_word_count(words: list[Word]) -> int:
    return len([w for w in words if not w.hidden and (w.display or w.text)])


DEFAULT_OMIT_STANDALONE_WORDS = {
    "a",
    "an",
    "and",
    "but",
    "for",
    "i",
    "it",
    "on",
    "so",
    "the",
    "to",
}


def omitted_standalone_words(cfg: dict[str, Any]) -> set[str]:
    raw = cfg.get("omitStandaloneWords", cfg.get("omit_standalone_words"))
    if raw is None:
        return set()
    if raw is True:
        return DEFAULT_OMIT_STANDALONE_WORDS
    if isinstance(raw, list):
        return {normalize_token(str(word)) for word in raw}
    return set()


def should_omit_page(page: CaptionPage, omit_words: set[str]) -> bool:
    visible = [w for w in page.words if not w.hidden and (w.display or w.text)]
    if len(visible) != 1:
        return False
    return normalize_token(visible[0].display or visible[0].text) in omit_words


def has_terminal_punctuation(word: Word) -> bool:
    return bool(re.search(r"[.!?;:]$", word.text.strip()))


def should_break_after(word: Word) -> bool:
    return word.break_after or has_terminal_punctuation(word)


def find_working_binary(name: str) -> str:
    """Find a working binary, skipping stale shims that exist but do not run."""
    candidates: list[Path] = []
    found = shutil.which(name)
    if found:
        candidates.append(Path(found))
    home = Path.home()
    candidates.extend([
        home / ".nix-profile" / "bin" / name,
        Path("/opt/homebrew/bin") / name,
        Path("/usr/local/bin") / name,
        Path("/usr/bin") / name,
    ])

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen or not candidate.exists():
            continue
        seen.add(candidate)
        proc = subprocess.run(
            [str(candidate), "-version"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if proc.returncode == 0:
            return str(candidate)
    raise RuntimeError(f"{name} not found on PATH or common install locations")


def probe_duration(path: Path) -> float:
    ffprobe = find_working_binary("ffprobe")
    out = subprocess.run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(out.stdout.strip())


# ---- transcript mapping ---------------------------------------------------

def merge_split_numeric_tokens(words: list[Word]) -> list[Word]:
    """Repair Whisper splits such as `2` + `,000` so paging sees one token."""
    merged: list[Word] = []
    i = 0
    while i < len(words):
        current = words[i]
        if (
            i + 1 < len(words) and
            re.fullmatch(r"\d+", current.text) and
            re.fullmatch(r",\d+[,.!?;:]*", words[i + 1].text)
        ):
            follower = words[i + 1]
            merged.append(Word(
                text=f"{current.text}{follower.text}",
                start=current.start,
                end=follower.end,
                display=current.display,
                role=current.role,
                emphasis=current.emphasis,
                phrase_id=current.phrase_id,
                break_after=follower.break_after,
                hidden=current.hidden,
            ))
            i += 2
            continue
        merged.append(current)
        i += 1
    return merged


def load_caption_words(cfg: dict[str, Any]) -> tuple[list[Word], list[tuple[float, float]]]:
    tighten_config = cfg.get("tighten_config")
    keep_windows: list[tuple[float, float]] = []
    if tighten_config:
        tighten_cfg = json.loads(resolve_path(tighten_config).read_text())
        keep_windows = [(float(w["start"]), float(w["end"])) for w in tighten_cfg["keep"]]

    words: list[Word] = []
    for tcfg in cfg["transcripts"]:
        trans = json.loads(resolve_path(tcfg["path"]).read_text())
        offset = float(tcfg.get("combined_offset", 0.0))
        leading_trim = float(tcfg.get("leading_trim", 0.0))
        speed = float(tcfg.get("speed", 1.0))
        max_original = tcfg.get("max_original")
        if max_original is not None:
            max_original = float(max_original)

        for seg in trans["segments"]:
            segment_words: list[Word] = []
            for w in seg.get("words", []):
                start_c = map_to_combined(w["start"], offset, leading_trim, max_original, speed)
                end_c = map_to_combined(w["end"], offset, leading_trim, max_original, speed)
                if start_c is None or end_c is None:
                    continue
                if keep_windows:
                    start_t = map_to_tightened(start_c, keep_windows)
                    end_t = map_to_tightened(end_c, keep_windows)
                    if start_t is None or end_t is None:
                        continue
                else:
                    start_t = start_c
                    end_t = end_c
                if end_t - start_t < 0.05:
                    end_t = start_t + 0.15
                text = str(w["word"]).strip()
                if text:
                    segment_words.append(Word(text=text, start=start_t, end=end_t))
            if segment_words:
                segment_words[-1].break_after = True
                words.extend(segment_words)

    words.sort(key=lambda w: w.start)
    words = merge_split_numeric_tokens(words)
    return words, keep_windows


# ---- Remotion payload generation -----------------------------------------

def build_phrase_specs(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    replacements = cfg.get("style", {}).get("text_replacements", {})
    specs: list[dict[str, Any]] = []

    def add(phrase: str, *, emphasis: bool, replacement: str | None = None) -> None:
        tokens = [normalize_token(t) for t in phrase.split()]
        tokens = [t for t in tokens if t]
        if len(tokens) < 2:
            return
        specs.append({
            "phrase": phrase,
            "tokens": tokens,
            "emphasis": emphasis,
            "replacement": replacement,
            "impact": False,
        })

    def add_impact(phrase: str) -> None:
        tokens = [normalize_token(t) for t in phrase.split()]
        tokens = [t for t in tokens if t]
        if len(tokens) < 2:
            return
        specs.append({
            "phrase": phrase,
            "tokens": tokens,
            "emphasis": True,
            "replacement": None,
            "impact": True,
        })

    for phrase in cfg.get("impactPhrases", []):
        add_impact(str(phrase))
    for term in cfg.get("emphasis_words", []):
        add(str(term), emphasis=True)
    for phrase in cfg.get("group_phrases", []):
        add(str(phrase), emphasis=False)
    for phrase in cfg.get("phrase_groups", []):
        add(str(phrase), emphasis=False)
    for old, new in replacements.items():
        add(str(old), emphasis=str(old).lower() in {
            str(t).lower() for t in cfg.get("emphasis_words", [])
        }, replacement=str(new))

    deduped: dict[tuple[str, ...], dict[str, Any]] = {}
    for spec in specs:
        key = tuple(spec["tokens"])
        prior = deduped.get(key)
        if prior is None or len(spec["tokens"]) > len(prior["tokens"]):
            deduped[key] = spec
        elif prior is not None:
            prior["emphasis"] = prior["emphasis"] or spec["emphasis"]
            prior["replacement"] = prior["replacement"] or spec["replacement"]
            prior["impact"] = prior.get("impact", False) or spec.get("impact", False)

    return sorted(deduped.values(), key=lambda s: -len(s["tokens"]))


def is_emphasis_word(text: str, cfg: dict[str, Any]) -> bool:
    lower = normalize_token(text)
    for term in cfg.get("emphasis_words", []):
        term_text = str(term).lower().strip()
        if " " in term_text:
            continue
        if lower == normalize_token(term_text):
            return True
    return False


def is_impact_word(text: str, cfg: dict[str, Any]) -> bool:
    lower = normalize_token(text)
    return lower in {normalize_token(str(term)) for term in cfg.get("impactWords", [])}


def display_word(text: str) -> str:
    stripped = text.strip()
    match = re.match(r"^(\W*)([\w']+)(\W*)$", stripped, flags=re.UNICODE)
    prefix = match.group(1) if match else ""
    core = match.group(2) if match else stripped
    suffix = match.group(3) if match else ""
    if not match:
        core = re.sub(r"[,.;:]+$", "", core)
        core = re.sub(r"[\"'“”‘’)\]}]+$", "", core)
        core = re.sub(r"^[\"'“”‘’([{]+", "", core)
        core = re.sub(r"^[,.;:]+", "", core)
    prefix = re.sub(r"^[\"'“”‘’([{]+", "", prefix)
    prefix = re.sub(r"^[,.;:]+", "", prefix)
    suffix = re.sub(r"[,.;:]+$", "", suffix)
    suffix = re.sub(r"[\"'“”‘’)\]}]+$", "", suffix)
    bare = normalize_token(core)
    acronym_map = {
        "ai": "AI",
        "api": "API",
        "cli": "CLI",
        "dm": "DM",
        "ig": "IG",
        "ui": "UI",
        "url": "URL",
        "x": "X",
    }
    number_words = {
        "thirty": "30",
    }
    if bare in acronym_map:
        return f"{prefix}{acronym_map[bare]}{suffix}"
    if bare in number_words:
        return f"{prefix}{number_words[bare]}{suffix}"
    return f"{prefix}{core}{suffix}"


def annotate_words(words: list[Word], cfg: dict[str, Any]) -> list[Word]:
    specs = build_phrase_specs(cfg)
    single_replacements = {
        normalize_token(str(old)): str(new)
        for old, new in cfg.get("style", {}).get("text_replacements", {}).items()
        if len([t for t in str(old).split() if normalize_token(t)]) == 1
    }
    impact_once_terms = {
        normalize_token(str(term))
        for term in cfg.get("impactOnceWords", cfg.get("impact_once_words", []))
    }
    impact_last_terms = {
        normalize_token(str(term))
        for term in cfg.get("impactLastWords", cfg.get("impact_last_words", []))
    }
    impact_last_indexes = {
        term: max(
            (idx for idx, word in enumerate(words) if normalize_token(word.text) == term),
            default=-1,
        )
        for term in impact_last_terms
    }
    used_once_terms: set[str] = set()

    def should_impact_word(word: Word, index: int) -> bool:
        lower = normalize_token(word.text)
        if lower in impact_last_terms:
            return index == impact_last_indexes.get(lower, -1)
        if lower in impact_once_terms and lower not in used_once_terms:
            used_once_terms.add(lower)
            return True
        return is_impact_word(word.text, cfg)

    out: list[Word] = []
    i = 0
    phrase_counter = 0

    while i < len(words):
        match = None
        for spec in specs:
            n = len(spec["tokens"])
            if i + n > len(words):
                continue
            candidate = [normalize_token(words[i + j].text) for j in range(n)]
            if candidate == spec["tokens"]:
                match = spec
                break

        if match is None:
            w = words[i]
            display = display_word(w.text)
            replacement = single_replacements.get(normalize_token(w.text))
            if replacement is not None:
                display = display_word(replacement)
            is_impact = should_impact_word(w, i)
            out.append(Word(
                text=w.text,
                start=w.start,
                end=w.end,
                display=display,
                role="impact" if is_impact else "word",
                emphasis=is_impact or is_emphasis_word(w.text, cfg),
                break_after=w.break_after,
            ))
            i += 1
            continue

        n = len(match["tokens"])
        phrase_id = f"phrase-{phrase_counter:03d}"
        phrase_counter += 1
        has_replacement = match.get("replacement") is not None
        replacement_tokens: list[str] = []
        if has_replacement:
            replacement_tokens = str(match["replacement"]).split()

        for j in range(n):
            w = words[i + j]
            display = display_word(w.text)
            hidden = False
            if has_replacement:
                if j < len(replacement_tokens):
                    display = display_word(replacement_tokens[j])
                else:
                    display = ""
                    hidden = True
            is_impact = not hidden and (
                bool(match.get("impact")) or should_impact_word(w, i + j)
            )
            out.append(Word(
                text=w.text,
                start=w.start,
                end=w.end,
                display=display,
                role="impact" if is_impact else "word",
                emphasis=is_impact or bool(match["emphasis"]) or is_emphasis_word(w.text, cfg),
                phrase_id=phrase_id if match.get("impact") else (None if is_impact else phrase_id),
                break_after=w.break_after,
                hidden=hidden,
            ))
        i += n

    return out


def group_units(words: list[Word]) -> list[list[Word]]:
    units: list[list[Word]] = []
    i = 0
    while i < len(words):
        word = words[i]
        if not word.phrase_id:
            units.append([word])
            i += 1
            continue

        phrase_id = word.phrase_id
        unit: list[Word] = []
        while i < len(words) and words[i].phrase_id == phrase_id:
            unit.append(words[i])
            i += 1
        units.append(unit)
    return units


def scene_value(
    cfg: dict[str, Any],
    t: float,
    key: str,
    default: str,
) -> str:
    for override in cfg.get("sceneOverrides", cfg.get("scene_overrides", [])):
        start = float(override.get("start", 0.0))
        end = float(override.get("end", 0.0))
        if start <= t < end and override.get(key):
            return str(override[key])
    return default


def build_caption_pages(words: list[Word], cfg: dict[str, Any]) -> list[CaptionPage]:
    max_words = int(cfg.get("maxWordsPerPage", cfg.get("max_words_per_page",
                    cfg.get("max_words_per_chunk", 3))))
    min_words = int(cfg.get("minWordsPerPage", 2))
    max_chars = int(cfg.get("maxCharsPerPage", cfg.get("max_chars_per_page", 24)))
    max_gap = float(cfg.get("maxGapWithinPage", 0.45))
    min_display = float(cfg.get("min_chunk_duration", cfg.get("minPageDuration", 0.40)))
    default_anchor = str(cfg.get("anchor", "lower_safe"))
    default_style = str(cfg.get("stylePreset", cfg.get("style_preset", "founder_pop")))
    impact_anchor = str(cfg.get("impactAnchor", "mid_safe"))
    impact_style = str(cfg.get("impactStylePreset", "impact_word"))
    omit_words = omitted_standalone_words(cfg)

    pages: list[CaptionPage] = []
    current: list[Word] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        start = current[0].start
        visible_words = [w for w in current if not w.hidden and (w.display or w.text)]
        is_impact_page = bool(visible_words) and all(w.role == "impact" for w in visible_words)
        pages.append(CaptionPage(
            words=current,
            anchor=impact_anchor if is_impact_page else scene_value(cfg, start, "anchor", default_anchor),
            style_preset=impact_style if is_impact_page else scene_value(cfg, start, "stylePreset", default_style),
        ))
        current = []

    for unit in group_units(words):
        if any(w.role == "impact" for w in unit):
            flush()
            current.extend(unit)
            flush()
            continue

        if current and should_break_after(current[-1]):
            flush()

        if current and unit[0].start - current[-1].end > max_gap:
            flush()

        candidate = current + unit
        candidate_word_count = len([w for w in candidate if not w.hidden and (w.display or w.text)])
        if current and (candidate_word_count > max_words or text_len(candidate) > max_chars):
            flush()
        current.extend(unit)
        if current and (
            visible_word_count(current) >= max_words or
            should_break_after(current[-1])
        ):
            flush()
    flush()

    if omit_words:
        pages = [page for page in pages if not should_omit_page(page, omit_words)]

    impact_hold = float(cfg.get("impactHoldSeconds", cfg.get("impact_hold_seconds", min_display)))
    for idx, page in enumerate(pages):
        visible_words = [w for w in page.words if not w.hidden and (w.display or w.text)]
        is_impact_page = bool(visible_words) and all(w.role == "impact" for w in visible_words)
        target_end = page.start + (impact_hold if is_impact_page else min_display)
        if page.end < target_end:
            if not is_impact_page and idx + 1 < len(pages):
                target_end = min(target_end, pages[idx + 1].start - 0.02)
            if target_end > page.end:
                page.words[-1].end = target_end

    return pages


def remotion_style(cfg: dict[str, Any]) -> dict[str, Any]:
    style = cfg.get("style", {})
    return {
        "fontFamily": cfg.get("fontFamily") or style.get("fontFamily") or "Manrope",
        "fontWeight": int(cfg.get("fontWeight") or style.get("fontWeight") or 800),
        "textColor": css_color(style.get("color"), "#FFFFFF"),
        "activeColor": css_color(style.get("activeColor") or style.get("emphasis_color"), "#FFA395"),
        "emphasisColor": css_color(style.get("emphasis_color"), "#FFA395"),
        "strokeColor": css_color(style.get("stroke_color") or style.get("outline_color"), "#0A0A0A"),
        "backColor": css_color(style.get("back_color"), "#0A0A0A"),
        "fontSize": int(cfg.get("fontSize") or style.get("remotion_size") or style.get("size") or 88),
        "activeScale": float(style.get("activeScale", 1.12)),
        "pageEnterFrames": int(style.get("pageEnterFrames", 5)),
        "wordRevealMode": str(style.get("wordRevealMode", style.get("word_reveal_mode", "all_at_once"))),
        "wordRevealFadeFrames": int(style.get("wordRevealFadeFrames", style.get("word_reveal_fade_frames", 2))),
        "videoDimAlpha": float(style.get("videoDimAlpha", style.get("video_dim_alpha", 0.0))),
        "captionMaxWidthPercent": float(style.get("captionMaxWidthPercent", style.get("caption_max_width_percent", 0.0)) or 0.0) or None,
        "oneLineBias": bool(style.get("oneLineBias", style.get("one_line_bias", False))),
        "minFontSize": int(style.get("minFontSize", style.get("min_font_size", 0)) or 0) or None,
        "oneLineMaxChars": int(style.get("oneLineMaxChars", style.get("one_line_max_chars", 0)) or 0) or None,
        "oneLineCharWidth": float(style.get("oneLineCharWidth", style.get("one_line_char_width", 0.0)) or 0.0) or None,
        "strokeWidth": float(style.get("strokeWidth", style.get("stroke_width", -1))),
        "lineHeight": float(style.get("lineHeight", style.get("line_height", 0.0)) or 0.0) or None,
        "wordGap": style.get("wordGap", style.get("word_gap")),
        "impactFontFamily": style.get("impactFontFamily", style.get("impact_font_family")),
        "impactFontWeight": int(style.get("impactFontWeight", style.get("impact_font_weight", cfg.get("fontWeight", 900))) or 900),
        "impactTextColor": css_color(style.get("impactTextColor", style.get("impact_text_color")), "#FFFFFF"),
        "impactStrokeColor": css_color(style.get("impactStrokeColor", style.get("impact_stroke_color")), "#0A0A0A"),
        "impactStrokeWidth": float(style.get("impactStrokeWidth", style.get("impact_stroke_width", 2.4))),
        "impactWordGap": style.get("impactWordGap", style.get("impact_word_gap")),
        "blackImpactTextColor": css_color(style.get("blackImpactTextColor", style.get("black_impact_text_color")), "#050505"),
        "blackImpactStrokeColor": css_color(style.get("blackImpactStrokeColor", style.get("black_impact_stroke_color")), "#FFFFFF"),
        "impactFontSize": int(style.get("impactFontSize", style.get("impact_font_size", 0)) or 0) or None,
        "impactMaxWidthPercent": float(style.get("impactMaxWidthPercent", style.get("impact_max_width_percent", 0.64))),
        "impactExitFrames": int(style.get("impactExitFrames", style.get("impact_exit_frames", 12))),
        "boxAlpha": float(style.get("remotion_box_alpha", 0.0)),
        "strokeAlpha": float(style.get("stroke_alpha", 0.58)),
        "uppercase": bool(style.get("fontUppercase", False)),
    }


def build_remotion_payload(
    cfg: dict[str, Any],
    input_path: Path,
    output_path: Path,
    pages: list[CaptionPage],
    words: list[Word],
) -> dict[str, Any]:
    width = int(cfg.get("width", 1080))
    height = int(cfg.get("height", 1920))
    fps = int(cfg.get("fps", 30))
    default_safe_zone = {"top": 0.12, "bottom": 0.22, "left": 0.08, "right": 0.08}
    safe_zone = cfg.get("safeZone", cfg.get("safe_zone", default_safe_zone))

    return {
        "version": 2,
        "engine": "remotion",
        "sourceVideo": str(input_path),
        "output": str(output_path),
        "width": width,
        "height": height,
        "fps": fps,
        "duration": probe_duration(input_path),
        "platform": cfg.get("platform", "reels"),
        "captionVariant": cfg.get("captionVariant", cfg.get("caption_variant", "founder_clean")),
        "safeZone": safe_zone,
        "style": remotion_style(cfg),
        "overlays": cfg.get("overlays", []),
        "pages": [
            {
                "start": round(page.start, 3),
                "end": round(page.end, 3),
                "anchor": page.anchor,
                "stylePreset": page.style_preset,
                "text": page.text,
                "words": [
                    {
                        "text": w.text,
                        "display": w.display or w.text,
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                        "role": w.role,
                        "emphasis": w.emphasis,
                        "phraseId": w.phrase_id,
                    }
                    for w in page.words
                    if not w.hidden and (w.display or w.text)
                ],
            }
            for page in pages
        ],
        "words": [
            {
                "text": w.text,
                "display": w.display or w.text,
                "start": round(w.start, 3),
                "end": round(w.end, 3),
                "role": w.role,
                "emphasis": w.emphasis,
                "phraseId": w.phrase_id,
            }
            for w in words
            if not w.hidden and (w.display or w.text)
        ],
    }


def render_remotion(payload_path: Path) -> None:
    script = CAPTIONER_DIR / "render-captioned.mjs"
    package_json = CAPTIONER_DIR / "package.json"
    node_modules = CAPTIONER_DIR / "node_modules"
    if not script.exists() or not package_json.exists():
        raise RuntimeError("captioner sidecar is missing")
    if not node_modules.exists():
        raise RuntimeError(
            "captioner dependencies are not installed. Run: cd captioner && npm install"
        )

    subprocess.run(
        ["node", str(script), "--config", str(payload_path)],
        cwd=REPO,
        check=True,
    )


def caption_remotion(cfg: dict[str, Any], input_path: Path, output_path: Path) -> Path:
    words, _keep_windows = load_caption_words(cfg)
    print(f"[caption] mapped {len(words)} words to caption timeline")
    annotated = annotate_words(words, cfg)
    pages = build_caption_pages(annotated, cfg)
    print(f"[caption] paged into {len(pages)} dynamic caption groups")

    payload = build_remotion_payload(cfg, input_path, output_path, pages, annotated)
    payload_path = output_path.parent / f"{output_path.stem}.captions.json"
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, indent=2))
    print(f"[caption] wrote {rel(payload_path)}")

    render_remotion(payload_path)
    print(f"[caption] wrote {rel(output_path)}")
    return output_path


# ---- ASS fallback ---------------------------------------------------------

def chunkify(
    words: list[Word],
    max_words: int = 3,
    emphasis_predicate=None,
    phrases: list[str] | None = None,
) -> list[Chunk]:
    """Group words into ASS chunks. Kept for the ffmpeg/libass fallback."""
    if phrases is None:
        phrases = []

    sorted_phrases = sorted(
        [[normalize_token(w) for w in p.split()] for p in phrases],
        key=lambda p: -len(p),
    )

    chunks: list[Chunk] = []
    current: list[Word] = []

    def flush() -> None:
        nonlocal current
        if current:
            chunks.append(Chunk(current))
            current = []

    i = 0
    while i < len(words):
        phrase_n = 0
        for phrase_words in sorted_phrases:
            n = len(phrase_words)
            if i + n > len(words):
                continue
            if [normalize_token(words[i + j].text) for j in range(n)] == phrase_words:
                phrase_n = n
                break

        if phrase_n > 0:
            flush()
            chunks.append(Chunk(words[i:i + phrase_n]))
            i += phrase_n
            continue

        w = words[i]
        is_single_emph = emphasis_predicate(w.text) if emphasis_predicate else False
        if is_single_emph:
            flush()
            chunks.append(Chunk([w]))
        else:
            current.append(w)
            if should_break_after(w) or len(current) >= max_words:
                flush()
        i += 1

    flush()
    return chunks


def hex_to_ass(rgb_hex: str) -> str:
    rgb_hex = rgb_hex.lstrip("#").lower()
    r, g, b = rgb_hex[0:2], rgb_hex[2:4], rgb_hex[4:6]
    return f"&H00{b}{g}{r}".upper()


def fmt_ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def resolve_font(declared: str) -> str:
    user_font = REPO / "fonts" / "main-bold.ttf"
    if user_font.exists():
        return str(user_font)
    return declared


def make_ass(
    chunks: list[Chunk],
    emphasis_predicate,
    style: dict[str, Any],
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
    back_color = hex_to_ass(style.get("back_color", "100E0B"))
    outline_w = style.get("outline", 4)
    shadow = style.get("shadow", 0)
    y_pos = style.get("y_position", 0.78)
    margin_v = int(height * (1 - y_pos))
    border_style = style.get("border_style", 3)
    box_alpha = style.get("box_alpha", "26")
    box_fill = f"&H{box_alpha}{back_color[4:]}"

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
        text = re.sub(r"[,.;:]+$", "", text)
        text = text.replace("\n", " ")
        for old, new in replacements.items():
            text = text.replace(old.upper(), new)
        style_name = "Emphasis" if emphasis_predicate(c.text) else "Default"
        lines.append(
            f"Dialogue: 0,{fmt_ass_time(c.start)},{fmt_ass_time(c.end)},"
            f"{style_name},,0,0,0,,{text}"
        )
    return "\n".join(lines) + "\n"


def caption_ass(cfg: dict[str, Any], input_path: Path, output_path: Path) -> Path:
    words, _keep_windows = load_caption_words(cfg)
    print(f"[caption] mapped {len(words)} words to caption timeline")

    emphasis_terms = [str(t).lower() for t in cfg.get("emphasis_words", [])]

    def is_emphasized(text: str) -> bool:
        lower = normalize_token(text)
        for term in emphasis_terms:
            if normalize_token(term) in lower:
                return True
        return False

    multi_word_emph = [t for t in cfg.get("emphasis_words", []) if " " in str(t)]
    group_phrases = cfg.get("group_phrases", [])
    all_phrases = list(set([str(t) for t in multi_word_emph + group_phrases]))

    chunks = chunkify(
        words,
        max_words=cfg.get("max_words_per_chunk", 3),
        emphasis_predicate=is_emphasized,
        phrases=all_phrases,
    )
    print(f"[caption] chunked into {len(chunks)} ASS caption groups")

    min_display = float(cfg.get("min_chunk_duration", 0.40))
    for i, c in enumerate(chunks):
        target_end = c.start + min_display
        if c.end < target_end:
            if i + 1 < len(chunks):
                target_end = min(target_end, chunks[i + 1].start - 0.02)
            if target_end > c.end:
                c.words[-1].end = target_end

    style = cfg.get("style", {})
    width = int(cfg.get("width", 1080))
    height = int(cfg.get("height", 1920))
    ass_content = make_ass(chunks, is_emphasized, style, width, height)

    ass_path = output_path.parent / f"{output_path.stem}.ass"
    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text(ass_content)
    print(f"[caption] wrote {rel(ass_path)}")

    ffmpeg = find_working_binary("ffmpeg")
    subprocess.run(
        [
            ffmpeg, "-y", "-loglevel", "error",
            "-i", str(input_path),
            "-vf", f"subtitles={ass_path}",
            *h264_quality_args(),
            "-c:a", "copy",
            str(output_path),
        ],
        check=True,
    )
    print(f"[caption] wrote {rel(output_path)}")
    return output_path


# ---- driver ---------------------------------------------------------------

def caption(config_path: Path, engine: str | None = None) -> Path:
    cfg = json.loads(config_path.read_text())
    input_path = resolve_path(cfg["input"])
    output_path = resolve_path(cfg["output"])

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    selected = (engine or cfg.get("engine") or "remotion").lower()
    if selected == "remotion":
        return caption_remotion(cfg, input_path, output_path)
    if selected == "ass":
        return caption_ass(cfg, input_path, output_path)
    raise ValueError(f"unknown caption engine: {selected}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--engine",
        choices=["remotion", "ass"],
        default=None,
        help="Caption renderer to use. Defaults to config.engine or remotion.",
    )
    args = parser.parse_args(argv)
    caption(args.config.resolve(), engine=args.engine)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
