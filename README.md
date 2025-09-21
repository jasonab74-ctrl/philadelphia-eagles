# Philadelphia Eagles — News

Live news feed for the Philadelphia Eagles.

- **GitHub Pages** serves `index.html` + `/static/`.
- **GitHub Actions** (`.github/workflows/collect.yml`) runs every 30 min, updates `items.json` from RSS feeds, and commits it back.
- Open [your Pages site URL] to see the latest Eagles headlines.

## Local test
```bash
pip install -r requirements.txt
python collect.py   # fetch items.json
python3 -m http.server 8000
# open http://localhost:8000
