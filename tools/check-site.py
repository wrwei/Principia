#!/usr/bin/env python3
"""Verification suite for the Principia marketing site.

Standard library only. Run from the repo root:

    python3 tools/check-site.py

Exit 0 = every check passed. Exit 1 = failures listed on stdout.
"""
import html.parser
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "case-study.html"]
CANONICAL_BASE = "https://wrwei.github.io/Principia/"

_failures = []


def fail(msg):
    _failures.append(msg)


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def pages():
    for name in PAGES:
        yield name, read(name)


# --- tag balance -----------------------------------------------------------

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "source", "track", "wbr"}


class _Balance(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}> at line {self.getpos()[0]}")
            return
        if self.stack[-1][0] != tag:
            open_tag, line = self.stack[-1]
            self.errors.append(
                f"expected </{open_tag}> (opened line {line}) but found "
                f"</{tag}> at line {self.getpos()[0]}")
            if any(t == tag for t, _ in self.stack):
                while self.stack and self.stack.pop()[0] != tag:
                    pass
            return
        self.stack.pop()


def check_well_formed():
    for name, src in pages():
        parser = _Balance()
        parser.feed(src)
        for err in parser.errors:
            fail(f"{name}: {err}")
        for tag, line in parser.stack:
            fail(f"{name}: <{tag}> opened at line {line} never closed")


# --- head / metadata -------------------------------------------------------

def _one(pattern, src, flags=0):
    return re.findall(pattern, src, flags)


def check_head():
    for name, src in pages():
        if not src.lstrip().lower().startswith("<!doctype html>"):
            fail(f"{name}: must start with <!doctype html>")
        if 'lang="en"' not in src:
            fail(f"{name}: <html> needs lang=\"en\"")
        if '<meta charset="utf-8">' not in src.lower():
            fail(f"{name}: missing <meta charset=\"utf-8\">")
        if 'name="viewport"' not in src:
            fail(f"{name}: missing viewport meta")

        titles = _one(r"<title>(.*?)</title>", src, re.S)
        if len(titles) != 1:
            fail(f"{name}: expected exactly 1 <title>, found {len(titles)}")
        elif not 10 <= len(titles[0].strip()) <= 65:
            fail(f"{name}: <title> is {len(titles[0].strip())} chars, want 10-65")

        descs = _one(r'<meta name="description" content="(.*?)"', src, re.S)
        if len(descs) != 1:
            fail(f"{name}: expected exactly 1 meta description")
        elif not 50 <= len(descs[0]) <= 170:
            fail(f"{name}: meta description is {len(descs[0])} chars, want 50-170")

        h1s = _one(r"<h1[ >]", src)
        if len(h1s) != 1:
            fail(f"{name}: expected exactly 1 <h1>, found {len(h1s)}")

        if 'rel="canonical"' not in src:
            fail(f"{name}: missing canonical link")
        for prop in ("og:title", "og:description", "og:image", "og:url", "og:type"):
            if f'property="{prop}"' not in src:
                fail(f"{name}: missing {prop}")
        if 'name="twitter:card"' not in src:
            fail(f"{name}: missing twitter:card")
        if "color-scheme" not in src:
            fail(f"{name}: missing <meta name=\"color-scheme\" content=\"light\">")


def check_structured_data():
    import json
    src = read("index.html")
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
    if not m:
        fail("index.html: missing JSON-LD structured data")
        return
    try:
        data = json.loads(m.group(1))
    except ValueError as exc:
        fail(f"index.html: JSON-LD is not valid JSON — {exc}")
        return
    if data.get("@type") != "SoftwareApplication":
        fail("JSON-LD: @type must be SoftwareApplication")
    for key in ("name", "url", "description", "featureList"):
        if not data.get(key):
            fail(f"JSON-LD: missing {key}")
    if "offers" in data or "price" in json.dumps(data).lower():
        fail("JSON-LD: the site is pre-commercial — no offers or pricing")


def check_skip_link():
    for name, src in pages():
        m = re.search(r'class="skip-link" href="#([\w-]+)"', src)
        if not m:
            fail(f"{name}: missing skip link (<a class=\"skip-link\" href=\"#id\">)")
            continue
        if f'id="{m.group(1)}"' not in src:
            fail(f"{name}: skip link targets #{m.group(1)} which does not exist")


