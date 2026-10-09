# coralpetal.ai

Website for **The Coral Petal Company**: enterprise Agentic AI adoption.
Plain static HTML/CSS in `site/`. No framework, no build tooling beyond `scripts/`.

## Environments

| Env | Branch | Hosted in | URL | Deploys |
|---|---|---|---|---|
| Development | `dev` | `litandlatte/coralpetal-dev` (gh-pages) | dev.coralpetal.ai | automatically on push |
| UAT | `uat` | `litandlatte/coralpetal-uat` (gh-pages) | uat.coralpetal.ai | automatically on push |
| Production | `main` | this repo (gh-pages) | coralpetal.ai | on push, **after approval** in GitHub |

Dev and UAT show an environment banner, send `noindex`, and block crawlers in `robots.txt`.
Each build writes `version.json` (env + commit) so you can see what is deployed where.

## How a change ships

1. Commit to `dev` (or merge a feature branch into it) → live on Development.
2. Open a PR `dev → uat`, merge → live on UAT. Review it there.
3. Open a PR `uat → main`, merge → the production job waits → approve it under
   **Actions → the run → Review deployments** → live on coralpetal.ai.

`uat` and `main` are protected: changes arrive only by pull request, and the **Site checks**
job must pass.

## Checks

`scripts/check_site.py` runs on every push and PR: HTML structure, `<title>` and
meta description, image alt text, broken internal links and in-page anchors.

```
python3 scripts/check_site.py site
bash scripts/build_env.sh uat /tmp/out-uat     # preview any environment's build locally
```

## Custom domains

Repo variable `DOMAINS_LIVE` (`true`/unset) switches all three environments onto their
custom domains. DNS lives at Hostinger:

| Type | Name | Value |
|---|---|---|
| A | @ | 185.199.108.153 · 185.199.109.153 · 185.199.110.153 · 185.199.111.153 |
| CNAME | www | litandlatte.github.io |
| CNAME | dev | litandlatte.github.io |
| CNAME | uat | litandlatte.github.io |

## Secrets

`DEV_DEPLOY_KEY` and `UAT_DEPLOY_KEY` are SSH deploy keys with write access to the
dev/uat hosting repos. Production uses the built-in `GITHUB_TOKEN`.
