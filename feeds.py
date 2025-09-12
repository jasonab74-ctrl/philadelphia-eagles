# feeds.py
# -----------------------------
# Curated feed list & allow-list for Philadelphia Eagles news.
# We purposely rely on Google/Bing News team queries (broad intake),
# but we filter to a tight set of trusted domains so the results
# stay Eagles-specific and your source dropdown shows ~8–10 sources.

GOOGLE_EAGLES = (
    'https://news.google.com/rss/search?q=%22Philadelphia%20Eagles%22'
    '%20OR%20Eagles%20NFL%20-team%3Aphiladelphiaeagles'
    '&hl=en-US&gl=US&ceid=US:en'
)

BING_EAGLES = (
    'https://www.bing.com/news/search?q=Philadelphia+Eagles&format=rss'
)

# You can add a direct team RSS here if you have one that’s reliable.
# (Keeping this blank avoids “dead feed” outages.)
EXTRA_FEEDS = [
    # 'https://www.philadelphiaeagles.com/rss.xml',
]

FEED_URLS = [GOOGLE_EAGLES, BING_EAGLES, *EXTRA_FEEDS]

# Map host substrings -> nice source names (what appears in the dropdown)
# Only items whose URL host contains one of these keys will be kept.
ALLOW_SOURCES = {
    'espn.com':                    'ESPN — Eagles',
    'bleedinggreennation.com':     'Bleeding Green Nation',
    'usatoday.com':                'Eagles Wire (USA Today)',
    'sports.yahoo.com':            'Yahoo Sports — Eagles',
    'nbcsports.com':               'ProFootballTalk — Eagles',  # nbcsports (PFT)
    'nbcsportsphiladelphia.com':   'NBC Sports Philadelphia',
    'inquirer.com':                'Philadelphia Inquirer',
    'theathletic.com':             'The Athletic — Eagles',
    'philadelphiaeagles.com':      'philadelphiaeagles.com',
    'si.com':                      'SI — Eagles Today',
}

# How many articles to keep
MAX_ITEMS = 50