# --- local references ------------------------------------------------------

REF = re.compile(r'(?:src|href)="([^"]+)"')


def _local_refs(src):
    for value in REF.findall(src):
        if value.startswith(("http://", "https://", "mailto:", "#", "//", "data:")):
            continue
        yield value


def check_paths_relative():
    for name, src in pages():
        for value in _local_refs(src):
            if value.startswith("/"):
                fail(f"{name}: absolute local path {value!r} — must be relative")


def check_refs_exist():
    for name, src in pages():
        for value in _local_refs(src):
            target = value.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            if not (ROOT / target).exists():
                fail(f"{name}: references missing file {target!r}")


# --- discoverability -------------------------------------------------------

def check_sitemap_and_robots():
    sitemap = read("sitemap.xml")
    for url in (CANONICAL_BASE, CANONICAL_BASE + "case-study.html"):
        if url not in sitemap:
            fail(f"sitemap.xml: missing {url}")
    robots = read("robots.txt")
    if "sitemap.xml" not in robots.lower():
        fail("robots.txt: should reference sitemap.xml")
    if not (ROOT / ".nojekyll").exists():
        fail(".nojekyll is missing — GitHub Pages will run Jekyll")


# --- design tokens ---------------------------------------------------------

REQUIRED_TOKENS = ["cream", "sand", "card", "line", "dark", "ink", "ink-2",
                   "brown", "brown-dark", "tick", "step-hero", "step-h2",
                   "step-body", "step-ui", "container", "prose"]

# (foreground token, background token, minimum ratio)
CONTRAST_PAIRS = [
    ("ink", "cream", 4.5), ("ink", "sand", 4.5), ("ink", "card", 4.5),
    ("ink-2", "cream", 4.5), ("ink-2", "sand", 4.5),
    ("brown", "cream", 4.5), ("brown-dark", "cream", 4.5),
    ("brown-dark", "sand", 4.5), ("tick", "cream", 4.5), ("tick", "sand", 4.5),
]

HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")


def _luminance(hex_colour):
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    channels = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(fg, bg):
    a, b = _luminance(fg), _luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def check_tokens():
    css = read("assets/css/tokens.css")
    declared = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", css))
    for token in REQUIRED_TOKENS:
        if token not in declared:
            fail(f"tokens.css: missing --{token}")
    if "color-scheme" not in css:
        fail("tokens.css: must declare color-scheme: light")
    if "prefers-color-scheme" in css:
        fail("tokens.css: spec is light-only — remove prefers-color-scheme")

    for fg, bg, minimum in CONTRAST_PAIRS:
        if fg not in declared or bg not in declared:
            continue
        fg_hex, bg_hex = declared[fg].strip(), declared[bg].strip()
        if not (HEX.fullmatch(fg_hex) and HEX.fullmatch(bg_hex)):
            fail(f"tokens.css: --{fg}/--{bg} must be plain hex for contrast checking")
            continue
        got = _ratio(fg_hex, bg_hex)
        if got < minimum:
            fail(f"tokens.css: --{fg} on --{bg} is {got:.2f}:1, need {minimum}:1")


def check_no_stray_hex():
    css = read("assets/css/site.css")
    stray = HEX.findall(css)
    if stray:
        fail(f"site.css: hex literals must live in tokens.css, found {sorted(set(stray))}")


# --- shared blocks ---------------------------------------------------------

def _block(src, name):
    m = re.search(rf"<!-- {name}:start -->(.*?)<!-- {name}:end -->", src, re.S)
    return m.group(1) if m else None


def check_shared_blocks():
    for name in ("nav", "footer"):
        blocks = {}
        for page, src in pages():
            block = _block(src, name)
            if block is None:
                fail(f"{page}: missing <!-- {name}:start -->…<!-- {name}:end --> markers")
            else:
                blocks[page] = block
        if len(blocks) == len(PAGES) and len(set(blocks.values())) != 1:
            fail(f"{name} block differs between pages — it must be byte-identical")


def check_nav_contract():
    src = read("index.html")
    nav = _block(src, "nav") or ""
    if 'id="nav-toggle"' not in nav:
        fail("nav: missing button#nav-toggle")
    if 'aria-expanded' not in nav:
        fail("nav: toggle needs aria-expanded")
    if 'aria-controls="nav-links"' not in nav or 'id="nav-links"' not in nav:
        fail("nav: toggle must control #nav-links")
    if "assets/img/logo.svg" not in nav:
        fail("nav: must show assets/img/logo.svg")


