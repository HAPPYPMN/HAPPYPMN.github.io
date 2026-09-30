"""Validate a Jekyll build: python scripts/check_site.py .preview-site."""
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import json
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.preview-site').resolve()
base = 'https://happypmn.github.io'
pages = [root / 'index.html', root / 'index_zh.html', *sorted((root / 'research').glob('*/index.html'))]
assert len(pages) == 15, f'Expected 2 homepages and 13 paper pages, got {len(pages)}'
errors = []
all_titles = set()
for path in pages:
    source = path.read_text(encoding='utf-8')
    soup = BeautifulSoup(source, 'html.parser')
    label = path.relative_to(root).as_posix()
    try:
        assert '{{' not in source and '{%' not in source, 'Unrendered Liquid'
        assert len(soup.select('h1')) == 1, 'Expected exactly one H1'
        title = soup.title.get_text()
        assert title not in all_titles, 'Duplicate title'
        all_titles.add(title)
        assert soup.select_one('meta[name=description]')['content'], 'Missing description'
        assert len(soup.select('link[rel=canonical]')) == 1
        canonical = soup.select_one('link[rel=canonical]')['href']
        assert canonical.startswith(base)
        scripts = soup.select('script[type="application/ld+json"]')
        assert scripts, 'Missing structured data'
        for script in scripts:
            data = json.loads(script.string)
        if 'research/' in label:
            assert data['@type'] == 'ScholarlyArticle'
            assert any(a.get('@id') == base + '/#person' for a in data['author'])
            assert soup.select_one('meta[name=citation_title]')
        else:
            assert len(soup.select('[data-publication]')) == 13
            assert len(soup.select('link[hreflang]')) == 3
            assert len(soup.select('.experience-card')) == 2
            assert 'AI Factory' in soup.get_text()
        ids = [el['id'] for el in soup.select('[id]')]
        assert len(ids) == len(set(ids)), 'Duplicate HTML IDs'
        for el in soup.select('a[href], img[src], script[src], link[rel=stylesheet], link[rel=icon]'):
            href = el.get('href', el.get('src', ''))
            assert href and '[' not in href, f'Empty or placeholder URL: {href}'
            parsed = urlparse(urljoin(canonical, href))
            if parsed.netloc != 'happypmn.github.io':
                continue
            target = root / unquote(parsed.path.lstrip('/'))
            if target.is_dir():
                target = target / 'index.html'
            assert target.is_file(), f'Missing local target {href}'
            if parsed.fragment and target.suffix == '.html':
                dest = BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
                assert dest.find(id=unquote(parsed.fragment)), f'Missing anchor {href}'
    except (AssertionError, KeyError, ValueError) as exc:
        errors.append(f'{label}: {exc}')

sitemap = ET.parse(root / 'sitemap.xml')
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls = [el.text for el in sitemap.findall('.//s:loc', ns)]
assert len(urls) == 19 and len(set(urls)) == 19, 'Sitemap should have 19 unique canonical URLs'
for url in urls:
    target = root / urlparse(url).path.lstrip('/')
    if target.is_dir():
        target /= 'index.html'
    assert target.is_file(), f'Sitemap missing page: {url}'
assert f'Sitemap: {base}/sitemap.xml' in (root / 'robots.txt').read_text()
assert not (root / 'resume_2p').exists(), 'Private working CV sources must not be built'
assert not (root / 'scripts').exists(), 'QA tooling must not be published'
assert (root / 'google04628dea8fc4532f.html').is_file(), 'Preserve Google verification file'
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, structured data, citation metadata, local links/anchors, bilingual alternates, and {len(urls)} sitemap URLs.')
