# Principia Marketing Site — Design

**Date:** 2026-08-09
**Repo:** `github.com/wrwei/Principia` (this repo, emptied of its 2025 prototype)
**Live at:** `https://wrwei.github.io/Principia/`
**Source material:** `Principia_UKAEA.pptx` (48 slides), `/Users/ranwei/Git/Principia_release`

## 1. Purpose

A two-page advertising site for Principia, a browser-based multi-domain MBSE and
assurance platform. The product itself lives in `Principia_release`; this repo hosts
only the site.

Primary audience is **commercial prospects** — engineering managers in aerospace,
defence, nuclear and automotive who are evaluating MBSE tooling and already know what
MBSE is. Investors and the academic/research community are served as secondary
audiences without their own pages: the contact block and footer carry the pilot
enquiry and the GitHub links.

Principia is **pre-commercial**. It is positioned as a mature prototype seeking pilot
deployments and design partners. There is no pricing, no signup, and no hosted trial
anywhere on the site. The single call to action is a pilot / walkthrough enquiry by
email.

Success criteria:

- A domain-literate visitor understands the differentiator (one continuous digital
  thread) within one screen, without scrolling.
- Every competitive claim survives a knowledgeable buyer checking it.
- The site loads fast enough that first paint waits on no image.
- Nothing on the site overstates what the platform does, and nothing names a third
  party without permission.

## 2. Scope

**In scope:** two hand-written static pages, one stylesheet, one small script, a
by-hand image conversion script, and the assets they need.

**Out of scope:** documentation hosting, a blog, pricing, any form backend, analytics,
a third page for research/academia, and any change to `Principia_release`.

## 3. Decisions

| Decision | Choice | Why |
|---|---|---|
| Stack | Hand-written static HTML/CSS/JS, no build | Two pages don't justify a toolchain; nothing to rot; anyone can edit it |
| Hosting | GitHub Pages, `main` / root | No Action, no build step |
| Domain | `wrwei.github.io/Principia` for now | Relative paths mean a custom domain later is a `CNAME` file and nothing else |
| Pages | `index.html` + `case-study.html` | ~90% of the deck's persuasive weight, minimal duplication |
| Hero | Direction C — thread diagram, inline SVG | States the one thing no competitor can copy; zero image payload |
| Feature status | All deck capabilities presented as shipped | Confirmed by the user; the release repo's docs are stale (see §9) |
| Comparison | By tool **category**, not by product | A per-vendor cell table was falsified within a year — see §5 and §9.5 |
| Formal verification | Its own band after the comparison | The strongest differentiator, and stated without an absolute claim about competitors |
| Third-party names | UKAEA is **not** named | No confirmed permission; implies endorsement |
| Institutional affiliation | Not claimed anywhere | User instruction; only the contact email carries the domain |
| Colour scheme | Light only, `color-scheme: light` | The warm cream identity *is* the brand; a dark variant doubles CSS for a brochure |
| Fonts | System stack, no webfont | Zero external requests, no FOUT |

## 4. Design tokens

Palette taken from the product's own UI so site and app read as one thing — warm
cream and brown, deliberately not generic SaaS blue. Every foreground/background pair
was measured, not eyeballed.

```
--cream       #FAF8F5   page background
--sand        #F3ECE3   alternating band background
--card        #FFFFFF   cards, diagram nodes
--line        #E7DED4   borders, rules
--dark        #2C2420   dark band / twin node
--ink         #221D19   body text            15.75:1 on cream
--ink-2       #6B6058   secondary text        5.76:1 on cream
--brown       #8A6A55   primary accent        4.64:1 on cream
--brown-dark  #6E5142   accent text           6.79:1 on cream
--tick        #3D6E49   matrix ticks          5.62:1 on cream
```

White on `--brown` is 4.91:1; cream `#F6F1EA` on `--dark` is 13.54:1. All pairs clear
WCAG AA for body text.

**Correction on the source material:** the deck's tick green `#4E8A5E` measures
3.87:1 on cream, which fails AA for body text. Darkened to `#3D6E49`.

