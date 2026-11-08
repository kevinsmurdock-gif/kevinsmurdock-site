#!/usr/bin/env python3
"""Local gate for the kevinsmurdock.com homepage refresh.

Run from the repository root:

    python3 scripts/validate_site.py
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"
ROBOTS = ROOT / "robots.txt"
OG = ROOT / "og-image.png"

ATTORNEY = (
    "Kevin agreed to this resolution solely to avoid the significant cost, "
    "time, and uncertainty of a lengthy trial. The Consent Judgment does not "
    "include any finding or admission of wrongdoing on Kevin's part. Kevin has "
    "consistently maintained that he did nothing improper and remains proud of "
    "the services his medical laboratory provided for residents throughout "
    "Greenville County and beyond."
)

REQUIRED_SNIPPETS = [
    ATTORNEY,
    "Attorney Statement",
    "For over 25 years, Kevin S. Murdock has been building healthcare companies",
    "Praised by US Senator Lindsey Graham as running one of the largest COVID variant labs in America.",
    "Shannon Forest Christian School",
    "Gold Star recipient, walk-on soccer player, and early graduate",
    "World Bank forestry project in Tunisia",
    "AstraZeneca",
    "Nexium and Crestor",
    "Premier Medical Laboratory Services",
    "the first private laboratory in South Carolina to receive FDA validation",
    "up to 300,000 tests per day with pooling",
    "Yale SalivaDirect",
    "employed 450 people",
    "As far as COVID goes, we are heavily invested in the variant testing",
    "From leading research and innovation to generously donating PPE",
    "Our mission is to positively impact patient lives",
    "There has been media coverage about legal matters.",
    "https://formspree.io/f/xgorwrnb",
    "G-H3GVQ6M8LM",
    "AW-18090292877",
    "https://www.linkedin.com/in/kevin-murdock-7a64a229/",
    "https://www.crunchbase.com/person/kevin-murdock-aa5f",
    "https://bibleai.ai",
    "https://firstinandpunished.com",
    "https://firstinbook.com",
    "Blue Cross Blue Shield preferred COVID lab",
    "6M test kits manufactured",
    "Garlington North",
    "Meta Lab DX",
    "Free COVID-19 Tests for All SC First Responders",
    "Thousands of N95 Masks Donated",
    "id=\"video\"",
]

FORBIDDEN = [
    "RepOS",
    "Precision DX",
    "TruView",
    "youtu.be",
    "youtube.com",
    "img.youtube.com",
    "story.mp4",
    "noindex",
    "no spin",
    "Plain facts",
]

ROBOTS_EXPECTED = "User-agent: *\nAllow: /\n\nSitemap: https://kevinsmurdock.com/sitemap.xml\n"

DESCRIPTION = (
    "Kevin S. Murdock, Greenville SC healthcare entrepreneur and Citadel Class "
    "of 1992 graduate, founded the state's first FDA-validated COVID testing lab."
)


def lin(channel: float) -> float:
    c = channel / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def contrast(a: str, b: str) -> float:
    def lum(h: str) -> float:
        h = h.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

    lighter, darker = sorted((lum(a), lum(b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.metas: list[tuple[str, str, str]] = []
        self.links: list[tuple[str, str]] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.scripts: list[tuple[str, str]] = []
        self.in_json = False
        self.json_parts: list[str] = []
        self.headings: list[tuple[int, str]] = []
        self.heading_level = 0
        self.heading_parts: list[str] = []
        self.hidden_depth = 0
        self.tag_stack: list[tuple[str, bool]] = []
        self.has_main = False
        self.has_header = False
        self.has_footer = False
        self.has_nav = False
        self.labels: set[str] = set()
        self.control_ids: set[str] = set()
        self.images: list[tuple[str, str | None]] = []
        self.skip = False
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        hidden = "hidden" in ad or self.hidden_depth > 0
        self.tag_stack.append((tag, "hidden" in ad))
        if "hidden" in ad:
            self.hidden_depth += 1
        if tag == "main":
            self.has_main = True
        elif tag == "header":
            self.has_header = True
        elif tag == "footer":
            self.has_footer = True
        elif tag == "nav":
            self.has_nav = True
        if "id" in ad:
            self.ids.append(ad["id"])
        if tag == "a" and "href" in ad:
            self.hrefs.append(ad["href"])
            if ad["href"] == "#main" and "skip" in ad.get("class", ""):
                self.skip = True
        if tag == "meta":
            self.metas.append((ad.get("name", ""), ad.get("property", ""), ad.get("content", "")))
        if tag == "link":
            self.links.append((ad.get("rel", ""), ad.get("href", "")))
        if tag == "title":
            self.in_title = True
        if tag == "script" and ad.get("type") == "application/ld+json":
            self.in_json = True
            self.json_parts = []
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and not hidden:
            self.heading_level = int(tag[1])
            self.heading_parts = []
            if tag == "h1":
                self.h1_count += 1
        if tag == "label" and "for" in ad:
            self.labels.add(ad["for"])
        if tag in {"input", "textarea", "select"} and "id" in ad:
            self.control_ids.add(ad["id"])
        if tag == "img":
            self.images.append((ad.get("src", ""), ad.get("alt")))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_json:
            self.scripts.append(("application/ld+json", "".join(self.json_parts)))
            self.in_json = False
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self.heading_level:
            self.headings.append((self.heading_level, "".join(self.heading_parts).strip()))
            self.heading_level = 0
        if self.tag_stack:
            opened, started_hidden = self.tag_stack.pop()
            if started_hidden and self.hidden_depth:
                self.hidden_depth -= 1
            if opened != tag and self.tag_stack:
                # Parser can see implied closures; keep the hidden counter honest.
                pass

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json:
            self.json_parts.append(data)
        if self.heading_level:
            self.heading_parts.append(data)


def meta(parser: Parser, *, name: str = "", prop: str = "") -> str:
    for n, p, content in parser.metas:
        if name and n == name:
            return content
        if prop and p == prop:
            return content
    return ""


def main() -> int:
    failures: list[str] = []

    def check(ok: bool, message: str) -> None:
        if not ok:
            failures.append(message)

    html = INDEX.read_text(encoding="utf-8")
    check(not (ROOT / "kevin_context.md").exists(), "kevin_context.md must not be published from this repo")
    for snippet in REQUIRED_SNIPPETS:
        check(snippet in html, f"missing required text: {snippet[:80]}")
    check(html.count(ATTORNEY) == 1, "attorney statement must appear exactly once")
    for bad in FORBIDDEN:
        check(bad not in html, f"forbidden string present: {bad}")
    # The dead YouTube id may remain only inside an HTML comment.
    outside_comments = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    check("hVFLJjfg_ls" not in outside_comments, "dead YouTube id remains outside an HTML comment")
    check("hVFLJjfg_ls" in html, "investigation comment should retain the dead YouTube id")

    parser = Parser()
    parser.feed(html)
    title = "".join(parser.title_parts).strip()
    check(title == "Kevin S. Murdock | Healthcare Entrepreneur | Greenville, SC", f"unexpected title: {title}")
    check(parser.h1_count == 1, f"expected one visible h1, found {parser.h1_count}")
    check(any(level == 1 and "Kevin S." in text and "Murdock" in text for level, text in parser.headings), "h1 is not the name")
    check(parser.has_main and parser.has_header and parser.has_footer and parser.has_nav, "missing landmark: header, nav, main, or footer")
    check(parser.skip, "skip link missing")
    check("video" in parser.ids, "#video anchor missing")
    check(meta(parser, name="description") == DESCRIPTION, "meta description mismatch")
    check(meta(parser, prop="og:description") == DESCRIPTION, "og:description mismatch")
    check(meta(parser, name="twitter:description") == DESCRIPTION, "twitter:description mismatch")
    check(50 <= len(DESCRIPTION) <= 160, f"description length {len(DESCRIPTION)}")
    canonical = next((href for rel, href in parser.links if rel == "canonical"), "")
    check(canonical == "https://kevinsmurdock.com/", f"canonical {canonical}")
    check(meta(parser, prop="og:url") == "https://kevinsmurdock.com/", "og:url mismatch")
    check(meta(parser, prop="og:title") == title, "og:title mismatch")
    check(meta(parser, name="twitter:title") == title, "twitter:title mismatch")
    check(meta(parser, prop="og:image") == "https://kevinsmurdock.com/og-image.png", "og:image is not the local card")
    check(meta(parser, name="twitter:image") == "https://kevinsmurdock.com/og-image.png", "twitter:image mismatch")
    check(meta(parser, name="robots") == "index, follow", "robots meta is not index, follow")
    check("noindex" not in meta(parser, name="robots").lower(), "noindex present")

    ids = set(parser.ids)
    for href in parser.hrefs:
        if href.startswith("#") and href != "#":
            check(href[1:] in ids, f"broken in-page link {href}")
    check(all(alt is not None and alt.strip() for src, alt in parser.images), "image missing alt")
    needed_controls = {"name", "email", "subject", "message"}
    check(needed_controls <= parser.control_ids, f"form controls missing: {needed_controls - parser.control_ids}")
    check(needed_controls <= parser.labels, f"form labels missing: {needed_controls - parser.labels}")

    previous = 0
    for level, text in parser.headings:
        check(level <= previous + 1, f"heading level skips to h{level}: {text}")
        previous = level

    check(len(parser.scripts) == 1, "expected one JSON-LD script")
    try:
        data = json.loads(parser.scripts[0][1])
    except json.JSONDecodeError as exc:
        failures.append(f"JSON-LD did not parse: {exc}")
        data = {}
    graph = data.get("@graph", [])
    person = next((node for node in graph if node.get("@type") == "Person"), None)
    page = next((node for node in graph if node.get("@type") == "ProfilePage"), None)
    website = next((node for node in graph if node.get("@type") == "WebSite"), None)
    check(person is not None, "Person node missing")
    check(page is not None, "ProfilePage node missing")
    check(website is not None, "WebSite node missing")
    if person:
        check(person.get("name") == "Kevin S. Murdock", "schema name mismatch")
        check(person.get("jobTitle") == "Healthcare Entrepreneur", "schema jobTitle mismatch")
        check(person.get("worksFor") is None, "schema worksFor must match the page, which names no current employer")
        check("image" not in person, "schema image is not backed by an approved portrait")
        check(person.get("description") == DESCRIPTION, "schema description mismatch")
        check(person.get("alumniOf", {}).get("name") == "The Citadel", "schema alumni mismatch")
        check("Greenville" in person.get("homeLocation", {}).get("name", ""), "schema location mismatch")
        same = person.get("sameAs", [])
        check("https://www.linkedin.com/in/kevin-murdock-7a64a229/" in same, "LinkedIn missing from sameAs")
        check("https://www.crunchbase.com/person/kevin-murdock-aa5f" in same, "Crunchbase missing from sameAs")
        check("https://firstinandpunished.com" in same, "firstinandpunished.com missing from sameAs")
        check("https://kevinsmurdock.com" not in same and "https://kevinsmurdock.com/" not in same, "canonical URL should not also be sameAs")
        check(all(not str(url).lower().endswith("rep-os.ai") for url in same), "RepOS URL in sameAs")
    if page:
        check(page.get("dateModified") == "2026-11-08", "schema dateModified is not the real edit date")
        check(page.get("description") == DESCRIPTION, "ProfilePage description mismatch")

    css_vars = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})", html))
    pairs = [
        ("--text-on-navy", "--navy", 4.5),
        ("--muted-on-navy", "--navy", 4.5),
        ("--muted-on-navy", "--navy-2", 4.5),
        ("--text-on-navy", "--navy-2", 4.5),
        ("--gold-on-navy", "--navy", 4.5),
        ("--gold-on-navy", "--navy-2", 4.5),
        ("--ink", "--cream", 4.5),
        ("--muted", "--cream", 4.5),
        ("--muted", "--paper", 4.5),
        ("--gold-text", "--cream", 4.5),
        ("--gold-text", "--paper", 4.5),
        ("--navy", "--gold-on-navy", 4.5),
    ]
    for fg, bg, minimum in pairs:
        check(fg in css_vars and bg in css_vars, f"missing color variable {fg} or {bg}")
        if fg in css_vars and bg in css_vars:
            ratio = contrast(css_vars[fg], css_vars[bg])
            check(ratio >= minimum, f"contrast {fg} on {bg} is {ratio:.2f}, need {minimum}")
    for match in re.finditer(r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([0-9.]+)\s*\)", html):
        check(float(match.group(1)) >= 0.85, f"low-contrast white alpha {match.group(0)}")

    check(ROBOTS.read_text(encoding="utf-8") == ROBOTS_EXPECTED, "robots.txt changed")
    sitemap = SITEMAP.read_text(encoding="utf-8")
    check("<loc>https://kevinsmurdock.com/</loc>" in sitemap, "sitemap loc missing")
    check("<lastmod>2026-11-08</lastmod>" in sitemap, "sitemap lastmod is not the real content-change date")
    check("<changefreq>weekly</changefreq>" in sitemap, "sitemap changefreq changed")
    check("<priority>1.0</priority>" in sitemap, "sitemap priority changed")
    check(sitemap.count("<loc>") == 1, "sitemap should still list only the homepage")
    check(OG.exists() and OG.read_bytes().startswith(b"\x89PNG"), "og-image.png missing or not a PNG")
    check(OG.stat().st_size < 400_000, "og image unexpectedly large")
    check((ROOT / "favicon.svg").exists(), "favicon missing")

    if failures:
        print(f"FAILED {len(failures)} check(s):")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASSED local site gate")
    print(f"  description length: {len(DESCRIPTION)}")
    print(f"  visible headings: {len(parser.headings)}")
    print(f"  in-page anchors: {sum(1 for href in parser.hrefs if href.startswith('#'))}")
    print(f"  og image bytes: {OG.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
