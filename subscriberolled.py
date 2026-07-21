#!/usr/bin/env python3.14
"""
YouTube Subscriber Watcher + Rickroll Prank
==========================================
Modernized version for Python 3.14+.

What does it do?
- Periodically checks the subscriber count of the specified YouTube channel.
- Plays a Rickroll in the browser whenever the subscriber count increases.

SECURITY NOTE
-------------
API key and channel ID are loaded from a ".env" file (see ".env.example").
Never commit ".env" to git — it's already listed in ".gitignore".
If you share this repo, only ".env.example" should go public.

Setup
-----
1) Copy the template and fill in your real values:
       cp .env.example .env
2) Install dependencies:
       pip install requests python-dotenv --break-system-packages

Run
---
    python3 youtube_watcher.py
    python3 youtube_watcher.py --interval 60
    python3 youtube_watcher.py --api-key XXX --channel-id YYY
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the project folder into environment variables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("youtube_watcher")

RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/channels"


@dataclass(slots=True)
class WatcherConfig:
    api_key: str
    channel_id: str
    interval_seconds: int
    state_file: Path


def load_config() -> WatcherConfig:
    parser = argparse.ArgumentParser(description="YouTube subscribers + rickroll prank")
    parser.add_argument(
        "--api-key",
        default=os.environ.get("YOUTUBE_API_KEY"),
        help="YouTube Data API v3 key (default: YOUTUBE_API_KEY from .env)",
    )
    parser.add_argument(
        "--channel-id",
        default=os.environ.get("YOUTUBE_CHANNEL_ID"),
        help="YouTube channel ID (default: YOUTUBE_CHANNEL_ID from .env)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check rate in seconds (Default: 300)",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path("subscriber_count.json"),
        help="Last subscriber count file",
    )
    parser.add_argument(
        "--test-rickroll",
        action="store_true",
        help="Skip everything else, just fire the rickroll once to test it works.",
    )
    args = parser.parse_args()

    if args.test_rickroll:
        trigger_rickroll()
        sys.exit(0)

    if not args.api_key or not args.channel_id:
        parser.error(
            "API key and channel ID required. Did you create .env from .env.example "
            "and fill it in? Or pass --api-key/--channel-id directly."
        )

    return WatcherConfig(
        api_key=args.api_key,
        channel_id=args.channel_id,
        interval_seconds=args.interval,
        state_file=args.state_file,
    )


def get_subscriber_count(api_key: str, channel_id: str) -> int:
    params = {"part": "statistics", "id": channel_id, "key": api_key}
    response = requests.get(YOUTUBE_API_URL, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()

    items = payload.get("items", [])
    if not items:
        raise RuntimeError(f"Channel not found or API error: {payload}")

    return int(items[0]["statistics"]["subscriberCount"])


def load_last_count(state_file: Path) -> int | None:
    if not state_file.exists():
        return None
    try:
        data = json.loads(state_file.read_text())
        return data.get("count")
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Could not read state file (%s), restarting.", e)
        return None


def save_count(state_file: Path, count: int) -> None:
    state_file.write_text(json.dumps({"count": count}))


def trigger_rickroll() -> None:
    log.info("New subscriber, sir! Playing rickroll...")
    webbrowser.open(RICKROLL_URL)


def run(config: WatcherConfig) -> None:
    last_count = load_last_count(config.state_file)
    log.info("Starting subscriber count (saved): %s", last_count)

    while True:
        try:
            current_count = get_subscriber_count(config.api_key, config.channel_id)
            log.info("Current subscribers: %d", current_count)

            if last_count is not None and current_count > last_count:
                trigger_rickroll()

            if current_count != last_count:
                save_count(config.state_file, current_count)
                last_count = current_count

        except requests.RequestException as e:
            log.error("YouTube API request failed: %s", e)
        except Exception as e:
            log.error("Unexpected error: %s", e)

        time.sleep(config.interval_seconds)


def main() -> int:
    config = load_config()
    try:
        run(config)
    except KeyboardInterrupt:
        log.info("Shutting down...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
