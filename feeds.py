# 8–10 reliable, team-accurate sources for Philadelphia Eagles.
# Use direct RSS when available; otherwise use Google/Yahoo News RSS with site filters.

SOURCES = [
    # Team site
    {"name": "philadelphiaeagles.com", "url": "https://www.philadelphiaeagles.com/rss/home-page.xml"},

    # ESPN — Eagles
    {"name": "ESPN — Eagles", "url": "https://www.espn.com/espn/rss/nfl/news"},  # ESPN doesn't publish team RSS; we'll keyword-filter in collect.py

    # Bleeding Green Nation
    {"name": "Bleeding Green Nation", "url": "https://www.bleedinggreennation.com/rss/index.xml"},

    # SI — Eagles Today
    {"name": "SI — Eagles Today", "url": "https://www.si.com/rss/aggregator/eagles"},  # SI aggregator path; keyword-filter in collector

    # USA Today — Eagles Wire
    {"name": "Eagles Wire (USA Today)", "url": "https://theeagleswire.usatoday.com/feed/"},

    # Yahoo Sports — Eagles
    {"name": "Yahoo Sports — Eagles", "url": "https://sports.yahoo.com/philadelphia-eagles/rss/"},

    # ProFootballTalk — Eagles (site feed; we keyword-filter)
    {"name": "ProFootballTalk — Eagles", "url": "https://profootballtalk.nbcsports.com/feed/"},

    # Google News — Eagles (broad but high-signal)
    {"name": "Google News — Eagles", "url": "https://news.google.com/rss/search?q=%22Philadelphia+Eagles%22&hl=en-US&gl=US&ceid=US:en"},

    # Bing News — Eagles (secondary aggregator)
    {"name": "Bing News — Eagles", "url": "https://www.bing.com/news/search?q=%22Philadelphia+Eagles%22&format=rss"},

    # The Athletic (if accessible; keyword filter will keep Eagles items)
    {"name": "The Athletic — NFL", "url": "https://theathletic.com/feed/nfl/"},
]