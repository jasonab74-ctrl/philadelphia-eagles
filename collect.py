#!/usr/bin/env python3
# collect.py — generic collector with Eagles-ready defaults
#
# - Pulls FEEDS from feeds.py
# - Filters to team content but "bootstraps" if volume is low
# - Dedupe by canonical URL + normalized title
# - Writes items.json with sources + updated_at
#
# Requirements: feedparser, requests

from __future__ import annotations
import json, re, time, hashlib, html, pathlib, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, urlunparse, unquote

import feedparser  # type: ignore

# ---- project config (from feeds.py) -----------------------------------------
try:
    from feeds import FEEDS, TEAM_NAME, TEAM_SLUG, EXCLUDE_TOKENS
except Exception as e:
    print(f"[collector] ERROR importing feeds.py: {e}", file=sys.stderr)
    raise

# ---- knobs ------------------------------------------------------------------
MAX_ITEMS       = 150   # cap for written items
BOOTSTRAP_MIN   = 16    # ensure at least this many render on page
RECENT_DAYS_MAX = 14    # prefer posts in the last N days

# ---- helpers ----------------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def to_timestamp(entry) -> float:
    # prefer published/updated parsed time; fallback to now
    for key in ("published_parsed", "updated_parsed"):
        ts = getattr(entry, key, None) or entry.get(key)
        if ts:
            try:
                return time.mktime(ts)
            except Exception:
                pass
    return time.time()

def strip_tracking(u: str) -> str:
    # remove common tracking params and unwrap Google News/bing redirects
    if not u:
        return u
    try:
        # Google News often wraps as ...url=ENCODED
        parsed = urlparse(u)
        q = parse_qs(parsed.query)

        # unwrap if there is a single 'url' param that looks like http(s)
        if "url" in q and q["url"]:
            candidate = unquote(q["url"][0])
            if candidate.startswith("http://") or candidate.startswith("https://"):
                u = candidate
                parsed = urlparse(u)
                q = parse_qs(parsed.query)

        # rebuild without common trackers
        drop = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","utm_id","ncid","ref","fbclid","gclid"}
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

def looks_like_team(text: str) -> bool:
    """Loose allow-list: keep if it obviously mentions the team."""
    t = (text or "").lower()
    if "eagles" in t:   # team nickname is the strongest signal
        return True
    if "philadelphia eagles" in t:
        return True
    return False

def is_excluded(text: str) -> bool:
    t = (text or "")
    for bad in EXCLUDE_TOKENS:
        if re.search(rf"\b{re.escape(bad)}\b", t, flags=re.I):
            return True
    return False

def extract_source(entry, feed_name: str) -> str:
    # prefer entry.source.title if present (some feeds set it)
    src = ""
    try:
        src = getattr(getattr(entry, "source", None), "title", "") or ""
    except Exception:
        src = ""
    if not src:
        src = feed_name or ""
    # normalize some known patterns like "SI.com - Eagles Today" → "SI — Eagles Today"
    src = src.replace(" - ", " — ")
    return src.strip() or "Unknown"

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

    # sort feeds so trusted run first (better for bootstrap)
    feeds_sorted = sorted(FEEDS, key=lambda f: (not f.get("trusted"), f.get("name","").lower()))

    for f in feeds_sorted:
        fname = f.get("name", "").strip() or "Feed"
        url   = f.get("url", "").strip()
        if not url:
            continue

        parsed = feedparser.parse(url)
        entries = parsed.entries or []

        for e in entries:
            item = entry_to_item(e, fname)

            # basic dedupe key: canonical url + title
            key = hashlib.sha1((item["link"] + " | " + item["title"].lower()).encode("utf-8")).hexdigest()
            if key in seen:
                continue

            # filtering
            title_ok = looks_like_team(item["title"])
            src_ok   = looks_like_team(item["source"])
            trusted  = feed_is_trusted(f)

            # exclude obvious wrong-sport/noise
            if is_excluded(item["title"]):
                continue

            # accept if trusted or clearly team
            keep = trusted or title_ok or src_ok

            # recency preference: allow older stories but score them lower
            # (sorting by published_ts at end will already handle freshness)

            if keep:
                seen.add(key)
                items.append(item)
                sources_set.add(item["source"])

    # Bootstrap: if volume low, relax and keep first N from trusted feeds titles regardless,
    # because trusted sources are team-specific.
    if len(items) < BOOTSTRAP_MIN:
        print(f"[collector] bootstrap engaged (have {len(items)}, need {BOOTSTRAP_MIN})")
        extras: list[dict] = []
        for f in feeds_sorted:
            if not feed_is_trusted(f):
                continue
            parsed = feedparser.parse(f.get("url",""))
            for e in parsed.entries or []:
                item = entry_to_item(e, f.get("name","Feed"))
                if is_excluded(item["title"]):
                    continue
                key = hashlib.sha1((item["link"] + " | " + item["title"].lower()).encode("utf-8")).hexdigest()
                if key in seen:
                    continue
                seen.add(key)
                extras.append(item)
                sources_set.add(item["source"])
        # add until we reach floor
        if extras:
            # sort extras newest first and take enough to reach BOOTSTRAP_MIN
            extras.sort(key=lambda x: x["published_ts"], reverse=True)
            need = max(0, BOOTSTRAP_MIN - len(items))
            items.extend(extras[:need])

    # Final sort newest → oldest, trim, and drop helper field
    items.sort(key=lambda x: x["published_ts"], reverse=True)
    items = items[:MAX_ITEMS]
    for it in items:
        it.pop("published_ts", None)

    out = {
        "team": TEAM_NAME,
        "slug": TEAM_SLUG,
        "updated_at": now_iso(),
        "count": len(items),
        "sources": sorted(sources_set),
        "items": items
    }
    return out

# ---- main -------------------------------------------------------------------
def main():
    data = collect()
    p = pathlib.Path("items.json")
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collector] wrote {data['count']} items; {len(data['sources'])} sources; updated items.json")

if __name__ == "__main__":
    main()