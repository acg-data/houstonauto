# Houston Auto Pros

Independent European and luxury auto service website at https://houstonautopros.com. Plain HTML, CSS and JavaScript are served as Cloudflare static assets. A separate existing Worker handles appointment email, and a small redirect Worker forwards the secondary domains.

## Develop and validate

```sh
npm ci
python -m pip install -r requirements.txt
npm run build:seo
npm run test:seo
npm run audit:seo
npm run check
npm test
npm run deploy:check
```

For frontend-only work, `python -m http.server 8080 --directory dist`. This does not run the appointment API. The API accepts production origins only; use the automated backend tests for local verification. Do not send real customer details during QA.

`npm run build:seo` generates 18 service detail pages, the Houston location and location hub, the Porsche film page, business config, metadata, structured data, crawl controls and the page manifest. `python scripts/expand_services.py` is a compatibility entry point for the same build. The existing premium design, automatic dropdowns and appointment forms are preserved. Run this build after shared HTML/CSS edits. `content/makes.json` still supplies the make list to frontend generation and backend validation.

Edit `content/business.json` for public business facts and contact preferences, `content/service-pages.json` for service guidance, `content/locations.json` for verified location evidence/content, and `content/social.json` for sharing media and source/license credits. `dist/config.js` is generated; do not edit it separately. The original service taxonomy remains in `content/services.json`.

## Appointment requests

Requests go to **justin@aryocg.com**, as requested by the owner. `dist/config.js` points to `https://houston-auto-pros.justin-b75.workers.dev/api/appointments`; the primary website origin is explicitly allowed through CORS. The form confirms success only after JSON `{ ok: true }`, following email-provider acceptance. A request does not reserve a time; the shop must confirm availability. Provider acceptance does not prove inbox placement.

The Worker uses the account's existing verified sending domain, `alerts.homeservicesecretshopper.com`, with display name Houston Auto Pros appointments. The binding is restricted to Justin's verified recipient address. Visitor email becomes Reply-To when supplied. Change to a dedicated business sender after its domain is verified.

The endpoint validates service, vehicle, contact details and requested date, limits body size, checks origin, uses a honeypot and form-age check, and applies a five-request-per-minute IP limit. Cloudflare's rate limiter is approximate and local to each data center. D1 stores only request IDs, payload hashes, delivery status, provider message IDs and timestamps, not customer contact fields. Atomic receipt insertion prevents concurrent duplicate sends. Ambiguous delivery failures are not retried automatically. Receipt metadata older than 30 days is removed after successful sends.

The dedicated `houston-auto-pros-booking` database is configured in `wrangler.jsonc`; apply `worker/schema.sql` when setting up a new account. No pre-existing application database or lead platform is modified. The fallback offers an email draft when delivery cannot be confirmed.

## Content and navigation

- Services: `/services/` links to 18 substantial guides at `/services/<slug>/`, each with unique intent, metadata, FAQs, related services and a preselected appointment category. Legacy individual service fragments forward to their new page while preserving query parameters.
- Location: `/locations/houston/` has the owner-confirmed Pagewood Lane address, directions, local arrival information and service links. `/locations/` is the coverage hub. No additional cities or branches were invented.
- Makes: Porsche, BMW and Mercedes-Benz have detailed landing pages. The wider European make list opens the appointment form with the selected make. No thin placeholder landing pages are generated.
- Services and Makes open on hover for desktop fine pointers and on keyboard focus; click/tap also works. Mobile navigation scrolls independently.
- Booking uses a native make dropdown, single-column phone fields, 16px text inputs and sticky actions with safe-area padding.
- Reviews and their navigation link remain hidden until real feedback or a real profile URL is configured. The shop has no Google Business Profile yet. Never invent quotes, ratings or counts.
- The address is 8614 Pagewood Ln, Houston, TX 77063. The owner explicitly requested no public phone number; phone and hours remain unpublished. Visitors can use the working appointment form. Its recipient is separate from the public shop email.

## Photography and identity

Graphite, gunmetal, satin steel, platinum and warm porcelain; self-hosted Manrope. No emoji interface controls. Brand marks identify vehicles serviced and imply no manufacturer affiliation.

The homepage hero reads “Exceptional Cars Deserve Exceptional Care.” All 18 supported European makes have self-hosted manufacturer marks in the gallery and Makes menu. `scripts/prepare_brand_marks.py` retrieves pinned Cardog SVGs and preserves the MIT notice in `dist/assets/brands/CARDOG-LICENSE.txt`; `brand-sources.json` records provenance. Link underlines and navigation underline effects are removed; visible keyboard focus remains. The gallery uses six columns on desktop and three on phones.

Vehicle photography is stored locally in responsive WebP sizes. `photography-sources.json` and `/photography.html` record image sources and explain that illustrative photos do not depict the actual shop. `brand-sources.json` records manufacturer-mark sources. Add approved premises, team and work photos when available. Keep image dimensions, alt text and responsive sources.

## Mobile and SEO

Marketing, service, location and watch pages include a visible appointment form in the closing section (`#contact`), with a footer link for direct access. Native make/service selectors, name, phone, model, optional email and notes send to the same restricted booking endpoint as the dialog. Choosing email as the contact preference makes it required. Make pages preselect their brand and service pages preselect their category. The phone booking bar hides while the closing section is visible. The SEO build preserves this form and the European logo gallery. A labeled live QA submission was accepted by the email provider and recorded as sent; this confirms submission acceptance, not inbox placement or a reserved appointment.

See `docs/mobile-seo-review.md` for the review and launch priorities. `python scripts/inspect_metadata.py` prints the static metadata baseline. The main marketing pages have unique titles/descriptions, self-referencing canonical URLs, one H1, Open Graph and Twitter cards, image dimensions and mobile viewport tags. The same content and metadata are served to desktop and phone screens. Brand pages include breadcrumb structured data; homepage includes WebSite data.

**Search indexing is enabled for 26 marketing/watch pages.** The three utility pages (404, brand guidelines and media credits) remain noindex. Canonicals, social metadata, static Service/Breadcrumb/AutoRepair data, robots and the sitemap agree with the production business record. No phone, opening hours, GBP, ratings, qualifications or shop photographs were invented. Public contact uses the verified address and working appointment form, honoring the owner's request to keep the phone hidden. See `docs/seo-strategy.md` for architecture, evidence gates and validation.

The remaining growth steps are:

1. Keep `https://houstonautopros.com` as the primary origin. The other six domains and www aliases already redirect to relevant pages; do not publish duplicate indexable copies.
2. Add approved original shop/work photos, actual project evidence and real customer feedback. Add hours or a phone only when the owner chooses to publish them.
3. Add further locations only after verified coverage, a serving shop, distinct local guidance and two approved local evidence items exist. Do not multiply services by every city or make.
4. Verify the primary domain in Search Console and submit `/sitemap.xml`. Add a Google Business Profile when available. Search visibility and crawl timing are controlled by search engines.
5. Measure field Core Web Vitals after launch; responsive checks and HTTP timings are not a Lighthouse score or field performance measurement.

## Social film

Homepage, Porsche and `/film/` include `og:video` with HTTPS MP4, MIME type and dimensions. Every page has a fresh 1200×630 Porsche still fallback, image alt text and versioned media URLs; Twitter remains a large-image card for broad compatibility. Social applications decide which media they display. The native film player uses `preload="none"`, so ordinary site visits do not automatically download the 4.8 MB clip. The clip is licensed Pexels footage by Kampus Production, credited on the film and photography pages. It does not depict the shop or its customers. `content/social.json` records source, license and dimensions.

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
