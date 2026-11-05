"""Build useful service/location pages and enforce a single, explicit search-launch state."""
from copy import deepcopy
from html import escape
from pathlib import Path
from urllib.parse import quote
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
REVIEWED = '2026-10-29'
SOURCES = {
    'manufacturer-manuals': [
        ('Porsche owner manuals', 'https://ask.porsche.com/us/en-US/owner-manual'),
        ('Mercedes-Benz owner manuals', 'https://www.mbusa.com/en/owners/manuals'),
    ],
    'bmw-maintenance': [('BMW maintenance information', 'https://www.bmwusa.com/explore/bmw-value/bmw-maintenance/ultimate-care.html/')],
}
UTILITY = {'/404.html', '/brand.html', '/photography.html'}


def destination_for(path):
    if not re.fullmatch(r'/(?:services/[a-z0-9-]+|locations(?:/[a-z0-9-]+)?|film)/', path):
        raise ValueError('Invalid generated route: ' + path)
    destination = (DIST / path.strip('/') / 'index.html').resolve()
    if not destination.is_relative_to(DIST.resolve()):
        raise ValueError('Generated route escapes dist')
    return destination


def read_json(name):
    return json.loads((ROOT / 'content' / name).read_text(encoding='utf-8'))


def address_text(address):
    region = ' '.join(filter(None, [address.get('region'), address.get('postalCode')]))
    return ', '.join(filter(None, [address.get('street'), address.get('city'), region]))


def directions(address):
    return 'https://www.google.com/maps/search/?api=1&query=' + quote(address_text(address))


def production_errors(business):
    if business['launchState'] != 'production':
        return []
    errors = []
    if not business.get('indexingApproved'):
        errors.append('Business indexing approval is missing')
    policy = business.get('contactPolicy', {})
    hidden_phone = policy.get('phone') == 'hidden-at-owner-request'
    if hidden_phone and any(business.get(key) for key in ('phone', 'phoneDisplay', 'textNumber')):
        errors.append('Owner requested a hidden phone; public phone fields must be empty')
    if not hidden_phone and not re.fullmatch(r'\+\d{7,15}', business.get('phone', '')):
        errors.append('Verified public E.164 phone number is missing')
    if not all(business['address'].get(key) for key in ('street', 'city', 'region', 'postalCode')):
        errors.append('Complete verified shop address is missing')
    if not business.get('hours') and policy.get('hours') != 'not-published':
        errors.append('Verified public opening hours are missing')
    if not business.get('booking', {}).get('endpoint', '').startswith('https://'):
        errors.append('A working HTTPS appointment endpoint is required')
    if not any(loc.get('staffed') and loc.get('addressVerified') for loc in business['physicalLocations']):
        errors.append('Verified staffed shop is missing')
    return errors


def location_errors(location, business):
    """Publication gate. Indexing has the additional business/individual approval gate."""
    errors = []
    if not location.get('coverageVerified'):
        errors.append('Coverage is not verified')
    serving = next((entry for entry in business['physicalLocations'] if entry['id'] == location.get('servingLocationId')), None)
    if not serving or not serving.get('staffed') or not serving.get('addressVerified'):
        errors.append('A verified serving shop is missing')
    elif not all(serving['address'].get(key) for key in ('street', 'city', 'region')):
        errors.append('Serving address is incomplete')
    evidence_ids = {entry['id'] for entry in business['evidence']}
    evidence = {entry['id'] for entry in location.get('localEvidence', []) if entry.get('approved') and entry['id'] in evidence_ids}
    if len(evidence) < 2:
        errors.append('Two approved local evidence items are required')
    if not location.get('intent') or not location.get('intro') or len(location.get('sections', [])) < 2 or len(location.get('faqs', [])) < 2:
        errors.append('Distinct local guidance and FAQs are incomplete')
    if location.get('status') != 'ready':
        errors.append('Location record is not ready')
    return errors


