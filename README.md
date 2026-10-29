# Houston Auto Pros

Independent European and luxury auto service website. The frontend is plain HTML, CSS and JavaScript; one Cloudflare Worker serves static assets and handles appointment email requests.

## Develop and validate

```sh
npm ci
npm run check
npm test
npm run deploy:check
```

For frontend-only work, `python -m http.server 8080 --directory dist`. This does not run the appointment API. The API accepts production origins only; use the automated backend tests for local verification. Do not send real customer details during QA.

`python scripts/expand_services.py` regenerates the 18-service catalogue and shared navigation. It invokes `scripts/refine_finish.py` and `scripts/polish_booking.py` to preserve the owner's refinements: automatic desktop dropdowns, broader European makes, native brand select, restrained icons, fewer side captions and no preview-mode notice. `content/makes.json` supplies the make list to both frontend generation and backend validation.

## Appointment requests

Requests go to **justin@aryocg.com**, as requested by the owner. `dist/config.js` uses `/api/appointments`. The form confirms success only after the backend returns JSON `{ ok: true }`, following email-provider acceptance. A request does not reserve a time; the shop must contact the visitor to confirm availability. Provider acceptance does not prove inbox placement.

The Worker uses the account's existing verified sending domain, `alerts.homeservicesecretshopper.com`, with display name Houston Auto Pros appointments. The binding is restricted to Justin's verified recipient address. Visitor email becomes Reply-To when supplied. Change to a dedicated business sender after its domain is verified.

The endpoint validates service, vehicle, contact details and requested date, limits body size, checks origin, uses a honeypot and form-age check, and applies a five-request-per-minute IP limit. Cloudflare's rate limiter is approximate and local to each data center. D1 stores only request IDs, payload hashes, delivery status, provider message IDs and timestamps, not customer contact fields. Atomic receipt insertion prevents concurrent duplicate sends. Ambiguous delivery failures are not retried automatically. Receipt metadata older than 30 days is removed after successful sends.

The dedicated `houston-auto-pros-booking` database is configured in `wrangler.jsonc`; apply `worker/schema.sql` when setting up a new account. No pre-existing application database or lead platform is modified. The fallback offers an email draft when delivery cannot be confirmed.

## Content and navigation

- Services: `/services/` with 18 linked descriptions, direct anchors and preselected appointment categories.
- Makes: Porsche, BMW and Mercedes-Benz have detailed landing pages. The wider European make list opens the appointment form with the selected make. No thin placeholder landing pages are generated.
- Services and Makes open on hover for desktop fine pointers and on keyboard focus; click/tap also works. Mobile navigation scrolls independently.
- Booking uses a native make dropdown, single-column phone fields, 16px text inputs and sticky actions with safe-area padding.
- Reviews and their navigation link remain hidden until real feedback or a real profile URL is configured. The shop has no Google Business Profile yet. Never invent quotes, ratings or counts.
- Missing phone, street address and hours remain hidden. The receiving address for appointments is separate from the public shop email.

## Photography and identity

Graphite, gunmetal, satin steel, platinum and warm porcelain; self-hosted Manrope. No emoji interface controls. Brand marks identify vehicles serviced and imply no manufacturer affiliation.

Vehicle photography is stored locally in responsive WebP sizes. `photography-sources.json` and `/photography.html` record image sources and explain that illustrative photos do not depict the actual shop. `brand-sources.json` records manufacturer-mark sources. Add approved premises, team and work photos when available. Keep image dimensions, alt text and responsive sources.

## Mobile and SEO

See `docs/mobile-seo-review.md` for the review and launch priorities. `python scripts/inspect_metadata.py` prints the static metadata baseline. The main marketing pages have unique titles/descriptions, self-referencing canonical URLs, one H1, Open Graph and Twitter cards, image dimensions and mobile viewport tags. The same content and metadata are served to desktop and phone screens. Brand pages include breadcrumb structured data; homepage includes WebSite data.

**Search launch is still pending.** The current workers.dev version deliberately has robots noindex/nofollow, an `X-Robots-Tag` header, blocked crawling and an empty sitemap. `launchState: 'staging'` suppresses AutoRepair schema. Changing config alone does not update static robots/meta/header/sitemap rules.

When the production domain is connected:

1. Choose `https://houstonautopros.com` as the primary origin and redirect secondary domains to relevant pages. Do not publish identical indexable copies across all seven domains.
2. Replace workers.dev URLs in canonical tags, social URLs/images, static JSON-LD and `config.js` with the primary domain.
3. Set verified phone, address, hours, map/profile URLs and service details in `config.js`; set `launchState: 'production'` to enable accurate AutoRepair data. Never create review schema from invented or self-authored ratings.
4. Set index/follow on the homepage, services and approved make pages; remove the global staging header and crawling block. Keep 404, brand guidelines and photography credits noindex. Allow crawlers to read the noindex instructions on those utility pages.
5. Populate the XML sitemap with canonical, indexable 200-status marketing URLs only. Verify the actual response headers, redirects and HTML after deployment.
6. Add the domain to Search Console and submit the sitemap. Add a Google Business Profile when available and match its verified business name, address and phone to the website.
7. Measure real-device Core Web Vitals and field data after launch. The responsive checks here are not a Lighthouse or field-performance score.

GA4, Google Ads and Meta tracking are optional and currently unconfigured. `generate_lead` fires only after confirmed API success; no customer contact fields are passed in analytics events.

## Deploy

The working Cloudflare URL is https://houston-auto-pros.justin-b75.workers.dev.

```sh
npm run deploy:check
npm run deploy
```

`wrangler.jsonc` defines the existing Worker, static-assets routing, restricted email binding, D1 receipt store and rate limiter. No paid plan was added. Check actual account usage separately; static asset traffic and API invocations have different Cloudflare limits.

The seven custom domains are in a shared account that currently denies Worker publishing. DNS was not changed. Moving this release there requires account-level Workers deployment access, the D1 schema and email recipient/sender verification in that account; uploading only `dist/` would omit the appointment endpoint. The older static-only domain-upload bundle is obsolete for booking-enabled deployment.

`.openai/hosting.json` is retained for the original Sites preview and is not this deployment target.
