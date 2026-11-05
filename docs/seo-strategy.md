# Service-led SEO architecture

## Published structure

The build now has 29 HTML pages: 26 indexable marketing/watch pages and three deliberately excluded utility pages. The owner approved Houston-area coverage and the Pagewood Lane shop address, and requested that no phone number be displayed. A working appointment form is the public contact route. No hours, reviews, GBP profile, credentials or additional offices are claimed.

| Archetype | Route | Visitor task |
|---|---|---|
| Home | `/` | Understand the European-care offering and request a visit |
| Service hub | `/services/` | Compare all 18 services |
| Service guide | `/services/<service>/` | Understand a specific concern, prepare details and request the appropriate service |
| Make guide | `/porsche/`, `/bmw/`, `/mercedes-benz/` | Plan care for a featured make |
| Location/coverage hub | `/locations/` | Find the actual Houston shop |
| Location detail | `/locations/houston/` | Get the verified address, directions and local arrival guidance |
| Watch page | `/film/` | Play the licensed Porsche film used in sharing metadata |

The contact form is integrated into the marketing pages. Media credits and brand guidelines are utility pages; their content is not used to inflate the search footprint.

## The 18 service routes

`oil-filter-service`, `scheduled-maintenance`, `fluid-service`, `vehicle-inspection`, `check-engine-light`, `engine-diagnostics`, `electrical-diagnostics`, `battery-charging`, `leak-diagnosis`, `brake-pads-rotors`, `brake-fluid`, `suspension`, `steering`, `cooling-system`, `overheating`, `air-conditioning`, `pre-purchase`, `pre-trip`.

Each guide has a distinct title, description, H1, self-canonical, breadcrumb, intent-specific copy, three considerations, useful preparation details, three tailored FAQs, related services, a location link and a service-aware booking form. The FAQs are visible content, without promises of FAQ rich results. Service, Organization, BreadcrumbList and AutoRepair data describe verified visible facts. No prices, ratings, technician credentials or diagnostic-equipment claims are invented.

The service menu and directory use ordinary links to detail pages. Old service fragments still have targets and now forward to the dedicated page, preserving campaign queries. Category fragments remain useful within the hub. Secondary domains remain permanent redirects to the primary site; the engine domain now goes directly to engine diagnostics.

## Growth without duplicate location pages

`content/locations.json` separates service coverage from the staffed physical shop. A new location must identify verified coverage, a real serving shop, distinct local guidance and FAQs, and at least two approved evidence items. Draft or unsupported records do not create public pages. The build removes an earlier generated location page if its eligibility is withdrawn, without touching unmanaged files.

The Houston record uses the owner-confirmed staffed address and sourced Harris County emissions-program context. The latter distinguishes general condition checks from registration inspections and does not advertise this shop as a certified state station. Postal code provenance is recorded separately. No service-city or make-service-city combinations are generated. Add such pages only for a distinct visitor decision with relevant original local/service evidence.

## Search launch and contact preference

Production indexing was requested as part of the SEO expansion. The owner's explicit instruction to keep the phone hidden overrides any assumption that a number must be published. The verified address and working form provide truthful contact information. Hours remain omitted. No empty telephone/hours fields are emitted in structured data.

The builder produces aligned robots meta, response headers, robots.txt, sitemap and canonicals from the business record. The sitemap contains only the 26 canonical indexable pages. The 404, brand and media-credit pages remain noindex and are excluded. The repository auditor is adapted from the local-service-seo auditor to recognize those three explicit exclusions; the unlinked 404 warning is intentional.

Next: verify domain ownership in Search Console and submit the sitemap, create the real GBP when available, add owner-approved premises/work imagery and actual project/customer evidence, then measure queries and leads before expanding coverage. Search indexing eligibility is not a ranking guarantee.

## Social video

A 7.2-second, 1920×1080 H.264 Porsche clip by Kampus Production is licensed under the Pexels license. The source is copied locally and remuxed for progressive playback without altering the frames. Its matching 1200×630 still has a versioned URL. Homepage, Porsche and film pages offer HTTPS `og:video` properties; Twitter and image-oriented consumers receive the still. The native watch page has VideoObject data and visible creator/source credits. No ordinary page visit automatically fetches the video. No actual shop/customer appearance or Porsche endorsement is claimed.

## Verification

- `npm run build:seo`: repeat builds produce byte-identical assets.
- `npm run test:seo`: publication gates, path safety, metadata uniqueness, service defaults, every local link/fragment, DOM IDs, JSON-LD parsing, social assets and crawl-state agreement.
- `npm run audit:seo`: all 29 pages, zero errors; one expected orphan-404 warning.
- `npm run check` and `npm test`: Worker types/TypeScript and existing appointment/redirect tests.
- Browser review: service and Houston page layouts, 390px phone layout, form defaults, hidden phone, film metadata/playback and old fragment navigation.
- HTTP checks after deployment record status, canonical, robots, sitemap coverage, media MIME/range support and document transfer timings. These timings are not Core Web Vitals. No Chrome DevTools performance-trace tool is connected, so no LCP/INP/CLS or Lighthouse score is claimed.

### Live release evidence

Static Worker version `222271b2-4323-4216-87a3-ae0ed1c4688e`; redirect Worker version `4e903580-36c6-4c4d-821c-59611881a351`. The appointment backend was unchanged.

Repository sync is pending: GitHub rejected the push with an account-suspension notice. The full deployed release is committed locally; PR #1 has not received this release.

Live HTTP checks passed for all 29 explicit HTML routes, the 26-entry sitemap, crawl controls, missing-route 404 behavior, social media and both updated engine-domain redirects. The explicit `/404.html` asset is served as a 200 utility page; genuinely missing paths return 404. The 7.2-second MP4 played through to completion without a media error. Its byte-range probe returned the complete 4,775,056-byte MP4 with status 200; partial-range serving was not observed. The file is short and remuxed for progressive playback, and it is not automatically downloaded on ordinary visits.

Google's smartphone Rich Results Test crawled the cooling-system page successfully and detected three valid items (Breadcrumbs, Local business and Organization). Its only Local business notices were the optional `telephone` and `priceRange` fields, intentionally omitted. The film page produced four valid items, including Video. Test records: [service](https://search.google.com/test/rich-results/result?id=U2mP194o4Bt68E6GNGFJUQ), [film](https://search.google.com/test/rich-results/result?id=Id9bD-FHpVHdfgSS-7mONQ). These are markup-eligibility checks, not evidence that Google has indexed or ranked the pages.

## Primary references

- [Google people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google doorway/scaled-content policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Google LocalBusiness data](https://developers.google.com/search/docs/appearance/structured-data/local-business)
- [Schema.org Service](https://schema.org/Service)
- [TCEQ vehicle emissions program](https://www.tceq.texas.gov/airquality/mobilesource/vim/overview.html)
- [Building address/postal reference](https://davis-commercial.com/wp-content/uploads/2023/05/NEW8614Pagewood-v6.pdf)
- [Open Graph protocol](https://ogp.me/)
- [Kampus Production source clip](https://www.pexels.com/video/a-cabriolet-car-parked-on-the-beach-8629197/)
- [Pexels license](https://www.pexels.com/license/)