def config_for(business):
    return {
        'showPlaceholders': False, 'launchState': business['launchState'], 'showReviewsPreview': False,
        'siteUrl': business['origin'],
        **{key: business[key] for key in ('phone', 'phoneDisplay', 'textNumber', 'email', 'address', 'geo', 'hours', 'rating', 'reviewsUrl', 'reviews', 'sameAs')},
        'mapsUrl': business.get('mapsUrl') or (directions(business['address']) if business['address'].get('street') else ''),
        'requestEndpoint': business['booking']['endpoint'], 'bookingEmail': business['booking']['recipient'],
        'schedulerUrl': business['booking']['schedulerUrl'], **business['analytics'],
    }


def metadata(soup, title, description, path, business):
    origin = business['origin']
    soup.title.string = title
    for selector, value in [
        ('meta[name="description"]', description), ('meta[property="og:title"]', title),
        ('meta[name="twitter:title"]', title), ('meta[property="og:description"]', description),
        ('meta[name="twitter:description"]', description), ('meta[property="og:url"]', origin + path),
    ]:
        tag = soup.select_one(selector)
        if tag:
            tag['content'] = value
    soup.select_one('link[rel="canonical"]')['href'] = origin + path
    for tag in soup.select('link[rel="preload"][as="image"], script[type="application/ld+json"]'):
        tag.decompose()


def breadcrumbs(items):
    links = ''
    for label, path in items:
        content = f'<a href="{escape(path, quote=True)}">{escape(label)}</a>' if path else escape(label)
        current = ' aria-current="page"' if path is None else ''
        links += f'<li{current}>{content}</li>'
    return f'<nav aria-label="Breadcrumb"><ol class="breadcrumb">{links}</ol></nav>'


def breadcrumb_schema(items, business):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': index, 'name': label, 'item': business['origin'] + path}
        for index, (label, path) in enumerate(items, 1)
    ]}


def add_schema(soup, entities, business):
    graph = [{
        '@type': 'Organization', '@id': business['origin'] + '/#organization',
        'name': business['name'], 'url': business['origin'] + '/',
        'logo': business['origin'] + '/assets/logo-512.png',
    }] + entities
    if business['launchState'] == 'production':
        graph.append({
            '@type': 'AutoRepair', '@id': business['origin'] + '/#business',
            'name': business['name'], 'url': business['origin'] + '/locations/houston/',
            **({'telephone': business['phone']} if business['phone'] else {}), 'image': business['origin'] + '/assets/logo-512.png',
            'address': {'@type': 'PostalAddress', 'streetAddress': business['address']['street'],
                        'addressLocality': business['address']['city'], 'addressRegion': business['address']['region'],
                        'postalCode': business['address']['postalCode'], 'addressCountry': 'US'},
            'areaServed': {'@type': 'City', 'name': 'Houston'},
        })
    tag = soup.new_tag('script', type='application/ld+json')
    tag['data-page-schema'] = ''
    if business['launchState'] == 'production':
        tag['data-business-schema'] = ''
    tag.string = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('</', '<\\/')
    soup.head.append(tag)


def faq_section(faqs):
    return '<section class="section porcelain service-faq"><h2>Before you book.</h2><div class="faq-list">' + ''.join(
        f'<details><summary>{escape(question)}<span class="plus" aria-hidden="true"><svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.25"><path d="M10 3v14M3 10h14"/></svg></span></summary><p>{escape(answer)}</p></details>'
        for question, answer in faqs) + '</div></section>'


def hero(heading, lead, crumb, service=None):
    return f'''<section class="service-detail-hero"><div>{crumb}<h1>{heading}</h1>
    <p>{escape(lead)}</p><a class="button platinum" href="#contact">Request an appointment</a></div>
    <figure><img src="/assets/atelier-hero-1280.webp" srcset="/assets/atelier-hero-768.webp 768w, /assets/atelier-hero-1280.webp 1280w" sizes="(max-width: 700px) 100vw, 50vw" alt="Silver European sports coupe in a dark automotive setting" width="1280" height="853" fetchpriority="high"></figure></section>'''


