"""Regression checks for publication safety, real routes and service conversion context."""
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import sys
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_seo


class PublicationGates(unittest.TestCase):
    def setUp(self):
        self.business = build_seo.read_json('business.json')
        self.location = build_seo.read_json('locations.json')[0]

    def test_houston_has_verified_publication_context(self):
        self.assertEqual([], build_seo.location_errors(self.location, self.business))
        self.assertTrue(self.location['indexingApproved'])

    def test_unverified_coverage_or_shop_cannot_publish(self):
        for key, value in [('coverageVerified', False), ('servingLocationId', 'invented-shop')]:
            location = deepcopy(self.location)
            location[key] = value
            self.assertTrue(build_seo.location_errors(location, self.business))

    def test_repeating_one_proof_item_does_not_pass(self):
        self.location['localEvidence'] = [self.location['localEvidence'][0]] * 3
        self.assertTrue(build_seo.location_errors(self.location, self.business))

    def test_city_name_without_local_content_does_not_pass(self):
        self.location['sections'] = []
        self.location['faqs'] = []
        self.assertTrue(build_seo.location_errors(self.location, self.business))

    def test_switching_one_flag_cannot_launch_incomplete_business(self):
        self.business['launchState'] = 'production'
        self.business['indexingApproved'] = True
        self.business['contactPolicy'] = {}
        errors = build_seo.production_errors(self.business)
        self.assertTrue(any('phone' in message for message in errors))
        self.assertTrue(any('hours' in message for message in errors))

    def test_owner_can_keep_phone_hidden_and_use_verified_address_and_booking(self):
        self.assertEqual([], build_seo.production_errors(self.business))
        self.business['phone'] = '+17135550100'
        self.assertTrue(any('hidden phone' in message for message in build_seo.production_errors(self.business)))

    def test_routes_cannot_escape_the_site(self):
        for path in ['/locations/../../private/', '/services/../', '//elsewhere/', '/services/<script>/']:
            with self.assertRaises(ValueError):
                build_seo.destination_for(path)


class BuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.business = build_seo.read_json('business.json')
        cls.pages = {path: BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser') for path in build_seo.DIST.rglob('*.html')}
        cls.details = build_seo.read_json('service-pages.json')

    def test_every_service_has_unique_metadata_and_selected_booking_category(self):
        titles, descriptions = set(), set()
        hub = self.pages[build_seo.DIST / 'services/index.html']
        for detail in self.details:
            path = '/services/' + detail['slug'] + '/'
            soup = self.pages[build_seo.DIST / path.strip('/') / 'index.html']
            title = soup.title.get_text()
            description = soup.select_one('meta[name="description"]')['content']
            self.assertNotIn(title, titles); titles.add(title)
            self.assertNotIn(description, descriptions); descriptions.add(description)
            self.assertEqual(1, len(soup.select('h1')))
            self.assertEqual(self.business['origin'] + path, soup.select_one('link[rel="canonical"]')['href'])
            self.assertIsNotNone(hub.select_one(f'a[href="{path}"]'))
            selected = soup.select_one('#appointment-form select[name="service"] option[selected]')
            self.assertEqual(soup.body['data-service'], selected.get_text())
            graph = json.loads(soup.select_one('script[data-page-schema]').string)['@graph']
            self.assertEqual(1, sum(entity['@type'] == 'Service' for entity in graph))
            self.assertFalse(any(entity['@type'] in ('FAQPage', 'AggregateRating') for entity in graph))
            for entity in graph:
                if entity['@type'] == 'AutoRepair':
                    self.assertNotIn('telephone', entity)
                    self.assertEqual('8614 Pagewood Ln', entity['address']['streetAddress'])

    def test_static_internal_links_and_fragments_resolve(self):
        missing = []
        for page, soup in self.pages.items():
            for link in soup.select('a[href]'):
                url = urlsplit(link['href'])
                if url.scheme or url.netloc:
                    continue
                target = (build_seo.DIST / url.path.lstrip('/')) if url.path.startswith('/') else page.parent / url.path
                if not url.path:
                    target = page
                elif target.is_dir() or url.path.endswith('/'):
                    target = target / 'index.html'
                target = target.resolve()
                if not target.exists():
                    missing.append((str(page.relative_to(build_seo.DIST)), link['href']))
                elif url.fragment and target.suffix == '.html':
                    destination = self.pages.get(target) or BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
                    if not destination.find(id=unquote(url.fragment)):
                        missing.append((str(page.relative_to(build_seo.DIST)), link['href']))
        self.assertEqual([], missing)

    def test_crawl_controls_agree_with_search_launch_state(self):
        production = self.business['launchState'] == 'production'
        sitemap = (build_seo.DIST / 'sitemap.xml').read_text()
        for path, soup in self.pages.items():
            url = soup.select_one('link[rel="canonical"]')['href']
            noindex = 'noindex' in soup.select_one('meta[name="robots"]')['content']
            self.assertEqual(not noindex, url in sitemap)
            if not production:
                self.assertTrue(noindex)
        if production:
            self.assertNotIn('X-Robots-Tag: noindex', (build_seo.DIST / '_headers').read_text())
            self.assertIn('Allow: /', (build_seo.DIST / 'robots.txt').read_text())
        else:
            self.assertIn('X-Robots-Tag: noindex', (build_seo.DIST / '_headers').read_text())
            self.assertIn('Disallow: /', (build_seo.DIST / 'robots.txt').read_text())
            self.assertNotIn('<loc>', sitemap)

    def test_social_video_and_fallback_are_real_local_assets(self):
        social = build_seo.read_json('social.json')
        for resource in ('video', 'image'):
            self.assertTrue((build_seo.DIST / social[resource].lstrip('/')).is_file())
        for canonical_path in social['videoPages']:
            path = build_seo.DIST / canonical_path.strip('/') / 'index.html'
            soup = self.pages[path]
            self.assertEqual(self.business['origin'] + social['video'], soup.select_one('meta[property="og:video:secure_url"]')['content'])
            self.assertEqual('video/mp4', soup.select_one('meta[property="og:video:type"]')['content'])
            self.assertEqual(self.business['origin'] + social['image'], soup.select_one('meta[property="og:image"]')['content'])
        film = self.pages[build_seo.DIST / 'film/index.html']
        self.assertEqual('none', film.video['preload'])
        self.assertIsNotNone(film.select_one(f'a[href="{social["source"]}"]'))

    def test_old_service_fragments_still_resolve_and_new_navigation_is_direct(self):
        hub = self.pages[build_seo.DIST / 'services/index.html']
        home = self.pages[build_seo.DIST / 'index.html']
        for detail in self.details:
            self.assertIsNotNone(hub.find(id=detail['slug']))
            self.assertIsNotNone(home.select_one(f'.services-dropdown a[href="/services/{detail["slug"]}/"]'))

    def test_json_ld_parses_and_dom_ids_are_unique(self):
        for path, soup in self.pages.items():
            ids = [element['id'] for element in soup.select('[id]')]
            self.assertEqual(len(ids), len(set(ids)), str(path))
            for script in soup.select('script[type="application/ld+json"]'):
                json.loads(script.string)


if __name__ == '__main__':
    unittest.main()
