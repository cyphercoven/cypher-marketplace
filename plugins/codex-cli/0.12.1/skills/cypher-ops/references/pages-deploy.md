# Cloudflare Pages deploy

PURPOSE: how a Cloudflare Pages project ships from a Forgejo source repo through
the `pages` job in cypherops' `.forgejo/workflows/ship.yaml` (engine
`scripts/deploy-pages.sh`). Load it from the `cypher-ops` core when deploying a
Pages site, adding a Pages project, or debugging a failed Pages deploy.

Rules:

- **One workflow, one engine.** The `pages` job in `ship.yaml` handles every
  Pages deploy for the account. Source repos are pure content: they hold no
  Cloudflare credential and no wrangler logic. (The old standalone
  `deploy-pages.yaml` workflow was retired; per-site config now lives in the
  script's `SITES` table and the dispatch input is just `pages_project`.)
- Auth is one Forgejo Actions secret holding a Pages-edit API token. The vault
  stays the canonical store; Forgejo holds the runtime copy. Which vault item and
  secret name: `knowledge {topic: "pages-deploy"}` — never print the value.
- The deploy runs wrangler with `--commit-dirty=false`, so an accidental
  dirty-tree deploy fails loudly. Keep it that way.
- Keep the `pages_project` choices an explicit enumeration: typo-tolerance comes
  from the list, not from free text.
- The Cloudflare account id is a workflow env var, not a secret; it is already
  public in the repo's inventory.

## One-time bootstrap

Done once per Forgejo repo that dispatches or holds the secret:

1. Read the token from the vault on the owner's machine (field per the knowledge
   topic) — the owner does this; an agent never fetches or echoes it.
2. Add it as a Forgejo Actions secret on the cypherops repo (Settings → Actions →
   Secrets). Forgejo masks it, so confirm only that the name appears in the list.
3. A repo that calls the workflow needs the secret in its **own** secret store;
   Forgejo does not pass secrets across dispatch boundaries.

## Day-to-day dispatch

Forgejo UI: cypherops → Actions → ship → Run workflow, set `pages_project`. Or
the API, with a Forgejo PAT in the `Authorization` header:

```
POST /api/v1/repos/<org>/cypherops/actions/workflows/ship.yaml/dispatches
{"ref": "main", "inputs": {"pages_project": "<name>"}}
```

The job clones the source, runs the site's build command, checks the dist
directory exists, installs wrangler, and runs `wrangler pages deploy`.

## Auto-deploy on push (optional)

A source repo can add a thin caller workflow on `push` to `main` that POSTs the
dispatch above with `{"inputs": {"pages_project": "<name>"}}`, using a PAT with
`write:repository` on cypherops stored as that repo's own secret. Mint that PAT
separately — do not reuse the deploy-runner's git credential.

## Adding a Pages project

1. Create the project in the Cloudflare dashboard (or OpenTofu).
2. Add its arm to the `SITES` table in `scripts/deploy-pages.sh` **and** to the
   `pages_project` choice list in `ship.yaml`.
3. Commit through the normal PR path (core §7).
4. Dispatch once with the new project to verify, then check the live site.

## Failure modes

| Symptom | Cause / fix |
|---|---|
| "secret not configured" | bootstrap not done — add the Actions secret |
| wrangler `Authentication error` | secret wrong or token revoked — the owner re-fetches and re-pastes |
| "dist not found after build" | the site's dist path does not match what the build emitted — fix the `SITES` entry |
| clone of the source ref fails | the branch/tag does not exist, or the runner cannot reach the forge — test from the runner |
| deploy succeeds, site empty | the build never populated the dist directory — add an explicit `ls` step before deploy |

Changing the token or any secret's value is a vault operation (load
**cypher-secrets**); this reference only tells you where it is consumed.