def service_links(slugs, services):
    return '<ul class="related-service-links">' + ''.join(
        f'<li><a href="/services/{slug}/"><span>{escape(services[slug]["name"])}</span><span>{escape(services[slug]["tag"])}</span></a></li>'
        for slug in slugs) + '</ul>'


def write_page(base, path, title, description, main, body_attrs, entities, business):
    soup = deepcopy(base)
    soup.body.attrs = body_attrs
    soup.main.clear()
    soup.main.append(BeautifulSoup(main, 'html.parser'))
    from polish_booking import closing_form
    closing = soup.new_tag('section', attrs={'class': 'contact', 'id': 'contact', 'aria-labelledby': 'appointment-title'})
    closing.append(BeautifulSoup(closing_form(), 'html.parser'))
    soup.main.append(closing)
    metadata(soup, title, description, path, business)
    soup.head.append(soup.new_tag('meta', attrs={'name': 'generator', 'content': 'Houston Auto Pros SEO'}))
    add_schema(soup, entities, business)
    destination = destination_for(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(str(soup).rstrip() + '\n', encoding='utf-8')


def build_services(base, services, details, business):
    for detail in details:
        slug = detail['slug']
        service = services[slug]
        path = f'/services/{slug}/'
        crumb = breadcrumbs([('Home', '/'), ('Services', '/services/'), (service['name'], None)])
        heading = escape(detail['title'].removesuffix(' in Houston')) + '<br><em>in Houston.</em>'
        main = hero(heading, detail['lead'], crumb, service)
        main += f'<section class="section porcelain service-explainer"><div class="service-reading"><h2>{escape(detail["heading"])}</h2><div>'
        main += ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in detail['overview']) + '</div></div>'
        main += '<div class="service-considerations">' + ''.join(f'<article><h3>{escape(heading)}</h3><p>{escape(copy)}</p></article>' for heading, copy in detail['considerations']) + '</div></section>'
        main += '<section class="section service-preparation"><h2>Bring the useful details.</h2><ul>' + ''.join(f'<li>{escape(item)}</li>' for item in detail['prepare']) + '</ul></section>'
        main += faq_section(detail['faqs'])
        main += '<section class="section porcelain service-related"><h2>Related services.</h2>' + service_links(detail['related'], services) + '</section>'
        main += '<section class="section porcelain service-location-link"><h2>Your Houston visit.</h2><p>' + escape(business['name'] + ' · ' + address_text(business['address'])) + '.</p><a class="text-link" href="/locations/houston/">Location and arrival details</a>'
        references = [entry for source_id in detail['sources'] for entry in SOURCES[source_id]]
        if references:
            main += '<details class="owner-resources"><summary>Manufacturer owner resources</summary><ul>' + ''.join(f'<li><a href="{escape(url, quote=True)}" rel="noopener" target="_blank">{escape(label)}</a></li>' for label, url in references) + '</ul></details>'
        main += '</section>'
        entities = [breadcrumb_schema([('Home', '/'), ('Services', '/services/'), (service['name'], path)], business), {
            '@type': 'Service', '@id': business['origin'] + path + '#service', 'name': service['name'],
            'serviceType': service['name'], 'description': detail['lead'], 'url': business['origin'] + path,
            'provider': {'@id': business['origin'] + '/#organization'}, 'areaServed': {'@type': 'City', 'name': 'Houston'},
        }]
        write_page(base, path, detail['title'] + ' | Houston Auto Pros', detail['description'], main,
                   {'data-page': 'service-detail', 'data-service': service['category'], 'data-service-name': service['name']}, entities, business)


