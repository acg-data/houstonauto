"""Build the service catalogue and keep shared navigation consistent across static pages."""
from pathlib import Path
from html import escape
import json, re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
GROUPS = [
 ('maintenance', 'Maintenance', 'Maintenance & service', [
  ('oil-filter-service','Oil & filter service','Routine care for the miles ahead.','Plan an oil and filter change around your vehicle, mileage and service history.'),
  ('scheduled-maintenance','Scheduled maintenance','A plan around your car.','Review the maintenance your car is due for, with its model, age and mileage in mind.'),
  ('fluid-service','Fluid checks & service','Small details. Important protection.','Discuss fluid condition, service intervals and any concerns with levels or leaks.'),
  ('vehicle-inspection','Vehicle condition checks','Know what needs attention.','Bring together a picture of visible wear, maintenance needs and the concerns you have noticed.'),
 ]),
 ('diagnostics', 'Diagnostics & repair', 'Diagnostics & repair', [
  ('check-engine-light','Check-engine lights','Start with an explanation.','Tell us which warning appeared, when it started and whether the car feels different. Discuss the next diagnostic steps.'),
  ('engine-diagnostics','Engine diagnostics','Understand what has changed.','Discuss rough running, unusual sounds, starting problems or a change in performance before planning repairs.'),
  ('electrical-diagnostics','Electrical diagnostics','Find a clearer way forward.','Describe intermittent electrical concerns, warning messages or accessories that are not behaving as expected.'),
  ('battery-charging','Battery & charging checks','For a more confident start.','Plan a check for slow cranking, a flat battery or a charging-system warning.'),
  ('leak-diagnosis','Oil & fluid leak diagnosis','Trace the source.','Discuss new drips, fluid loss or a burning smell, with inspection and diagnosis before a repair recommendation.'),
 ]),
 ('brakes-chassis', 'Brakes, suspension & steering', 'Brakes & suspension', [
  ('brake-pads-rotors','Brake pads & rotors','Look after the way it stops.','Discuss brake wear, noise, vibration or a change in pedal feel and plan an inspection.'),
  ('brake-fluid','Brake fluid service','Care beyond the visible parts.','Review brake-fluid service needs alongside the age, history and condition of your vehicle.'),
  ('suspension','Suspension checks & repair','Keep the connection to the road.','Describe clunks, changes in ride quality or uneven tire wear so the next checks can be planned.'),
  ('steering','Steering concerns','A more considered diagnosis.','Discuss changes in steering feel, vibration, pulling or unusual sounds before deciding on repairs.'),
 ]),
 ('cooling-climate', 'Cooling & air conditioning', 'Cooling & air conditioning', [
  ('cooling-system','Cooling-system checks','Keep temperature in perspective.','Plan checks for coolant loss, leaks or changes in operating temperature.'),
  ('overheating','Overheating diagnosis','Get to the cause.','Discuss temperature warnings and when they occur so the cooling system can be assessed.'),
  ('air-conditioning','Air-conditioning diagnosis','Comfort for Houston driving.','Describe weak cooling, unusual noises or inconsistent airflow and discuss the right checks.'),
 ]),
 ('inspections', 'Inspections', 'Pre-purchase inspection', [
  ('pre-purchase','Pre-purchase inspections','Before the car becomes yours.','Discuss an inspection of a car you are considering, including visible condition, service history and questions for the seller.'),
  ('pre-trip','Pre-trip condition checks','A little preparation for the road.','Review maintenance needs and the concerns you want checked before a longer drive.'),
 ]),
]

def logo(name, css=''):
 ext='webp' if name=='mercedes-benz' else 'svg'
 return f'<img class="brand-logo {css}" src="/assets/brands/{name}.{ext}" alt="" width="96" height="96" loading="lazy">'

brands='''<section class="brand-strip" aria-labelledby="brand-strip-title"><div><h2 id="brand-strip-title">The makes we service.</h2><p>Independent European care. No manufacturer affiliation.</p></div><div class="brand-links">'''+''.join(f'<a href="/{name}/">{logo(name)}<span>{label}</span></a>' for name,label in [('porsche','Porsche'),('bmw','BMW'),('mercedes-benz','Mercedes-Benz')])+'''</div></section>'''

dropdown='''<details class="nav-services"><summary>Services <svg viewBox="0 0 12 8" width="12" height="8" aria-hidden="true"><path d="m1 1 5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></summary><div class="services-dropdown"><div class="dropdown-heading"><p>Care, down to the detail.</p><a href="/services/">Explore all 18 services <span aria-hidden="true">↗</span></a></div><div class="dropdown-groups">'''
for slug,title,category,services in GROUPS:
 dropdown+=f'<div><h2><a href="/services/#{slug}">{escape(title)}</a></h2>'
 for key,name,tag,copy in services:
  dropdown+=f'<a href="/services/#{key}">{escape(name)}</a>'
 dropdown+='</div>'
dropdown+='''</div></div></details>'''
nav='''<nav class="nav" id="site-nav" aria-label="Main">'''+dropdown+'''<a href="/porsche/">Porsche</a><a href="/bmw/">BMW</a><a href="/mercedes-benz/">Mercedes-Benz</a><a href="/#reviews">Reviews</a><a href="/#prepare">Visit guide</a><div class="nav-mobile"><button class="button platinum" type="button" data-book data-source="menu"><span>Plan a service</span><span aria-hidden="true">↗</span></button><a class="button outline" href="/#visit" data-action="call" data-requires="phone" data-source="menu">Call the shop ↗</a></div></nav>'''

