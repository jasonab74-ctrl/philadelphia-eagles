import json
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
import feedparser
from dateutil import parser as dateparser
from pathlib import Path
from feeds.py import SOURCES  # same folder

TEAM_KEYWORDS = [
    "philadelphia eagles", "eagles", "philly eagles", "nfl eagles", "fly eagles fly",
    "jalen hurts", "nick sirianni", "lincoln financial field", "linc"
]

ITEM_LIMIT = 50

def is_eagles_related(title: str, summary: str, link: str) -> bool:
    blob = " ".join(filter(None, [title, summary, link])).lower()
    return any(k in blob for k in TEAM_KEYWORDS)

def safe_datetime(entry):
    # Try feed-provided date fields; fall back to parse from string
    for key in ("published", "updated", "pubDate"):
        val = entry.get(key) or entry.get(f"{key}_parsed")
        if isinstance(val, str):
            try:
                return dateparser.parse(val)
            except Exception:
                pass
        elif val:
            # struct_time -> datetime
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    # Last resort: now (keeps sorting reasonable)
    return datetime.now(timezone.utc)

def hostname(u):
    try:
        return urlparse(u).hostname or ""
    except Exception:
        return ""

def norm(s):
    return " ".join((s or "").split())

def dedupe(items):
    seen = set()
    unique = []
    for it in items:
        key = hashlib.sha1(it["link"].encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        unique.append(it)
    return unique

def collect():
    all_items = []
    source_names = set()

    for src in SOURCES:
        name, url = src["name"], src["url"]
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue

        for e in feed.entries:
            title = norm(getattr(e, "title", "") or "")
            summary = norm(getattr(e, "summary", "") or "")
            link = getattr(e, "link", "") or ""

            if not title or not link:
                continue

            if not is_eagles_related(title, summary, link):
                # Keep strictly Eagles-related
                continue

            dt = safe_datetime(e)
            source_names.add(name)

            all_items.append({
                "title": title,
                "link": link,
                "source": name if name else (hostname(link) or "source"),
                "published_at": dt.astimezone(timezone.utc).isoformat(),
            })

    # Clean up, sort, cap
    all_items = dedupe(all_items)
    all_items.sort(key=lambda x: x["published_at"], reverse=True)
    all_items = all_items[:ITEM_LIMIT]

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": sorted(source_names),
        "items": all_items,
    }

    Path("items.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    collect()
    print("OK: items.json written.")