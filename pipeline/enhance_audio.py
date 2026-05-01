#!/usr/bin/env python3
"""
Enhance spoken voice audio for short-form video.

The stage extracts the source audio, sends it to a speech enhancement provider,
then muxes the enhanced audio back into the original video without touching the
video stream. This keeps caption timing and visual edits stable.

Provider selection:
    auto        Cleanvoice if configured, then ElevenLabs, then Resemble, else local
    cleanvoice  Studio polish for decent phone recordings
    elevenlabs  Voice isolation for noisy clips / music / background ambience
    resemble    Async noise removal + normalization + studio sound
    local       Offline ffmpeg denoise/compress/loudnorm fallback

Usage:
    python3 pipeline/enhance_audio.py edits/day_02/proxy.mp4 \\
        --provider auto --out edits/day_02/proxy.voice.mp4

    CLEANVOICE_API_KEY=... python3 pipeline/enhance_audio.py input.mp4 \\
        --provider cleanvoice --out output.mp4

    ELEVENLABS_API_KEY=... python3 pipeline/enhance_audio.py input.mp4 \\
        --provider elevenlabs --out output.mp4

Environment:
    CLEANVOICE_API_KEY
    ELEVENLABS_API_KEY
    RESEMBLE_API_KEY
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from ffmpeg_quality import aac_quality_args


REPO = Path(__file__).resolve().parent.parent

CLEANVOICE_API = "https://api.cleanvoice.ai/v2"
ELEVENLABS_API = "https://api.elevenlabs.io/v1"
RESEMBLE_API = "https://app.resemble.ai/api/v2"

LOCAL_AUDIO_FILTER = ",".join(
    [
        "highpass=f=80",
        "afftdn=nr=10",
        "acompressor=threshold=-20dB:ratio=3:attack=20:release=250",
        "loudnorm=I=-14:LRA=11:TP=-1.5",
        "aresample=48000",
    ]
)


class EnhanceError(RuntimeError):
    pass


def rel(path: Path) -> str:
    return str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path)


def load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE lines without overwriting the shell environment."""
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip().strip("\"'")
        os.environ[key] = value


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
            subprocess.run(
                [candidate, "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return candidate
        except (OSError, subprocess.CalledProcessError):
            continue
    raise EnhanceError(f"{name} not found")


def require_key(provider: str, explicit: str | None, env_name: str) -> str:
    key = explicit or os.environ.get(env_name)
    if not key:
        raise EnhanceError(f"{provider} requires --api-key or {env_name}")
    return key


def http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: int = 120,
) -> tuple[bytes, dict[str, str]]:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read(), dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise EnhanceError(f"{method} {url} failed: HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise EnhanceError(f"{method} {url} failed: {exc}") from exc


def http_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req_headers = {"Accept": "application/json", **(headers or {})}
    if payload is not None:
        req_headers["Content-Type"] = "application/json"
    raw, _ = http_request(method, url, headers=req_headers, data=body, timeout=timeout)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise EnhanceError(f"{method} {url} returned non-JSON response") from exc


def download(url: str, out_path: Path, *, headers: dict[str, str] | None = None) -> Path:
    raw, _ = http_request("GET", url, headers=headers, timeout=300)
    out_path.write_bytes(raw)
    return out_path


def multipart_body(
    *,
    fields: dict[str, str],
    files: dict[str, Path],
) -> tuple[bytes, str]:
    boundary = f"----contentcopilot-{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                str(value).encode(),
                b"\r\n",
            ]
        )

    for name, path in files.items():
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="{name}"; '
                    f'filename="{path.name}"\r\n'
                ).encode(),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                path.read_bytes(),
                b"\r\n",
            ]
        )

    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def has_video_stream(path: Path) -> bool:
    proc = subprocess.run(
        [
            tool("ffprobe"),
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(proc.stdout.strip())


def extract_voice_track(source: Path, out_wav: Path) -> None:
    subprocess.run(
        [
            tool("ffmpeg"),
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
            str(out_wav),
        ],
        check=True,
    )


def mux_enhanced_audio(source_video: Path, enhanced_audio: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            tool("ffmpeg"),
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source_video),
            "-i",
            str(enhanced_audio),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-filter:a",
            "apad",
            *aac_quality_args(),
            "-shortest",
            "-movflags",
            "+faststart",
            str(out_path),
        ],
        check=True,
    )


def polish_audio_only(source_audio: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            tool("ffmpeg"),
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(source_audio),
            "-vn",
            "-af",
            LOCAL_AUDIO_FILTER,
            *aac_quality_args(),
            str(out_path),
        ],
        check=True,
    )