Fluid type scale via `clamp()`, no media queries needed for type:

```
headline   clamp(2.5rem, 1.6rem + 4.2vw, 4rem)     40px → 64px
section h2 clamp(1.75rem, 1.3rem + 2vw, 2.5rem)    28px → 40px
body       clamp(1rem, 0.95rem + 0.25vw, 1.1875rem) 16px → 19px
nav / UI   0.9375rem                                15px
eyebrow    0.78rem, 2.4px tracking, uppercase
```

Spacing on a 4px base; radii 8/10/12px; one shadow token for screenshot framing.
Container max-width 1200px, prose max-width 68ch.

## 5. Landing page (`index.html`)

Eleven bands. Sources cited as deck slide numbers.

| # | Band | Source | Content |
|---|---|---|---|
| 1 | Sticky nav | — | Logo, Platform / Case study / Standards, "Book a walkthrough" |
| 2 | Hero | new | Eyebrow "One continuous digital thread"; h1 "Change a requirement. Watch it ripple to the twin."; inline SVG thread diagram; "Arrange a pilot" + "See the full walkthrough"; stat row |
| 3 | Proof strip | s24, s30, s35 | Three screenshots: Model / Simulate / Assure |
| 4 | The problem | s4, s6 | Document-centric SE compressed to one screen: no standardisation → information silos → untraceable change |
| 5 | Nine capabilities | s14 | 3×3 grid, one line each |
| 6 | Nine languages | s15 | Two groups — Modelling (6) and Formal (3) |
| 7 | Capability matrix | s12 | 10 tools × 8 criteria, Principia row highlighted, last |
| 8 | Formal verification | s34, s37 | Its own band: proof → evidence → assurance argument |
| 9 | Three deep-dives | s42, s41, s18 | Alternating text/screenshot rows |
| 10 | Case study teaser | s21, s22 | Two screenshots, link through |
| 11 | Contact + footer | s48 | Pilot enquiry, GitHub, proprietary notice |

### Hero diagram (band 2)

Inline SVG, `viewBox="0 0 780 208"`, six stages left to right:

```
Requirements → Architecture → Simulation → Assurance →  Verification  → Digital twin
satisfy·derive  parts·ports    Modelica·FMU  GSN·CAE   Dafny·FDR·Isabelle  live telemetry
```

The last node is `--dark` filled; the rest are white cards with a brown left rule.
Solid arrows connect adjacent stages; three dashed arcs labelled "trace link" and
"evidence link" leap non-adjacent stages, showing that the thread is a graph and not
a pipeline. Labels at 13px within the viewBox so they render ~16px at container
width. No raster asset, so first paint waits on nothing.

The Verification node's sublabel reads "Dafny · Isabelle" rather than naming all
three provers: at 11px in a 110-unit box, "Dafny · FDR · Isabelle" overflows into the
adjacent node. CSP/FDR is named in full in the languages band, the formal
verification band, and the mobile thread below.

**Below 820px the SVG is replaced, not scaled.** Squeezed into ~330px its labels
render at roughly 5px. An `<ol class="thread">` carrying the same six stages and
sublabels is shown instead, as stacked cards with a brown left rule and a `--dark`
terminal node. Only one of the two is ever displayed, so assistive technology never
sees duplicate content.

### Stat row (band 2)

`95+` SysML v2 meta types · `9` languages, one model · `8.31M` lines of code (s47).

### The problem (band 4)

The only MBSE-101 content retained, compressed from six slides to one band. Slides
5, 7 and 8 (what is MBSE, three pillars, NASA/Boeing/Siemens practice) are dropped
entirely — a buyer in this market does not need the INCOSE definition, but does
respond to their own pain being named. Slides 10–11 survive only as matrix rows.

### Nine capabilities (band 5)

From s14: B/S SaaS platform · full SysML v2 · V-model full lifecycle · deep model
management (Epsilon) · real-time collaboration · executable trace links ·
AI4Engineering · digital thread & twin · SysML–simulation binding.

### Nine languages (band 6)

