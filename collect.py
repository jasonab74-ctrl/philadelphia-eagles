# collect.py
# ------------------------------------
# Pulls news, filters to Philadelphia Eagles sources, writes items.json
# Schema: { "updated_at": str, "sources": [str], "items": [{title, link, source, published}] }

import json, time, pathlib, sys, urllib.parse
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import feedparser

from feeds import FEED_URLS, ALLOW_SOURCES, MAX_ITEMS

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "items.json"

def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()

def _final_url_from_google_or_bing(link: str) -> str:
    """
    Google News/Bing sometimes wrap the publisher URL.
    Try to unwrap ?url=… or &u=…; otherwise return original link.
    """
    try:
        u = urllib.parse.urlparse(link)
        qs = urllib.parse.parse_qs(u.query)
        for key in ("url", "u"):
            if key in qs and qs[key]:
                return qs[key][0]
    except Exception:
        pass
    return link

def _host(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""

def _nice_source(host: str) -> Tuple[str, str]:
    """
    Return (matched_key, pretty_name) if host is allowed; otherwise ("","")
    """
    for key, pretty in ALLOW_SOURCES.items():
        if key in host:
            return key, pretty
    return "", ""

def _pick_time(entry) -> datetime:
    # Try published, then updated; fall back to "now" so we never lose items
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.fromtimestamp(time.mktime(val), tz=timezone.utc)
            except Exception:
                pass
    return datetime.now(tz=timezone.utc)

def collect() -> Dict:
    seen_links = set()
    items: List[Dict] = []
    src_counter: Dict[str, str] = {}  # key -> pretty

    for url in FEED_URLS:
        parsed = feedparser.parse(url)
        for e in parsed.entries:
            raw_link = getattr(e, "link", "") or ""
            final_link = _final_url_from_google_or_bing(raw_link)
            host = _host(final_link)

            # keep only allowed sources
            key, pretty = _nice_source(host)
            if not key:
                continue

            if final_link in seen_links:
                continue
            seen_links.add(final_link)

            title = (getattr(e, "title", "") or "").strip()
            if not title:
                continue

            published_dt = _pick_time(e)

            items.append({
                "title": title,
                "link": final_link,
                "source": pretty,
                "published": _iso(published_dt),
            })
            src_counter[key] = pretty

    # Sort newest first and trim
    items.sort(key=lambda x: x["published"], reverse=True)
    items = items[:MAX_ITEMS]

    # Build sources dropdown list from what actually appears
    sources = sorted({it["source"] for it in items})

    # If, for some reason, filtering left us empty, fail “softly”:
    # keep the page alive by including a single stub explaining no items.
    if not items:
        items = [{
            "title": "No Eagles articles found from the allowed sources.",
            "link": "https://www.philadelphiaeagles.com/",
            "source": "System",
            "published": _iso(datetime.now(tz=timezone.utc)),
        }]
        sources = ["System"]

    out = {
        "updated_at": _iso(datetime.now(tz=timezone.utc)),
        "sources": sources,
        "items": items,
    }
    return out

def main() -> int:
    data = collect()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    # Console summary (visible in Actions logs)
    print("---- items.json summary ----")
    print("items:", len(data.get("items", [])))
    print("sources:", ", ".join(data.get("sources", [])))
    print("updated_at:", data.get("updated_at"))
    return 0

if __name__ == "__main__":
    sys.exit(main())