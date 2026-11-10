#!/usr/bin/env python3
"""Local gate for the kevinsmurdock.com site.

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
CSS = ROOT / "css" / "site.css"
REDIRECTS = ROOT / "_redirects"

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
    "The Citadel Class of 1992",
    "Premier Medical Laboratory Services",
    "first private commercial testing facility in South Carolina",
    "The Citadel Today",
    "WIS-TV",
    "Diversified Medical Healthcare",
    "founded in 2011",
    "$51 million",
    "185 new jobs",
    "315 Tanner Price Way",
    "6000 Pelham Road",
    "expected to be completed by 2025",
    "toured Premier Medical Laboratories",
    "senior staff of Sen. Tim Scott",
    "From leading research and innovation to generously donating PPE",
    "Our mission is to positively impact patient lives",
    "100,000 tests per day",
    "98% of results",
    "Vessel Medical announced donations of N95 masks",
    "CPT Medical, Vessel Medical, and OnGen",
    "The Post and Courier",
    "SCBIO Foundation",
    "There has been media coverage about legal matters.",
    "https://formspree.io/f/xgorwrnb",
    "G-H3GVQ6M8LM",
    "AW-18090292877",
    "https://www.linkedin.com/in/kevin-murdock-7a64a229/",
    "https://www.crunchbase.com/person/kevin-murdock-aa5f",
    "https://firstinandpunished.com",
    "https://firstinbook.com",
    "id=\"video\"",
    "Updated November 10, 2026",
    "What is Kevin Murdock known for in Greenville, SC?",
    "What did Premier Medical Laboratory Services do during COVID-19?",
    "https://www.wyff4.com/article/upstate-commercial-lab-becomes-first-in-sc-to-test-for-covid-19-testing/31917255",
    "https://governor.sc.gov/news/2022-02/diversified-medical-healthcare-expanding-operations-greenville-county",
    "https://scbiz.com/greenville-lab-validated-for-covid-19-tests/",
    "announced an expansion in Greenville County",
    "https://www.postandcourier.com/greenville/business/greenville-medical-firm-adds-185-jobs-invests-51m-in-expansion/article_5feb28e8-93e0-11ec-9080-2bc7f038245e.html",
    "https://scbiz.com/diversified-medical-healthcare-to-invest-51-million-add-185-jobs/",
    "https://www.wyff4.com/article/greenville-county-lab-among-largest-in-country-testing-for-covid-19-variants-strains/36178979",
    "https://scbiz.com/coping-with-covid-cpt-medical/",
    "https://scbiz.com/greenville-companies-partner-to-patch-a-hole-in-covid-19-supply-chain/",
    "https://www.prnewswire.com/news-releases/first-commercial-laboratory-in-south-carolina-validated-for-covid-19-testing-301028937.html",
    "PRNewswire (company press release)",
    "https://www.genomeweb.com/pcr/premier-medical-laboratory-services-exclusively-offer-patia-type-2-diabetes-risk-test-us",
    "exclusive U.S. provider of the PATIA DiabetesPredict test",
    "The company reported more than",
    "https://www.prnewswire.com/news-releases/one-year-since-fda-validation-of-south-carolinas-first-covid-19-testing-laboratory-301254210.html",
    "https://www.prnewswire.com/news-releases/senator-tim-scotts-senior-staff-visits-scs-first-covid-19-testing-lab-at-one-year-mark-301265250.html",
    "https://scbiz.com/greenville-lab-honored-for-nations-highest-covid-19-testing-capacity/",
    "https://www.prnewswire.com/news-releases/us-senator-lindsey-graham-speaks-on-the-importance-of-variant-tracking-amid-increasing-spread-of-the-delta-variant-301315031.html",
    "https://www.postandcourier.com/greenville/politics/graham-calls-for-hearings-on-covid-questions-surrounding-wuhan-lab-during-greenville-visit/article_6a07b858-c7be-11eb-88dc-b74da1ccd884.html",
    "held a press availability there",
    "Kevin Murdock, CEO, appeared with him",
    "https://greenvillejournal.com/branded-content/sen-tim-scotts-staff-visits-greenville-sc-medical-lab/",
    "sponsored/branded content",
    "introduced them to the company",
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
    "Kevin S. Murdock, Citadel Class of 1992, founded Premier Medical "
    "Laboratory Services, SC's first private commercial COVID-19 testing lab."
)

LLMS = ROOT / "llms.txt"

SOURCE_URLS = [
    "https://today.citadel.edu/upstate-commercial-lab-becomes-first-in-sc-to-test-for-covid-19/",
    "https://www.wyff4.com/article/upstate-commercial-lab-becomes-first-in-sc-to-test-for-covid-19-testing/31917255",
    "https://www.wistv.com/2020/04/16/sc-lab-providing-free-covid-testing-all-first-responders/",
    "https://governor.sc.gov/news/2022-02/diversified-medical-healthcare-expanding-operations-greenville-county",
    "https://scbiz.com/greenville-lab-validated-for-covid-19-tests/",
    "https://www.postandcourier.com/greenville/business/greenville-medical-firm-adds-185-jobs-invests-51m-in-expansion/article_5feb28e8-93e0-11ec-9080-2bc7f038245e.html",
    "https://scbiz.com/diversified-medical-healthcare-to-invest-51-million-add-185-jobs/",
    "https://www.wyff4.com/article/greenville-county-lab-among-largest-in-country-testing-for-covid-19-variants-strains/36178979",
    "https://scbiz.com/coping-with-covid-cpt-medical/",
    "https://scbiz.com/greenville-companies-partner-to-patch-a-hole-in-covid-19-supply-chain/",
    "https://www.prnewswire.com/news-releases/first-commercial-laboratory-in-south-carolina-validated-for-covid-19-testing-301028937.html",
    "https://www.genomeweb.com/pcr/premier-medical-laboratory-services-exclusively-offer-patia-type-2-diabetes-risk-test-us",
    "https://www.prnewswire.com/news-releases/one-year-since-fda-validation-of-south-carolinas-first-covid-19-testing-laboratory-301254210.html",
    "https://www.prnewswire.com/news-releases/senator-tim-scotts-senior-staff-visits-scs-first-covid-19-testing-lab-at-one-year-mark-301265250.html",
    "https://scbiz.com/greenville-lab-honored-for-nations-highest-covid-19-testing-capacity/",
    "https://www.prnewswire.com/news-releases/us-senator-lindsey-graham-speaks-on-the-importance-of-variant-tracking-amid-increasing-spread-of-the-delta-variant-301315031.html",
    "https://www.postandcourier.com/greenville/politics/graham-calls-for-hearings-on-covid-questions-surrounding-wuhan-lab-during-greenville-visit/article_6a07b858-c7be-11eb-88dc-b74da1ccd884.html",
    "https://greenvillejournal.com/branded-content/sen-tim-scotts-staff-visits-greenville-sc-medical-lab/",
]

FAQ_REQUIRED = [
    "Who is Kevin Murdock?",
    "Who is Kevin S. Murdock?",
    "What is Kevin Murdock known for in Greenville, SC?",
    "What did Premier Medical Laboratory Services do during COVID-19?",
    "Where is Kevin S. Murdock based?",
    "Did Kevin Murdock graduate from The Citadel?",
    "What is Premier Medical Laboratory Services, and who founded it?",
    "What did Diversified Medical Healthcare announce in February 2022?",
    "Is Kevin S. Murdock of Greenville the same person as Kevin Murdock of Growth & Exit Partners?",
    "What press outlets have covered Kevin Murdock or Premier Medical Laboratory Services?",
    "How can members of the press or a business partner reach him?",
]

HOME_TITLE = "Kevin S. Murdock | Healthcare Entrepreneur | Greenville, SC"
ABOUT_TITLE = "Kevin S. Murdock of Greenville | Citadel, Class of 1992"
COMPANIES_TITLE = "Premier Medical Laboratory Services | Kevin S. Murdock"
PRESS_TITLE = "Press and Coverage | Kevin S. Murdock"
FAQ_TITLE = "Who Is Kevin Murdock? | FAQ for Kevin S. Murdock"

ABOUT_DESC = (
    "Kevin S. Murdock is a Greenville, South Carolina healthcare entrepreneur, "
    "Citadel Class of 1992, and founder of Premier Medical Laboratory Services."
)
COMPANIES_DESC = (
    "Kevin S. Murdock founded Premier Medical Laboratory Services and Vessel Medical, "
    "later named with CPT Medical and OnGen in a February 2022 announcement."
)
PRESS_DESC = (
    "Press coverage of Kevin S. Murdock, including The Citadel Today, WYFF, WIS-TV, "
    "SCBiz, The Post and Courier, and the South Carolina governor's office."
)
FAQ_DESC = (
    "Answers about Kevin S. Murdock of Greenville, SC: Citadel Class of 1992, "
    "founder of Premier Medical Laboratory Services, and companies named in 2022."
)

PAGES = [
    ("home", ROOT / "index.html", HOME_TITLE, "https://kevinsmurdock.com/", DESCRIPTION),
    ("about", ROOT / "about" / "index.html", ABOUT_TITLE, "https://kevinsmurdock.com/about/", ABOUT_DESC),
    ("companies", ROOT / "companies" / "index.html", COMPANIES_TITLE, "https://kevinsmurdock.com/companies/", COMPANIES_DESC),
    ("press", ROOT / "press" / "index.html", PRESS_TITLE, "https://kevinsmurdock.com/press/", PRESS_DESC),
    ("faq", ROOT / "faq" / "index.html", FAQ_TITLE, "https://kevinsmurdock.com/faq/", FAQ_DESC),
]


def visible_faq_pairs(section_html: str) -> list[tuple[str, str]]:
    pairs = re.findall(
        r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>",
        section_html,
        flags=re.S,
    )
    if not pairs:
        pairs = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", section_html, flags=re.S)
    visible: list[tuple[str, str]] = []
    for question, answer in pairs:
        q_text = re.sub(r"<[^>]+>", "", question)
        a_text = re.sub(r"<[^>]+>", "", answer)
        q_text = re.sub(r"\s+", " ", q_text).replace("&rsquo;", "\u2019").replace("&amp;", "&").strip()
        a_text = re.sub(r"\s+", " ", a_text).replace("&rsquo;", "\u2019").replace("&amp;", "&").strip()
        visible.append((q_text, a_text))
    return visible



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

    pages: dict[str, tuple[Path, str]] = {}
    for name, path, _title, _canonical, _desc in PAGES:
        check(path.exists(), f"{name} page missing: {path}")
        pages[name] = (path, path.read_text(encoding="utf-8") if path.exists() else "")

    all_html = "\n".join(html for _path, html in pages.values())
    check(not (ROOT / "kevin_context.md").exists(), "kevin_context.md must not be published from this repo")
    for snippet in REQUIRED_SNIPPETS:
        check(snippet in all_html, f"missing required text: {snippet[:80]}")
    check(all_html.count(ATTORNEY) == 1, "attorney statement must appear exactly once")
    for bad in FORBIDDEN:
        check(bad not in all_html, f"forbidden string present: {bad}")

    home_html = pages["home"][1]
    outside_comments = re.sub(r"<!--.*?-->", "", home_html, flags=re.S)
    check("hVFLJjfg_ls" not in outside_comments, "dead YouTube id remains outside an HTML comment")
    check("hVFLJjfg_ls" in home_html, "investigation comment should retain the dead YouTube id")

    # Kevin Scott Murdock may appear only in schema alternateName, not in visible body copy.
    for name, (_path, html) in pages.items():
        visible = re.sub(r"<script type=\"application/ld\+json\">.*?</script>", "", html, flags=re.S)
        check("Kevin Scott Murdock" not in visible, f"{name} has Kevin Scott Murdock in visible copy")

    heading_counts: dict[str, int] = {}
    parsed: dict[str, Parser] = {}

    for name, path, expected_title, canonical, expected_desc in PAGES:
        html = pages[name][1]
        if not html:
            continue
        parser = Parser()
        parser.feed(html)
        parsed[name] = parser
        title = "".join(parser.title_parts).strip()
        check(title == expected_title, f"{name} unexpected title: {title}")
        check(parser.h1_count == 1, f"{name} expected one visible h1, found {parser.h1_count}")
        if name == "home":
            check(
                any(level == 1 and "Kevin S." in text and "Murdock" in text for level, text in parser.headings),
                "h1 is not the name",
            )
        check(parser.has_main and parser.has_header and parser.has_footer and parser.has_nav, f"{name} missing landmark: header, nav, main, or footer")
        check(parser.skip, f"{name} skip link missing")
        check(meta(parser, name="description") == expected_desc, f"{name} meta description mismatch")
        check(meta(parser, prop="og:description") == expected_desc, f"{name} og:description mismatch")
        check(meta(parser, name="twitter:description") == expected_desc, f"{name} twitter:description mismatch")
        check(50 <= len(expected_desc) <= 160, f"{name} description length {len(expected_desc)}")
        found_canonical = next((href for rel, href in parser.links if rel == "canonical"), "")
        check(found_canonical == canonical, f"{name} canonical {found_canonical}")
        check(meta(parser, prop="og:url") == canonical, f"{name} og:url mismatch")
        check(meta(parser, prop="og:title") == title, f"{name} og:title mismatch")
        check(meta(parser, name="twitter:title") == title, f"{name} twitter:title mismatch")
        check(meta(parser, prop="og:image") == "https://kevinsmurdock.com/og-image.png", f"{name} og:image is not the local card")
        check(meta(parser, name="twitter:image") == "https://kevinsmurdock.com/og-image.png", f"{name} twitter:image mismatch")
        check(meta(parser, name="robots") == "index, follow", f"{name} robots meta is not index, follow")
        check("noindex" not in meta(parser, name="robots").lower(), f"{name} noindex present")
        ids = set(parser.ids)
        for href in parser.hrefs:
            if href.startswith("#") and href != "#":
                check(href[1:] in ids, f"{name} broken in-page link {href}")
        check(all(alt is not None and alt.strip() for src, alt in parser.images), f"{name} image missing alt")
        previous = 0
        for level, text in parser.headings:
            check(level <= previous + 1, f"{name} heading level skips to h{level}: {text}")
            previous = level
        check(len(parser.scripts) == 1, f"{name} expected one JSON-LD script")
        heading_counts[name] = len(parser.headings)

    home_parser = parsed.get("home")
    if home_parser:
        check("video" in home_parser.ids, "#video anchor missing")
        needed_controls = {"name", "email", "subject", "message"}
        check(needed_controls <= home_parser.control_ids, f"form controls missing: {needed_controls - home_parser.control_ids}")
        check(needed_controls <= home_parser.labels, f"form labels missing: {needed_controls - home_parser.labels}")

    # Home + press schema: Person, 18 NewsArticles, subjectOf, sameAs
    def parse_graph(html: str):
        parser = Parser()
        parser.feed(html)
        if not parser.scripts:
            return {}
        try:
            return json.loads(parser.scripts[0][1])
        except json.JSONDecodeError as exc:
            failures.append(f"JSON-LD did not parse: {exc}")
            return {}

    def check_person(graph: dict, label: str) -> None:
        nodes = graph.get("@graph", [])
        person = next((node for node in nodes if node.get("@type") == "Person"), None)
        check(person is not None, f"{label} Person node missing")
        if not person:
            return
        check(person.get("name") == "Kevin S. Murdock", f"{label} schema name mismatch")
        check(person.get("jobTitle") == "Healthcare Entrepreneur", f"{label} schema jobTitle mismatch")
        check(person.get("worksFor") is None, "schema worksFor must match the page, which names no current employer")
        check("image" not in person, "schema image is not backed by an approved portrait")
        check(person.get("description") == DESCRIPTION, f"{label} schema description mismatch")
        check(person.get("alumniOf", {}).get("name") == "The Citadel", f"{label} schema alumni mismatch")
        check("Greenville" in person.get("homeLocation", {}).get("name", ""), f"{label} schema location mismatch")
        same = person.get("sameAs", [])
        check("https://www.linkedin.com/in/kevin-murdock-7a64a229/" in same, "LinkedIn missing from sameAs")
        check("https://www.crunchbase.com/person/kevin-murdock-aa5f" in same, "Crunchbase missing from sameAs")
        check("https://firstinandpunished.com" in same, "firstinandpunished.com missing from sameAs")
        check("https://kevinsmurdock.com" not in same and "https://kevinsmurdock.com/" not in same, "canonical URL should not also be sameAs")
        check(all(not str(url).lower().endswith("rep-os.ai") for url in same), "RepOS URL in sameAs")
        alts = person.get("alternateName") or []
        if not isinstance(alts, list):
            alts = [alts]
        check("Kevin Murdock" in alts, f"{label} alternateName missing Kevin Murdock")
        check("Kevin Scott Murdock" in alts, f"{label} alternateName missing Kevin Scott Murdock")
        subject = person.get("subjectOf") or []
        if not isinstance(subject, list):
            subject = [subject]
        subject_ids = {
            item.get("@id") if isinstance(item, dict) else str(item)
            for item in subject
        }
        articles = [node for node in nodes if node.get("@type") == "NewsArticle"]
        article_urls = {node.get("url") for node in articles}
        article_ids = {node.get("@id") for node in articles}
        for url in SOURCE_URLS:
            check(url in article_urls, f"{label} NewsArticle missing for {url}")
        check(article_ids <= subject_ids, f"{label} Person subjectOf does not reference every NewsArticle")
        check(len(articles) >= 18, f"{label} expected at least eighteen NewsArticle nodes")
        # DMH may be named, but founder credit is not confirmed
        for node in nodes:
            if node.get("@type") == "Organization" and node.get("name") == "Diversified Medical Healthcare":
                check("founder" not in node, f"{label} Diversified Medical Healthcare should not list an unconfirmed founder")

    home_graph = parse_graph(pages["home"][1])
    check(next((n for n in home_graph.get("@graph", []) if n.get("@type") == "ProfilePage"), None) is not None, "ProfilePage node missing")
    check(next((n for n in home_graph.get("@graph", []) if n.get("@type") == "WebSite"), None) is not None, "WebSite node missing")
    page = next((n for n in home_graph.get("@graph", []) if n.get("@type") == "ProfilePage"), None)
    if page:
        check(page.get("dateModified") == "2026-11-10", "schema dateModified is not the real edit date")
        check(page.get("description") == DESCRIPTION, "ProfilePage description mismatch")
    check_person(home_graph, "home")
    press_graph = parse_graph(pages["press"][1])
    check_person(press_graph, "press")

    # Breadcrumbs on inner pages
    for name in ("about", "companies", "press", "faq"):
        graph = parse_graph(pages[name][1])
        crumbs = next((n for n in graph.get("@graph", []) if n.get("@type") == "BreadcrumbList"), None)
        check(crumbs is not None, f"{name} BreadcrumbList missing")
        person = next((n for n in graph.get("@graph", []) if n.get("@type") == "Person"), None)
        check(person is not None, f"{name} Person node missing")

    # FAQPage lives on /faq/ and must match visible accordion text
    faq_html = pages["faq"][1]
    faq_graph = parse_graph(faq_html)
    faq_page = next((node for node in faq_graph.get("@graph", []) if node.get("@type") == "FAQPage"), None)
    check(faq_page is not None, "FAQPage node missing")
    # Home should not host a competing FAQPage
    home_faq = next((n for n in home_graph.get("@graph", []) if n.get("@type") == "FAQPage"), None)
    check(home_faq is None, "FAQPage schema should live on /faq/, not the homepage")
    if faq_page:
        faq_section = re.search(r'<section id="faq".*?</section>', faq_html, flags=re.S)
        check(faq_section is not None, "visible FAQ section missing")
        visible = visible_faq_pairs(faq_section.group(0) if faq_section else "")
        schema_qs = faq_page.get("mainEntity") or []
        check(len(schema_qs) == len(visible), f"FAQPage has {len(schema_qs)} questions, page has {len(visible)}")
        for required in FAQ_REQUIRED:
            check(any(question == required for question, _answer in visible), f"visible FAQ missing {required}")
        for schema_q, visible_pair in zip(schema_qs, visible):
            name = schema_q.get("name", "")
            answer = (schema_q.get("acceptedAnswer") or {}).get("text", "")
            check(name == visible_pair[0], f"FAQ schema question mismatch: {name!r} != {visible_pair[0]!r}")
            check(answer == visible_pair[1], f"FAQ schema answer mismatch for {name}")

    check(LLMS.exists(), "llms.txt missing")
    if LLMS.exists():
        llms = LLMS.read_text(encoding="utf-8")
        check("https://kevinsmurdock.com/" in llms, "llms.txt does not link the homepage")
        check("https://kevinsmurdock.com/press/" in llms, "llms.txt does not link the press page")
        check("https://kevinsmurdock.com/faq/" in llms, "llms.txt does not link the FAQ page")
        check("https://kevinsmurdock.com/about/" in llms, "llms.txt does not link the about page")
        check("https://kevinsmurdock.com/companies/" in llms, "llms.txt does not link the companies page")
        check("https://kevinsmurdock.com/#press" in llms, "llms.txt does not link the press section")
        check("https://kevinsmurdock.com/#faq" in llms, "llms.txt does not link the FAQ section")
        for url in SOURCE_URLS:
            check(url in llms, f"llms.txt missing source {url}")
        check("The Citadel Class of 1992" in llms, "llms.txt missing Citadel Class of 1992")
        check("first private commercial testing facility in South Carolina" in llms, "llms.txt missing FDA-validation fact")
        check("announced expansion" in llms, "llms.txt should describe the 2022 investment as an announced expansion")
        check("company press release" in llms.lower(), "llms.txt should label the March 24, 2020 PR Newswire item as a company press release")
        for bad in ("indictment", "consent judgment", "lawsuit"):
            check(bad not in llms.lower(), f"llms.txt contains legal-matter wording: {bad}")

    contrast_source = (CSS.read_text(encoding="utf-8") if CSS.exists() else "") + all_html
    check(CSS.exists(), "css/site.css missing")
    css_vars = dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})", contrast_source))
    pairs = [
        ("--ink", "--cream", 4.5),
        ("--ink", "--paper", 4.5),
        ("--ink", "--band", 4.5),
        ("--muted", "--cream", 4.5),
        ("--muted", "--paper", 4.5),
        ("--muted", "--band", 4.5),
        ("--blue", "--cream", 4.5),
        ("--blue", "--paper", 4.5),
        ("--blue", "--band", 4.5),
        ("--accent-light", "--cream", 4.5),
        ("--accent-light", "--paper", 4.5),
        ("--accent-light", "--band", 4.5),
        ("--blue-2", "--cream", 4.5),
        ("--blue-2", "--paper", 4.5),
        ("--blue-2", "--band", 4.5),
        ("--text-on-accent", "--accent", 4.5),
    ]
    for fg, bg, minimum in pairs:
        check(fg in css_vars and bg in css_vars, f"missing color variable {fg} or {bg}")
        if fg in css_vars and bg in css_vars:
            ratio = contrast(css_vars[fg], css_vars[bg])
            check(ratio >= minimum, f"contrast {fg} on {bg} is {ratio:.2f}, need {minimum}")
    for match in re.finditer(r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*([0-9.]+)\s*\)", contrast_source):
        check(float(match.group(1)) >= 0.85, f"low-contrast white alpha {match.group(0)}")

    check(ROBOTS.read_text(encoding="utf-8") == ROBOTS_EXPECTED, "robots.txt changed")
    sitemap = SITEMAP.read_text(encoding="utf-8")
    check("<lastmod>2026-11-10</lastmod>" in sitemap, "sitemap lastmod is not the real content-change date")
    check("<changefreq>weekly</changefreq>" in sitemap, "sitemap changefreq changed")
    check("<priority>1.0</priority>" in sitemap, "sitemap priority changed")
    for _name, _path, _title, canonical, _desc in PAGES:
        check(f"<loc>{canonical}</loc>" in sitemap, f"sitemap missing {canonical}")
    check(sitemap.count("<loc>") == 5, f"sitemap should list all five pages, found {sitemap.count('<loc>')}")
    check(OG.exists() and OG.read_bytes().startswith(b"\x89PNG"), "og-image.png missing or not a PNG")
    check(OG.stat().st_size < 400_000, "og image unexpectedly large")
    check((ROOT / "favicon.svg").exists(), "favicon missing")
    check(REDIRECTS.exists(), "_redirects missing")
    if REDIRECTS.exists():
        redirects = REDIRECTS.read_text(encoding="utf-8")
        for path in ("/about", "/companies", "/press", "/faq", "/work"):
            check(path in redirects, f"_redirects missing {path}")

    if failures:
        print(f"FAILED {len(failures)} check(s):")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("PASSED local site gate")
    print(f"  description length: {len(DESCRIPTION)}")
    print(f"  pages: {', '.join(name for name, *_ in PAGES)}")
    print(f"  visible headings: {sum(heading_counts.values())}")
    home_hrefs = parsed["home"].hrefs if "home" in parsed else []
    print(f"  in-page anchors: {sum(1 for href in home_hrefs if href.startswith('#'))}")
    print(f"  og image bytes: {OG.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
