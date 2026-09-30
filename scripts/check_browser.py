"""Headless rendering regression check; serves only the supplied build on loopback."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import sys
import json
from playwright.sync_api import sync_playwright

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.preview-site').resolve()
out = Path('artifacts/homepage-qa')
out.mkdir(parents=True, exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(root)))
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}'
results = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in [1440, 1024, 768, 390, 320]:
            for route, lang in [('/', 'en'), ('/index_zh.html', 'zh')]:
                page = browser.new_page(viewport={'width': width, 'height': 1000}, device_scale_factor=1)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}') if response.status >= 400 else None)
                page.goto(base + route, wait_until='networkidle')
                assert page.locator('h1').count() == 1
                assert page.locator('[data-publication]:visible').count() == 13
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Horizontal overflow: {width} {lang}'
                assert page.locator('img').evaluate_all('(imgs) => imgs.every(i => i.complete && i.naturalWidth > 0)'), 'Image did not load'
                if width in [1440,390]:
                    page.screenshot(path=str(out / f'{lang}-{width}.png'), full_page=True)
                    page.screenshot(path=str(out / f'{lang}-{width}-hero.png'))
                page.locator('button[data-topic="3DGS"]').click()
                assert page.locator('[data-publication]:visible').count() == 4
                assert page.locator('button[data-topic="3DGS"]').get_attribute('aria-pressed') == 'true'
                page.locator('button[data-topic="LLM / VLA"]').click()
                assert page.locator('[data-publication]:visible').count() == 5
                page.locator('button[data-topic="all"]').click()
                assert page.locator('[data-publication]:visible').count() == 13
                page.locator('a.language-link').click()
                assert page.locator('html').get_attribute('lang') == ('zh-CN' if lang == 'en' else 'en')
                assert not errors, errors
                results.append({'width':width,'language':lang,'overflow':False,'filters':'pass','language_switch':'pass'})
                page.close()
        for width in [1440,390,320]:
            page=browser.new_page(viewport={'width':width,'height':900})
            page.goto(base+'/research/degs/',wait_until='networkidle')
            assert page.locator('h1').inner_text().startswith('DeGS:')
            assert page.locator('meta[name="citation_title"]').count() == 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            if width==1440:
                page.screenshot(path=str(out/'paper-desktop.png'),full_page=True)
            page.close()
        context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        page=context.new_page()
        page.goto(base+'/')
        assert page.locator('[data-publication]:visible').count()==13
        assert page.locator('[data-filters]:visible').count()==0
        context.close()
        page=browser.new_page(reduced_motion='reduce')
        page.goto(base+'/')
        assert page.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
        page.keyboard.press('Tab')
        assert page.locator('.skip-link').evaluate('(el) => el === document.activeElement')
        page.close()
        browser.close()
    (out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('PASS: 10 bilingual viewport checks, publication filters, language switching, 3 paper viewports, no-JS content, reduced motion, keyboard skip link. Screenshots: '+str(out))
finally:
    server.shutdown()
    server.server_close()