def local_enhance(source: Path, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if has_video_stream(source):
        subprocess.run(
            [
                tool("ffmpeg"),
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-filter_complex",
                f"[0:a]{LOCAL_AUDIO_FILTER},apad[a]",
                "-map",
                "0:v:0",
                "-map",
                "[a]",
                "-c:v",
                "copy",
                *aac_quality_args(),
                "-shortest",
                "-movflags",
                "+faststart",
                str(out_path),
            ],
            check=True,
        )
    else:
        polish_audio_only(source, out_path)
    return out_path


def cleanvoice_enhance(
    audio_path: Path,
    out_path: Path,
    *,
    api_key: str,
    poll_interval: float,
    timeout_seconds: float,
) -> Path:
    sys.stderr.write("[enhance-audio] cleanvoice: requesting upload URL\n")
    content_type = mimetypes.guess_type(audio_path.name)[0] or "audio/wav"
    try:
        upload = http_json(
            "POST",
            f"{CLEANVOICE_API}/uploads",
            headers={"X-API-Key": api_key},
            payload={"filename": audio_path.name, "content_type": content_type},
            timeout=60,
        )
    except EnhanceError:
        upload = http_json(
            "POST",
            f"{CLEANVOICE_API}/upload?filename={urllib.parse.quote(audio_path.name)}",
            headers={"X-API-Key": api_key},
            timeout=60,
        )
    signed_url = upload.get("signedUrl") or upload.get("signed_url") or upload.get("upload_url")
    if not signed_url:
        raise EnhanceError(f"Cleanvoice upload response missing signed URL: {upload}")

    sys.stderr.write("[enhance-audio] cleanvoice: uploading extracted voice track\n")
    http_request(
        "PUT",
        signed_url,
        headers={"Content-Type": content_type},
        data=audio_path.read_bytes(),
        timeout=300,
    )

    file_url = upload.get("file_url") or upload.get("fileUrl") or signed_url.split("?", 1)[0]
    payload = {
        "input": {
            "files": [file_url],
            "config": {
                "remove_noise": True,
                "studio_sound": True,
                "normalize": True,
                "target_lufs": -14,
                "export_format": "wav",
            },
        }
    }
    sys.stderr.write("[enhance-audio] cleanvoice: starting studio polish edit\n")
    edit = http_json(
        "POST",
        f"{CLEANVOICE_API}/edits",
        headers={"X-API-Key": api_key},
        payload=payload,
        timeout=60,
    )
    edit_id = edit.get("id") or edit.get("edit_id")
    if not edit_id:
        raise EnhanceError(f"Cleanvoice edit response missing id: {edit}")

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status_payload = http_json(
            "GET",
            f"{CLEANVOICE_API}/edits/{edit_id}",
            headers={"X-API-Key": api_key},
            timeout=60,
        )
        status = str(status_payload.get("status", "")).upper()
        sys.stderr.write(f"[enhance-audio] cleanvoice: {edit_id} {status}\n")
        if status == "SUCCESS":
            result = status_payload.get("result") or {}
            download_url = (
                result.get("download_url")
                or result.get("downloadUrl")
                or status_payload.get("download_url")
            )
            if not download_url:
                raise EnhanceError(f"Cleanvoice success missing download URL: {status_payload}")
            return download(download_url, out_path)
        if status == "FAILURE":
            raise EnhanceError(f"Cleanvoice edit failed: {status_payload}")
        time.sleep(poll_interval)

    raise EnhanceError(f"Cleanvoice edit timed out after {timeout_seconds:.0f}s: {edit_id}")


def elevenlabs_enhance(audio_path: Path, out_path: Path, *, api_key: str) -> Path:
    body, content_type = multipart_body(fields={}, files={"audio": audio_path})
    sys.stderr.write("[enhance-audio] elevenlabs: isolating voice\n")
    raw, headers = http_request(
        "POST",
        f"{ELEVENLABS_API}/audio-isolation",
        headers={"xi-api-key": api_key, "Content-Type": content_type},
        data=body,
        timeout=300,
    )
    response_type = headers.get("Content-Type", "")
    if "application/json" in response_type:
        raise EnhanceError(f"ElevenLabs returned JSON instead of audio: {raw[:500]!r}")
    out_path.write_bytes(raw)
    return out_path


def resemble_enhance(
    audio_path: Path,
    out_path: Path,
    *,
    api_key: str,
    poll_interval: float,
    timeout_seconds: float,
) -> Path:
    fields = {
        "enhancement_engine": "v2",
        "remove_noise": "true",
        "normalize": "true",
        "studio_sound": "true",
    }
    body, content_type = multipart_body(fields=fields, files={"audio_file": audio_path})
    sys.stderr.write("[enhance-audio] resemble: starting audio enhancement\n")
    raw, _ = http_request(
        "POST",
        f"{RESEMBLE_API}/audio_enhancements",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": content_type},
        data=body,
        timeout=120,
    )
    try:
        created = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise EnhanceError("Resemble create enhancement returned non-JSON response") from exc

    enhancement_id = created.get("uuid")
    if not enhancement_id:
        raise EnhanceError(f"Resemble response missing uuid: {created}")

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status_payload = http_json(
            "GET",
            f"{RESEMBLE_API}/audio_enhancements/{enhancement_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60,
        )
        status = str(status_payload.get("status", "")).lower()
        sys.stderr.write(f"[enhance-audio] resemble: {enhancement_id} {status}\n")
        if status == "completed":
            download_url = status_payload.get("enhanced_audio_url")
            if not download_url:
                raise EnhanceError(f"Resemble success missing enhanced_audio_url: {status_payload}")
            return download(download_url, out_path)
        if status == "failed":
            raise EnhanceError(f"Resemble enhancement failed: {status_payload}")
        time.sleep(poll_interval)

    raise EnhanceError(f"Resemble enhancement timed out after {timeout_seconds:.0f}s: {enhancement_id}")


def choose_provider(provider: str) -> str:
    if provider != "auto":
        return provider
    if os.environ.get("CLEANVOICE_API_KEY"):
        return "cleanvoice"
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    if os.environ.get("RESEMBLE_API_KEY"):
        return "resemble"
    return "local"


def enhance_audio(
    source: Path,
    out_path: Path,
    *,
    provider: str,
    api_key: str | None = None,
    poll_interval: float = 5.0,
    timeout_seconds: float = 600.0,
    keep_extracted_audio: Path | None = None,
) -> Path:
    if not source.exists():
        raise FileNotFoundError(source)

    selected = choose_provider(provider)
    sys.stderr.write(f"[enhance-audio] provider={selected}\n")

    if selected == "local":
        local_enhance(source, out_path)
        sys.stderr.write(f"[enhance-audio] wrote {rel(out_path)}\n")
        return out_path

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        extracted = tmp_dir / f"{source.stem}.voice.wav"
        enhanced = tmp_dir / f"{source.stem}.{selected}.wav"
        extract_voice_track(source, extracted)

        if keep_extracted_audio:
            keep_extracted_audio.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(extracted, keep_extracted_audio)

        if selected == "cleanvoice":
            cleanvoice_enhance(
                extracted,
                enhanced,
                api_key=require_key("Cleanvoice", api_key, "CLEANVOICE_API_KEY"),
                poll_interval=poll_interval,
                timeout_seconds=timeout_seconds,
            )
        elif selected == "elevenlabs":
            elevenlabs_enhance(
                extracted,
                enhanced,
                api_key=require_key("ElevenLabs", api_key, "ELEVENLABS_API_KEY"),
            )
        elif selected == "resemble":
            resemble_enhance(
                extracted,
                enhanced,
                api_key=require_key("Resemble", api_key, "RESEMBLE_API_KEY"),
                poll_interval=poll_interval,
                timeout_seconds=timeout_seconds,
            )
        else:
            raise EnhanceError(f"unsupported provider: {selected}")

        if has_video_stream(source):
            mux_enhanced_audio(source, enhanced, out_path)
        else:
            shutil.copy2(enhanced, out_path)

    sys.stderr.write(f"[enhance-audio] wrote {rel(out_path)}\n")
    return out_path


def main(argv: list[str]) -> int:
    load_env_file(REPO / ".env.local")

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="Input audio or video file")
    parser.add_argument("--out", type=Path, required=True, help="Enhanced output path")
    parser.add_argument(
        "--provider",
        choices=["auto", "cleanvoice", "elevenlabs", "resemble", "local"],
        default=os.environ.get("AUDIO_ENHANCE_PROVIDER", "auto"),
        help="Enhancement provider (default: auto)",
    )
    parser.add_argument("--api-key", help="Provider API key; otherwise read provider env var")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=600.0, help="Async provider timeout in seconds")
    parser.add_argument(
        "--keep-extracted-audio",
        type=Path,
        help="Optional path to save the extracted mono WAV sent to the provider",
    )
    args = parser.parse_args(argv)

    try:
        enhance_audio(
            args.input.resolve(),
            args.out.resolve(),
            provider=args.provider,
            api_key=args.api_key,
            poll_interval=args.poll_interval,
            timeout_seconds=args.timeout,
            keep_extracted_audio=args.keep_extracted_audio.resolve()
            if args.keep_extracted_audio
            else None,
        )
    except (EnhanceError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"enhance_audio: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
