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


CHECKS = [
    check_well_formed,
    check_head,
    check_skip_link,
    check_paths_relative,
    check_refs_exist,
    check_sitemap_and_robots,
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
