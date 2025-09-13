import json
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import feedparser
from dateutil import parser as dtparser

from feeds import SOURCES

TEAM = "eagles"                 # <— this instance is for the Eagles site
MAX_ITEMS = 50                  # cap the page to the 50 most recent team items
KEYWORDS_FALLBACK = ["Philadelphia Eagles", "Eagles", "PHI"]  # safety net

def _norm(s: str) -> str:
    return (s or "").strip()

def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""

def _as_epoch(dt):
    try:
        return int(dt.timestamp())
    except Exception:
        return None

def _pick_published(entry):
    """
    Try to get a timezone-aware datetime from common feedparser fields.
    """
    # feedparser puts parsed date into .published_parsed or .updated_parsed (time.struct_time)
    for k in ("published_parsed", "updated_parsed"):
        if getattr(entry, k, None):
            try:
                return datetime.fromtimestamp(time.mktime(getattr(entry, k)), tz=timezone.utc)
            except Exception:
                pass

    # fallbacks: try string fields
    for k in ("published", "updated"):
        if getattr(entry, k, None):
            try:
                return dtparser.parse(getattr(entry, k)).astimezone(timezone.utc)
            except Exception:
                pass

    return None

def _passes_keywords(entry, kws):
    text = " ".join([
        _norm(getattr(entry, "title", "")),
        _norm(getattr(entry, "summary", "")),
    ]).lower()
    for kw in (kws or []):
        if kw.lower() in text:
            return True
    # Small safety for ESPN/PFT articles that put team in tags
    for tag in getattr(entry, "tags", []) or []:
        if any(kw.lower() in _norm(getattr(tag, "term", "")).lower() for kw in (kws or [])):
            return True
    return False

def _load_sources():
    srcs = SOURCES.get(TEAM, [])
    # ensure keyword list on non-team-specific
    for s in srcs:
        if not s.get("team_specific"):
            s.setdefault("keywords", KEYWORDS_FALLBACK)
    return srcs

def collect():
    gathered = []
    seen_links = set()
    dropdown_sources = set()

    for src in _load_sources():
        title = src["title"]
        url = src["url"]
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue

        for entry in getattr(feed, "entries", []) or []:
            link = _norm(getattr(entry, "link", ""))
            if not link or link in seen_links:
                continue

            if not src.get("team_specific", False):
                if not _passes_keywords(entry, src.get("keywords")):
                    continue

            pub_dt = _pick_published(entry)
            item = {
                "title": _norm(getattr(entry, "title", "")),
                "link": link,
                "source": title if src.get("team_specific", False) else f"{title}",
                "domain": _domain(link),
                "published": pub_dt.isoformat() if pub_dt else None,
                "published_ts": _as_epoch(pub_dt) if pub_dt else None,
            }

            # Very light sanity check: must have a title and link
            if not item["title"] or not item["link"]:
                continue

            gathered.append(item)
            seen_links.add(link)
            dropdown_sources.add(item["source"])

    # sort newest first by timestamp; unknown dates sink to bottom
    gathered.sort(key=lambda x: (x["published_ts"] or 0), reverse=True)
    if len(gathered) > MAX_ITEMS:
        gathered = gathered[:MAX_ITEMS]

    out = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": gathered,
        "sources": sorted(dropdown_sources),
    }

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    collect()