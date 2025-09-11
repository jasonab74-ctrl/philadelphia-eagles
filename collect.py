# collect.py — build items.json for the Eagles site (max 50 recent)
# Requirements: feedparser (installed by the workflow)

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import feedparser  # type: ignore

from feeds import FEEDS

OUT_PATH = "items.json"
MAX_ITEMS = 50

# Basic filters to avoid non-football "Eagles" (e.g., Phillies, hockey, etc.)
NEGATIVE_PATTERNS = [
    r"\bPhillies?\b",
    r"\bbaseball\b",
    r"\bAHL\b",
    r"\bcollege\b",
    r"\bBoston College\b",
    r"\bSoaring\b",  # occasional travel/lifestyle noise
]
NEG_RE = re.compile("|".join(NEGATIVE_PATTERNS), re.IGNORECASE)

TEAM_RE = re.compile(r"\b(Philadelphia\s+Eagles|Eagles)\b", re.IGNORECASE)


def _to_epoch(entry) -> Tuple[int, str]:
    """
    Return (epoch_seconds, iso8601) for an entry.
    Tries published, updated, or falls back to now.
    """
    # feedparser normalizes to published_parsed / updated_parsed when possible
    ts = None
    if getattr(entry, "published_parsed", None):
        ts = entry.published_parsed
    elif getattr(entry, "updated_parsed", None):
        ts = entry.updated_parsed

    if ts:
        epoch = int(time.mktime(ts))
        dt = datetime.fromtimestamp(epoch, tz=timezone.utc)
    else:
        # fallback = now, but keeps ordering deterministic for missing dates
        dt = datetime.now(tz=timezone.utc)
        epoch = int(dt.timestamp())

    return epoch, dt.isoformat().replace("+00:00", "Z")


def is_team_relevant(title: str, summary: str) -> bool:
    # Keep if it clearly references the team and NOT a negative topic
    text = f"{title} {summary or ''}"
    if NEG_RE.search(text):
        return False
    return bool(TEAM_RE.search(text))


def normalize_source(feed_title: str, default_name: str) -> str:
    # Prefer a clean, short label
    if not feed_title:
        return default_name
    # A few friendly trims
    feed_title = feed_title.replace(" - NFL", "").strip()
    return feed_title


def collect() -> Dict[str, object]:
    seen_links = set()
    items: List[Dict[str, object]] = []
    source_names = set()

    for feed_cfg in FEEDS:
        url = feed_cfg["url"]
        default_name = feed_cfg["name"]

        parsed = feedparser.parse(url)
        src = normalize_source(parsed.feed.get("title", ""), default_name)

        # track source even if empty today
        source_names.add(src)

        for e in parsed.entries:
            link = e.get("link") or ""
            title = (e.get("title") or "").strip()
            summary = (e.get("summary") or e.get("description") or "")

            if not link or not title:
                continue

            if not is_team_relevant(title, summary):
                continue

            if link in seen_links:
                continue
            seen_links.add(link)

            epoch, iso = _to_epoch(e)

            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": src,
                    "published": iso,          # ISO 8601 with Z (fixes “Invalid Date” in UI)
                    "timestamp": epoch,        # numeric for sorting
                }
            )

    # Sort newest first and cap
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    items = items[:MAX_ITEMS]

    updated_at = datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")

    # Build a stable sources list from the items we actually kept
    used_sources = sorted({it["source"] for it in items}) or sorted(source_names)

    payload = {
        "team": "Philadelphia Eagles",
        "updated_at": updated_at,
        "count": len(items),
        "sources": used_sources,
        "items": items,
    }
    return payload


if __name__ == "__main__":
    data = collect()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(
        f"Wrote {OUT_PATH}: {data['count']} items from {len(data['sources'])} sources • updated_at={data['updated_at']}"
    )