homepath=DIST/'index.html'
home=homepath.read_text(encoding='utf-8')
if 'class="brand-strip"' not in home:
 home=home.replace('    <section class="makes', '    '+brands+'\n\n    <section class="makes',1)
if 'class="service-directory-link' not in home:
 home=home.replace('    <section class="statement"', '    <div class="service-directory-link porcelain"><a class="button outline-dark" href="/services/">Explore all 18 services <span aria-hidden="true">↗</span></a><p>Maintenance, diagnostics, brakes, cooling and inspections.</p></div>\n\n    <section class="statement"',1)
if 'data-reviews-empty' not in home:
 home=home.replace('<div class="reviews-grid" data-reviews></div>', '<div class="reviews-grid" data-reviews></div><div class="reviews-pending" data-reviews-empty hidden><div><h3>Customer reviews are on the way.</h3><p>This space is reserved for real customer feedback. Reviews will appear here as they become available.</p></div><a class="text-link" href="/services/">Explore our services <span aria-hidden="true">↗</span></a></div>')
homepath.write_text(home,encoding='utf-8')

main='''<main id="main"><section class="services-intro"><div><ol class="breadcrumb" aria-label="Breadcrumb"><li><a href="/">Home</a></li><li aria-current="page">Services</li></ol><h1>Care for every part<br>of the drive.</h1><p>Explore maintenance, diagnostics and repair for your Porsche, BMW or Mercedes-Benz. Start with what your car needs; plan the details from there.</p><a class="button platinum" href="#service-directory">Explore services <span aria-hidden="true">↓</span></a></div><figure><img src="/assets/atelier-hero-1280.webp" alt="Silver sports coupe in a dark automotive setting" width="1280" height="853" fetchpriority="high"></figure></section>'''+brands.replace('brand-strip-title','services-brand-title')+'''<section class="section porcelain services-directory" id="service-directory"><div class="section-heading"><h2>What can we<br>help with?</h2><p>18 ways to start a service conversation. Select a service to see more, then add it to your visit plan.</p></div><nav class="service-jump-links" aria-label="Service categories">'''
main+=''.join(f'<a href="#{slug}">{escape(title)}</a>' for slug,title,_,_ in GROUPS)+'</nav>'
for slug,title,category,services in GROUPS:
 main+=f'<section class="service-group" id="{slug}" aria-labelledby="{slug}-title"><h2 id="{slug}-title">{escape(title)}</h2><div class="service-options">'
 for key,name,tag,copy in services:
  request_category='Maintenance & service' if key=='pre-trip' else category
  main+=f'<details class="service-option" id="{key}"><summary><span><strong>{escape(name)}</strong><small>{escape(tag)}</small></span><svg viewBox="0 0 12 8" width="16" height="10" aria-hidden="true"><path d="m1 1 5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg></summary><div class="service-option-body"><p>{escape(copy)}</p><button type="button" class="text-link" data-book data-source="service-directory" data-service="{escape(request_category,quote=True)}" data-note="{escape(name,quote=True)}">Plan this service <span aria-hidden="true">↗</span></button></div></details>'
 main+='</div></section>'
main+='''</section><section class="contact"><div class="contact-grid"><h2>Not sure<br><em>where to start?</em></h2><div><p>Describe what you’re noticing.<br>The conversation starts there.</p><button class="button platinum" type="button" data-book data-source="services-closing">Plan your visit <span aria-hidden="true">↗</span></button></div></div></section></main>'''
head=home.split('<body>')[0]
head=re.sub(r'<title>.*?</title>','<title>European Auto Services in Houston | Houston Auto Pros</title>',head)
head=re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*',r'\g<1>Explore 18 maintenance, diagnostic and repair services for Porsche, BMW and Mercedes-Benz in Houston.',head)
head=head.replace('href="https://houstonautopros.com/"','href="https://houstonautopros.com/services/"')
head=head.replace('property="og:url" content="https://houstonautopros.com/"','property="og:url" content="https://houstonautopros.com/services/"')
head=head.replace('Houston Auto Pros — Precision you can feel.','European Auto Services | Houston Auto Pros')
head=re.sub(r'<link rel="preload" as="image"[^>]*>','',head)
head=re.sub(r'<script type="application/ld\+json">.*?</script>','',head)
header=home.split('<body>')[1].split('  <main')[0]
tail=home.split('  </main>',1)[1]
(DIST/'services').mkdir(exist_ok=True)
(DIST/'services/index.html').write_text(head+'<body data-page="services">'+header+main+tail,encoding='utf-8')

for page in DIST.rglob('*.html'):
 text=page.read_text(encoding='utf-8')
 text=re.sub(r'<nav class="nav" id="site-nav".*?</nav>',nav,text,flags=re.S)
 text=text.replace('/style.css?v=2','/style.css?v=3').replace('/app.js?v=2','/app.js?v=3').replace('/config.js?v=2','/config.js?v=3')
 if page.parent.name in ('porsche','bmw','mercedes-benz') and 'hero-brand-logo' not in text:
  text=text.replace('<p class="eyebrow light">',logo(page.parent.name,'hero-brand-logo')+'<p class="eyebrow light">',1)
 text=text.replace('<li><a href="/#services">','<li><a href="/services/">')
 page.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n',encoding='utf-8')

(ROOT/'content').mkdir(exist_ok=True)
(ROOT/'content/services.json').write_text(json.dumps(GROUPS,indent=2,ensure_ascii=False),encoding='utf-8')
print('18 services, shared dropdown navigation, brand assets and review section prepared.')
from refine_finish import refine
refine()