def build_locations(base, locations, services, business):
    eligible = [location for location in locations if not location_errors(location, business)]
    for location in locations:
        stale = destination_for(location['candidatePath'])
        if location_errors(location, business) and stale.exists():
            old = BeautifulSoup(stale.read_text(encoding='utf-8'), 'html.parser')
            if old.select_one('meta[name="generator"][content="Houston Auto Pros SEO"]'):
                stale.unlink()
    for location in eligible:
        path = location['candidatePath']
        serving = next(entry for entry in business['physicalLocations'] if entry['id'] == location['servingLocationId'])
        crumb = breadcrumbs([('Home', '/'), ('Locations', '/locations/'), (location['name'], None)])
        main = hero(escape(location['h1']), location['intro'], crumb)
        main += '<section class="section porcelain location-arrival"><div><h2>The Pagewood Lane shop.</h2><address>' + escape(address_text(serving['address'])) + '</address>'
        main += f'<a class="button dark" href="{escape(directions(serving["address"]), quote=True)}" target="_blank" rel="noopener">Get directions</a></div><div><h3>Arrange your arrival.</h3><p>Send your preferred day and any drop-off questions with the appointment request. We’ll contact you to confirm availability and arrival details.</p><a class="text-link" href="#contact">Request a visit</a></div></section>'
        for section in location['sections']:
            main += f'<section class="section porcelain location-reading"><h2>{escape(section["heading"])}</h2><div>'
            main += ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in section['paragraphs'])
            if section.get('source'):
                main += f'<a class="text-link" href="{escape(section["source"], quote=True)}" target="_blank" rel="noopener">{escape(section["sourceLabel"])}</a>'
            main += '</div></section>'
        main += '<section class="section porcelain service-related"><h2>Services for your Houston visit.</h2>' + service_links(location['serviceSlugs'], services) + '<a class="text-link" href="/services/">Explore all services</a></section>'
        main += faq_section(location['faqs'])
        entities = [breadcrumb_schema([('Home', '/'), ('Locations', '/locations/'), (location['name'], path)], business)]
        write_page(base, path, location['title'], location['description'], main, {'data-page': 'location'}, entities, business)

    crumb = breadcrumbs([('Home', '/'), ('Locations & service area', None)])
    main = hero('European care.<br><em>Serving Houston.</em>', 'Plan your visit to Houston Auto Pros on Pagewood Lane. Explore the services, find the shop and request an appointment for your European vehicle.', crumb)
    main += '<section class="section porcelain location-hub"><h2>Our Houston location.</h2><ul>'
    for location in eligible:
        serving = next(entry for entry in business['physicalLocations'] if entry['id'] == location['servingLocationId'])
        main += f'<li><a href="{location["candidatePath"]}"><h3>{escape(location["name"])}</h3><p>{escape(address_text(serving["address"]))}</p><span>Directions, services and arrival details</span></a></li>'
    main += '</ul><p>We serve Houston-area drivers from the Pagewood Lane shop. Include your preferred day and any arrival questions in your request.</p></section>'
    main += '<section class="section porcelain service-related"><h2>Find the right service.</h2>' + service_links(['scheduled-maintenance', 'engine-diagnostics', 'brake-pads-rotors', 'cooling-system', 'air-conditioning', 'pre-purchase'], services) + '<a class="text-link" href="/services/">View the full service directory</a></section>'
    write_page(base, '/locations/', 'Houston Location & Service Area | Houston Auto Pros',
               'Find Houston Auto Pros at 8614 Pagewood Ln, Houston, TX. Browse European auto services, get directions and request your visit.',
               main, {'data-page': 'locations'}, [breadcrumb_schema([('Home', '/'), ('Locations', '/locations/')], business)], business)


