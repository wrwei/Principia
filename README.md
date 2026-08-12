# Principia — marketing site

The advertising site for Principia, a browser-based MBSE and assurance platform.
Published at <https://principia-modelling.com/>.

The platform itself lives in a separate repository; this one contains only the
site. The pre-2026 prototype that used to live here is preserved at the
`prototype-archive` tag.

## Layout

    index.html          landing page
    case-study.html     atmosphere detritiation system walkthrough
    assets/css/         tokens.css (design tokens) + site.css (components)
    assets/js/site.js   nav, lightbox, matrix hint
    assets/img/shots/   committed WebP screenshots, two widths each
    tools/              image pipeline, OG card generator, verification suite
    docs/superpowers/   design spec and implementation plan

## No build step

There is deliberately no toolchain — no Node, no bundler, no CI pipeline. Edit
the HTML and CSS directly and commit. Generated assets are committed because
nothing runs in CI.

Two rules keep it that way:

- `assets/css/tokens.css` is the only file allowed to contain hex colours.
  Everything else uses `var(--token)`.
- No external requests. No webfonts, CDNs, analytics or third-party scripts.

## Verify before committing

    python3 tools/check-site.py

This is the test suite. It checks tag balance, page metadata, relative paths,
that every referenced file exists, colour contrast against WCAG AA, declared
image dimensions against the actual files, the image size budget, matrix
accessibility, the JS budget, and the copy rules. It must print PASS.

## Regenerating screenshots

    ./tools/build-images.sh /path/to/deck.pptx
    python3 tools/make-og-card.py

Requires `cwebp` (`brew install webp`) and Pillow. The source deck is private
and git-ignored — never commit it.

## Editing the nav or footer

Both pages carry byte-identical blocks between the `<!-- nav:start -->` /
`<!-- nav:end -->` and `<!-- footer:start -->` / `<!-- footer:end -->` markers.
Change one, copy it to the other; `check-site.py` fails if they diverge. This is
the accepted cost of having no templating. At four or five pages, revisit it.

## Deployment

GitHub Pages, **Settings → Pages → Deploy from a branch → `main` / `(root)`**.
Pushing to `main` publishes. `.nojekyll` stops Jekyll touching the files.

The site is served at **https://principia-modelling.com/** via the `CNAME` file at
the repo root. `wrwei.github.io/Principia/` 301-redirects to it.

### Changing the domain

Asset paths are relative throughout and need no attention, but **12 absolute URLs
do**, and `tools/check-site.py` asserts two of them. All of these must move together:

| File | Occurrences |
|---|---|
| `CNAME` | the hostname itself |
| `index.html` | 4 — canonical, `og:url`, `og:image`, JSON-LD `url` |
| `case-study.html` | 3 — canonical, `og:url`, `og:image` |
| `sitemap.xml` | 2 |
| `robots.txt` | 1 — the `Sitemap:` line |
| `tools/check-site.py` | 1 — `CANONICAL_BASE` |
| `README.md` | 1 — the link above |

DNS for the current domain: four apex `A` records to `185.199.108.153`,
`185.199.109.153`, `185.199.110.153`, `185.199.111.153`, and a `www` `CNAME` to
`wrwei.github.io.` — GitHub then redirects `www` to the apex.
