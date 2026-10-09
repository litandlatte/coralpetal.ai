#!/usr/bin/env bash
# Deploy a built environment to Hostinger over SSH (rsync).
#   scripts/deploy_hostinger.sh <dev|uat|prod> <built_dir>
# Needs env: HOSTINGER_HOST, HOSTINGER_PORT, HOSTINGER_USER, and an SSH key at ~/.ssh/id
# with the server's pinned host keys in ~/.ssh/known_hosts.
#
# SAFETY: the same hosting account also holds litandlatte.com. The target path is
# computed here (never passed in) and checked against an allow-list before rsync runs.
set -euo pipefail

ENV="$1"; SRC="$2"
BASE="/home/${HOSTINGER_USER}/domains/coralpetal.ai/public_html"

case "$ENV" in
  prod) TARGET="$BASE" ;;
  uat)  TARGET="$BASE/uat" ;;
  dev)  TARGET="$BASE/dev" ;;
  *) echo "unknown env: $ENV" >&2; exit 2 ;;
esac

# Guard: exactly one of the three coralpetal.ai docroots, nothing else.
if ! [[ "$TARGET" =~ ^/home/u[0-9]+/domains/coralpetal\.ai/public_html(/dev|/uat)?$ ]]; then
  echo "REFUSING to deploy to unexpected path: $TARGET" >&2; exit 3
fi
[ -f "$SRC/index.html" ] || { echo "no index.html in $SRC" >&2; exit 4; }

SSH="ssh -i $HOME/.ssh/id -p ${HOSTINGER_PORT} -o StrictHostKeyChecking=yes -o BatchMode=yes"
REMOTE="${HOSTINGER_USER}@${HOSTINGER_HOST}"

# The remote folder must already exist (created by hPanel); never create paths blindly.
$SSH "$REMOTE" "test -d '$TARGET'" || { echo "target missing on server: $TARGET" >&2; exit 5; }

# --delete keeps the docroot an exact mirror of the build, EXCEPT:
#   prod: the dev/ and uat/ subdomain folders that live inside it
#   all:  .well-known/ (Hostinger SSL validation)
EXCLUDES=(--exclude=/.well-known/)
if [ "$ENV" = prod ]; then
  EXCLUDES+=(--exclude=/dev/ --exclude=/uat/)
fi

rsync -rlz --checksum --delete --chmod=D755,F644 "${EXCLUDES[@]}" -e "$SSH" "$SRC"/ "$REMOTE:$TARGET/"
echo "deployed $ENV → $TARGET"