def build_film(base, social, business):
    crumb = breadcrumbs([('Home', '/'), ('Porsche film', None)])
    main = f'''<section class="film-intro">{crumb}<h1>{escape(social['name'])}</h1>
      <p>Exceptional Cars Deserve Exceptional Care.</p>
      <video controls playsinline preload="none" width="{social['videoWidth']}" height="{social['videoHeight']}" poster="{social['image']}" aria-label="Porsche cabriolet film">
        <source src="{social['video']}" type="video/mp4">
        <a href="{social['video']}">Open the Porsche film</a>
      </video>
      <p class="film-credit">Illustrative stock footage by <a href="{social['creatorUrl']}" target="_blank" rel="noopener">{escape(social['creator'])}</a> · <a href="{social['source']}" target="_blank" rel="noopener">Pexels source</a>. This film does not depict our shop or customers.</p>
    </section>'''
    video = {'@type': 'VideoObject', '@id': business['origin'] + '/film/#video', 'name': social['name'],
             'description': social['description'], 'thumbnailUrl': business['origin'] + social['image'],
             'contentUrl': business['origin'] + social['video'], 'uploadDate': social['published'], 'duration': 'PT7.2S',
             'creator': {'@type': 'Organization', 'name': social['creator'], 'url': social['creatorUrl']},
             'license': social['license']}
    write_page(base, '/film/', 'Porsche Film | Houston Auto Pros', social['description'], main, {'data-page': 'film'},
               [breadcrumb_schema([('Home', '/'), ('Porsche film', '/film/')], business), video], business)


def apply_social(soup, path, social, business):
    def meta(key, value, kind='property'):
        tag = soup.select_one(f'meta[{kind}="{key}"]')
        if not tag:
            tag = soup.new_tag('meta', attrs={kind: key}); soup.head.append(tag)
        tag['content'] = str(value)
    image = business['origin'] + social['image']
    meta('og:url', business['origin'] + path)
    meta('og:site_name', business['name']); meta('og:locale', 'en_US')
    if not soup.select_one('meta[property="og:title"]'):
        meta('og:title', soup.title.get_text())
    if not soup.select_one('meta[property="og:description"]'):
        meta('og:description', soup.select_one('meta[name="description"]')['content'])
    for key, value in {'og:image': image, 'og:image:secure_url': image, 'og:image:type': 'image/jpeg',
                       'og:image:width': social['imageWidth'], 'og:image:height': social['imageHeight'],
                       'og:image:alt': social['imageAlt']}.items():
        meta(key, value)
    meta('twitter:image', image, 'name'); meta('twitter:image:alt', social['imageAlt'], 'name')
    meta('twitter:card', 'summary_large_image', 'name')
    if path == '/':
        meta('og:title', social['title']); meta('twitter:title', social['title'], 'name')
    meta('og:type', 'video.other' if path == social['watchPage'] else 'website')
    for tag in soup.select('meta[property^="og:video"]'):
        tag.decompose()
    if path in social['videoPages']:
        video = business['origin'] + social['video']
        for key, value in {'og:video': video, 'og:video:url': video, 'og:video:secure_url': video,
                           'og:video:type': 'video/mp4', 'og:video:width': social['videoWidth'],
                           'og:video:height': social['videoHeight'], 'og:video:image': image}.items():
            meta(key, value)


