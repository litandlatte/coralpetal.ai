#!/usr/bin/env bash
# Review a site locally before releasing it.
#   scripts/preview.sh                → main site: checks, production build, http://localhost:8000
#   scripts/preview.sh 8080           → main site on another port
#   scripts/preview.sh academy        → academy.coralpetal.ai: checks, build, http://localhost:8001
#   scripts/preview.sh academy 8081   → academy on another port
# Ctrl+C to stop. Nothing is deployed.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = academy ]; then
  PORT="${2:-8001}"
  OUT="$(mktemp -d)/academy-preview"
  python3 scripts/check_site.py academy
  python3 scripts/check_courses.py academy/courses.json
  GITHUB_SHA="preview" bash scripts/build_academy.sh "$OUT" >/dev/null
  WHAT="the academy (academy.coralpetal.ai)"
else
  PORT="${1:-8000}"
  OUT="$(mktemp -d)/coralpetal-preview"
  python3 scripts/check_site.py site
  GITHUB_SHA="preview" bash scripts/build_env.sh prod "$OUT" >/dev/null
  WHAT="the main site (coralpetal.ai)"
fi

echo
echo "  Preview of $WHAT: http://localhost:$PORT"
echo "  (this is exactly what would be deployed; Ctrl+C to stop)"
echo
( sleep 1; open "http://localhost:$PORT" 2>/dev/null || true ) &
python3 -m http.server "$PORT" --directory "$OUT" --bind 127.0.0.1
