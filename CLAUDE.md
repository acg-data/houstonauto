# Project context

## Current hosting and visual preference

The current public staging target is Cloudflare Workers Static Assets, configured in `wrangler.jsonc`; deploy with `npm run deploy`. The Cloudflare account's Pages project quota is full. The earlier private Sites manifest is retained as historical metadata; do not treat it as the current hosting target.

The user wants a restrained, high-end appearance. Do not add emojis, decorative Unicode arrows, rating-star glyphs or ornamental numbering. Keep controls textual and use SVG line icons only for functional disclosures, menus and close buttons. `scripts/refine_finish.py` applies this finish to generated HTML and runs after `scripts/expand_services.py`.

The user also wants section-heading side blurbs, ornamental labels and redundant supporting copy removed. Services and Makes open automatically on desktop hover and keyboard focus, while remaining tap controls on touch devices. The booking form uses a native brand dropdown from `content/makes.json`, covering the broader European/luxury range. `scripts/polish_booking.py` preserves these changes after generation. Do not restore preview-mode notices or the service-brief-only flow.

Appointment requests send to the temporary, owner-supplied `justin@aryocg.com` through `/api/appointments`. This is a request flow; availability is confirmed by a person. The Worker uses an existing verified infrastructure sender and a binding restricted to this recipient. D1 stores delivery receipts/hashes, not the visitor's contact details. Keep server validation, origin checks, body limits, honeypot, rate limiter and duplicate-send protection. No appointment data is sent to unrelated lead-routing systems.

Houston Auto Pros is an independent premium European automotive repair brand in Houston, covering the broader luxury European range. Porsche, BMW and Mercedes-Benz have dedicated landing pages. The website turns visits into calls and appointment requests while keeping the premium brand.

## Design direction

Preserve the approved graphite, gunmetal, satin steel and warm porcelain system. The influence is sculptural German sports-car design, especially the Porsche Mission design language: flowing surfaces, thin horizontal lines, precision, restrained typography and material honesty. Keep the brand independent; do not copy manufacturer marks or imply factory affiliation.

Use the files in design-reference as aesthetic references. Maintain the original H emblem: two subtly sculpted pillars (curved top and bottom edges, the inner edge shorter), a wide gap and one thin crossbar. Use a flat SVG mark on the web. Metallic treatments belong mainly in physical mockups.

Homepage: cinematic dark hero, large light typography, generous warm porcelain information sections, editorial service rows, spacious approach section, and dark closing invitation.

## Structure

- `dist/index.html` homepage; `dist/porsche/`, `dist/bmw/`, `dist/mercedes-benz/` make landing pages (`<body data-make="…">` pre-selects the make in the request form); `dist/brand.html` brand guidelines (noindex, footer link only); `dist/404.html`.
- `dist/config.js` is the single source for business details, request endpoint, reviews and analytics IDs. Never hard-code a phone number, address, hours or rating in HTML — use the `data-biz` / `data-action` / `data-requires` hooks that `app.js` fills from config.
- `dist/app.js`: config binding, opening-hours status (America/Chicago), structured data, photo slots, header and menu, three-step request flow, conversion tracking, palette copy buttons.
- Photo slots: `<figure class="slot" data-hint="…"><img src="/assets/photos/<name>.jpg" …></figure>`. A missing file shows a branded panel (plus an instruction while `showPlaceholders` is true). `data-fallback` sets a substitute image.

## Working rules

Edit the files in `dist/` directly. No build step. Run with `python -m http.server 8080 --directory dist`. Do not introduce a framework unless requested. The header, footer, mobile action bar and request dialog are repeated on every page: when you change one, change all six HTML files.

Keep responsive layouts, keyboard accessibility (dialog focus, Escape, visible focus), WCAG AA contrast (small text uses `--ink-3` or darker on porcelain) and reduced-motion behavior. Preserve the service disclosures, the request flow and the palette copy buttons.

The request form confirms success only when `requestEndpoint` returns a 2xx response with JSON `{ ok: true }` after provider acceptance. Otherwise say delivery could not be confirmed and offer email. A request is never a confirmed booking — never claim it is. Do not invent contact information, reviews, ratings, qualifications, warranty coverage, manufacturer affiliation, prices or business history. Empty reviews and their navigation link remain hidden until real feedback is available. Obtain verified business details for launch.

All assets are local (self-hosted Manrope, hero images). No secrets or hosting IDs are required.
