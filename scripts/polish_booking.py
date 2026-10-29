"""Preserve the owner's clean-copy, broader-makes and appointment-form refinements."""
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import json, re

ROOT = Path(__file__).resolve().parents[1]
MAKES = json.loads((ROOT / 'content/makes.json').read_text(encoding='utf-8'))
FEATURED = {'Porsche': '/porsche/', 'BMW': '/bmw/', 'Mercedes-Benz': '/mercedes-benz/'}
GALLERY_MAKES = list(FEATURED) + [make for make in MAKES if make not in FEATURED and make != 'Other European make']

def mark(make, css_class):
    slug = re.sub(r'[^a-z0-9]+', '-', make.lower())
    return f'<img class="{css_class}" src="/assets/brands/{slug}-mark.svg" alt="" width="96" height="96" loading="lazy" decoding="async">'

def make_control(make, content, source):
    if make in FEATURED:
        return f'<a href="{FEATURED[make]}">{content}</a>'
    return f'<button type="button" data-book data-make="{escape(make, quote=True)}" data-source="{source}">{content}</button>'

def closing_form():
    makes = ''.join(f'<option value="{escape(make, quote=True)}">{escape(make)}</option>' for make in MAKES)
    services = ['Maintenance & service', 'Diagnostics & repair', 'Brakes & suspension', 'Cooling & air conditioning', 'Pre-purchase inspection', 'Something else']
    options = ''.join(f'<option>{escape(service)}</option>' for service in services)
    return f'''<div class="contact-grid appointment-grid">
      <div class="appointment-intro">
        <h2 id="appointment-title">For the road<br><em>ahead.</em></h2>
        <p>Tell us about your car. We’ll be in touch to confirm your visit.</p>
        <a class="text-link" href="/#makes">Explore the European makes we service</a>
        <small>Houston, Texas</small>
      </div>
      <form id="appointment-form" class="appointment-form" method="post" aria-labelledby="inline-booking-title" novalidate>
        <fieldset class="appointment-fields">
          <legend id="inline-booking-title">Request an appointment</legend>
          <p class="form-guidance">Fields marked * are required.</p>
          <div class="form-row">
            <label class="field">Your name *<input name="name" autocomplete="name" required minlength="2" maxlength="120"></label>
            <label class="field">Phone number *<input name="phone" type="tel" autocomplete="tel" required maxlength="40" title="Enter a phone number with 7 to 15 digits."></label>
          </div>
          <div class="form-row">
            <label class="field">Vehicle make *<select name="make" required><option value="" disabled selected>Select your brand</option>{makes}</select></label>
            <label class="field">Model *<input name="model" required maxlength="120" placeholder="Model or trim"></label>
          </div>
          <label class="field">Service *<select name="service" required><option value="" disabled selected>What can we help with?</option>{options}</select></label>
          <div class="form-row">
            <label class="field">Email <span class="optional" data-inline-email-optional>(optional)</span><input name="email" type="email" autocomplete="email" maxlength="254"></label>
            <label class="field">Preferred contact<select name="contact"><option>Call</option><option>Text</option><option>Email</option></select></label>
          </div>
          <label class="field">How can we help? <span class="optional">(optional)</span><textarea name="message" maxlength="3000" rows="3" placeholder="Describe the issue or suggest a day for your visit."></textarea></label>
          <input class="hp" name="company" tabindex="-1" autocomplete="off" aria-hidden="true">
          <input type="hidden" name="requestId"><input type="hidden" name="startedAt">
          <button class="button dark appointment-submit" type="submit" disabled>Request an appointment</button>
          <p class="form-guidance confirmation-note">We’ll contact you to confirm availability.</p>
        </fieldset>
        <div class="appointment-result" role="status" hidden></div>
        <noscript><p>Please enable JavaScript to send an appointment request.</p></noscript>
      </form>
    </div>'''

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

            menu_grid = nav.select_one('.makes-menu-grid')
            if menu_grid:
                menu_grid.clear()
                for make in MAKES:
                    if make == 'Other European make': continue
                    content = mark(make, 'make-menu-logo') + f'<span>{escape(make)}</span>'
                    menu_grid.append(BeautifulSoup(make_control(make, content, 'makes-menu'), 'html.parser'))

        for strip in soup.select('.brand-strip'):
            strip['class'] = list(dict.fromkeys(strip.get('class', []) + ['brand-gallery']))
            links = strip.select_one('.brand-links')
            if links:
                gallery = '<ul class="brand-links">' + ''.join('<li>' + make_control(make, mark(make, 'brand-logo') + f'<span>{escape(make)}</span>', 'brand-gallery') + '</li>' for make in GALLERY_MAKES) + '</ul>'
                links.replace_with(BeautifulSoup(gallery, 'html.parser'))
        for duplicate in soup.select('.additional-makes'):
            duplicate.decompose()

        contact = soup.select_one('section.contact')
        if contact:
            contact.clear()
            contact['id'] = 'contact'
            contact['aria-labelledby'] = 'appointment-title'
            contact.append(BeautifulSoup(closing_form(), 'html.parser'))
            visit_links = soup.select_one('footer .foot-top > div:last-child')
            if visit_links and not visit_links.select_one('a[href="#contact"]'):
                visit_links.select_one('h2').insert_after(BeautifulSoup('<a class="footer-booking-link" href="#contact">Request an appointment</a>', 'html.parser'))
            for link in soup.select('footer a[href="#contact"]'):
                link['class'] = ['footer-booking-link']
        for gallery_title in soup.select('.brand-gallery h2'):
            gallery_title.string = 'European makes we service.'

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
            gallery = soup.select_one('.brand-gallery')
            if gallery: gallery['id'] = 'makes'
            featured_makes = soup.select_one('section.makes')
            if featured_makes:
                featured_makes['id'] = 'featured-makes'
                featured_makes['aria-label'] = 'Featured makes'
            hero_heading = soup.select_one('.hero h1')
            if hero_heading:
                hero_heading.clear()
                hero_heading.append('Exceptional Cars ')
                hero_heading.append(soup.new_tag('br'))
                hero_heading.append('Deserve Exceptional Care.')
            soup.title.string = 'European & Luxury Auto Repair in Houston | Houston Auto Pros'
            for description in soup.select('meta[name="description"], meta[property="og:description"]'):
                description['content'] = 'European and luxury auto repair in Houston. Maintenance, diagnostics, brakes and inspections for Porsche, BMW, Mercedes-Benz, Audi and more.'
            for title in soup.select('meta[property="og:title"], meta[name="twitter:title"]'):
                title['content'] = 'European & Luxury Auto Repair in Houston | Houston Auto Pros'
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
                asset[key] = re.sub(r'\?v=\d+', '?v=9', asset[key])
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
