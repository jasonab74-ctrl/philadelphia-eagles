#!/usr/bin/env python3
# collect.py — Eagles-tuned collector
#
# - Prefers trusted feeds but now requires team signal (title or URL looks NFL/Eagles)
# - Filters obvious non-team noise
# - Dedupe by URL+title
# - Writes items.json with sources + updated_at
#
# pip install feedparser requests

from __future__ import annotations
import json, re, time, hashlib, html, pathlib, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, urlunparse, unquote

import feedparser  # type: ignore

# ---- project config ----------------------------------------------------------
try:
    from feeds import FEEDS, TEAM_NAME, TEAM_SLUG, EXCLUDE_TOKENS
except Exception as e:
    print(f"[collector] ERROR importing feeds.py: {e}", file=sys.stderr)
    raise

# ---- knobs -------------------------------------------------------------------
MAX_ITEMS       = 50    # <= requested hard cap
BOOTSTRAP_MIN   = 16    # floor so the page never looks empty
RECENT_DAYS_MAX = 14    # (kept for future use)

# ---- helpers ----------------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def to_timestamp(entry) -> float:
    for key in ("published_parsed", "updated_parsed"):
        ts = getattr(entry, key, None) or entry.get(key)
        if ts:
            try:
                return time.mktime(ts)
            except Exception:
                pass
    return time.time()

def strip_tracking(u: str) -> str:
    if not u:
        return u
    try:
        parsed = urlparse(u)
        q = parse_qs(parsed.query)

        # Unwrap Google News redirects (url=)
        if "url" in q and q["url"]:
            candidate = unquote(q["url"][0])
            if candidate.startswith("http://") or candidate.startswith("https://"):
                u = candidate
                parsed = urlparse(u)
                q = parse_qs(parsed.query)

        drop = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","utm_id",
                "ncid","ref","fbclid","gclid"}
        new_q = []
        for k, vals in q.items():
            if k.lower() in drop:
                continue
            for v in vals:
                new_q.append(f"{k}={v}")
        query = "&".join(new_q)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", query, ""))
    except Exception:
        return u

def norm_title(t: str) -> str:
    t = html.unescape((t or "").strip())
    t = re.sub(r"\s+", " ", t)
    return t

def looks_like_team_title_or_source(text: str) -> bool:
    t = (text or "").lower()
    return ("eagles" in t) or ("philadelphia eagles" in t)

def looks_like_team_url(u: str) -> bool:
    try:
        p = urlparse(u)
        path = (p.path or "").lower()
        query = (p.query or "").lower()
        net = (p.netloc or "").lower()
        if "eagles" in path or "philadelphia-eagles" in path:
            return True
        if "/nfl/" in path or net.endswith("nfl.com"):
            return True
        if "team=phi" in query:
            return True
        return False
    except Exception:
        return False

def is_excluded(text: str) -> bool:
    t = (text or "")
    for bad in EXCLUDE_TOKENS:
        if re.search(rf"\b{re.escape(bad)}\b", t, flags=re.I):
            return True
    return False

def extract_source(entry, feed_name: str) -> str:
    src = ""
    try:
        src = getattr(getattr(entry, "source", None), "title", "") or ""
    except Exception:
        src = ""
    if not src:
        src = feed_name or ""
    return (src.replace(" - ", " — ").strip() or "Unknown")

def entry_to_item(entry, feed_name: str) -> dict:
    title = norm_title(getattr(entry, "title", "") or entry.get("title", ""))
    link  = getattr(entry, "link", "") or entry.get("link", "")
    link  = strip_tracking(link)
    published_ts = to_timestamp(entry)
    published_iso = datetime.fromtimestamp(published_ts, tz=timezone.utc).isoformat()
    source = extract_source(entry, feed_name)
    return {
        "title": title,
        "link": link,
        "published": published_iso,
        "published_ts": published_ts,
        "source": source
    }

def feed_is_trusted(feed_cfg: dict) -> bool:
    return bool(feed_cfg.get("trusted"))

# ---- collection -------------------------------------------------------------
def collect() -> dict:
    items: list[dict] = []
    seen: set[str] = set()
    sources_set: set[str] = set()

    feeds_sorted = sorted(FEEDS, key=lambda f: (not f.get("trusted"), f.get("name","").lower()))

    for f in feeds_sorted:
        fname = f.get("name", "").strip() or "Feed"
        url   = f.get("url", "").strip()
        if not url:
            continue

        parsed = feedparser.parse(url)
        entries = parsed.entries or []

        for e in entries:
            it = entry_to_item(e, fname)
            key = hashlib.sha1((it["link"] + " | " + it["title"].lower()).encode("utf-8")).hexdigest()
            if key in seen:
                continue

            # drop obvious noise by title
            if is_excluded(it["title"]):
                continue

            # acceptance rules
            trusted = feed_is_trusted(f)
            title_hit  = looks_like_team_title_or_source(it["title"])
            source_hit = looks_like_team_title_or_source(it["source"])
            url_hit    = looks_like_team_url(it["link"])

            # NEW: trusted also needs team-in-title OR NFL/team-ish URL
            if trusted:
                keep = title_hit or url_hit or source_hit
            else:
                keep = title_hit or source_hit

            if not keep:
                continue

            seen.add(key)
            items.append(it)
            sources_set.add(it["source"])

    # Bootstrap to ensure page looks alive
    if len(items) < BOOTSTRAP_MIN:
        extras: list[dict] = []
        for f in feeds_sorted:
            if not feed_is_trusted(f):
                continue
            parsed = feedparser.parse(f.get("url",""))
            for e in parsed.entries or []:
                it = entry_to_item(e, f.get("name","Feed"))
                if is_excluded(it["title"]):
                    continue
                # still require at least a weak signal for bootstrap
                if not (looks_like_team_title_or_source(it["title"]) or looks_like_team_url(it["link"]) or looks_like_team_title_or_source(it["source"])):
                    continue
                key = hashlib.sha1((it["link"] + " | " + it["title"].lower()).encode("utf-8")).hexdigest()
                if key in seen:
                    continue
                seen.add(key)
                extras.append(it)
                sources_set.add(it["source"])
        extras.sort(key=lambda x: x["published_ts"], reverse=True)
        need = max(0, BOOTSTRAP_MIN - len(items))
        if need:
            items.extend(extras[:need])

    # sort newest first, trim, drop helper field
    items.sort(key=lambda x: x["published_ts"], reverse=True)
    items = items[:MAX_ITEMS]
    for it in items:
        it.pop("published_ts", None)

    return {
        "team": TEAM_NAME,
        "slug": TEAM_SLUG,
        "updated_at": now_iso(),
        "count": len(items),
        "sources": sorted(sources_set),
        "items": items
    }

def main():
    data = collect()
    pathlib.Path("items.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collector] wrote {data['count']} items; {len(data['sources'])} sources; updated items.json")

if __name__ == "__main__":
    main()