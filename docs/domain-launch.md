# Custom-domain launch — 29 October 2026

Latest visual release: `141298a3-9cbf-42bf-a046-ac1ffd3d78d6`. The hero now reads “Exceptional cars. Exacting care.” All 18 supported makes have self-hosted logos in the gallery and Makes menu; decorative link underlines are removed. Checked the 320px/390px phone layouts and desktop gallery, brand prefill and keyboard dropdown opening. All marks loaded, no horizontal overflow or visible text underlines were found, and the static SEO audit still reports zero errors. [Live hero](../outputs/hero-brand-update/hero-live.jpg) · [Live brand gallery](../outputs/hero-brand-update/brands-live.jpg).

https://houstonautopros.com is live with HTTPS, the latest frontend and the working appointment form. All fourteen apex/www hostnames were checked over HTTPS. The primary returns 200, and the thirteen aliases return 301 to the destinations below. Tracking query parameters survive redirects, and existing deep paths are preserved.

| Domain, including its www alias | Root destination |
| --- | --- |
| houstonautopros.com | https://houstonautopros.com/ (www redirects to the apex) |
| houstonautodiagpro.com | https://houstonautopros.com/services/#diagnostics |
| houstonbmwpros.com | https://houstonautopros.com/bmw/ |
| houstonenginebuilders.com | https://houstonautopros.com/services/#engine-diagnostics |
| houstonporschemechanic.com | https://houstonautopros.com/porsche/ |
| houstonporschepros.com | https://houstonautopros.com/porsche/ |
| houstonporscherepair.com | https://houstonautopros.com/porsche/ |

## Deployment record

- Shared Anoni account: static `houston-auto-pros`, version `9efadf54-ea3d-456b-91d7-42744ee7bfc9`, deployed with `wrangler.site.jsonc`.
- Shared Anoni account: `houston-auto-domain-redirects`, version `baa82a64-5529-4ee4-be64-1b469d131a8f`, deployed with `wrangler.redirects.jsonc`.
- Justin account: existing appointment `houston-auto-pros`, version `3ecd7219-3cf8-47a9-9132-f7da74c62dae`, deployed with `wrangler.jsonc`. Non-API requests to its former preview address now redirect to the primary domain.

Cloudflare Custom Domains created the web routing/DNS records and managed certificates. Always Use HTTPS is enabled for the primary zone in SSL/TLS → Edge Certificates; a live HTTP deep link returned 301 to the same HTTPS path and query. Keep that zone setting enabled for future deployments. No paid plan or subscription was added. The primary static site has no application script on its request path. Redirect and booking script usage remains subject to the accounts' existing quotas; this is not a promise of unlimited free dynamic traffic.

## Verification

The homepage, service directory and three make pages return 200 with their primary-domain canonicals. Unknown pages return 404. Nine automated tests pass, including domain redirects, query preservation, fixed redirect origins and the existing appointment validation/duplicate-delivery tests. Type checking, both shared-account deployment dry runs, backend dry run and the eight-page staging SEO audit pass; only the intentionally unlinked 404 produces a warning.

One clearly labeled QA request was submitted from https://houstonautopros.com through the actual browser form to the existing appointment endpoint. The browser displayed success, and D1 recorded `sent` after provider acceptance. This confirms the domain's cross-origin form flow, not inbox placement. The CORS preflight returns 204 and explicitly permits https://houstonautopros.com.

Evidence: [live site](../outputs/domain-launch/houstonautopros-live.jpg), [booking confirmation](../outputs/domain-launch/booking-confirmation.jpg), [all fourteen HTTPS routing checks](../outputs/domain-launch/domain-routing.json).

## Remaining business setup

The website is public, but remains noindex with staged robots/sitemap settings until verified phone, address, hours and service claims are ready. Keep absent contact fields and reviews hidden; no Google Business Profile exists yet. Then enable approved marketing-page indexing and populate the sitemap together. Do not fabricate business details or reviews to pass a launch checklist.
