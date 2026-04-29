#!/usr/bin/env python3
"""
Stage 7: Publish to Instagram Reels + TikTok via the Post for Me API.

Mirrors the `publish-reel` Claude Code skill — same Post for Me flow, just
wrapped as a per-day script that fits the rest of the pipeline. Either this
script OR the skill works; pick whichever is more convenient.

Setup (one-time per machine):
  1. API key in macOS Keychain:
       security add-generic-password -a "$USER" -s "postforme-api-key-2" -w
  2. Load in ~/.zshrc:
       export POSTFORME_API_KEY="$(security find-generic-password -a "$USER" \\
                                     -s "postforme-api-key-2" -w)"
  3. Verify: $POSTFORME_API_KEY is set, prefix should be pfm_live or pfm_test.
  4. IG must be a Business or Creator account linked to a Facebook Page.

Usage:
    python pipeline/publish.py series/days/01-publish.json

The script will:
  1. Verify $POSTFORME_API_KEY is set.
  2. List connected social accounts; error if IG or TikTok missing.
  3. Upload the video via Post for Me's create-upload-url flow.
  4. Publish to all platforms in the config in one API call.
  5. Poll /v1/social-post-results for ~30 seconds.
  6. Save the receipt (post_id + per-platform permalinks) to the output path.

Config shape (series/days/NN-publish.json):
{
  "video":     "edits/day_NN/final.mp4",
  "caption":   "Day N of...",
  "platforms": ["instagram", "tiktok"],          // optional; default both
  "output":    "published/day_NN/receipt.json",
  "platform_configurations": { ... }             // optional, see Post for Me docs
}
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


REPO = Path(__file__).resolve().parent.parent
API = "https://api.postforme.dev"


def die(msg: str, code: int = 2) -> None:
    sys.stderr.write(f"[publish] ERROR: {msg}\n")
    sys.exit(code)


def get_token() -> str:
    tok = os.environ.get("POSTFORME_API_KEY", "").strip()
    if not tok:
        die(
            "POSTFORME_API_KEY not set in env. Load it from your keychain via\n"
            '       export POSTFORME_API_KEY="$(security find-generic-password '
            '-a \\"$USER\\" -s \\"postforme-api-key-2\\" -w)"'
        )
    if not (tok.startswith("pfm_live") or tok.startswith("pfm_test")):
        sys.stderr.write(
            f"[publish] WARN: token prefix is {tok[:8]}... — expected pfm_live "
            f"or pfm_test. Continuing anyway.\n"
        )
    return tok


def curl_json(args: list[str]) -> dict:
    """Run curl, parse stdout as JSON. Errors raised with full body."""
    proc = subprocess.run(
        ["curl", "-s", "-S", "-w", "\\n%{http_code}", *args],
        check=False, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        die(f"curl failed: {proc.stderr.strip() or proc.stdout.strip()}")
    body, _, code = proc.stdout.rpartition("\n")
    try:
        status = int(code.strip())
    except ValueError:
        status = 0
    if not body.strip():
        if status >= 400:
            die(f"empty body, http {status}")
        return {}
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        die(f"bad JSON (http {status}): {e}\n--- body ---\n{body[:500]}")
    if status >= 400:
        die(f"http {status}: {json.dumps(data, indent=2)[:500]}")
    return data


def list_accounts(token: str) -> list[dict]:
    out = curl_json([
        f"{API}/v1/social-accounts",
        "-H", f"Authorization: Bearer {token}",
    ])
    return out.get("data", [])


def find_account(accounts: list[dict], platform: str) -> Optional[dict]:
    for a in accounts:
        if a.get("platform", "").lower() == platform.lower():
            return a
    return None


def auth_url(token: str, platform: str) -> str:
    out = curl_json([
        "-X", "POST", f"{API}/v1/social-accounts/auth-url",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"platform": platform}),
    ])
    return out.get("url", "")


def upload_video(token: str, video_path: Path) -> str:
    """Use Post for Me's create-upload-url flow. Returns the public media_url."""
    sys.stderr.write(f"[publish] requesting upload URL...\n")
    init = curl_json([
        "-X", "POST", f"{API}/v1/media/create-upload-url",
        "-H", f"Authorization: Bearer {token}",
    ])
    upload_url = init.get("upload_url")
    media_url = init.get("media_url")
    if not upload_url or not media_url:
        die(f"create-upload-url missing fields: {init}")

    size_mb = video_path.stat().st_size / 1024 / 1024
    sys.stderr.write(f"[publish] PUT {video_path.name} ({size_mb:.1f} MB)...\n")
    proc = subprocess.run(
        [
            "curl", "-s", "-S", "-X", "PUT", upload_url,
            "--data-binary", f"@{video_path}",
            "-H", "Content-Type: video/mp4",
        ],
        check=False, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        die(f"upload PUT failed: {proc.stderr.strip()}")
    sys.stderr.write(f"[publish] uploaded → {media_url}\n")
    return media_url


def publish_post(token: str, caption: str, account_ids: list[str],
                 media_url: str, platform_configs: Optional[dict] = None) -> str:
    body: dict = {
        "caption": caption,
        "social_accounts": account_ids,
        "media": [{"url": media_url}],
    }
    if platform_configs:
        body["platform_configurations"] = platform_configs

    out = curl_json([
        "-X", "POST", f"{API}/v1/social-posts",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(body),
    ])
    post_id = out.get("id") or out.get("data", {}).get("id")
    if not post_id:
        die(f"publish response missing post id: {out}")
    return post_id


def poll_results(token: str, post_id: str, timeout: int = 60) -> list[dict]:
    deadline = time.time() + timeout
    last: list[dict] = []
    while time.time() < deadline:
        out = curl_json([
            f"{API}/v1/social-post-results?social_post_id={post_id}",
            "-H", f"Authorization: Bearer {token}",
        ])
        last = out.get("data", [])
        # Done when no platform is still 'pending' or 'processing'.
        if last and all(
            r.get("status", "").lower() not in {"pending", "processing", "queued"}
            for r in last
        ):
            return last
        time.sleep(3)
    return last


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", type=Path,
                        help="Path to NN-publish.json")
    args = parser.parse_args()

    cfg_path = args.config.resolve()
    cfg = json.loads(cfg_path.read_text())

    def resolve(p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else (REPO / path)

    video = resolve(cfg["video"])
    caption = cfg["caption"]
    platforms = cfg.get("platforms", ["instagram", "tiktok"])
    output_path = resolve(cfg["output"])
    platform_configs = cfg.get("platform_configurations") or None

    if not video.exists():
        die(f"video not found: {video}")

    token = get_token()

    sys.stderr.write(f"[publish] checking connected accounts...\n")
    accounts = list_accounts(token)
    sa_ids: list[str] = []
    missing: list[str] = []
    for p in platforms:
        a = find_account(accounts, p)
        if not a:
            missing.append(p)
        else:
            sa_ids.append(a["id"])
            sys.stderr.write(
                f"[publish]   {p}: {a.get('username', '?')}  ({a['id']})\n"
            )
    if missing:
        sys.stderr.write(
            f"[publish] missing connections: {', '.join(missing)}\n"
            f"[publish] generate auth URLs with:\n"
        )
        for p in missing:
            sys.stderr.write(
                f"    curl -s -X POST {API}/v1/social-accounts/auth-url \\\n"
                f"      -H \"Authorization: Bearer $POSTFORME_API_KEY\" \\\n"
                f"      -H \"Content-Type: application/json\" \\\n"
                f"      -d '{{\"platform\":\"{p}\"}}' | jq -r .url | xargs open\n"
            )
        die("connect missing platforms first; re-run when done")

    media_url = upload_video(token, video)

    sys.stderr.write(f"[publish] publishing to {', '.join(platforms)}...\n")
    post_id = publish_post(token, caption, sa_ids, media_url, platform_configs)
    sys.stderr.write(f"[publish] post_id: {post_id}\n")

    results = poll_results(token, post_id, timeout=90)
    receipt = {
        "post_id": post_id,
        "video": str(video.relative_to(REPO)) if video.is_relative_to(REPO) else str(video),
        "caption": caption,
        "platforms": platforms,
        "platform_configurations": platform_configs,
        "media_url": media_url,
        "results": results,
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2))

    rel = output_path.relative_to(REPO) if output_path.is_relative_to(REPO) else output_path
    sys.stderr.write(f"[publish] wrote receipt → {rel}\n")
    for r in results:
        plat = r.get("platform", "?")
        status = r.get("status", "?")
        link = r.get("permalink") or r.get("link") or ""
        sys.stderr.write(f"[publish]   {plat}: {status}  {link}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