| Modelling (6) | Formal (3) |
|---|---|
| SysML v2 — 95+ meta types, ~82-file standard library, bidirectional graphical/textual | CSP — CSPm, refinement-checked by FDR |
| Ecore/EMF — metamodel editor, auto-generated editors | Dafny — proof obligations |
| GSN 3.0 | Isabelle/HOL — Isabelle2023-CyPhyAssure build |
| CAE 1.0 / SACM | |
| Modelica — OpenModelica + FMU co-simulation | |
| Custom DSL — metamodel in, Vue 3 editor out | |

Verified in the release repo rather than taken from the deck:
`frontend/src/api/formalModelApi.ts:15` declares
`FormalDomain = 'dafny' | 'fdr' | 'isabelle'`; Monaco registers `cspm`, `dafny` and
`isabelle`; `server/formal-tools.json.example` wires all three tools; and
`server/seed/ads/` carries seeded Dafny and FDR models.

### Comparison table (band 7)

**The deck's ten-product, eight-criteria matrix (s12) is not used.** It was verified
in August 2026 and found materially out of date — see §9.5. It is replaced by a
comparison across the four *categories* of tool a team would otherwise buy.

Columns: Architecture tool · Simulation tool · Assurance tool · Proof assistant ·
**Principia** (last, highlighted, the arrival point). Rows:

| Capability | Arch | Sim | Assur | Proof | Principia |
|---|---|---|---|---|---|
| SysML v2 system model | ✔ | — | — | — | ✔ |
| Modelica and FMU simulation | — | ✔ | — | — | ✔ |
| GSN, CAE and SACM argument | — | — | ✔ | — | ✔ |
| CSP, Dafny and Isabelle proof | — | — | — | ✔ | ✔ |
| SysML parameters bound to simulation variables | — | — | — | — | ✔ |
| Trace links spanning all four domains | — | — | — | — | ✔ |
| Proof results re-run as assurance evidence | — | — | — | — | ✔ |

The top four rows concede each category its own strength. The bottom three are
cross-cutting, and a single-category tool cannot satisfy them by construction — which
is why this framing stays true as vendors ship features. A closing note states that
the comparison is by category precisely because per-product cells go stale.

