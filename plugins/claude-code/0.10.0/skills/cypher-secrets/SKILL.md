---
name: "cypher-secrets"
description: "How to read and register secrets in the product owner's Proton Pass \"Cypher\" vault (audited pass-cli). Use whenever any project needs an API key, token, password, credential or connection string, a .env needs a secret, or before inventing any other secret-handling approach."
---

# Cypher secrets

The product owner keeps every secret — for the cypher suite AND for any other
project — in one Proton Pass vault named `Cypher`. An audited `pass-cli`
session, run on the owner's infrastructure, logs every single read (who, what,
why, when — never the value) before forwarding it. That audit trail, plus
Proton's own agent monitor, is what makes it safe to let AI sessions fetch
secrets autonomously. Work with that design, not around it.

How to reach it (hosts, commands, recovery) is not in this skill: call
`knowledge {topic: "credentials"}`. It is owner-only; if it refuses you, report
the item that is missing or unreachable; do not hand anyone commands to run.

A secret's address is a triple, written `Cypher / <item> / <field>`
(vault / item title / field name).

## Hard rules

1. **Never put a secret value in git, in a committed file, or in a file that
   could be committed.** Rendered `.env` files live only on the target host and
   are gitignored. If a value ever lands in a repo, that is a security
   incident: tell the product owner immediately so they can rotate it.
2. **Never echo a secret value into the chat unless the product owner explicitly asks to
   see it.** Prefer piping the value directly into its destination (a file on
   the target host, a command's stdin, an env var of a process you start).
   Everything printed to the conversation lands in a transcript.
3. **Always read through the audited wrapper, never the bare binary.** The bare
   binary bypasses the audit log (`knowledge {topic: "credentials"}`).
4. **Always supply a real reason and caller** (see "Reading a secret") — an
   empty or lazy reason defeats the audit.
5. **No alternative secret stores.** Not Docker secrets, not SOPS, not
   HashiCorp Vault, not Kubernetes secrets, not values baked into images or
   Dockerfiles. Proton Pass is the single source of truth; everything else is
   a rendered, disposable copy.
6. **You create and update vault items yourself, through the gateway**
   (`vault_create`, `vault_update`, `vault_rotate`); the gateway audits every
   write and never returns a value. Never print a value you write. Deleting an
   item is ask-first (`vault_delete`).
7. **Never ask the product owner to run a command, rename an item or copy a
   value.** Read the real item fields yourself; the agent reads and injects
   through the gateway, and a missing credential is reported with the item to
   create.

## Namespacing — which keys belong to which project

This convention is **forward-only and fully backwards compatible**: it applies
to NEW entries for projects outside the cypher suite. Nothing that already
exists in the vault gets renamed — ever. Renaming an existing entry breaks
every consumer that fetches it by title, so never propose a rename sweep;
existing titles (whatever their shape) are correct by definition, and the
registries below are the source of truth for their exact spelling.

The cypher suite has its own established naming, owned by
`cypherops/secrets/README.md` — leave those entries exactly as they are and
follow that README when working inside the suite.

For everything else, one rule is enough to keep the vault legible: **prefix the
item title with the project's slug**, so anyone scanning the vault or the audit
log can see immediately which project a key belongs to:

```
<project>-<rest-of-name>
```

`<project>` is one lowercase word (`orqastudio`, `myblog`, …); the rest of the
name is whatever reads naturally, kebab-case recommended. Field names short and
lowercase: `key`, `token`, `secret`, `password`, `username`, `url`, `id`.

| Address | Meaning |
|---|---|
| `Cypher / orqastudio-openai-api / key` | OrqaStudio's OpenAI API key |
| `Cypher / myblog-cloudflare-deploy / token` | Deploy token for a blog project |
| `Cypher / shared-github-pat / token` | A key deliberately shared across projects |

Use the `shared-` prefix for credentials intentionally used by more than one
project — though prefer a per-project key when the provider allows it, so each
project can be rotated or revoked independently. Titles without a project
prefix are the cypher suite's territory: never create new ones from an
outside project.

When looking an item up, remember titles are matched as typed — some suite
items are Title-Case. If a read
comes back "not found", check the project's secret registry (below) for the
exact title rather than guessing variants.

## Reading a secret

Call `knowledge {topic: "credentials"}` for the paths that work in your
session (gateway tools or the suite's deploy-time rendering), the exact command shape, and how to batch several
values. Always give a real reason and caller so the audit is useful. Pipe the
value straight to its destination; never bring it into the chat.

## Registering a new secret

When a project needs a credential that doesn't exist yet, you create it:

1. **Pick the address** using the namespacing rules above, and check it doesn't
   collide with an existing entry (`vault_list`).
2. **Create the item** with `vault_create` (or change it with `vault_update` /
   `vault_rotate`). If the value comes from the product owner, they give it to
   the gateway, not to the chat; you never echo it.
3. **Verify** with an audited read (see `knowledge {topic: "credentials"}`) — a
   successful fetch proves the address is right before anything depends on it.
4. **Register it** in the owning project's secret index so future sessions can
   find it: a `secrets/README.md` (or a "Secrets" section in the project
   README) listing `Vault / Item / Field` and what uses it — same shape as
   `cypherops/secrets/README.md`. Never the value, only the address. For
   cypher-suite entries, the cypherops README row lands in the same PR as the
   code that consumes it.

## Troubleshooting and audit

A read that fails ("not found", an authentication error, a timeout, a wedged
container) has a fix per symptom in `knowledge {topic: "credentials"}`. Report
anything that persists to the product owner rather than force-recreating
anything. Every read is audited; write reasons and callers as if they will be
read in a review — because that is what they are for.
