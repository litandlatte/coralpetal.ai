# coralpetal.ai

Website for **The Coral Petal Company**: enterprise Agentic AI adoption.
Plain static HTML/CSS in `site/`. Hosted on **Hostinger** (Premium plan).

## How a change ships

1. Work on a branch (never directly on `main`).
2. **Review locally:** `scripts/preview.sh` runs the checks, builds exactly what Production
   would get, and opens http://localhost:8000.
3. Open a pull request into `main` → **Site checks** run.
4. Merge → the Production job **waits for Rohit's approval** (Actions → the run →
   Review deployments) → deploys to Hostinger → confirms https://coralpetal.ai serves the
   new commit (`/version.json`). The run fails if it does not.

`main` is protected: changes arrive only by pull request, and Site checks must pass.

## Checks

`scripts/check_site.py` — HTML structure, `<title>` and meta description, image alt text,
broken internal links and in-page anchors. Runs on every PR and before every deploy.

## Hosting and deploy

- Server folder: `~/domains/coralpetal.ai/public_html` (account `u574260001`, SSH port 65002).
- `scripts/deploy_hostinger.sh` mirrors the build there with rsync over SSH. It **refuses
  any other path** — `litandlatte.com` lives on the same hosting account.
- Secrets/variables: `HOSTINGER_SSH_KEY` (deploy key), `HOSTINGER_HOST`, `HOSTINGER_PORT`,
  `HOSTINGER_USER`, `HOSTINGER_KNOWN_HOSTS` (pinned server fingerprints).
- HTTPS: Hostinger's free SSL, forced in hPanel. `.htaccess` sends www → apex and serves `404.html`.

## History

Dev and UAT environments ran briefly on 2026-10-09 and were retired the same day in favour of
local review. Their server folders were moved (not deleted) to `~/retired/coralpetal.ai-2026-10-09/`.
