# Project context

## Current hosting and visual preference

The current public staging target is Cloudflare Workers Static Assets, configured in `wrangler.jsonc`; deploy with `npm run deploy`. The Cloudflare account's Pages project quota is full. The earlier private Sites manifest is retained as historical metadata; do not treat it as the current hosting target.

The user wants a restrained, high-end appearance. Do not add emojis, decorative Unicode arrows, rating-star glyphs or ornamental numbering. Keep controls textual and use SVG line icons only for functional disclosures, menus and close buttons. `scripts/refine_finish.py` applies this finish to generated HTML and runs after `scripts/expand_services.py`.

Houston Auto Pros is an independent premium European automotive repair brand in Houston, focused on Porsche, BMW and Mercedes-Benz owners. This is the website. Its job is to turn visits into calls and appointment requests while keeping the premium brand.

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

The request form only sends when `requestEndpoint` is set and the endpoint returns 2xx. Otherwise it must say plainly that nothing was sent. A request is never a confirmed booking — never claim it is. Do not invent contact information, reviews, ratings, qualifications, warranty coverage, manufacturer affiliation, prices or business history. Placeholders must be visibly placeholders. Obtain verified business details for launch.

All assets are local (self-hosted Manrope, hero images). No secrets or hosting IDs are required.
