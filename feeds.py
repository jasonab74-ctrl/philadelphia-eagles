# feeds.py — Philadelphia Eagles sources (8–10), all RSS-friendly
# We use Google News RSS with domain filters so everything stays Eagles-focused.

from urllib.parse import quote

def gn(query: str) -> str:
    base = "https://news.google.com/rss/search?q="
    tail = "&hl=en-US&gl=US&ceid=US:en"
    return f"{base}{quote(query)}{tail}"

SOURCES = [
    # Team site
    ("philadelphiaeagles.com", gn('site:philadelphiaeagles.com "Philadelphia Eagles"')),
    # Major outlets — domain-scoped to keep it Eagles-related
    ("ESPN — Eagles",                  gn("Philadelphia Eagles site:espn.com")),
    ("Yahoo Sports — Eagles",          gn("Philadelphia Eagles site:sports.yahoo.com")),
    ("SI — Eagles Today",              gn("Philadelphia Eagles site:si.com")),
    ("Eagles Wire (USA Today)",        gn("site:eagleswire.usatoday.com")),
    ("Bleeding Green Nation",          gn("site:bleedinggreennation.com")),
    ("ProFootballTalk — Eagles",       gn("Philadelphia Eagles site:profootballtalk.nbcsports.com")),
    ("CBS Sports — Eagles",            gn("Philadelphia Eagles site:cbssports.com")),
    ("The Athletic — Eagles",          gn("Philadelphia Eagles site:theathletic.com")),
    # Community
    ("Reddit — r/eagles", "https://www.reddit.com/r/eagles/.rss"),
]

# Trim to first 10 (safety if list grows)
SOURCES = SOURCES[:10]