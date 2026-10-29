"""Print the static metadata and image baseline without executing site JavaScript."""
from pathlib import Path
from bs4 import BeautifulSoup
import json

pages = []
for path in Path('dist').rglob('*.html'):
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    def meta(**attrs):
        node = soup.find('meta', attrs=attrs)
        return node.get('content') if node else None
    pages.append({
        'page': str(path), 'title': soup.title.get_text(),
        'description': meta(name='description'), 'viewport': meta(name='viewport'),
        'robots': meta(name='robots'), 'h1_count': len(soup.select('h1')),
        'canonical': canonical.get('href') if (canonical := soup.select_one('link[rel="canonical"]')) else None,
        'social_tags': [m.get('property') or m.get('name') for m in soup.find_all('meta') if (m.get('property') or m.get('name') or '').startswith(('og:', 'twitter:'))],
        'images_without_dimensions': [i.get('src') for i in soup.select('img') if not (i.get('width') and i.get('height'))],
        'preloads': [link.get('href') for link in soup.select('link[rel="preload"]')],
        'structured_data': len(soup.find_all('script', type='application/ld+json')),
    })
print(json.dumps(pages, indent=2))