No product is named anywhere in the table, and a checker assertion fails the build if
one reappears, or if any of the retracted absolute claims ("covers all eight", "the
only platform", "they don't have at all") returns to the page.

Placed mid-page deliberately: arriving after bands 3–6 it summarises things already
shown.

**`.matrix-scroll` must also be `position: relative`.** Each cell carries an
absolutely positioned `.visually-hidden` span; without a positioned ancestor those
resolve against the initial containing block, escape the container's `overflow`
entirely, and drag the document ~370px wide — the page then pans sideways on a phone
even though every visible element fits. `clip:` hides painting but does not remove an
element from overflow. Verified with `scrollTo(9999)` returning `scrollX=0`, and
guarded by a checker assertion.

Implementation: a real `<table>` with `<caption>`, `<th scope="col">` and
`<th scope="row">`, inside `.table-scroll { overflow-x: auto }` that is
`tabindex="0"`, `role="region"` and `aria-label`-ed so keyboard users can scroll it.
The tool-name column is `position: sticky; left: 0` on an opaque background. Ticks are
`<span aria-hidden="true">✔</span>` plus visually-hidden "supported" / "not
supported" text — otherwise a screen reader meets a wall of ambiguous dashes. A
right-edge fade plus a "scroll →" hint that JS removes on first scroll.

### Formal verification (band 8)

The strongest story on the site and absent from every competitor in band 7. Trace and
failures refinement checked in FDR, proof obligations discharged in Dafny, theorems in
Isabelle — and the results land as evidence attached to GSN Solution nodes, which can
be re-run in one click and marked sound or problematic (s34, s37). A closed loop from
machine-checked proof to certifiable safety argument.

### Three deep-dives (band 9)

Alternating text/screenshot rows:

1. **SysML ↔ simulation binding** (s42) — one-to-one parameter binding between SysML
   elements and OpenModelica/FMU variables with one-click sync.
2. **Executable trace links and change impact** (s41, s43) — links open the target
   editor directly; a requirement change identifies affected design, simulation and
   argument.
3. **AI4Engineering** (s18) — multi-agent LLM integration, requirements to model
   generation. **Text-only, no screenshot** (see §9).

## 6. Case study page (`case-study.html`)

The ADS walkthrough in the deck's own phase order, with its "Highlights" bullets as
captions. Twenty-five screenshots are available (§7); **24 are used** — s45
(`digital-thread-3`) is dropped because it repeats s43–s44's highlights verbatim.
Nine phases:

1. Home and project management (s21, s22)
2. Requirements (s23, s24, s25)
3. System design, incl. Epsilon analysis (s26, s27, s28)
4. Module design — state machine, Modelica, FMU, FMEA (s29–s32)
5. Implementation — Java, formal verification (s33, s34)
6. Integration — GSN, CAE, evidence auto-run (s35, s36, s37)
7. Digital twin (s38, s39)
8. Trace links and simulation binding (s40, s41, s42)
9. Digital thread (s43, s44, s45)

**Naming:** the subject is described as "an atmosphere detritiation system for a
fusion fuel cycle". UKAEA is not named anywhere on the site.

**Caption correction:** s38–s39 highlights read "Satellite 3D model bound to SysML",
but the deck covers the ADS only. Captioned as the ADS 3D asset bound to the SysML
model; the "satellite" wording is dropped.

## 7. Assets and image pipeline

Screenshots are extracted from the deck (`ppt/media/imageN.png`, mostly
1859×1169). A committed `tools/build-images.sh`, run by hand — not in CI, since this
stays a no-build site — produces two WebP widths per shot:

```
cwebp -q 78 -resize 1600 0  →  assets/img/shots/<slug>-1600.webp   ~120–200KB
cwebp -q 78 -resize 900 0   →  assets/img/shots/<slug>-900.webp    ~50–80KB
```

`cwebp` is present on the build machine; ImageMagick is not and is not required.
Source PNGs are **not** committed — they live in the deck.

Slide-to-slug inventory:

| Slide | Deck image | Slug | Used on |
|---|---|---|---|
| 21 | image17 | `dashboard` | landing (teaser), case study |
| 22 | image18 | `project-vmodel` | landing (teaser), case study |
| 23 | image19 | `model-create` | case study |
| 24 | image20 | `requirements-editor` | landing (proof), case study |
| 25 | image21 | `phase-complete` | case study |
| 26 | image22 | `design-create` | case study |
| 27 | image23 | `sysml-graphical-textual` | case study |
| 28 | image24 | `epsilon-analysis` | case study |
| 29 | image25 | `state-machine` | case study |
| 30 | image26 | `modelica-sim` | landing (proof), case study |
| 31 | image27 | `fmu-runtime` | case study |
| 32 | image28 | `fmea` | case study |
| 33 | image29 | `java-impl` | case study |
| 34 | image30 | `formal-verification` | landing (band 8), case study |
| 35 | image31 | `gsn` | landing (proof), case study |
| 36 | image32 | `cae` | case study |
| 37 | image33 | `gsn-evidence-run` | landing (band 8), case study |
| 38 | image34 | `twin-3d` | case study |
| 39 | image35 | `twin-dashboard` | case study |
| 40 | image36 | `trace-panel` | case study |
| 41 | image37 | `trace-navigate` | landing (deep-dive 2), case study |
| 42 | image38 | `sim-binding` | landing (deep-dive 1), case study |
| 43 | image39 | `digital-thread` | case study |
| 44 | image40 | `digital-thread-2` | case study |
| 45 | image41 | `digital-thread-3` | case study |

Every `<img>` carries explicit `width`/`height` to prevent layout shift, plus
`loading="lazy"` and `decoding="async"` below the fold. The landing page ships nine
screenshots; the case study 24, all lazy. Declared dimensions must match the actual
file per image — 24 of the 25 are 1600×1007 but `cae` is 1600×988, so a single
hard-coded height would cause layout shift. The checker parses each WebP header and
compares.

Logo: the product's rounded-square "P" mark redrawn as `assets/img/logo.svg`
(brown fill, cream glyph) — no logo asset exists in either repo, only the mark inside
screenshots. Favicon derived from the same SVG. `og-card.png` at 1200×630, composed
from the thread diagram plus the mark.

## 8. Behaviour, discoverability, deployment

`assets/js/site.js`, under 80 lines, no dependencies:

1. Mobile nav toggle.
2. Case-study screenshot lightbox using native `<dialog>` — Esc and backdrop-close
   come free.
3. Removal of the matrix scroll hint on first scroll.

No scroll-jacking and no animation library. The few CSS transitions sit behind
`prefers-reduced-motion`.

Discoverability: per-page `<title>` and description; canonical
`https://wrwei.github.io/Principia/`; Open Graph and Twitter card against
`og-card.png`; JSON-LD `SoftwareApplication` on the landing page listing name, url,
description and featureList, with no `offers` or price since the site is
pre-commercial; hand-written `robots.txt` and a two-URL
`sitemap.xml`. Skip link, one `<h1>` per page, semantic landmarks.

Deployment: GitHub Pages, **Settings → Pages → Deploy from a branch → main /
(root)** — a manual one-off by the repo owner. `.nojekyll` present so no filename is
ever swallowed by Jekyll.

**Accepted cost:** without templating, nav and footer are duplicated across two
pages. At two pages this is cheaper than a toolchain. Both blocks are kept
byte-identical so an edit is a copy-paste, and the README says so. Four or five pages
would be the moment to revisit Astro.

## 9. Known gaps and follow-ups

1. **No AI4Engineering screenshot exists.** Slide 18 carries only icons, not UI. The
   AI4Engineering deep-dive (band 9, item 3) is text-only until a screenshot is
   supplied. It is not omitted, because AI copilot is a ticked column in band 7 and
   the matrix must not claim something the page never shows.
2. **`Principia_release/docs/PRINCIPIA_OVERVIEW.md` is stale.** It lists FMEA, FTA,
   digital thread, digital twin and formal verification under "Planned Features",
   while the deck shows all of them working and the user confirms they ship. That doc
   should be corrected in the other repo. Out of scope here, but a public site
   contradicting the project's own docs is a credibility risk if a prospect finds
   both.
3. **Repo state.** The 2025 prototype (139 files) is staged for deletion but not yet
   committed; the pre-cleanup state is tagged `prototype-archive` (`b9928ee`).
   Committing that removal is the first implementation step.
4. **`.superpowers/` and `.DS_Store`** are already git-ignored. `Principia_UKAEA.pptx`
   sits in the repo root and should **not** be committed — it names a third party and
   is the private source material. Add it to `.gitignore` or move it out.
5. **The deck's competitive matrix was verified and retired.** Checked against vendor
   documentation in August 2026, four of nine competitor rows had a wrong SysML v2
   cell, and the claim built on them did not hold:

   - **CATIA Magic / Cameo** — SysML v2 ships in the 2026x release with two-way
     text↔diagram sync, in the M2E/M3E configurations (not Cameo Systems Modeler
     Architect or MagicDraw + SysML plugin).
   - **IBM Rhapsody Systems Engineering 1.8** (GA 9 July 2026) — cloud-native and
     browser-based with SysML v2 graphical editors, so both its "B/S architecture"
     and "SysML v2" cells were wrong.
   - **Siemens Systems Modeler for SysML v2** — powered by Rhapsody SE, in the
     Xcelerator portfolio with Teamcenter integration.
   - **Sparx Enterprise Architect / Trechoro** — full SysML v2, KerML-native,
     textual and graphical.

   Consequences: "the only MBSE platform meeting all eight criteria" is false;
   bidirectional graphical/textual SysML v2 sync is no longer distinctive; and the
   remaining ~70 cells were never verified. The table was replaced rather than
   corrected (§5). Principia's own capabilities are unaffected — only the claims
   about other products were wrong.
