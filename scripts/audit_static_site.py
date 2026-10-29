#!/usr/bin/env python3
"""Local-service-seo auditor, adapted with explicit utility-route noindex exceptions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.h1_count = 0
        self.metas: list[dict[str, str]] = []
        self.links: list[str] = []
        self.canonicals: list[str] = []
        self.images: list[dict[str, str]] = []
        self.jsonld_raw: list[str] = []
        self._jsonld: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            self.metas.append(data)
        elif tag == "a" and data.get("href"):
            self.links.append(data["href"])
        elif tag == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonicals.append(data.get("href", ""))
        elif tag == "img":
            self.images.append(data)
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._jsonld = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        elif tag.lower() == "script" and self._jsonld is not None:
            self.jsonld_raw.append("".join(self._jsonld).strip())
            self._jsonld = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._jsonld is not None:
            self._jsonld.append(data)


def page_url(path: Path, root: Path, origin: str) -> str:
    rel = path.relative_to(root).as_posix()
    if rel == "index.html":
        route = "/"
    elif rel.endswith("/index.html"):
        route = "/" + rel[: -len("index.html")]
    else:
        route = "/" + rel
    return urljoin(origin.rstrip("/") + "/", route.lstrip("/"))


def meta_value(parser: PageParser, *, name: str | None = None, prop: str | None = None) -> str:
    for meta in parser.metas:
        if name and meta.get("name", "").lower() == name.lower():
            return meta.get("content", "").strip()
        if prop and meta.get("property", "").lower() == prop.lower():
            return meta.get("content", "").strip()
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dist", type=Path)
    ap.add_argument("--origin", required=True)
    ap.add_argument("--production", action="store_true")
    ap.add_argument("--allow-noindex", action="append", default=[], help="Explicit utility path that must remain excluded from search")
    ap.add_argument("--json", dest="json_path", type=Path)
    args = ap.parse_args()

    root = args.dist.resolve()
    files = sorted(root.rglob("*.html")) if root.is_dir() else []
    if not files:
        print(f"ERROR: no HTML files found in {root}")
        return 2

    findings: list[dict[str, str]] = []
    pages: list[dict[str, object]] = []

    def add(level: str, url: str, message: str) -> None:
        findings.append({"level": level, "url": url, "message": message})

    for path in files:
        url = page_url(path, root, args.origin)
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        title = re.sub(r"\s+", " ", parser.title).strip()
        description = meta_value(parser, name="description")
        robots = meta_value(parser, name="robots").lower()

        if not title:
            add("error", url, "missing title")
        if not description:
            add("error", url, "missing meta description")
        if parser.h1_count != 1:
            add("error", url, f"expected one H1, found {parser.h1_count}")
        if not meta_value(parser, prop="og:title"):
            add("error", url, "missing og:title")
        if not meta_value(parser, prop="og:description"):
            add("error", url, "missing og:description")
        if not meta_value(parser, prop="og:url") and args.production:
            add("error", url, "missing og:url")
        if args.production:
            utility = urlparse(url).path in args.allow_noindex
            if "noindex" in robots and not utility:
                add("error", url, "production page is noindex")
            if utility and "noindex" not in robots:
                add("error", url, "utility page must remain noindex")
            if len(parser.canonicals) != 1:
                add("error", url, f"expected one canonical, found {len(parser.canonicals)}")
            elif parser.canonicals[0] != url:
                add("error", url, f"canonical mismatch: {parser.canonicals[0]}")
        elif "noindex" not in robots:
            add("error", url, "non-production page must be noindex")

        for image in parser.images:
            if "alt" not in image:
                add("error", url, f"image missing alt: {image.get('src', '<unknown>')}")
            if not image.get("width") or not image.get("height"):
                add("warning", url, f"image missing explicit dimensions: {image.get('src', '<unknown>')}")

        for raw in parser.jsonld_raw:
            if not raw:
                add("error", url, "empty JSON-LD block")
                continue
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                add("error", url, f"invalid JSON-LD: {exc.msg}")

        pages.append({"url": url, "title": title, "description": description, "links": parser.links})

    for field in ("title", "description"):
        counts = Counter(str(page[field]).lower() for page in pages if page[field])
        for value, count in counts.items():
            if count > 1:
                add("error", "site", f"duplicate {field} across {count} pages: {value}")

    known = {str(page["url"]).rstrip("/") for page in pages}
    origin_host = urlparse(args.origin).netloc
    inbound = Counter()
    for page in pages:
        for href in page["links"]:
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            absolute = urljoin(str(page["url"]), href)
            parsed = urlparse(absolute)
            if parsed.netloc != origin_host:
                continue
            target = absolute.split("#", 1)[0].split("?", 1)[0].rstrip("/")
            if target in known:
                inbound[target] += 1
            elif not Path(parsed.path).suffix:
                add("error", str(page["url"]), f"broken internal link: {href}")

    home = args.origin.rstrip("/")
    for page in pages:
        target = str(page["url"]).rstrip("/")
        if target != home and inbound[target] == 0:
            add("warning", target, "orphan page: no crawlable internal inbound link")

    report = {
        "root": str(root),
        "origin": args.origin,
        "production": args.production,
        "intentionalNoindexPaths": args.allow_noindex,
        "pages": len(pages),
        "errors": sum(item["level"] == "error" for item in findings),
        "warnings": sum(item["level"] == "warning" for item in findings),
        "findings": findings,
    }
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(rendered + "\n", encoding="utf-8")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
