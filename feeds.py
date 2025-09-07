TEAM_NAME = "Philadelphia Eagles"
TEAM_SLUG = "philadelphia-eagles"

TEAM_KEYWORDS  = [
    "Eagles", "Philadelphia", "Philly",
    "Jalen Hurts", "Hurts", "Sirianni", "Nick Sirianni",
    "Lincoln Financial", "The Linc"
]
SPORT_TOKENS   = [
    "NFL", "football", "game", "preview", "recap",
    "roster", "depth", "injury", "transaction",
    "training camp", "preseason", "regular season", "playoffs", "Super Bowl"
]
EXCLUDE_TOKENS = [
    "Flyers", "Sixers", "76ers", "Phillies", "Union",
    "NBA", "NHL", "MLB", "MLS",
    "women", "wbb", "soccer", "college"
]

FEEDS = [
    {"name": "philadelphiaeagles.com",        "url": "https://www.philadelphiaeagles.com/rss/",                               "trusted": True},
    {"name": "NFL.com — Philadelphia Eagles", "url": "https://www.nfl.com/rss/team/phi",                                     "trusted": True},
    {"name": "Eagles Wire (USA Today)",       "url": "https://theeagleswire.usatoday.com/feed/",                              "trusted": True},
    {"name": "Bleeding Green Nation",         "url": "https://www.bleedinggreennation.com/rss/index.xml",                    "trusted": True},
    {"name": "ESPN — Eagles",                 "url": "https://www.espn.com/espn/rss/nfl/team?team=phi",                       "trusted": True},
    {"name": "Yahoo Sports — Eagles",         "url": "https://sports.yahoo.com/nfl/teams/phi/rss/",                           "trusted": True},
    {"name": "SI — Eagles Today",             "url": "https://www.si.com/nfl/eagles/.rss",                                    "trusted": True},
    {"name": "ProFootballTalk — Eagles",      "url": "https://profootballtalk.nbcsports.com/team/philadelphia-eagles/feed/", "trusted": True},

    {"name": "\"Philadelphia Eagles\" — Google News",
     "url": "https://news.google.com/rss/search?q=%22Philadelphia+Eagles%22&hl=en-US&gl=US&ceid=US:en",
     "trusted": False},
    {"name": "Bing News — Philadelphia Eagles",
     "url": "https://www.bing.com/news/search?q=Philadelphia+Eagles&format=rss",
     "trusted": False},
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
    {"label":"Standings","url":"https://www.nfl.com/standings/league/2025/REG"},
]