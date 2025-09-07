# collect.py — Philadelphia Eagles collector
# - Real outlet in item.source (parsed from title suffix; fallback: <source> tag; fallback: article domain)
# - Removes outlet suffix from title for display
# - Strong dedupe: canonical URL + normalized title
# - Eagles-only filtering (stricter for Google/Bing)
# - Tight source allowlist (keeps dropdown clean)

import feedparser, json, re, time, html
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from feeds import FEEDS

MAX_ITEMS = 50

# ------------------- filters (Eagles-specific) -------------------
KEYWORDS_ANY = [
    "philadelphia eagles", "eagles", "fly eagles fly",
    "jalen hurts", "nick sirianni", "howie roseman",
    "a.j. brown", "aj brown", "devonta smith", "dallas goedert",
    "jordan mailata", "lane johnson", "haason reddick", "darius slay",
    "lincoln financial field", "lincoln financial", "philly eagles",
    "eagles vs", "eagles at", "vs eagles", "at eagles",
]
FOOTBALL_HINTS = [
    "nfl", "football", "qb", "quarterback", "rb", "wr", "te",
    "defense", "offense", "linebacker", "cornerback", "safety",
    "depth chart", "injury report", "practice squad", "roster move",
]
EXCLUDE_ANY = [
    "philadelphia phillies", "sixers", "76ers", "flyers", "union",
    "eagle scouts", "high school", "alabama crimson tide", "oregon ducks",
]

AGGREGATORS = {"news.google.com", "www.bing.com", "bing.com"}

# Host allowlist: reputable national + trusted Philly/Eagles outlets
ALLOWED_SOURCES = {
    # Official
    "philadelphiaeagles.com",
    # Philly local / beat
    "inquirer.com", "phillyvoice.com", "nbcsportsphiladelphia.com",
    "6abc.com", "nbcphiladelphia.com", "cbsnews.com", "cbsnews.com/philadelphia",
    "fox29.com", "crossingbroad.com",
    # Regionals that regularly cover Eagles
    "nj.com", "pennlive.com", "delcotimes.com",
    # Major national sports
    "espn.com", "cbssports.com", "foxsports.com", "si.com",
    "theathletic.com", "apnews.com", "sportingnews.com",
    "yahoo.com", "sports.yahoo.com", "bleacherreport.com", "nfl.com",
    "profootballtalk.nbcsports.com", "pff.com",
    # SB Nation team blog
    "bleedinggreennation.com",
}

# Pretty labels
DOMAIN_LABELS = {
    "philadelphiaeagles.com": "Philadelphia Eagles (Official)",
    "inquirer.com": "Inquirer.com",
    "phillyvoice.com": "PhillyVoice",
    "nbcsportsphiladelphia.com": "NBC Sports Philadelphia",
    "6abc.com": "6abc Philadelphia",
    "nbcphiladelphia.com": "NBC10 Philadelphia",
    "fox29.com": "FOX 29 Philadelphia",
    "crossingbroad.com": "Crossing Broad",
    "nj.com": "NJ.com",
    "pennlive.com": "PennLive",
    "delcotimes.com": "Delco Times",
    "espn.com": "ESPN",
    "cbssports.com": "CBS Sports",
    "foxsports.com": "FOX Sports",
    "si.com": "Sports Illustrated",
    "theathletic.com": "The Athletic",
    "apnews.com": "AP News",
    "sportingnews.com": "Sporting News",
    "yahoo.com": "Yahoo",
    "sports.yahoo.com": "Yahoo Sports",
    "bleacherreport.com": "Bleacher Report",
    "nfl.com": "NFL.com",
    "profootballtalk.nbcsports.com": "ProFootballTalk",
    "pff.com": "PFF",
    "bleedinggreennation.com": "Bleeding Green Nation",
}

# ------------------- helpers -------------------
UNICODE_SPACES = re.compile(r"[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000]")

def normalize_spaces(s: str) -> str:
    s = UNICODE_SPACES.sub(" ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def strip_tags(s: str) -> str:
    if not s: return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return normalize_spaces(s)

def unwrap_redirect(u: str) -> str:
    """Unwrap Google/Bing news links to the real article when possible."""
    try:
        p = urlparse(u)
        q = dict(parse_qsl(p.query, keep_blank_values=True))
        if p.netloc == "news.google.com" and "url" in q:
            return q["url"]
        if p.netloc in {"www.bing.com", "bing.com"}:
            return q.get("url") or q.get("u") or u
        return u
    except Exception:
        return u

def clean_url(u: str) -> str:
    """Canonicalize final URL and drop tracking params."""
    try:
        u = unwrap_redirect(u)
        p = urlparse(u)
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith(("utm_", "fbclid", "gclid", "ocid"))]
        host = (p.netloc or "").lower()
        if host.startswith("www."): host = host[4:]
        return urlunparse((p.scheme, host, p.path, "", urlencode(q), ""))
    except Exception:
        return u

