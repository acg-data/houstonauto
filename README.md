# Houston Auto Pros

Complete editable source for the website, including the generated automotive hero photo and visual brand references.

## Run locally

From this folder:

```bash
python -m http.server 8080 --directory dist
```

On Windows, `py -m http.server 8080 --directory dist` also works.
Open http://localhost:8080. Use a web server rather than opening the HTML file directly because asset and navigation paths start at the site root.

## Files

- `dist/index.html` — full homepage
- `dist/brand.html` — identity, palette and application concepts
- `dist/style.css` — all styling and responsive breakpoints
- `dist/app.js` — appointment draft dialog, menu, clipboard swatches
- `dist/assets/atelier-hero.jpg` — included generated hero photography
- `design-reference/` — approved direction and expanded concept board; these are visual references, not screenshots of the coded website
- `CLAUDE.md` — context for continuing development in Claude Code

Plain HTML, CSS, JavaScript and inline SVG. No bundler, npm dependencies, API key or build step. Manrope loads from Google Fonts; Arial is the fallback. Publish the contents of `dist/` using any static web host with root-relative path support.

## Current limitations

The appointment form only prepares a downloadable text draft in the browser. It sends nothing, stores nothing on a server, and does not confirm bookings. Connect a real booking or contact destination before launch. Business contact details, exact services, hours and business claims should be confirmed before public launch. The website intentionally has no invented testimonials, ratings or certifications.

The typography and inline SVG mark are editable web interpretations of the image-based brand concept, not final production logo artwork. The concept boards may show illustrative copy and details that need business verification.

## Palette

Graphite #17191B
Gunmetal #343A40
Satin steel #A6ADB4
Platinum #E4E3DF
Warm porcelain #F3F1EB

The export intentionally excludes ChatGPT hosting configuration and Git history, so it can be used independently.