# --- generated imagery -----------------------------------------------------

SLUGS = ["dashboard", "project-vmodel", "model-create", "requirements-editor",
         "phase-complete", "design-create", "sysml-graphical-textual",
         "epsilon-analysis", "state-machine", "modelica-sim", "fmu-runtime",
         "fmea", "java-impl", "formal-verification", "gsn", "cae",
         "gsn-evidence-run", "twin-3d", "twin-dashboard", "trace-panel",
         "trace-navigate", "sim-binding", "digital-thread", "digital-thread-2",
         "digital-thread-3"]

MAX_BYTES = {"1600": 260_000, "900": 110_000}


def check_images():
    shots = ROOT / "assets" / "img" / "shots"
    for slug in SLUGS:
        for width, limit in MAX_BYTES.items():
            path = shots / f"{slug}-{width}.webp"
            if not path.exists():
                fail(f"missing generated image {path.relative_to(ROOT)}")
            elif path.stat().st_size > limit:
                fail(f"{path.name} is {path.stat().st_size // 1024}KB, "
                     f"over the {limit // 1024}KB budget")

    card = ROOT / "assets" / "img" / "og-card.png"
    if not card.exists():
        fail("missing assets/img/og-card.png")
    else:
        data = card.read_bytes()[:33]
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        if (width, height) != (1200, 630):
            fail(f"og-card.png is {width}x{height}, must be 1200x630")


# --- hero ------------------------------------------------------------------

HERO_STAGES = ["Requirements", "Architecture", "Simulation",
               "Assurance", "Verification", "Digital twin"]


def check_hero():
    src = read("index.html")
    m = re.search(r'<section class="hero".*?</section>', src, re.S)
    if not m:
        fail("index.html: missing <section class=\"hero\">")
        return
    hero = m.group(0)
    if 'viewBox="0 0 780 208"' not in hero:
        fail("hero: diagram must use viewBox=\"0 0 780 208\"")
    if "<img" in hero:
        fail("hero: must contain no raster image — first paint waits on nothing")
    for stage in HERO_STAGES:
        if f">{stage}</text>" not in hero:
            fail(f"hero diagram: missing stage label {stage!r}")
    if 'class="hero__arc"' not in hero:
        fail("hero diagram: missing the dashed trace/evidence arc group")
    if "stroke-dasharray" not in read("assets/css/site.css"):
        fail("site.css: .hero__arc must be dashed (stroke-dasharray)")
    for label in ("trace link", "evidence link"):
        if label not in hero:
            fail(f"hero diagram: missing {label!r} annotation")
    for figure in ("95+", "8.31M"):
        if figure not in hero:
            fail(f"hero stats: missing {figure!r}")
    if "9</b>" not in hero and ">9<" not in hero:
        fail("hero stats: missing the '9 languages' figure")
    if 'id="platform"' not in src:
        fail("index.html: missing #platform anchor for the nav")

    # Narrow screens get a vertical thread instead of the SVG, whose labels
    # would otherwise render at roughly 5px.
    thread = re.search(r'<ol class="thread">(.*?)</ol>', hero, re.S)
    if not thread:
        fail("hero: missing the <ol class=\"thread\"> mobile fallback")
    else:
        if thread.group(1).count("<li") != 6:
            fail(f"hero thread: expected 6 stages, found "
                 f"{thread.group(1).count('<li')}")
        for stage in HERO_STAGES:
            if f"<b>{stage}</b>" not in thread.group(1):
                fail(f"hero thread: missing stage {stage!r}")
    css = read("assets/css/site.css")
    if ".hero__diagram { display: none; }" not in css:
        fail("site.css: the SVG diagram must be hidden below 820px in favour "
             "of .thread")


# --- figures and mid-page bands -------------------------------------------

FIG = re.compile(r"<img\b[^>]*>", re.S)


def _webp_size(path):
    """Width and height from a WebP header, without leaving the stdlib."""
    data = path.read_bytes()[:32]
    if data[12:16] == b"VP8 ":
        return (int.from_bytes(data[26:28], "little") & 0x3FFF,
                int.from_bytes(data[28:30], "little") & 0x3FFF)
    if data[12:16] == b"VP8X":
        return (int.from_bytes(data[24:27], "little") + 1,
                int.from_bytes(data[27:30], "little") + 1)
    return None


