"""Verify the deployed public routes and media against the generated release manifest."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from statistics import median
from time import perf_counter
from xml.etree import ElementTree
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'content/page-manifest.json').read_text(encoding='utf-8'))
social = json.loads((ROOT / 'content/social.json').read_text(encoding='utf-8'))
business = json.loads((ROOT / 'content/business.json').read_text(encoding='utf-8'))
origin = business['origin']


def inspect(page):
    start = perf_counter()
    response = requests.get(page['canonical'], timeout=30)
    elapsed = round((perf_counter() - start) * 1000)
    soup = BeautifulSoup(response.text, 'html.parser')
    canonical = soup.select_one('link[rel="canonical"]')
    robots = soup.select_one('meta[name="robots"]')
    errors = []
    # The explicit /404.html asset is a 200 utility page; missing routes must return 404.
    if response.status_code != 200:
        errors.append('Unexpected status')
    if not canonical or canonical['href'] != page['canonical']:
        errors.append('Canonical mismatch')
    if not robots or ('noindex' in robots['content']) != (page['indexState'] == 'noindex'):
        errors.append('Robots mismatch')
    if page['indexState'] == 'index' and 'noindex' in response.headers.get('x-robots-tag', ''):
        errors.append('Indexable page has a blocking response header')
    if page['path'] in social['videoPages']:
        video = soup.select_one('meta[property="og:video:secure_url"]')
        if not video or video['content'] != origin + social['video']:
            errors.append('Missing social video')
    return {'path': page['path'], 'status': response.status_code, 'canonical': canonical.get('href') if canonical else None,
            'robots': robots.get('content') if robots else None, 'xRobotsTag': response.headers.get('x-robots-tag'),
            'contentType': response.headers.get('content-type'), 'decodedHtmlBytes': len(response.content),
            'responseHeadersMs': round(response.elapsed.total_seconds() * 1000), 'totalMs': elapsed, 'errors': errors}


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        pages = list(pool.map(inspect, manifest['pages']))
    sitemap = requests.get(origin + '/sitemap.xml', timeout=30)
    urls = {node.text for node in ElementTree.fromstring(sitemap.content).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    expected = {page['canonical'] for page in manifest['pages'] if page['indexState'] == 'index'}
    robot_response = requests.get(origin + '/robots.txt', timeout=30)
    video = requests.get(origin + social['video'], headers={'Range': 'bytes=0-1023'}, timeout=30)
    image = requests.get(origin + social['image'], timeout=30)
    image_size = Image.open(BytesIO(image.content)).size
    errors = [page['path'] + ': ' + issue for page in pages for issue in page['errors']]
    if urls != expected: errors.append('Live sitemap does not match indexable pages')
    if 'Disallow: /' in robot_response.text or 'Allow: /' not in robot_response.text: errors.append('Live robots.txt blocks crawling')
    if video.status_code not in (200, 206) or 'video/mp4' not in video.headers.get('content-type', ''): errors.append('MP4 is not accessible with the expected MIME type')
    if image.status_code != 200 or image_size != (1200, 630): errors.append('Social image is not a 1200x630 image')
    missing = requests.get(origin + '/not-a-real-service-qa/', timeout=30)
    if missing.status_code != 404: errors.append('Unknown route does not return 404')
    redirects = []
    for host in ('houstonenginebuilders.com', 'www.houstonenginebuilders.com'):
        response = requests.get('https://' + host + '/', timeout=30, allow_redirects=False)
        target = origin + '/services/engine-diagnostics/'
        redirects.append({'host': host, 'status': response.status_code, 'location': response.headers.get('location')})
        if response.status_code != 301 or response.headers.get('location') != target: errors.append(host + ' redirect mismatch')
    report = {'pagesChecked': len(pages), 'sitemapEntries': len(urls), 'errors': errors,
              'medianResponseHeadersMs': median(page['responseHeadersMs'] for page in pages),
              'timingScope': 'Requests HTTP response-header elapsed time; not LCP, INP, CLS or a browser performance score.',
              'pages': pages, 'robotsTxt': robot_response.text,
              'missingRouteStatus': missing.status_code,
              'video': {'status': video.status_code, 'contentType': video.headers.get('content-type'), 'contentRange': video.headers.get('content-range'),
                        'rangeSupported': video.status_code == 206, 'responseBytes': len(video.content)},
              'image': {'status': image.status_code, 'dimensions': image_size}, 'redirects': redirects}
    (ROOT / 'outputs/seo/live-http.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'pages'}, indent=2))
    raise SystemExit(1 if errors else 0)
