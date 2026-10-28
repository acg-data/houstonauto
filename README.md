# Houston Auto Pros

Website for an independent Porsche, BMW and Mercedes-Benz specialist in Houston. Plain HTML, CSS and JavaScript — no framework, no build step, no npm.

## Run locally

```bash
python -m http.server 8080 --directory dist
```

On Windows, `py -m http.server 8080 --directory dist` also works. Open http://localhost:8080. Use a web server rather than opening the files directly, because paths start at the site root.

Publish the contents of `dist/` to any static host (Netlify, Cloudflare Pages, Vercel, GitHub Pages, S3…). `404.html` is picked up automatically by most of them.

## Pages

| Page | Purpose |
| --- | --- |
| `dist/index.html` | Homepage: hero, make cards, services, approach, reviews, workshop gallery, FAQ, visit details |
| `dist/porsche/`, `dist/bmw/`, `dist/mercedes-benz/` | Search and ad landing pages, one per make. Every booking button pre-selects that make |
| `dist/brand.html` | Brand guidelines (palette, stationery). Linked from the footer only; set to `noindex` |
| `dist/404.html` | Not-found page with routes back to booking and the make pages |

## Before launch

Everything below is a placeholder until verified details are added. While `showPlaceholders` is `true` in `config.js`, every missing detail and empty photo slot is outlined on the page with a note saying what goes there.

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

## Photos

Drop a photo into `dist/assets/photos/` with the file name below and it appears. No code changes are needed. Use JPGs about 1600–2400px on the long edge, compressed to under ~400 KB. Real photos of the real shop beat stock or AI images every time.

| File | Where it shows | What to shoot |
| --- | --- | --- |
| `make-porsche.jpg` · `make-bmw.jpg` · `make-mercedes-benz.jpg` | Homepage make cards (4:3) | A customer car of each make in the shop |
| `porsche-hero.jpg` · `bmw-hero.jpg` · `mercedes-benz-hero.jpg` | Full-screen hero on each make page | Your best photo of that make: wide, dark background, car on the right half. Porsche falls back to the current hero image until replaced |
| `statement.jpg` | "Not just how it runs" band (darkened) | Moody detail: reflections across bodywork. Falls back to the hero image |
| `conversation.jpg` | Under "Our approach" (very wide) | A technician walking an owner through findings beside the car |
| `workshop-bay.jpg` | Gallery, large tile | Wide shot of a clean bay with a car on the lift |
| `technician.jpg` · `diagnostics.jpg` · `detail.jpg` · `handover.jpg` | Gallery tiles | Hands and tools at work · a scan tool connected · a close detail (brakes, engine bay, wheel) · a key handover at the counter |
| `shop-exterior.jpg` | Visit section | The front of the shop with the sign visible, so people recognize it when they arrive |

To replace the homepage hero, overwrite `dist/assets/atelier-hero.jpg` and the three `atelier-hero-*.webp` sizes (768, 1280 and 1536px wide). Or delete the `<source>` line in the hero's `<picture>` so only the JPG is used.

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
