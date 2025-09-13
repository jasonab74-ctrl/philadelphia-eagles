# Feeds for team-specific collectors.
# Keep each feed as "title", "url", and whether it's already team-specific.
# If team_specific=False, the collector will keyword-filter for the team.

EAGLES_KEYWORDS = [
    "Philadelphia Eagles",
    "Eagles",
    "PHI"
]

SOURCES = {
    "eagles": [
        # Official / near-official
        {"title": "philadelphiaeagles.com", "url": "https://www.philadelphiaeagles.com/rss", "team_specific": True},

        # USA Today: Eagles Wire
        {"title": "Eagles Wire (USA Today)", "url": "https://rss.app/feeds/oO5q0kI3wR6GxZ9M.xml", "team_specific": True},

        # SI FanNation — Eagles Today
        {"title": "SI — Eagles Today", "url": "https://rss.app/feeds/Aq3p5MGfX2b3q1yK.xml", "team_specific": True},

        # Bleeding Green Nation
        {"title": "Bleeding Green Nation", "url": "https://www.bleedinggreennation.com/rss/index.xml", "team_specific": True},

        # Yahoo Sports team feed
        {"title": "Yahoo Sports — Eagles", "url": "https://sports.yahoo.com/nfl/teams/phi/rss/", "team_specific": True},

        # ESPN (site-wide; filter by keywords)
        {"title": "ESPN", "url": "https://www.espn.com/espn/rss/nfl/news", "team_specific": False, "keywords": EAGLES_KEYWORDS},

        # ProFootballTalk (site-wide; filter)
        {"title": "ProFootballTalk — Eagles", "url": "https://profootballtalk.nbcsports.com/feed/", "team_specific": False, "keywords": EAGLES_KEYWORDS},

        # Google News query (already scoped)
        {"title": "Google News — Eagles", "url": "https://news.google.com/rss/search?q=%22Philadelphia+Eagles%22&hl=en-US&gl=US&ceid=US:en", "team_specific": True},

        # Bing News query (already scoped)
        {"title": "Bing News — Eagles", "url": "https://www.bing.com/news/search?q=%22Philadelphia+Eagles%22&format=rss", "team_specific": True},
    ]
}