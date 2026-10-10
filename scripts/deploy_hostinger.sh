#!/usr/bin/env bash
# Deploy the production build to Hostinger over SSH (rsync).
#   scripts/deploy_hostinger.sh <built_dir>
# Needs env: HOSTINGER_HOST, HOSTINGER_PORT, HOSTINGER_USER, and an SSH key at ~/.ssh/id
# with the server's pinned host keys in ~/.ssh/known_hosts.
#
# SAFETY: the same hosting account also holds litandlatte.com. The target path is
# computed here (never passed in) and checked against an allow-list before rsync runs.
set -euo pipefail

SRC="$1"
TARGET="/home/${HOSTINGER_USER}/domains/coralpetal.ai/public_html"

# Guard: exactly the coralpetal.ai docroot, nothing else.
if ! [[ "$TARGET" =~ ^/home/u[0-9]+/domains/coralpetal\.ai/public_html$ ]]; then
  echo "REFUSING to deploy to unexpected path: $TARGET" >&2; exit 3
fi
[ -f "$SRC/index.html" ] || { echo "no index.html in $SRC" >&2; exit 4; }

SSH="ssh -i $HOME/.ssh/id -p ${HOSTINGER_PORT} -o StrictHostKeyChecking=yes -o BatchMode=yes"
REMOTE="${HOSTINGER_USER}@${HOSTINGER_HOST}"

# The remote folder must already exist (created by hPanel); never create paths blindly.
$SSH "$REMOTE" "test -d '$TARGET'" || { echo "target missing on server: $TARGET" >&2; exit 5; }

# Subdomains created in hPanel live in folders INSIDE this docroot. --delete must never
# touch them. Add a name here whenever a new subdomain is created.
SUBDOMAIN_FOLDERS=(academy career)
for d in "${SUBDOMAIN_FOLDERS[@]}"; do
  [ ! -e "$SRC/$d" ] || { echo "build must not contain /$d — it belongs to $d.coralpetal.ai" >&2; exit 6; }
done
EXCLUDES=(--exclude=/.well-known/)
for d in "${SUBDOMAIN_FOLDERS[@]}"; do EXCLUDES+=("--exclude=/$d/"); done

# --delete keeps the docroot an exact mirror of the build, except .well-known/
# (Hostinger SSL validation files) and the subdomain folders above.
rsync -rlz --checksum --delete --chmod=D755,F644 "${EXCLUDES[@]}" \
  -e "$SSH" "$SRC"/ "$REMOTE:$TARGET/"
echo "deployed prod → $TARGET"
