# Mobile and SEO review — 29 October 2026

## Completed

Responsive review covered 320px and 390px phone layouts and a 1440px desktop layout. Services remains scrollable on phones; the desktop dropdown opens for keyboard focus, and desktop pointer-hover opening is implemented. Makes opens the appointment form with the chosen brand. The native dropdown includes 18 European makes plus an other-European option. Inputs use 16px text; phone fields stack vertically. Booking actions remain reachable and include safe-area padding. Corrected the Back-button inset and hid the floating booking bar while the menu or appointment dialog is open. Background page scrolling is locked while the dialog is open.

Removed redundant section captions, numbered decorative labels, preview-mode explanations and the downloadable service-brief flow. Empty review content and its navigation link are hidden until real reviews or a profile URL are available.

The homepage title and description now cover European and luxury repair in Houston. Main marketing pages have unique descriptions, canonical URLs, one H1, mobile viewport tags, descriptive image alt text and explicit image dimensions. Added matching Twitter title, description, image and alt metadata alongside existing Open Graph cards and locale. WebP images and the font are self-hosted, hero images load eagerly and secondary images load lazily. The service page exposes all 18 descriptions in the HTML, including collapsed disclosures.

## Highest-priority remaining launch items

| Priority | Item | Why it matters |
| --- | --- | --- |
| 1 | Connect the primary custom domain | The shared domain account currently denies Worker deployment. Keep one canonical business website and redirect the other six domains to relevant pages. |
| 1 | Remove staging search controls during domain launch | Current HTML/meta, HTTP headers and robots rules prevent normal indexing; the sitemap is empty. These must change together. |
| 1 | Verify shop phone, address and hours | These are needed for useful local contact content and accurate AutoRepair structured data. They must not be fabricated. |
| 2 | Add Search Console and submit the production sitemap | Check actual indexing, selected canonicals and crawl errors after launch. |
| 2 | Add Google Business Profile and authentic reviews when available | Provides verifiable local-business information and customer feedback. No ratings or review counts are currently claimed. |
| 2 | Add actual shop/work photography | The current automotive photos are illustrative and credited. Original evidence will make the site more useful and distinctive. |
| 3 | Measure real-device performance after launch | Responsive layout checks do not establish Core Web Vitals or a Lighthouse score. |

Avoid making duplicate websites for all seven domains or hundreds of near-identical service/location pages. Add pages when there is distinct, verified work, expertise or service-area information to explain.

## Verification

Static audit: eight HTML pages, zero errors; the unlinked 404 page is an expected warning. Metadata inspection confirmed a single H1 on every page and image dimensions on all image elements. Seven automated backend tests cover validation, recipient restrictions, escaping, retries, concurrent duplicates, delivery failure, origins, throttling and honeypot behavior. Worker type checking and deployment validation also pass.

Released to the existing Cloudflare Worker as version `576d2f75-3e73-4890-9a47-af5a5f4f972b`. Live homepage, services and all three make pages return 200; an unknown path returns 404. Staging search headers remain present. One clearly labeled QA appointment submission completed through the live phone form; the email provider accepted it and D1 recorded status `sent`. This verifies provider acceptance, not inbox placement. No JavaScript console errors appeared during that flow.

Screenshots: [phone homepage](../outputs/mobile-seo-review/homepage-phone.jpg), [phone booking form](../outputs/mobile-seo-review/booking-phone.jpg), [live request confirmation](../outputs/mobile-seo-review/booking-confirmation.jpg).

## Primary references

- [Google mobile-first indexing guidance](https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing): responsive pages should preserve the same content and metadata across devices.
- [Google canonicalization guidance](https://developers.google.com/search/docs/crawling-indexing/canonicalization): redirects, sitemap entries and canonical tags should agree on the preferred URLs.
- [Google meta-description guidance](https://developers.google.com/search/docs/appearance/snippet): use descriptions specific to each page; Google may choose a different snippet.
- [Google noindex guidance](https://developers.google.com/search/docs/crawling-indexing/block-indexing): noindex prevents eligible pages from appearing in search, and crawlers must be able to read the instruction.
