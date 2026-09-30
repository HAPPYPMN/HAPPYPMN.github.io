# Minnan Pei · 裴旻楠

Bilingual academic homepage, built with Jekyll on GitHub Pages. The design follows conventional research homepages: white background, a compact biography and portrait, plain blue links, and a text-based publication list.

- English: https://happypmn.github.io/
- 中文: https://happypmn.github.io/index_zh.html
- Sitemap: https://happypmn.github.io/sitemap.xml

## Editing

- `_data/t.yml`: both homepage languages, internship dates and teams, education, and academic service.
- `_data/publications.yml`: shared paper titles, author order and equal-contribution marks, publication status, topic, summaries, and public links. Do not turn under-review work into accepted work without confirmation from the author.
- `_publications/<key>.md`: each paper's stable URL and page metadata. Add a matching file when adding a publication. Keep its title and description in sync with the shared data.
- `_includes/home.html`, `_layouts/`: semantic HTML templates.
- `assets/css/style.scss`: custom responsive theme; no remote fonts or CSS dependencies.
- `assets/images/portrait.webp`: optimized display photo; the original remains at `assets/images/1.jpg`.
- `assets/Minnan-Pei-CV.pdf`: existing public CV. The website update does not regenerate this PDF.

The two homepages share all publication data. The site does not require JavaScript. There is currently no selected-projects section. Avoid promotional slogans, oversized hero text, decorative illustrations, card grids, and numbered section labels. Existing `/index.html`, `/index_zh.html`, and RouteCraft URLs remain usable.

## Build and check

```sh
bundle install
bundle exec jekyll build --destination .preview-site
python -m pip install beautifulsoup4 playwright
python -m playwright install chromium
python scripts/check_site.py .preview-site
python scripts/check_browser.py .preview-site
```

Browser QA writes screenshots and a results file to the ignored `artifacts/homepage-qa/` directory. It checks desktop, tablet, and mobile widths, both languages, language switching, paper layout, no-JavaScript content, keyboard entry, and removal of the projects section. `check_site.py` checks local links and fragments, JSON-LD, metadata, and sitemap URLs. Update expected counts in the checks when adding papers.

GitHub Pages builds from `main` at the repository root. `.preview-site` is for local testing. The legacy tracked `_site` directory is not the publishing source. Working CV sources, temporary files, QA tools, and internal research notes are excluded from the Jekyll output. The existing Google verification HTML is preserved.

## Search visibility

Implemented: descriptive bilingual titles and descriptions; self-canonical URLs; reciprocal `hreflang`; visible topic and project vocabulary; paper-specific URLs; `ProfilePage` / `Person` / `ScholarlyArticle` JSON-LD; basic citation metadata; a canonical XML sitemap; robots discovery; Open Graph and Twitter sharing metadata.

Paper pages currently contain short research overviews, not the full author-written abstracts. External arXiv PDFs remain ordinary links. They are deliberately not declared as `citation_pdf_url`, which Google Scholar requires to point into the abstract page's own directory. These pages support ordinary web search discovery; the metadata alone does not make them eligible for Google Scholar. To target Scholar inclusion later, add the complete author-approved abstract and any authorized local full text, with accurate bibliographic details.

After deployment, the site owner can submit `https://happypmn.github.io/sitemap.xml` in Google Search Console and Bing Webmaster Tools, inspect both homepages and representative paper URLs, and request a recrawl. No search-engine account submission is performed by this code change. Keep the homepage linked from Google Scholar, GitHub, and institutional profiles, and monitor actual search queries before adjusting copy. No ranking or indexing outcome is guaranteed.

References: [Google localized pages](https://developers.google.com/search/docs/specialty/international/localized-versions), [profile structured data](https://developers.google.com/search/docs/appearance/structured-data/profile-page), [sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), and [Scholar inclusion](https://scholar.google.com/intl/en/scholar/inclusion.html).

Primary design reference: [Jon Barron's academic homepage](https://jonbarron.info/). Also reviewed [Academic Pages](https://academicpages.github.io/) and [Shun Zhang's homepage](https://shunzh.github.io/). The site keeps its own Jekyll implementation rather than introducing a new theme dependency.
