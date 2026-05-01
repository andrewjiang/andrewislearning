"""Shared ffmpeg encoding presets for social video exports."""
from __future__ import annotations


DEFAULT_VIDEO_CRF = 16
DEFAULT_VIDEO_PRESET = "slow"
DEFAULT_AUDIO_BITRATE = "256k"


def h264_quality_args(
    *,
    crf: int = DEFAULT_VIDEO_CRF,
    preset: str = DEFAULT_VIDEO_PRESET,
    level: str = "4.2",
    faststart: bool = True,
) -> list[str]:
    """High-quality H.264 args compatible with Instagram/TikTok style uploads."""
    args = [
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", preset,
        "-crf", str(crf),
        "-profile:v", "high",
        "-level:v", level,
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        "-colorspace", "bt709",
    ]
    if faststart:
        args.extend(["-movflags", "+faststart"])
    return args


def aac_quality_args(*, bitrate: str = DEFAULT_AUDIO_BITRATE) -> list[str]:
    return ["-c:a", "aac", "-b:a", bitrate]
