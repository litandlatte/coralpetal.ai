#!/usr/bin/env bash
# Deploy the careers build to Hostinger over SSH (rsync).
#   scripts/deploy_careers.sh <built_dir>
# Needs env: HOSTINGER_HOST, HOSTINGER_PORT, HOSTINGER_USER, and an SSH key at ~/.ssh/id
# with the server's pinned host keys in ~/.ssh/known_hosts.
#
# SAFETY: the same hosting account also holds litandlatte.com, and hPanel nests the
# careers.coralpetal.ai folder INSIDE the coralpetal.ai docroot. The target path is
# computed here (never passed in) and must be exactly that careers folder: never the
# main docroot, never anything else.
set -euo pipefail

SRC="$1"
TARGET="/home/${HOSTINGER_USER}/domains/coralpetal.ai/public_html/careers"

# Guard: exactly the careers folder, nothing else.
if ! [[ "$TARGET" =~ ^/home/u[0-9]+/domains/coralpetal\.ai/public_html/careers$ ]]; then
  echo "REFUSING to deploy to unexpected path: $TARGET" >&2; exit 3
fi
[ -f "$SRC/index.html" ] || { echo "no index.html in $SRC" >&2; exit 4; }
[ -f "$SRC/version.json" ] || { echo "no version.json in $SRC (use scripts/build_careers.sh)" >&2; exit 4; }

SSH="ssh -i $HOME/.ssh/id -p ${HOSTINGER_PORT} -o StrictHostKeyChecking=yes -o BatchMode=yes"
REMOTE="${HOSTINGER_USER}@${HOSTINGER_HOST}"

# The folder must already exist (created by hPanel with the subdomain); never create it.
$SSH "$REMOTE" "test -d '$TARGET'" || { echo "target missing on server: $TARGET" >&2; exit 5; }

# First deploy only: the folder still holds Hostinger's placeholder page (no version.json).
# Move whatever is there to ~/retired/ instead of letting --delete remove it (never delete).
$SSH "$REMOTE" "set -e; T='$TARGET'
  if [ ! -f \"\$T/version.json\" ]; then
    R=\"\$HOME/retired/careers-\$(date +%Y-%m-%d-%H%M%S)\"; mkdir -p \"\$R\"
    find \"\$T\" -mindepth 1 -maxdepth 1 ! -name .well-known -exec mv {} \"\$R\"/ \;
    echo \"moved the placeholder content to \$R\"
  fi"

# --delete keeps the folder an exact mirror of the build, except .well-known/
# (Hostinger SSL validation files for the careers certificate).
rsync -rlz --checksum --delete --chmod=D755,F644 --exclude=/.well-known/ \
  -e "$SSH" "$SRC"/ "$REMOTE:$TARGET/"
echo "deployed careers → $TARGET"