def update_links(services, business):
    """Upgrade old fragments to real pages while keeping the old hub anchor targets working."""
    for page in DIST.rglob('*.html'):
        soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        for link in soup.select('a[href]'):
            href = link['href']
            if href.startswith('/services/#') and href.partition('#')[2] in services:
                link['href'] = '/services/' + href.partition('#')[2] + '/'
        for link in soup.select('#site-nav > a[href="/#prepare"]'):
            link['href'] = '/locations/houston/'
            link.string = 'Visit us'
        visit = soup.select_one('footer .foot-top > div:last-child')
        if visit:
            if not visit.select_one('a[href="/locations/"]'):
                visit.append(BeautifulSoup('<a class="footer-booking-link" href="/locations/">Locations &amp; service area</a>', 'html.parser'))
            if not visit.select_one('a[href="/film/"]'):
                visit.append(BeautifulSoup('<a class="footer-booking-link" href="/film/">Porsche film</a>', 'html.parser'))
            address = visit.select_one('[data-biz="address"]')
            if not address:
                address = soup.new_tag('p', attrs={'data-biz': 'address'})
                visit.append(address)
            address.clear()
            address.append(business['address']['street'])
            address.append(soup.new_tag('br'))
            address.append(business['address']['city'] + ', ' + business['address']['region'] + ' ' + business['address'].get('postalCode', ''))
            for paragraph in list(visit.select('p')):
                if paragraph != address and paragraph.get_text(' ', strip=True) == 'Houston, Texas':
                    paragraph.decompose()
        page.write_text(str(soup).rstrip() + '\n', encoding='utf-8')

    home = DIST / 'index.html'
    soup = BeautifulSoup(home.read_text(encoding='utf-8'), 'html.parser')
    actions = soup.select_one('.hero-actions')
    if actions and not actions.select_one('a[href="/film/"]'):
        actions.append(BeautifulSoup('<a class="text-link hero-film-link" href="/film/">Watch the Porsche film</a>', 'html.parser'))
    home.write_text(str(soup).rstrip() + '\n', encoding='utf-8')

    credits = DIST / 'photography.html'
    soup = BeautifulSoup(credits.read_text(encoding='utf-8'), 'html.parser')
    if not soup.select_one('#film-credit'):
        social = read_json('social.json')
        soup.main.append(BeautifulSoup(f'<section id="film-credit"><h2>Film credits.</h2><p>Illustrative Porsche footage by <a href="{social["creatorUrl"]}">{social["creator"]}</a>. <a href="{social["source"]}">Original clip on Pexels</a> · <a href="{social["license"]}">Pexels license</a>. No manufacturer endorsement or shop/customer depiction is implied.</p><a href="/film/">Watch the Porsche film</a></section>', 'html.parser'))
    credits.write_text(str(soup).rstrip() + '\n', encoding='utf-8')


def update_hub(services, business):
    path = DIST / 'services/index.html'
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    for slug, service in services.items():
        body = soup.select_one(f'#{slug} .service-option-body')
        if not body:
            raise ValueError('Missing service hub entry: ' + slug)
        body.parent['data-service-url'] = f'/services/{slug}/'
        if not body.select_one('.service-detail-link'):
            body.insert(1, BeautifulSoup(f'<a class="text-link service-detail-link" href="/services/{slug}/">Explore {escape(service["name"].lower())}</a>', 'html.parser'))
    if not soup.select_one('script[data-page-schema]'):
        add_schema(soup, [breadcrumb_schema([('Home', '/'), ('Services', '/services/')], business)], business)
    path.write_text(str(soup).rstrip() + '\n', encoding='utf-8')


