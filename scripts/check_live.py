"""Check public deployment resources and metadata; saves a local HTTP report."""
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

root = Path(__file__).resolve().parents[1]
base = 'https://happypmn.github.io'

def fetch(route):
    with urlopen(Request(base + route, headers={'User-Agent': 'HomepageReleaseCheck/1.0'}), timeout=45) as response:
        return route, response.status, response.read()

routes = ['/', '/index_zh.html', '/robots.txt', '/sitemap.xml', '/assets/css/style.css',
          '/favicon.ico', '/assets/images/favicon-p.svg', '/assets/images/portrait.webp',
          '/assets/images/social-card.png', '/google04628dea8fc4532f.html']
routes.extend('/research/' + path.stem + '/' for path in (root / '_publications').glob('*.md'))
with ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(fetch, routes))
report = []
for route, status, body in results:
    assert status == 200, (route, status)
    if route in ['/', '/index_zh.html']:
        soup = BeautifulSoup(body, 'html.parser')
        assert 'AI Factory' in soup.get_text()
        assert len(soup.select('[data-publication]')) == 13
        assert len(soup.select('.experience-entry')) == 2
        assert not soup.select('#projects, .hero-statement, .profile-card')
        assert soup.select_one('link[type="image/svg+xml"]')['href'].endswith('favicon-p.svg')
        json.loads(soup.select_one('script[type="application/ld+json"]').string)
    if route.startswith('/research/'):
        soup = BeautifulSoup(body, 'html.parser')
        assert soup.select_one('meta[name=citation_title]')
        assert json.loads(soup.select_one('script[type="application/ld+json"]').string)['@type'] == 'ScholarlyArticle'
    if route == '/sitemap.xml':
        assert len(ET.fromstring(body)) == 19
    if route == '/favicon.ico':
        assert body[:4] == bytes([0, 0, 1, 0]), 'Invalid ICO'
    if route == '/assets/images/favicon-p.svg':
        assert b'<path' in body and b'<text' not in body, 'Icon must not depend on an installed font'
    report.append({'url': base + route, 'status': status, 'bytes': len(body)})
    print(f'{status} {route}')
out = root / '.local/qa/live'
out.mkdir(parents=True, exist_ok=True)
(out / 'http-results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('PASS: deployed homepages, 13 papers, metadata, favicons, and public assets.')
