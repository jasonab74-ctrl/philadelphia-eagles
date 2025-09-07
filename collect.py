import re, json, time, html, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
import requests, feedparser
import feeds

USER_AGENT = "TeamNewsCollector/1.2 (+https://github.com/)"
TIMEOUT = 12
MAX_ITEMS = 100
BOOTSTRAP_MIN = 12

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

def _http_final_url(url: str) -> str:
    try:
        r = SESSION.get(url, allow_redirects=True, timeout=TIMEOUT)
        return r.url or url
    except Exception:
        return url

def canonicalize(u: str) -> str:
    try:
        u = _http_final_url(u)
        p = urlparse(u)
        path = re.sub(r"/+$", "", (p.path or ""))
        return urlunparse((p.scheme, p.netloc.lower(), path, "", "", ""))
    except Exception:
        return u

def normalize_title(t: str) -> str:
    t = html.unescape(t or "").strip()
    t = re.sub(r"\s+[–—-]\s+[^|]+$", "", t)
    return re.sub(r"\s+", " ", t)

def extract_source(entry, feed_name: str) -> str:
    src = None
    if getattr(entry, "source", None):
        src = getattr(entry.source, "title", None) or getattr(entry.source, "href", None)
    if not src and getattr(entry, "authors", None):
        src = entry.authors[0].get("name")
    if not src:
        src = getattr(entry, "publisher", None)
    if not src:
        src = feed_name
    src = (src or "Unknown").strip()
    src = re.sub(r"^https?://(www\.)?", "", src)
    return src[:80]

def ts_from_entry(entry) -> float:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, key, None)
        if val:
            try: return time.mktime(val)
            except Exception: pass
    return time.time()

def allow_item(item) -> bool:
    if item.get("trusted"):
        return True
    blob = f"{item.get('title','')} {item.get('summary','')}".lower()
    if getattr(feeds, "TEAM_KEYWORDS", []) and not any(k.lower() in blob for k in feeds.TEAM_KEYWORDS):
        return False
    if getattr(feeds, "SPORT_TOKENS", []) and not any(s.lower() in blob for s in feeds.SPORT_TOKENS):
        return False
    if any(b.lower() in blob for b in getattr(feeds, 'EXCLUDE_TOKENS', [])):
        return False
    return True

def fetch_feed(fd):
    url, name, trusted = fd["url"], fd["name"], bool(fd.get("trusted", False))
    items = []
    try:
        d = feedparser.parse(url)
        for e in d.entries:
            title = normalize_title(getattr(e, "title", "") or "")
            link = getattr(e, "link", "") or ""
            if not title or not link:
                continue
            items.append({
                "title": title,
                "url": canonicalize(link),
                "source": extract_source(e, name),
                "summary": html.unescape(getattr(e, "summary", "") or "").strip(),
                "published": datetime.fromtimestamp(ts_from_entry(e), tz=timezone.utc).isoformat(),
                "trusted": trusted,
            })
    except Exception as ex:
        print(f"[WARN] Feed error: {name} -> {ex}", file=sys.stderr)
    return items

def dedupe(items):
    seen, out = set(), []
    for it in items:
        k = (it["title"].lower(), it["url"])
        if k in seen: continue
        seen.add(k); out.append(it)
    return out

def main():
    all_items, trusted_raw = [], []
    for fd in getattr(feeds, "FEEDS", []):
        batch = fetch_feed(fd)
        all_items.extend(batch)
        if fd.get("trusted"): trusted_raw.extend(batch)

    filtered = [it for it in all_items if allow_item(it)]
    filtered = dedupe(filtered)
    filtered.sort(key=lambda x: x.get("published",""), reverse=True)

    if len(filtered) < BOOTSTRAP_MIN:
        trusted_raw = dedupe(trusted_raw)
        trusted_raw.sort(key=lambda x: x.get("published",""), reverse=True)
        merged, seen = [], set()
        for it in trusted_raw + filtered:
            k = (it["title"].lower(), it["url"])
            if k in seen: continue
            seen.add(k); merged.append(it)
        filtered = merged

    filtered = filtered[:MAX_ITEMS]
    sources = sorted({it["source"] for it in filtered})

    payload = {
        "team": {"name": getattr(feeds, "TEAM_NAME", "Team"), "slug": getattr(feeds, "TEAM_SLUG", "team")},
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "static_links": getattr(feeds, "STATIC_LINKS", []),
        "items": filtered,
        "sources": sources,
    }

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[collector] wrote {len(filtered)} items; {len(sources)} sources; updated items.json")

if __name__ == "__main__":
    main()