def crawl_controls(business, locations):
    production = business['launchState'] == 'production'
    errors = production_errors(business)
    if errors:
        raise ValueError('Search launch blocked: ' + '; '.join(errors))
    manifest = []
    detail_records = {entry['slug']: entry for entry in read_json('service-pages.json')}
    social = read_json('social.json')
    eligible_locations = {entry['candidatePath']: entry for entry in locations if not location_errors(entry, business)}
    for page in sorted(DIST.rglob('*.html')):
        relative = page.relative_to(DIST).as_posix()
        path = '/' + relative.removesuffix('index.html') if page.name == 'index.html' else '/' + relative
        soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        indexable = production and not path.startswith('/auto-repair-meta/') and path not in UTILITY and (path not in eligible_locations or eligible_locations[path]['indexingApproved'])
        robots = soup.select_one('meta[name="robots"]')
        if not robots:
            robots = soup.new_tag('meta', attrs={'name': 'robots'}); soup.head.append(robots)
        robots['content'] = 'index,follow' if indexable else 'noindex,nofollow'
        preset = soup.body.get('data-service') if soup.body else None
        if preset:
            for select in soup.select('#appointment-form select[name="service"]'):
                for option in select.select('option'):
                    option.attrs.pop('selected', None)
                    if option.get('value', option.get_text()) == preset:
                        option['selected'] = ''
        canonical = soup.select_one('link[rel="canonical"]')
        if not canonical:
            canonical = soup.new_tag('link', rel='canonical'); soup.head.append(canonical)
        canonical['href'] = business['origin'] + path
        description = soup.select_one('meta[name="description"]')
        if not description:
            description = soup.new_tag('meta', attrs={'name': 'description', 'content': 'Photography sources and image credits for the Houston Auto Pros website.'})
            soup.head.append(description)
        apply_social(soup, path, social, business)
        page.write_text(str(soup).rstrip() + '\n', encoding='utf-8')
        service_slug = path.split('/')[2] if path.startswith('/services/') and path != '/services/' else None
        service_record = detail_records.get(service_slug)
        location_record = eligible_locations.get(path)
        image = soup.select_one('main img')
        page_type = ('utility' if path in UTILITY else 'home' if path == '/' else 'service-hub' if path == '/services/' else
                     'make' if soup.body and soup.body.get('data-make') else soup.body.get('data-page', 'marketing'))
        manifest.append({'path': path, 'type': page_type,
                         'title': soup.title.get_text(), 'description': description['content'],
                         'h1': soup.h1.get_text(' ', strip=True) if soup.h1 else '', 'canonical': business['origin'] + path,
                         'indexState': 'index' if indexable else 'noindex',
                         'uniqueIntent': service_record['lead'] if service_record else location_record['intent'] if location_record else soup.title.get_text(),
                         'serviceRef': service_slug, 'locationRef': 'houston' if path not in UTILITY else None,
                         'evidenceIds': location_record['evidenceIds'] if location_record else ['owner-houston', 'owner-services'],
                         'contentOwner': business['name'], 'reviewed': REVIEWED,
                         'hero': image.get('src') if image else None, 'photoProvenance': 'photography-sources.json',
                         'socialImage': social['image'], 'socialVideo': social['video'] if path in social['videoPages'] else None})
    urls = ''.join(f'<url><loc>{escape(entry["canonical"])}</loc></url>' for entry in manifest if entry['indexState'] == 'index')
    (DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n', encoding='utf-8')
    (DIST / 'robots.txt').write_text('User-agent: *\n' + ('Allow: /\nSitemap: ' + business['origin'] + '/sitemap.xml\n' if production else 'Disallow: /\n'), encoding='utf-8')
    (DIST / '_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n' + ('' if production else '  X-Robots-Tag: noindex, nofollow\n'), encoding='utf-8')
    report = {'launchState': business['launchState'], 'pages': manifest, 'locations': [
        {'id': entry['id'], 'candidatePath': entry['candidatePath'], 'publicationErrors': location_errors(entry, business),
         'indexState': 'index' if production and entry['indexingApproved'] and not location_errors(entry, business) else 'noindex',
         'evidenceIds': entry['evidenceIds']} for entry in locations
    ]}
    (ROOT / 'content/page-manifest.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return manifest


def build():
    business, groups, details, locations = (read_json(name) for name in ('business.json', 'services.json', 'service-pages.json', 'locations.json'))
    errors = production_errors(business)
    if errors:
        raise ValueError('Search launch blocked: ' + '; '.join(errors))
    services = {slug: {'name': name, 'tag': tag, 'copy': copy, 'group': group, 'category': 'Maintenance & service' if slug == 'pre-trip' else category}
                for group, title, category, entries in groups for slug, name, tag, copy in entries}
    if {entry['slug'] for entry in details} != set(services) or len(details) != len(services):
        raise ValueError('Every service requires exactly one detailed content record')
    if any(related not in services for entry in details for related in entry['related']):
        raise ValueError('Unknown related service')
    (DIST / 'config.js').write_text('// Generated from content/business.json by scripts/build_seo.py. Edit the business record, then rebuild.\nwindow.HAP_CONFIG = ' + json.dumps(config_for(business), ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
    update_links(services, business)
    update_hub(services, business)
    base = BeautifulSoup((DIST / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    build_services(base, services, details, business)
    build_locations(base, locations, services, business)
    build_film(base, read_json('social.json'), business)
    from polish_booking import polish
    polish()
    manifest = crawl_controls(business, locations)
    print(f'Built {len(details)} service pages, {sum(not location_errors(entry, business) for entry in locations)} location page and a locations hub; {len(manifest)} total HTML pages. Search state: {business["launchState"]}.')


if __name__ == '__main__':
    build()
