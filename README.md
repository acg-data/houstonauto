# Houston Auto Pros

Website for an independent Porsche, BMW and Mercedes-Benz specialist in Houston. Plain HTML, CSS and JavaScript. No framework or build step; npm is used only for Cloudflare deployment tooling.

## Run locally

```bash
python -m http.server 8080 --directory dist
```

On Windows, `py -m http.server 8080 --directory dist` also works. Open http://localhost:8080. Use a web server rather than opening the files directly, because paths start at the site root.

Publish the contents of `dist/` to any static host (Netlify, Cloudflare Pages, Vercel, GitHub Pages, S3…). `404.html` is picked up automatically by most of them.

## Pages

The shared Services dropdown opens on click/tap and supports keyboard navigation and Escape. On mobile it sits in a full-height, scrollable menu. `/services/` contains 18 service options with direct links that expand the matching description and prefill the service planner. `scripts/expand_services.py` regenerates the service page and shared navigation; its catalogue is also exported to `content/services.json`. Confirm the service catalogue with the shop before public launch.

Brand identification assets are self-hosted in `dist/assets/brands/`, with sources recorded in `brand-sources.json`. The manufacturer marks identify vehicles serviced and do not indicate manufacturer affiliation.

The shop does not yet have a Google Business Profile. The staging site displays an honest “reviews are on the way” state through `showReviewsPreview: true`. No quotes, stars or review counts are invented. Add verified reviews and the profile URL to `config.js` when available; the review cards then replace the empty state. The empty state is suppressed automatically in production.

| Page | Purpose |
| --- | --- |
| `dist/index.html` | Homepage: cinematic hero, photographed make cards, services, approach, FAQ and visit guide |
| `dist/porsche/`, `dist/bmw/`, `dist/mercedes-benz/` | Search and ad landing pages, one per make. Every booking button pre-selects that make |
| `dist/brand.html` | Original brand guidelines (palette, stationery); linked from photography credits; noindex |
| `dist/photography.html` | Image sources, license and clear illustrative-photo disclosure |
| `dist/404.html` | Not-found page with routes back to booking and the make pages |

## Before launch

The Cloudflare version is a public, polished staging site. It opens without ChatGPT sign-in and stays noindex until the business setup is complete. `showPlaceholders` is false: missing reviews and contact details are hidden. The planner creates a downloadable service brief and clearly says nothing is sent. No customer contact endpoint has been configured.

`launchState` is `staging`. All pages are noindex/nofollow, robots disallows crawling, the sitemap is empty and AutoRepair schema is suppressed. For a public launch, complete the verified business record below, connect booking, set `launchState: 'production'`, restore appropriate index/follow tags and robots rules, and populate the sitemap with the approved production URLs. Keep brand, photography and 404 pages noindex.

1. **Business details** — fill in `dist/config.js`: phone, text number (only if it can receive texts), email, address, hours, Google rating and review link. That one file feeds the header, the call/text buttons, the mobile action bar, the visit section, the footer, the "open today" status and the local-business structured data.
2. **Request form** — set `requestEndpoint` (see below). Until then the form honestly says nothing was sent and offers text, email or download.
3. **Domain** — replace the placeholder domain everywhere:
   ```bash
   grep -rl "houstonautopros.example" dist | xargs sed -i 's#https://houstonautopros.example#https://www.YOUR-DOMAIN.com#g'
   ```
   (On macOS use `sed -i ''`.) This covers canonical tags, social preview tags, `robots.txt`, `sitemap.xml` and `config.js`.
4. **Photos** — add real photos (below), then delete any slot you won't fill.
5. **Reviews** — paste real Google reviews into `config.js → reviews`, word for word. Never write or edit reviews.
6. **Confirm the copy** — the service lists, model lists and "what owners ask about" topics on the make pages describe common work for these cars. Remove anything the shop doesn't do. Check the FAQ answers match how the shop actually works.
7. **Analytics** — add `ga4Id`, `googleAdsConversion` and/or `metaPixelId` in `config.js`.
8. **Switch off placeholders** — set `showPlaceholders: false`. Anything still missing is then hidden instead of outlined.
9. Submit `https://YOUR-DOMAIN/sitemap.xml` in Google Search Console, and make sure the Google Business Profile uses exactly the same name, address and phone as `config.js`.

