#!/usr/bin/env python3
# Sports App Project — collector (HARDENED + TEAM-AGNOSTIC)
# - Always writes buttons (links), items, and updated timestamp
# - Normalizes publisher names
# - Enforces an allowlist for the Source dropdown
# - Produces ISO timestamps; UI formats them to local time

import json, time, re, hashlib
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime, timezone
import feedparser

from feeds import FEEDS, STATIC_LINKS  # team-specific feeds + buttons

MAX_ITEMS = 60

ALLOWED_SOURCES = {
    # national
    "ESPN","Yahoo Sports","Sports Illustrated","CBS Sports","SB Nation",
    "Bleacher Report","The Athletic","NFL.com","PFF","Pro-Football-Reference",
    "NBC Sports","USA Today",
    # eagles locals
    "Philadelphia Eagles","Philadelphia Inquirer","PhillyVoice",
    "NBC Sports Philadelphia","94WIP","Crossing Broad","Bleeding Green Nation",
    # generic reddit labels used by our feeds
    "Reddit — r/eagles","Reddit — r/Colts","Reddit — r/azcardinals"
}

# ---------------- utilities ----------------

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
    # national
    "espn.com":"ESPN",
    "sports.yahoo.com":"Yahoo Sports",
    "si.com":"Sports Illustrated",
    "cbssports.com":"CBS Sports",
    "sbnation.com":"SB Nation",
    "bleacherreport.com":"Bleacher Report",
    "theathletic.com":"The Athletic",
    "nfl.com":"NFL.com",
    "pff.com":"PFF",
    "pro-football-reference.com":"Pro-Football-Reference",
    "nbcsports.com":"NBC Sports",
    "usatoday.com":"USA Today",
    # philly
    "philadelphiaeagles.com":"Philadelphia Eagles",
    "inquirer.com":"Philadelphia Inquirer",
    "phillyvoice.com":"PhillyVoice",
    "nbcsportsphiladelphia.com":"NBC Sports Philadelphia",
    "audacy.com":"94WIP",
    "crossingbroad.com":"Crossing Broad",
    "bleedinggreennation.com":"Bleeding Green Nation",
}

def source_label(link: str, feed_name: str) -> str:
    L = feed_name.strip()
    hl = _host(link)
    # collapse reddit
    if "reddit.com/r/eagles" in link or "r/eagles" in feed_name.lower():
        return "Reddit — r/eagles"
    return ALIASES.get(hl, L)

KEEP_PATTERNS = [
    r"\bEagles\b", r"\bPhiladelphia\b", r"\bPhilly\b",
]
DROP_PATTERNS = [r"\bwomen'?s\b", r"\bWBB\b", r"\bvolleyball\b", r"\bbasketball\b", r"\bbaseball\b"]

def text_ok(title: str, summary: str) -> bool:
    t = f"{title} {summary}"
    if not any(re.search(p, t, re.I) for p in KEEP_PATTERNS): return False
    if any(re.search(p, t, re.I) for p in DROP_PATTERNS): return False
    return True

def parse_time(entry):
    for key in ("published_parsed","updated_parsed"):
        if entry.get(key):
            try:
                return time.strftime("%Y-%m-%dT%H:%M:%S%z", entry[key])
            except Exception:
                pass
    return now_iso()

# ---------------- pipeline ----------------

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
                continue

            title = (e.get("title") or "").strip()
            summary = (e.get("summary") or e.get("description") or "").strip()
            if not text_ok(title, summary): continue

            items.append({
                "id": key,
                "title": title or "(untitled)",
                "link": link,
                "source": src,
                "feed": fname,
                "published": parse_time(e),
                "summary": summary,
            })
            seen.add(key)

    items.sort(key=lambda x: x["published"], reverse=True)
    return items[:MAX_ITEMS]

def write_items(items):
    payload = {
        "updated": now_iso(),
        "items": items,
        "links": STATIC_LINKS  # ALWAYS include buttons
    }
    with open("items.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    write_items(fetch_all())