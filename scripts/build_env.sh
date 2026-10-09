#!/usr/bin/env bash
# Build the deployable copy of site/ for one environment.
#   scripts/build_env.sh <dev|uat|prod> <out_dir> [custom_domain]
# dev/uat get a visible environment banner and are hidden from search engines.
set -euo pipefail

ENV="$1"; OUT="$2"; DOMAIN="${3:-}"

rm -rf "$OUT"
cp -R site "$OUT"
touch "$OUT/.nojekyll"

if [ -n "$DOMAIN" ]; then
  printf '%s\n' "$DOMAIN" > "$OUT/CNAME"
fi

SHA="${GITHUB_SHA:-local}"
printf '{"env":"%s","commit":"%s","built":"%s"}\n' "$ENV" "${SHA:0:7}" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/version.json"

if [ "$ENV" != "prod" ]; then
  LABEL=$(echo "$ENV" | tr '[:lower:]' '[:upper:]')
  printf 'User-agent: *\nDisallow: /\n' > "$OUT/robots.txt"
  rm -f "$OUT/sitemap.xml"
  BANNER="<div style=\"position:fixed;left:0;right:0;bottom:0;z-index:99;background:#0f172a;color:#fff;font:600 12px/1 system-ui,sans-serif;letter-spacing:.08em;text-align:center;padding:8px\">${LABEL} ENVIRONMENT · ${SHA:0:7} · not the live site</div>"
  for f in "$OUT"/*.html; do
    python3 - "$f" "$BANNER" <<'PY'
import sys
path, banner = sys.argv[1], sys.argv[2]
s = open(path, encoding="utf-8").read()
s = s.replace("<head>", '<head>\n  <meta name="robots" content="noindex, nofollow">', 1)
s = s.replace("</body>", banner + "\n</body>", 1)
open(path, "w", encoding="utf-8").write(s)
PY
  done
fi

echo "built $ENV → $OUT ${DOMAIN:+(domain $DOMAIN)}"
