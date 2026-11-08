#!/usr/bin/env bash
# Build the deployable copy of academy/ (academy.coralpetal.ai).
#   scripts/build_academy.sh <out_dir>
# Adds version.json (site + commit + build time) so the live academy can be checked
# against the commit that was released. <out_dir> must not exist yet (CI and preview
# use fresh paths), so nothing is ever overwritten or removed.
set -euo pipefail

OUT="$1"
[ ! -e "$OUT" ] || { echo "$OUT already exists; pass a new path" >&2; exit 2; }
cp -R academy "$OUT"

SHA="${GITHUB_SHA:-local}"
printf '{"site":"academy","commit":"%s","built":"%s"}\n' "${SHA:0:7}" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/version.json"

echo "built academy → $OUT"
