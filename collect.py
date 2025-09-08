#!/usr/bin/env python3
# Philadelphia Eagles — collector (HARDENED, curated sources + guaranteed links/dates)

import json, time, re, hashlib
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime, timezone
import feedparser
from feeds import FEEDS, STATIC_LINKS

MAX_ITEMS = 60

# 1) Exactly the 10 sources you want in the dropdown (curated, stable labels)
CURATED_SOURCES = [
    "Philadelphia Eagles",
    "Philadelphia Inquirer",
    "PhillyVoice",
    "NBC Sports Philadelphia",
    "Bleeding Green Nation",
    "ESPN",
    "Yahoo Sports",
    "Sports Illustrated",
    "CBS Sports",
    "The Athletic",
]

# 2) Only collect from these sources (keeps noise out)
ALLOWED_SOURCES = set(CURATED_SOURCES)

# ---------- utils ----------
def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def _host(u: str) -> str:
    try:
        n = urlparse(u).netloc.lower()
        for p in ("www.","m.","amp."):
            if n.startswith(p): n = n[len(p):]
        return n
    except Exception:
        return ""

def canonical(u: str) -> str:
    try:
        p = urlparse(u)
        keep = {"id","story","v","p"}
        q = parse_qs(p.query)
        q = {k:v for k,v in q.items() if k in keep}
        p = p._replace(query=urlencode(q, doseq=True), fragment="", netloc=_host(u))
        return urlunparse(p)
    except Exception:
        return u

def hid(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

ALIASES = {
    # locals
    "philadelphiaeagles.com":"Philadelphia Eagles",
    "inquirer.com":"Philadelphia Inquirer",
    "phillyvoice.com":"PhillyVoice",
    "nbcsportsphiladelphia.com":"NBC Sports Philadelphia",
    "bleedinggreennation.com":"Bleeding Green Nation",
    # national
    "espn.com":"ESPN",
    "sports.yahoo.com":"Yahoo Sports",
    "si.com":"Sports Illustrated",
    "cbssports.com":"CBS Sports",
    "theathletic.com":"The Athletic",
}

KEEP = [r"\bEagles\b", r"\bPhiladelphia\b", r"\bPhilly\b"]
DROP = [r"\bwomen'?s\b", r"\bWBB\b", r"\bvolleyball\b", r"\bbasketball\b", r"\bbaseball\b"]

def text_ok(title: str, summary: str) -> bool:
    t = f"{title} {summary}"
    if not any(re.search(p, t, re.I) for p in KEEP): return False
    if any(re.search(p, t, re.I) for p in DROP): return False
    return True

def parse_time(entry):
    for key in ("published_parsed","updated_parsed"):
        if entry.get(key):
            try:
                return time.strftime("%Y-%m-%dT%H:%M:%S%z", entry[key])
            except Exception:
                pass
    return now_iso()  # guaranteed fallback so dates always render

def source_label(link: str, feed_name: str) -> str:
    return ALIASES.get(_host(link), feed_name.strip())

# ---------- pipeline ----------
def fetch_all():
    items, seen = [], set()
    for f in FEEDS:
        fname, furl = f["name"].strip(), f["url"].strip()
        try:
            parsed = feedparser.parse(furl)
        except Exception:
            continue
        for e in parsed.entries[:120]:
            link = canonical((e.get("link") or e.get("id") or "").strip())
            if not link: continue
            key = hid(link)
            if key in seen: continue

            src = source_label(link, fname)
            if src not in ALLOWED_SOURCES:
                continue  # hard gate → dropdown stays clean

            title = (e.get("title") or "").strip()
            summary = (e.get("summary") or e.get("description") or "").strip()
            if not text_ok(title, summary): continue

            items.append({
                "id": key,
                "title": title or "(untitled)",
                "link": link,
                "source": src,
                "feed": fname,
                "published": parse_time(e),   # ISO string (always present)
                "summary": summary,
            })
            seen.add(key)

    items.sort(key=lambda x: x["published"], reverse=True)
    return items[:MAX_ITEMS]

def write_items(items):
    payload = {
        "updated": now_iso(),
        "items": items,
        "links": STATIC_LINKS,          # buttons ALWAYS included
        "sources": CURATED_SOURCES,     # prebuilt list → dropdown always shows 10
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    write_items(fetch_all())