## Photography

The make cards and landing-page heroes use locally stored Unsplash vehicle photography. `photography-sources.json` records each source, license, image dimensions and output files. `dist/photography.html` credits the images and explains they do not depict this shop, its staff or customer cars. The original cinematic homepage image is retained.

`dist/assets/photos/{porsche,bmw,mercedes-benz}-{640,1280,1920}.webp` supplies responsive images. `scripts/prepare_photography.py` recreates them (Python, requests, Pillow). The largest new image is under 230 KB. There are no remote image dependencies at runtime.

The empty workshop gallery has been removed. Do not restore it with stock photographs presented as the shop. Add approved photos of the actual premises, team and work when available. Contact sections reveal themselves when verified address, phone or email fields are filled in. Reviews render only from configured real reviews.

## Connecting the request form

`requestEndpoint` can be any HTTPS URL that accepts a `multipart/form-data` POST and returns a 2xx status. The site shows "Request sent" only after a 2xx response. On any error it says the request was **not** sent and offers text, email and call instead.

- **Formspree / Basin / Getform** — create a form and paste its endpoint URL. Fields arrive by email; `_subject` is set to "Appointment request — {vehicle}".
- **Supabase Edge Function** (or any small backend) — store the row, then notify the shop, for example with an email from Resend or a text message.
- **Shop software scheduler** — if the shop's management software has online booking, set `schedulerUrl` and every "Request a visit" button opens it instead.

Fields sent: `service`, `make`, `model`, `year`, `mileage`, `message`, `name`, `phone`, `email`, `contact`, `date`, `time`, `vehicle`, `summary`, `page`, plus attribution for ads: `landing_page`, `referrer`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `gclid`, `gbraid`, `wbraid`, `fbclid`, `msclkid` (when present). A hidden spam-trap field is never sent.

## Conversion tracking

Events are pushed to `dataLayer` (so Google Tag Manager works too) and to GA4, Google Ads and Meta when configured:

| Event | When |
| --- | --- |
| `book_open` | The request form opens (`source` says which button) |
| `book_step` | A step is completed |
| `generate_lead` | A request is sent successfully. Also fires the Google Ads conversion and Meta `Lead` |
| `request_prepared` · `request_fallback` | No endpoint or a failed send; the visitor chose text, email or download |
| `call_click` · `text_click` · `email_click` | Tap-to-call, text or email links. Meta `Contact` |
| `directions_click` · `reviews_click` | Maps and review links |

## SEO

- Keyword-led titles, meta descriptions, canonical URLs and social preview tags on every page, with a 1200×630 preview image at `assets/og-image.jpg`.
- `AutoRepair` local-business structured data, built from `config.js`, with only the fields you've filled in. The make pages also carry breadcrumb data.
- `robots.txt`, `sitemap.xml`, favicons, self-hosted Manrope font, responsive WebP hero images (the mobile hero went from 280 KB to 28 KB).

## Palette

Graphite #17191B · Gunmetal #343A40 · Satin steel #A6ADB4 · Platinum #E4E3DF · Warm porcelain #F3F1EB

`design-reference/` holds the approved brand direction and the expanded concept board. They are visual references, not screenshots of the coded site.

## Cloudflare hosting

The current site is hosted with Cloudflare Workers Static Assets at https://houston-auto-pros.justin-b75.workers.dev. The account has reached its Cloudflare Pages project limit, so an assets-only Worker serves the same static website. There is no application Worker script, backend, database or new booking integration.

```sh
npm ci
npm run deploy:check
npm run deploy
```

`wrangler.jsonc` selects the account, site name, static output and normal HTML/404 routing. The original `.openai/hosting.json` records the earlier private Sites preview; it is retained for reference and is not the current deployment target.

All decorative Unicode arrows and stars have been removed from the interface. Dropdowns, disclosure controls and close buttons use consistent SVG line icons. `scripts/refine_finish.py` applies the same finish whenever the service page is regenerated.

The public staging site keeps robots meta, robots.txt and `X-Robots-Tag` set to noindex. Remove the staging crawl controls only after business details, services, booking and the final domain are approved.
