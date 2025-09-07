# feeds.py — Philadelphia Eagles

TEAM_NAME = "Philadelphia Eagles"
TEAM_SLUG = "philadelphia-eagles"

# Filter out obvious cross-sport noise
EXCLUDE_TOKENS = [
    "Flyers", "Sixers", "76ers", "Phillies", "Union",
    "NBA", "NHL", "MLB", "MLS", "soccer", "tennis", "golf",
    "women", "wbb", "college", "NCAA"
]

FEEDS = [
    # Team-focused (trusted)
    {"name": "Bleeding Green Nation",    "url": "https://www.bleedinggreennation.com/rss/index.xml",                    "trusted": True},
    {"name": "Eagles Wire (USA Today)",  "url": "https://theeagleswire.usatoday.com/feed/",                              "trusted": True},
    {"name": "ESPN — Eagles",            "url": "https://www.espn.com/espn/rss/nfl/team?team=phi",                       "trusted": True},
    {"name": "Yahoo Sports — Eagles",    "url": "https://sports.yahoo.com/nfl/teams/phi/rss/",                           "trusted": True},
    {"name": "SI — Eagles Today",        "url": "https://www.si.com/nfl/eagles/.rss",                                    "trusted": True},
    {"name": "ProFootballTalk — Eagles", "url": "https://profootballtalk.nbcsports.com/team/philadelphia-eagles/feed/", "trusted": True},
    {"name": "CBS Sports — Eagles",      "url": "https://www.cbssports.com/nfl/teams/PHI/philadelphia-eagles/rss/",      "trusted": True},

    # Local voices (filtered via GN)
    {"name": "Philly Inquirer — Eagles (GN)",
     "url": "https://news.google.com/rss/search?q=site:inquirer.com+%22Philadelphia+Eagles%22&hl=en-US&gl=US&ceid=US:en",
     "trusted": False},
    {"name": "NBC Sports Philadelphia — Eagles (GN)",
     "url": "https://news.google.com/rss/search?q=site:nbcsportsphiladelphia.com+%22Eagles%22&hl=en-US&gl=US&ceid=US:en",
     "trusted": False},
    {"name": "94WIP — Eagles (GN)",
     "url": "https://news.google.com/rss/search?q=site:94wip.com+%22Eagles%22&hl=en-US&gl=US&ceid=US:en",
     "trusted": False},
    {"name": "Crossing Broad — Eagles (GN)",
     "url": "https://news.google.com/rss/search?q=site:crossingbroad.com+%22Eagles%22&hl=en-US&gl=US&ceid=US:en",
     "trusted": False},

    # Broad aggregators (filtered)
    {"name": "\"Philadelphia Eagles\" — Google News",
     "url": "https://news.google.com/rss/search?q=%22Philadelphia+Eagles%22&hl=en-US&gl=US&ceid=US:en",
     "trusted": False},
    {"name": "Bing News — Philadelphia Eagles",
     "url": "https://www.bing.com/news/search?q=Philadelphia+Eagles&format=rss",
     "trusted": False}
]

STATIC_LINKS = [
    {"label":"Schedule","url":"https://www.philadelphiaeagles.com/schedule/"},
    {"label":"Roster","url":"https://www.philadelphiaeagles.com/team/players-roster/"},
    {"label":"Depth Chart","url":"https://www.philadelphiaeagles.com/team/depth-chart/"},
    {"label":"Injury Report","url":"https://www.philadelphiaeagles.com/team/injury-report/"},
    {"label":"Tickets","url":"https://www.ticketmaster.com/philadelphia-eagles-tickets/artist/805961"},
    {"label":"Team Shop","url":"https://store.philadelphiaeagles.com/"},
    {"label":"Reddit","url":"https://www.reddit.com/r/eagles/"},
    {"label":"Bleacher Report","url":"https://bleacherreport.com/philadelphia-eagles"},
    {"label":"ESPN Team","url":"https://www.espn.com/nfl/team/_/name/phi/philadelphia-eagles"},
    {"label":"Yahoo Team","url":"https://sports.yahoo.com/nfl/teams/phi/"},
    {"label":"PFF Team Page","url":"https://www.pff.com/nfl/teams/philadelphia-eagles"},
    {"label":"Pro-Football-Reference","url":"https://www.pro-football-reference.com/teams/phi/"},
    {"label":"NFL Power Rankings","url":"https://www.nfl.com/news/power-rankings"},
    {"label":"Stats","url":"https://www.nfl.com/teams/philadelphia-eagles/stats/"},
    {"label":"Standings","url":"https://www.nfl.com/standings/league/2025/REG"}
]