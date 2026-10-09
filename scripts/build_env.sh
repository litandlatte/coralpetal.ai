#!/usr/bin/env bash
# Build the deployable copy of site/.
#   scripts/build_env.sh prod <out_dir>
# Adds version.json (env + commit + build time) so the live site can be checked
# against the commit that was released.
set -euo pipefail

ENV="$1"; OUT="$2"
[ "$ENV" = prod ] || { echo "only 'prod' exists (dev/uat retired 2026-10-09)" >&2; exit 2; }

rm -rf "$OUT"
cp -R site "$OUT"

SHA="${GITHUB_SHA:-local}"
printf '{"env":"%s","commit":"%s","built":"%s"}\n' "$ENV" "${SHA:0:7}" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/version.json"

echo "built $ENV → $OUT"
