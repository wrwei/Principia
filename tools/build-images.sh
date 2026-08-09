#!/usr/bin/env bash
# Convert the source deck's screenshots into the two committed WebP widths.
#
# Run by hand — this project has no build step in CI, so the outputs are
# committed. Requires cwebp (brew install webp) and unzip.
#
#   ./tools/build-images.sh ~/Downloads/Principia_UKAEA.pptx
#
# The deck itself is git-ignored and must never be committed: it names a
# third party and is private source material.
set -euo pipefail

DECK="${1:-}"
[ -f "$DECK" ] || { echo "usage: $0 <path-to-deck.pptx>" >&2; exit 1; }
command -v cwebp >/dev/null || { echo "cwebp not found: brew install webp" >&2; exit 1; }

REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$REPO/assets/img/shots"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

unzip -q "$DECK" 'ppt/media/*' -d "$TMP"
mkdir -p "$OUT"

# deck image -> site slug. Slide numbers are in the design spec, §7.
MAP="
image17 dashboard
image18 project-vmodel
image19 model-create
image20 requirements-editor
image21 phase-complete
image22 design-create
image23 sysml-graphical-textual
image24 epsilon-analysis
image25 state-machine
image26 modelica-sim
image27 fmu-runtime
image28 fmea
image29 java-impl
image30 formal-verification
image31 gsn
image32 cae
image33 gsn-evidence-run
image34 twin-3d
image35 twin-dashboard
image36 trace-panel
image37 trace-navigate
image38 sim-binding
image39 digital-thread
image40 digital-thread-2
image41 digital-thread-3
"

count=0
while read -r src slug; do
  [ -n "${src:-}" ] || continue
  in="$TMP/ppt/media/$src.png"
  [ -f "$in" ] || { echo "missing $src.png in deck" >&2; exit 1; }
  cwebp -quiet -q 78 -resize 1600 0 "$in" -o "$OUT/$slug-1600.webp"
  cwebp -quiet -q 78 -resize 900 0  "$in" -o "$OUT/$slug-900.webp"
  count=$((count + 1))
done <<< "$MAP"

echo "converted $count screenshots into $OUT"
du -sh "$OUT"
