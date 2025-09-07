
# Philadelphia Eagles — News

Static GitHub Pages site + GitHub Actions collector.
- `collect.py` fetches feeds -> writes `items.json`
- `index.html` renders cards from `items.json`
- `.nojekyll` required for Pages
- `.github/workflows/collect.yml` runs every 30 min + on-demand
