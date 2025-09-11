
# feeds.py — Philadelphia Eagles sources only

FEEDS = [
    # Team site
    {
        "name": "philadelphiaeagles.com",
        "url": "https://www.philadelphiaeagles.com/rss/news",
    },

    # USA Today network (Eagles Wire)
    {
        "name": "Eagles Wire (USA Today)",
        "url": "https://sports.yahoo.com/rss/u/collegiate-football/teams/philadelphia-eagles"  # fallback if USA Today RSS blocks;
    },
    {
        "name": "Eagles Wire (USA Today)",
        "url": "https://sports.yahoo.com/philadelphia-eagles/rss/",  # second fallback (Yahoo mirrors many EW posts)
    },

    # ESPN team feed
    {
        "name": "ESPN — Eagles",
        "url": "https://www.espn.com/espn/rss/nfl/team/_/name/phi",
    },

    # Yahoo team
    {
        "name": "Yahoo Sports — Eagles",
        "url": "https://sports.yahoo.com/nfl/teams/philadelphia-eagles/rss/",
    },

    # SB Nation
    {
        "name": "Bleeding Green Nation",
        "url": "https://www.bleedinggreennation.com/rss/index.xml",
    },

    # Sports Illustrated
    {
        "name": "SI — Eagles Today",
        "url": "https://www.si.com/rss/philadelphia-eagles.xml",
    },

    # ProFootballTalk tag
    {
        "name": "ProFootballTalk — Eagles",
        "url": "https://profootballtalk.nbcsports.com/team/philadelphia-eagles/feed/",
    },

    # Google News (team-focused query; tends to surface outlets like AP, local papers, etc.)
    {
        "name": "Google News — Eagles",
        "url": (
            "https://news.google.com/rss/search?"
            "q=%22Philadelphia%20Eagles%22%20OR%20Eagles%20when%3A7d&hl=en-US&gl=US&ceid=US:en"
        ),
    },
]