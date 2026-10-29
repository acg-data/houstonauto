# Houston Auto Pros

Independent European and luxury auto service website at https://houstonautopros.com. Plain HTML, CSS and JavaScript are served as Cloudflare static assets. A separate existing Worker handles appointment email, and a small redirect Worker forwards the secondary domains.

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

Requests go to **justin@aryocg.com**, as requested by the owner. `dist/config.js` points to `https://houston-auto-pros.justin-b75.workers.dev/api/appointments`; the primary website origin is explicitly allowed through CORS. The form confirms success only after JSON `{ ok: true }`, following email-provider acceptance. A request does not reserve a time; the shop must confirm availability. Provider acceptance does not prove inbox placement.

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

The homepage hero reads “Exceptional cars. Exacting care.” All 18 supported European makes have self-hosted manufacturer marks in the gallery and Makes menu. `scripts/prepare_brand_marks.py` retrieves pinned Cardog SVGs and preserves the MIT notice in `dist/assets/brands/CARDOG-LICENSE.txt`; `brand-sources.json` records provenance. Link underlines and navigation underline effects are removed; visible keyboard focus remains. The gallery uses six columns on desktop and three on phones.

Vehicle photography is stored locally in responsive WebP sizes. `photography-sources.json` and `/photography.html` record image sources and explain that illustrative photos do not depict the actual shop. `brand-sources.json` records manufacturer-mark sources. Add approved premises, team and work photos when available. Keep image dimensions, alt text and responsive sources.

## Mobile and SEO

See `docs/mobile-seo-review.md` for the review and launch priorities. `python scripts/inspect_metadata.py` prints the static metadata baseline. The main marketing pages have unique titles/descriptions, self-referencing canonical URLs, one H1, Open Graph and Twitter cards, image dimensions and mobile viewport tags. The same content and metadata are served to desktop and phone screens. Brand pages include breadcrumb structured data; homepage includes WebSite data.

**Search launch is still pending.** The website is publicly accessible on its custom domain, with canonical/social/schema URLs aligned to that domain. Noindex/nofollow, the staging response header, blocked crawling and an empty sitemap remain until verified shop contact details and claims are ready. `launchState: 'staging'` suppresses AutoRepair schema. Changing config alone does not update static robots/meta/header/sitemap rules.

Domain setup is complete; the remaining search-launch steps are:

1. Keep `https://houstonautopros.com` as the primary origin. The other six domains and www aliases already redirect to relevant pages; do not publish duplicate indexable copies.
2. Keep canonical tags, social URLs/images, static JSON-LD and `config.js` aligned to the primary domain. The workers.dev URL remains only as the booking endpoint.
3. Set verified phone, address, hours, map/profile URLs and service details in `config.js`; set `launchState: 'production'` to enable accurate AutoRepair data. Never create review schema from invented or self-authored ratings.
4. Set index/follow on the homepage, services and approved make pages; remove the global staging header and crawling block. Keep 404, brand guidelines and photography credits noindex. Allow crawlers to read the noindex instructions on those utility pages.
5. Populate the XML sitemap with canonical, indexable 200-status marketing URLs only. Verify the actual response headers, redirects and HTML after deployment.
6. Add the domain to Search Console and submit the sitemap. Add a Google Business Profile when available and match its verified business name, address and phone to the website.
7. Measure real-device Core Web Vitals and field data after launch. The responsive checks here are not a Lighthouse or field-performance score.

GA4, Google Ads and Meta tracking are optional and currently unconfigured. `generate_lead` fires only after confirmed API success; no customer contact fields are passed in analytics events.

## Deploy

The public URL is https://houstonautopros.com. See `docs/domain-launch.md` for the verified routing and release record.

```sh
npm run deploy:check
npm run deploy:site     # public static website, shared Anoni account
npm run deploy:domains  # secondary-domain redirects, shared Anoni account
npm run deploy          # appointment backend only, Justin account
```

`wrangler.site.jsonc` serves the static website on houstonautopros.com. `wrangler.redirects.jsonc` manages the other six domains plus all www aliases. `wrangler.jsonc` keeps the restricted email binding, D1 receipt store and rate limiter in Justin's account; its non-API URLs redirect to the primary domain. The site and redirect workers have workers.dev disabled. No paid plan was added. Check actual account usage separately; static asset traffic and script invocations have different Cloudflare limits.

The shared account now permits deployments. All fourteen apex/www hostnames are connected through Cloudflare Custom Domains, which manages their web DNS records and certificates. Booking stays in the original account to preserve the existing verified email sender and database. Do not migrate those bindings without setting up the recipient/sender and schema in the destination account. The earlier domain-upload bundle is obsolete; deploy from this repository.

`.openai/hosting.json` is retained for the original Sites preview and is not this deployment target.