def _attr(tag, name):
    m = re.search(rf'{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def _check_figure_contract(page, src, *, require_lazy=True):
    for tag in FIG.findall(src):
        if 'src="assets/img/logo.svg"' in tag:
            continue  # the mark is not a screenshot
        for attr in ("width=", "height=", "alt=", "srcset="):
            if attr not in tag:
                fail(f"{page}: <img> missing {attr.rstrip('=')} — {tag[:70]}…")
        if "-1600.webp" not in tag or "-900.webp" not in tag:
            fail(f"{page}: <img> srcset must offer both widths — {tag[:70]}…")
        if require_lazy and 'loading="lazy"' not in tag:
            fail(f"{page}: below-fold <img> needs loading=\"lazy\" — {tag[:70]}…")

        # Declared dimensions must match the largest candidate, or the
        # reserved box is the wrong shape and the page shifts as it loads.
        widest = re.search(r"([\w./-]+-1600\.webp)", tag)
        declared_w, declared_h = _attr(tag, "width"), _attr(tag, "height")
        if widest and declared_w and declared_h:
            path = ROOT / widest.group(1)
            if path.exists():
                actual = _webp_size(path)
                if actual and actual != (int(declared_w), int(declared_h)):
                    fail(f"{page}: {path.name} is {actual[0]}x{actual[1]} but the "
                         f"tag declares {declared_w}x{declared_h} — causes layout shift")


def check_landing_bands():
    src = read("index.html")
    _check_figure_contract("index.html", src)

    strip = re.search(r'<section class="band shots".*?</section>', src, re.S)
    if not strip:
        fail("index.html: missing proof strip section")
    else:
        n = len(FIG.findall(strip.group(0)))
        if n != 3:
            fail(f"proof strip: expected 3 screenshots, found {n}")
        for slug in ("requirements-editor", "modelica-sim", "gsn"):
            if slug not in strip.group(0):
                fail(f"proof strip: missing {slug}")

    caps = re.search(r'<ul class="grid-9">(.*?)</ul>', src, re.S)
    if not caps:
        fail("index.html: missing capabilities grid (ul.grid-9)")
    elif caps.group(1).count("<li") != 9:
        fail(f"capabilities grid: expected 9 items, found {caps.group(1).count('<li')}")

    langs = re.search(r'<section class="band band--sand langs".*?</section>', src, re.S)
    if not langs:
        fail("index.html: missing languages band")
    else:
        for lang in ("SysML v2", "Ecore", "GSN 3.0", "CAE", "Modelica",
                     "DSL", "CSP", "Dafny", "Isabelle"):
            if lang not in langs.group(0):
                fail(f"languages band: missing {lang!r}")
    if 'id="standards"' not in src:
        fail("index.html: missing #standards anchor for the nav")


# --- capability matrix -----------------------------------------------------

# Compared by tool category, never by product. A cell-by-cell vendor table went
# stale within a year: SysML v2 shipped across CATIA Magic/Cameo 2026x, IBM
# Rhapsody SE, Siemens Systems Modeler and Sparx Trechoro, which falsified four
# cells and the "only one with all eight" claim built on them.
VENDOR_NAMES = ["MagicDraw", "Cameo", "Simcenter", "Ansys", "Enterprise Architect",
                "Rhapsody", "Capella", "OSATE", "OpenModelica", "Simulink",
                "Sparx", "Trechoro", "Siemens", "Dassault"]

RETRACTED_CLAIMS = ["covers all eight", "all eight criteria", "the only one that",
                    "the only MBSE", "the only platform", "they don't have at all"]


def check_matrix():
    src = read("index.html")
    m = re.search(r'<table class="matrix">.*?</table>', src, re.S)
    if not m:
        fail("index.html: missing <table class=\"matrix\">")
        return
    table = m.group(0)

    if "<caption" not in table:
        fail("matrix: needs a <caption>")

    col_headers = re.findall(r'<th scope="col">([^<]*)</th>', table)
    if len(col_headers) != 5:
        fail(f"matrix: expected 5 scope=\"col\" headers, found {len(col_headers)}")
    elif col_headers[-1].strip() != "Principia":
        fail(f"matrix: last column must be Principia, got {col_headers[-1]!r}")

    rows = re.findall(r"<tr>.*?</tr>", table, re.S)
    data_rows = [r for r in rows if 'scope="row"' in r]
    if len(data_rows) != 7:
        fail(f"matrix: expected 7 capability rows, found {len(data_rows)}")
    for row in data_rows:
        cells = re.findall(r'<td>.*?</td>', row, re.S)
        if len(cells) != 5:
            fail(f"matrix: row has {len(cells)} cells, expected 5 — {row[:60]}")
        elif 'class="tick"' not in cells[-1]:
            fail("matrix: every capability must be ticked in the Principia column")

    for cell in re.findall(r'<span class="(?:tick|no)"[^>]*>.*?</span>', table, re.S):
        if 'aria-hidden="true"' not in cell:
            fail(f"matrix: symbol needs aria-hidden — {cell[:50]}")
    if table.count("visually-hidden") < 35:
        fail("matrix: every cell needs visually-hidden yes/no text")

    for vendor in VENDOR_NAMES:
        if vendor in table:
            fail(f"matrix: names the product {vendor!r} — the table compares tool "
                 f"categories, not products, because per-product cells go stale")

    for claim in RETRACTED_CLAIMS:
        if claim in src.lower():
            fail(f"index.html: retracted claim {claim!r} — verified false in "
                 f"August 2026 (see design spec §5)")

    scroll = re.search(r'<div class="matrix-scroll"[^>]*>', src)
    if not scroll:
        fail("index.html: matrix must sit inside div.matrix-scroll")
    else:
        for attr in ('tabindex="0"', 'role="region"', "aria-label"):
            if attr not in scroll.group(0):
                fail(f"matrix-scroll: missing {attr}")
        if 'id="matrix-scroll"' not in scroll.group(0):
            fail("matrix-scroll: missing id=\"matrix-scroll\" for the JS hint")
    if 'id="matrix-hint"' not in src:
        fail("index.html: missing #matrix-hint scroll affordance")

    css = read("assets/css/site.css")
    if "position: sticky" not in css or "left: 0" not in css:
        fail("site.css: matrix first column must be position: sticky; left: 0")
    # Regression guard: the cells' absolutely positioned .visually-hidden spans
    # escape .matrix-scroll unless it is a containing block, which pans the whole
    # document sideways on narrow screens.
    scroll_rule = re.search(r"\.matrix-scroll\s*\{[^}]*\}", css, re.S)
    if not scroll_rule:
        fail("site.css: missing .matrix-scroll rule")
    elif "position: relative" not in scroll_rule.group(0):
        fail("site.css: .matrix-scroll needs position: relative, or the hidden "
             "cell labels escape its overflow and the page scrolls horizontally")


# --- closing bands and copy rules -----------------------------------------

def check_closing_bands():
    src = read("index.html")

    formal = re.search(r'<section class="band band--dark formal".*?</section>', src, re.S)
    if not formal:
        fail("index.html: missing formal verification band")
    else:
        for term in ("CSP", "FDR", "Dafny", "Isabelle", "GSN"):
            if term not in formal.group(0):
                fail(f"formal band: missing {term!r}")

    splits = re.findall(r'<section class="band[^"]*\bsplit\b[^"]*">.*?</section>',
                        src, re.S)
    if len(splits) != 3:
        fail(f"expected 3 deep-dive sections, found {len(splits)}")
    else:
        ai = [s for s in splits if "AI4Engineering" in s]
        if not ai:
            fail("deep-dives: missing the AI4Engineering section")
        elif "<img" in ai[0]:
            fail("AI4Engineering deep-dive must stay text-only — no screenshot "
                 "exists for it (design spec §9.1)")
        for slug in ("sim-binding", "trace-navigate"):
            if slug not in " ".join(splits):
                fail(f"deep-dives: missing {slug} screenshot")

    teaser = re.search(r'<section class="band teaser".*?</section>', src, re.S)
    if not teaser:
        fail("index.html: missing case-study teaser")
    elif "case-study.html" not in teaser.group(0):
        fail("teaser: must link to case-study.html")

    contact = re.search(r'<section class="band band--sand contact".*?</section>', src, re.S)
    if not contact:
        fail("index.html: missing contact band")
    else:
        body = contact.group(0)
        if "mailto:r.wei5@lancaster.ac.uk" not in body:
            fail("contact: missing the pilot enquiry mailto")
        if "github.com/wrwei" not in body:
            fail("contact: should link github.com/wrwei")


FORBIDDEN = {
    "UKAEA": "third party must not be named (design spec §6)",
    "Lancaster University": "institutional affiliation must not be claimed",
    "satellite": "erroneous deck caption, the subject is the ADS (design spec §6)",
    "Satellite": "erroneous deck caption, the subject is the ADS (design spec §6)",
}
PRICING_WORDS = ["per seat", "per-seat", "Pricing", "Sign up", "Free trial",
                 "Start free"]


def check_copy_rules():
    for name, src in pages():
        for word, why in FORBIDDEN.items():
            if word in src:
                fail(f"{name}: contains {word!r} — {why}")
        for word in PRICING_WORDS:
            if word in src:
                fail(f"{name}: contains {word!r} — the site is pre-commercial, "
                     f"no pricing or signup (design spec §1)")


# --- case study ------------------------------------------------------------

PHASES = ["Home and project management", "Requirements", "System design",
          "Module design", "Implementation", "Integration", "Digital twin",
          "Trace links", "Digital thread"]


def check_case_study():
    src = read("case-study.html")
    _check_figure_contract("case-study.html", src)

    for phase in PHASES:
        if phase not in src:
            fail(f"case-study.html: missing phase heading {phase!r}")
    # Match the class token exactly — "phase-intro" must not count as "phase".
    sections = [c for c in re.findall(r'<section class="([^"]*)"', src)
                if "phase" in c.split()]
    if len(sections) != 9:
        fail(f"case-study.html: expected 9 phase sections, found {len(sections)}")

    # Real screenshots only: not the nav mark, not the lightbox's own <img>.
    screenshots = [f for f in FIG.findall(src)
                   if "logo.svg" not in f and 'id="lightbox-img"' not in f]
    if len(screenshots) != 24:
        fail(f"case-study.html: expected 24 screenshots, found {len(screenshots)}")
    for tag in screenshots:
        if "data-lightbox" not in tag:
            fail(f"case-study.html: screenshot needs data-lightbox — {tag[:70]}…")

    if "fusion fuel cycle" not in src:
        fail("case-study.html: should describe the subject as an atmosphere "
             "detritiation system in a fusion fuel cycle")
    if 'id="lightbox"' not in src:
        fail("case-study.html: missing <dialog id=\"lightbox\">")


# --- behaviour -------------------------------------------------------------

def check_js():
    js = read("assets/js/site.js")
    lines = [ln for ln in js.splitlines() if ln.strip()]
    if len(lines) > 80:
        fail(f"site.js has {len(lines)} non-blank lines, budget is 80")
    for banned in ("import ", "require(", "http://", "https://", "cdn"):
        if banned in js:
            fail(f"site.js must have no external dependencies, found {banned!r}")
    for needed in ("nav-toggle", "nav-links", "matrix-hint", "data-lightbox",
                   "showModal", "aria-expanded"):
        if needed not in js:
            fail(f"site.js: missing {needed!r} wiring")
    for name, src in pages():
        if 'src="assets/js/site.js" defer' not in src:
            fail(f"{name}: site.js must be loaded with defer")


def check_readme():
    readme = read("README.md")
    for topic in ("build-images.sh", "nav:start", "Pages", "check-site.py"):
        if topic not in readme:
            fail(f"README.md: should document {topic}")


CHECKS = [
    check_well_formed,
    check_head,
    check_structured_data,
    check_skip_link,
    check_paths_relative,
    check_refs_exist,
    check_sitemap_and_robots,
    check_tokens,
    check_no_stray_hex,
    check_shared_blocks,
    check_nav_contract,
    check_images,
    check_hero,
    check_landing_bands,
    check_matrix,
    check_closing_bands,
    check_copy_rules,
    check_case_study,
    check_js,
    check_readme,
]


def main():
    for check in CHECKS:
        try:
            check()
        except FileNotFoundError as exc:
            fail(f"{check.__name__}: missing file {exc.filename}")
    if _failures:
        print(f"FAIL — {len(_failures)} problem(s):")
        for msg in _failures:
            print(f"  • {msg}")
        return 1
    print(f"PASS — {len(CHECKS)} check group(s), no problems found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