# Accept hyphen, en dash, or em dash; spaces are normalized.
DASH = r"[-–—]"
OUTLET_RE = re.compile(rf"\s{DASH}\s([A-Za-z0-9&@.,'()/:+ ]+)$")

def split_title_outlet(title: str):
    """Return (clean_title, outlet or None) parsed from 'Headline – Outlet'."""
    t = normalize_spaces(title)
    m = OUTLET_RE.search(t)
    if not m:
        return t, None
    outlet = m.group(1).strip()
    if len(outlet) < 2:
        return t, None
    clean = t[:m.start()].rstrip()
    return clean, outlet

def outlet_from_url(u: str, default_feed_name: str) -> str:
    try:
        host = urlparse(u).netloc.lower()
        if host.startswith("www."): host = host[4:]
        if host and host not in AGGREGATORS:
            return DOMAIN_LABELS.get(host, host)
        return default_feed_name
    except Exception:
        return default_feed_name

def entry_source_title(entry) -> str | None:
    """Read <source> or source_detail title (Google News includes this)."""
    try:
        src = entry.get("source")
        if isinstance(src, dict):
            t = src.get("title") or src.get("href")
            if t: return normalize_spaces(str(t))
    except Exception:
        pass
    try:
        sd = entry.get("source_detail")
        if isinstance(sd, dict):
            t = sd.get("title") or sd.get("href")
            if t: return normalize_spaces(str(t))
    except Exception:
        pass
    return None

def looks_like_football(text: str) -> bool:
    t = text.lower()
    if "football" in t or "nfl" in t: return True
    return any(k in t for k in FOOTBALL_HINTS)

def allowed(title: str, summary: str, feed_host: str) -> bool:
    t = f"{title} {summary}".lower()
    if any(x in t for x in EXCLUDE_ANY): return False
    if not any(k in t for k in KEYWORDS_ANY): return False
    if feed_host in AGGREGATORS and not looks_like_football(t): return False
    return True

def ts_from_entry(e) -> float:
    for k in ("published_parsed", "updated_parsed"):
        v = e.get(k)
        if v:
            try: return time.mktime(v)
            except Exception: pass
    return time.time()

def norm_title(t: str) -> str:
    # normalize spaces/dashes then strip a trailing " - Outlet", then sanitize
    t = normalize_spaces(t)
    t = re.sub(r"[–—]", "-", t)
    t = re.sub(rf"\s-\s[a-z0-9&@.,'()/:+ ]+$", "", t.lower())
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def make_id(link: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (link or "").lower()).strip("-")[:120]

# ------------------- main -------------------
def collect():
    items = []
    seen_links  = set()  # canonical URL dedupe
    seen_titles = set()  # global normalized-title dedupe

    for feed in FEEDS:
        feed_name = feed["name"]
        feed_url  = feed["url"]
        feed_host = urlparse(feed_url).netloc.lower()

        parsed = feedparser.parse(feed_url)
        for e in parsed.entries:
            raw_title = e.get("title") or ""
            title = strip_tags(raw_title)
            link  = clean_url(e.get("link") or "")
            if not title or not link:
                continue

            summary = strip_tags(e.get("summary") or "")
            if not allowed(title, summary, feed_host):
                continue

            # Dedupe by canonical URL
            if link in seen_links:
                continue

            # Extract outlet from title suffix; cleaned title for display/dedupe
            base_title, outlet_from_title = split_title_outlet(title)

            # Dedupe by normalized title (after removing outlet suffix)
            title_key = norm_title(base_title)
            if title_key in seen_titles:
                continue

            # Prefer outlet from title; else GN <source>; else article domain
            src_tag = entry_source_title(e)
            if outlet_from_title:
                source = outlet_from_title
            elif src_tag and "google" not in src_tag.lower():
                source = src_tag
            else:
                source = outlet_from_url(link, feed_name)

            # Tighten: allowlist on final host
            host = urlparse(link).netloc.lower()
            if host.startswith("www."): host = host[4:]
            if host not in ALLOWED_SOURCES:
                continue

            ts = ts_from_entry(e)
            items.append({
                "id": make_id(link),
                "title": base_title,
                "link": link,
                "source": source,                # drives dropdown
                "ts": float(ts),
                "published_iso": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
            })

            seen_links.add(link)
            seen_titles.add(title_key)

    items.sort(key=lambda x: x["ts"], reverse=True)
    items = items[:MAX_ITEMS]

    with open("items.json", "w", encoding="utf-8") as f:
        json.dump({
            "updated_iso": datetime.now(tz=timezone.utc).isoformat(),
            "count": len(items),
            "items": items
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    collect()