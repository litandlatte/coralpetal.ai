#!/usr/bin/env bash
# Review the site locally before releasing it.
#   scripts/preview.sh            → runs the checks, builds production, serves http://localhost:8000
#   scripts/preview.sh 8080       → same, on another port
# Ctrl+C to stop. Nothing is deployed.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${1:-8000}"
OUT="$(mktemp -d)/coralpetal-preview"

python3 scripts/check_site.py site
GITHUB_SHA="preview" bash scripts/build_env.sh prod "$OUT" >/dev/null

echo
echo "  Preview: http://localhost:$PORT"
echo "  (this is exactly what Production would get; Ctrl+C to stop)"
echo
( sleep 1; open "http://localhost:$PORT" 2>/dev/null || true ) &
python3 -m http.server "$PORT" --directory "$OUT" --bind 127.0.0.1
