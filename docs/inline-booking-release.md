# Inline appointment form — 29 October 2026

Live: https://houstonautopros.com/#contact

The homepage, services page and dedicated Porsche, BMW and Mercedes-Benz pages now end with a visible appointment form. The porcelain form sits in the existing dark closing section and stacks into one column on phones. Native selectors include the 18 European makes plus an other-make option, and the six existing service categories. Make pages preselect their brand. Email becomes required when the visitor chooses email contact. Notes can include preferred timing; availability is confirmed by a person.

Both the inline form and existing dialog use shared request collection and delivery helpers. Controls disable while sending; provider acceptance is required before displaying success. A failed or unconfirmed request preserves its fields and offers an email fallback. No new recipient, backend, subscription or business claim was added. The mobile booking bar hides while the closing section is visible. Footer links jump directly to the form.

All 18 self-hosted European manufacturer marks remain visible in the gallery and Makes menu. The gallery heading now explicitly identifies European makes. Sources and license records remain in `brand-sources.json`.

Validation:

- Browser checks at desktop and 390px phone width: layout, native dropdowns, required-field focus and conditional email requirement.
- BMW page automatically selects BMW; Audi gallery control still opens the existing dialog with Audi selected.
- One clearly labeled live QA request sent to the existing owner-supplied booking recipient. The UI confirmed acceptance, and receipt `1c1735ae-deed-4e15-99e3-0aec1aee7084` was recorded as `sent`. No real visit was requested. Inbox arrival was not independently verified.
- Static SEO audit: 8 pages, zero errors; the existing unlinked 404 warning remains. Search-launch restrictions remain unchanged.
- JavaScript syntax check and static-site deployment dry run passed.

Final static Worker version: `8111c2c6-173d-43a3-97bd-ea924076d51a`, deployed with `wrangler.site.jsonc` in the shared domain account. The appointment backend and redirect Worker were unchanged.

Screenshots are in `outputs/inline-booking/`.
