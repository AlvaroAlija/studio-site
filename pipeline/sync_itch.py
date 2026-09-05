#!/usr/bin/env python3
"""Sync itch.io game data into content/games.json.

Runs on every build and nightly (sync-itch.yml), so cover changes and new
releases propagate without a manual commit. Only fields that itch.io owns are
overwritten (cover, itchUrl, embedUrl, downloadUrl, status published-ness);
editorial fields (story, detail, controls, ...) stay as authored in git.

Requires the ITCH_API_KEY environment variable (itch.io → Settings → API keys).
Games are matched by slug against the itch.io game url (e.g. alvaro.itch.io/hollow-signal).

    python3 pipeline/sync_itch.py            # writes content/games.json if changed
    python3 pipeline/sync_itch.py --dry-run  # prints the diff summary only
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "content" / "games.json"
API_BASE = "https://itch.io/api/1"


def fetch_my_games(api_key: str) -> list[dict[str, Any]]:
    url = f"{API_BASE}/{api_key}/my-games"
    request = urllib.request.Request(url, headers={"User-Agent": "alvaro-works-sync/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"itch.io API request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"itch.io API returned invalid JSON: {exc}") from exc

    games = payload.get("games")
    if not isinstance(games, list):
        raise RuntimeError(f"unexpected itch.io API payload: {list(payload)}")
    return games


def slug_of(itch_game: dict[str, Any]) -> str:
    """itch.io game url -> trailing path segment, e.g. .../hollow-signal."""
    url = str(itch_game.get("url", ""))
    return url.rstrip("/").rsplit("/", 1)[-1].lower()


def merge(entries: list[dict[str, Any]], itch_games: list[dict[str, Any]]) -> list[str]:
    """Overlay itch-owned fields onto manifest entries. Returns changed slugs."""
    by_slug = {slug_of(g): g for g in itch_games}
    changed: list[str] = []

    for entry in entries:
        game = by_slug.get(str(entry.get("slug", "")).lower())
        if game is None:
            continue

        updates: dict[str, Any] = {}
        cover = game.get("cover_url")
        if cover and cover != entry.get("cover"):
            updates["cover"] = cover
        url = game.get("url")
        if url and url != entry.get("itchUrl"):
            updates["itchUrl"] = url
        if game.get("embed") and game["embed"].get("url") != entry.get("embedUrl"):
            updates["embedUrl"] = game["embed"]["url"]

        if updates:
            entry.update(updates)
            changed.append(entry["slug"])

    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    api_key = os.environ.get("ITCH_API_KEY")
    if not api_key:
        print("error: ITCH_API_KEY is not set", file=sys.stderr)
        return 1

    try:
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if not isinstance(entries, list):
            raise RuntimeError(f"{MANIFEST} must contain a JSON array")
        itch_games = fetch_my_games(api_key)
        changed = merge(entries, itch_games)
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not changed:
        print("games.json is up to date")
        return 0

    if args.dry_run:
        print(f"would update: {', '.join(changed)}")
        return 0

    MANIFEST.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated: {', '.join(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
