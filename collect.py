import json, time, hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import feedparser, requests
from feeds import FEEDS

USER_AGENT = "EaglesNewsBot/1.0"
TIMEOUT = 20

EAGLES_KEYWORDS = {
    "jalen hurts","nick sirianni","aj brown","a.j. brown","devonta smith","dallas goedert",
    "lane johnson","jordan mailata","darius slay","saquon barkley","jalen carter","josh sweat",
    "james bradberry","nolan smith","kelee ringo","kirk cousins","lincoln financial field","novacare complex"
}

def normalize_url(u):
    try:
        p = urlparse(u)
        qs = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith(("utm_","fbclid"))]
        return urlunparse((p.scheme, p.netloc, p.path, p.params, urlencode(qs), ""))
    except Exception:
        return u

def allow_item(title, summary, trusted):
    t = f"{title} {summary}".lower()
    if trusted and ("eagles" in t or any(k in t for k in EAGLES_KEYWORDS)):
        return True
    if ("eagles" in t or "philadelphia eagles" in t) and not any(team in t for team in ["chiefs","cowboys","giants","commanders"]):
        return True
    if "philadelphia" in t and any(k in t for k in EAGLES_KEYWORDS):
        return True
    return False

def fetch(url):
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception:
        return feedparser.parse(b"")

def collect():
    items, seen, sources = [], set(), set()
    for feed in FEEDS:
        parsed = fetch(feed["url"])
        trusted = bool(feed.get("trusted"))
        src = feed.get("name") or parsed.feed.get("title") or urlparse(feed["url"]).netloc
        for e in parsed.entries[:80]:
            title = (e.get("title") or "").strip()
            link = normalize_url((e.get("link") or "").strip())
            if not title or not link:
                continue
            summary = e.get("summary", e.get("description","")) or ""
            ts = None
            for key in ("published_parsed","updated_parsed"):
                if getattr(e, key, None):
                    ts = time.mktime(getattr(e, key)); break
            if not ts: ts = time.time()
            if not allow_item(title, summary, trusted):
                continue
            key = hashlib.md5((title+link).encode("utf-8")).hexdigest()
            if key in seen: 
                continue
            seen.add(key)
            items.append({"title": title, "link": link, "source": src, "published": int(ts)})
            sources.add(src)
    items.sort(key=lambda x: x["published"], reverse=True)
    payload = {
        "team": "Philadelphia Eagles",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": sorted(list(sources)),
        "items": items[:200]
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    collect()
