# collect.py — collect the latest Eagles articles and write items.json
# Keeps 50 most-recent items, normalizes timestamps, and summarizes sources.

import json, pathlib, time, datetime, hashlib
import feedparser

from feeds import SOURCES

OUT_PATH = pathlib.Path("items.json")
TEAM_NAME = "Philadelphia Eagles"
MAX_ITEMS = 50

# Friendly UA helps a ton with some hosts
REQUEST_HEADERS = {
    "User-Agent": "news-bot/1.0 (+github pages collector; compatible; +https://github.com)"
}

def parse_dt(entry):
    ts = entry.get("published_parsed") or entry.get("updated_parsed")
    if isinstance(ts, time.struct_time):
        # feedparser gives UTC struct_time
        return datetime.datetime(*ts[:6], tzinfo=datetime.timezone.utc)
    # fallbacks: try text fields
    for key in ("published", "updated", "date"):
        val = entry.get(key)
        if val:
            try:
                # feedparser sometimes exposes parsed date under "updated_parsed" etc,
                # if not available, leave None and we’ll fill later
                return None
            except Exception:
                pass
    return None

def iso_utc(dt: datetime.datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def clean_title(t: str) -> str:
    return (t or "").replace("\xa0", " ").strip()

def collect():
    items = []
    for source_name, url in SOURCES:
        try:
            feed = feedparser.parse(url, request_headers=REQUEST_HEADERS)
            for e in feed.entries:
                title = clean_title(e.get("title", ""))
                link  = e.get("link", "").strip()
                if not title or not link:
                    continue
                dt = parse_dt(e)
                # fallback: treat missing dates as epoch 0 and we’ll push them down
                if dt is None:
                    dt = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

                items.append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "published_at": iso_utc(dt),
                })
        except Exception:
            # don’t let a single bad source kill the run
            continue

    # De-dup by link (normalized)
    seen = set()
    deduped = []
    for it in items:
        key = hashlib.sha1(it["link"].encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)

    # Sort newest first and keep top N
    deduped.sort(key=lambda x: x["published_at"], reverse=True)
    deduped = deduped[:MAX_ITEMS]

    # Surface actual sources present (sorted)
    present_sources = sorted({it["source"] for it in deduped})

    payload = {
        "team": TEAM_NAME,
        "updated_at": iso_utc(datetime.datetime.now(datetime.timezone.utc)),
        "sources": present_sources,
        "items": deduped,
    }

    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    collect()
    # quick summary in logs for the GH Action
    try:
        d = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        print("---- items.json summary ----")
        print("items:", len(d.get("items", [])))
        print("sources:", len(d.get("sources", [])))
        print("updated_at:", d.get("updated_at"))
    except Exception as e:
        print("Unable to print summary:", e)