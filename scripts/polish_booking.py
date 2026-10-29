"""Preserve the owner's clean-copy, broader-makes and appointment-form refinements."""
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import json, re

ROOT = Path(__file__).resolve().parents[1]
MAKES = json.loads((ROOT / 'content/makes.json').read_text(encoding='utf-8'))
FEATURED = {'Porsche': '/porsche/', 'BMW': '/bmw/', 'Mercedes-Benz': '/mercedes-benz/'}

def polish():
    for page in (ROOT / 'dist').rglob('*.html'):
        text = page.read_text(encoding='utf-8')
        soup = BeautifulSoup(text, 'html.parser')
        for heading in soup.select('.section-heading'):
            for paragraph in heading.find_all('p', recursive=False):
                paragraph.decompose()
        for filler in soup.select('.hero-note, .preparation-action > p, .service-directory-link > p, .dropdown-heading > p, .brand-strip > div > p, [data-form-note], .dialog-top > .eyebrow'):
            filler.decompose()
        for kicker in soup.select('main .eyebrow'):
            kicker.decompose()
        for index in soup.select('.prep-index, .steps article > span'):
            index.decompose()

        nav = soup.select_one('#site-nav')
        for review_link in soup.select('a[href="#reviews"], a[href="/#reviews"]'):
            review_link['data-requires'] = 'reviews'
        if nav:
            for link in list(nav.find_all('a', recursive=False)):
                if link.get('href') in FEATURED.values(): link.decompose()
            if not nav.select_one('.nav-makes'):
                menu = '<details class="nav-makes"><summary>Makes <svg viewBox="0 0 12 8" width="12" height="8" aria-hidden="true"><path d="m1 1 5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></summary><div class="makes-dropdown"><a class="makes-overview" href="/#makes">European makes we service</a><div class="makes-menu-grid">'
                for make in MAKES:
                    if make == 'Other European make': continue
                    if make in FEATURED:
                        menu += f'<a href="{FEATURED[make]}">{escape(make)}</a>'
                    else:
                        menu += f'<button type="button" data-book data-make="{escape(make, quote=True)}" data-source="makes-menu">{escape(make)}</button>'
                menu += '</div></div></details>'
                nav.select_one('.nav-services').insert_after(BeautifulSoup(menu, 'html.parser'))

        for form in soup.select('#request-form'):
            group = next((f for f in form.select('fieldset.inline') if f.select_one('input[name="make"]')), None)
            if group:
                group.replace_with(BeautifulSoup('<label class="field make-field">Vehicle make<select name="make" required autocomplete="off"><option value="" disabled selected>Select your brand</option>'+''.join(f'<option value="{escape(make, quote=True)}">{escape(make)}</option>' for make in MAKES)+'</select></label>', 'html.parser'))
            for field in form.select('input[name="name"], input[name="phone"]'):
                field['maxlength'] = '120' if field['name'] == 'name' else '40'
            for field in form.select('input[name="model"]'):
                field['placeholder'] = 'Model or trim'; field['maxlength'] = '120'
            for field in form.select('input[name="email"]'): field['maxlength'] = '254'
            for field in form.select('textarea[name="message"]'): field['maxlength'] = '3000'
            if not form.select_one('input[name="requestId"]'):
                form.append(BeautifulSoup('<input type="hidden" name="requestId"><input type="hidden" name="startedAt">', 'html.parser'))

        for button in soup.select('[data-book]'):
            if button.get('data-make'): continue
            span = button.find('span', recursive=False)
            label = 'Request this service' if button.get('data-service') else 'Request an appointment'
            if 'nav-cta' in button.get('class', []) or 'action-book' in button.get('class', []): label = 'Book a visit'
            if span: span.string = label
            else: button.string = label
        for paragraph in soup.select('.hero-lede'):
            if page.name == 'index.html' and page.parent == ROOT / 'dist':
                paragraph.string = 'Independent maintenance, diagnostics and repair for European and luxury vehicles in Houston.'
        for description in soup.select('meta[name="description"], meta[property="og:description"], meta[name="twitter:description"]'):
            description['content'] = description.get('content', '').replace('for Porsche, BMW and Mercedes-Benz owners', 'for European and luxury vehicle owners').replace('for Porsche, BMW and Mercedes-Benz in Houston', 'for European and luxury vehicles in Houston').replace('Plan a service online.', 'Request an appointment online.')
        if page.parent == ROOT / 'dist' and page.name == 'index.html':
            soup.title.string = 'European & Luxury Auto Repair in Houston | Houston Auto Pros'
            for description in soup.select('meta[name="description"], meta[property="og:description"]'):
                description['content'] = 'European and luxury auto repair in Houston. Maintenance, diagnostics, brakes and inspections for Porsche, BMW, Mercedes-Benz, Audi and more.'
            for title in soup.select('meta[property="og:title"], meta[name="twitter:title"]'):
                title['content'] = 'European & Luxury Auto Repair in Houston | Houston Auto Pros'
            makes = soup.select_one('#makes')
            if makes and not makes.select_one('.additional-makes'):
                extra = '<div class="additional-makes"><h2>More European makes.</h2><div class="additional-makes-list">'+''.join(f'<button type="button" data-book data-make="{escape(make, quote=True)}" data-source="makes">{escape(make)}</button>' for make in MAKES if make not in FEATURED and make != 'Other European make')+'</div></div>'
                makes.append(BeautifulSoup(extra, 'html.parser'))
        for paragraph in soup.select('.services-intro > div > p'):
            paragraph.string = 'Maintenance, diagnostics and repair for European and luxury vehicles in Houston.'
        for faq in soup.select('.faq-list details'):
            summary = faq.select_one('summary')
            if summary and 'Are you affiliated with' in summary.get_text():
                summary.contents[0].replace_with('Are you affiliated with a manufacturer?')
                faq.select_one('p').string = 'Houston Auto Pros is an independent European automotive shop with no manufacturer affiliation.'
        for footer in soup.select('.footer-bottom'):
            for node in list(footer.find_all(string=True)):
                if 'Not affiliated with Porsche AG, BMW AG or Mercedes-Benz Group AG' in node:
                    node.replace_with(str(node).replace('Not affiliated with Porsche AG, BMW AG or Mercedes-Benz Group AG', 'No manufacturer affiliation'))
        for asset in soup.select('script[src], link[href]'):
            key = 'src' if asset.name == 'script' else 'href'
            if re.match(r'^/(app\.js|config\.js|style\.css)\?v=', asset.get(key, '')):
                asset[key] = re.sub(r'\?v=\d+', '?v=5', asset[key])
        if soup.head and not soup.select_one('meta[property="og:locale"]'):
            meta = soup.new_tag('meta', property='og:locale', content='en_US'); soup.head.append(meta)
        for name, source in [('twitter:title', 'og:title'), ('twitter:description', 'og:description'), ('twitter:image', 'og:image'), ('twitter:image:alt', 'og:image:alt')]:
            existing = soup.select_one(f'meta[name="{name}"]')
            original = soup.select_one(f'meta[property="{source}"]')
            if original:
                if existing: existing['content'] = original['content']
                else: soup.head.append(soup.new_tag('meta', attrs={'name': name, 'content': original['content']}))
        page.write_text(str(soup).rstrip()+'\n', encoding='utf-8')

if __name__ == '__main__': polish()
