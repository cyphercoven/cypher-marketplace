# Capability bundles in practice

PURPOSE: how the capability-bundle model works at runtime — where bundles are
stored, how the gateway consults them on every tool call, what a denial looks
like, how a sub-agent's bundle inherits, and how to author one. Load it from the
`cypher-ops` core when adding a service's bundle, debugging a denied tool call,
or reasoning about a sub-agent's permissions.

Rules:

- Bundles are **subsets, not unions.** A child bundle (a sub-agent spawned by the
  orchestrator) can never hold more than its parent. The spawn handler enforces
  the subset check before issuing the child identity.
- The bundle is the contract; the SPIFFE SAN is the identity it attaches to. Both
  are needed.
- Every allow/deny emits an audit entry to the separate audit tenant.
- "Give X access to Y" almost always means **edit X's bundle**, not open up Y.
  Bundles are how the suite stays least-privilege without ad-hoc ACLs.
- Entries use the suite's vocabulary (tool names, vault-scope strings, egress
  hostnames, model ids). Inventing new vocabulary is ADR-required.
- Forbidden: `tools: ["*"]`, `vault_scopes: ["*"]`. Write the names out.

## Where bundles live

Runtime source of truth: a table of bundles in the orchestrator's database
(columns: `san`, `parent_san`, `tools`, `ssh_targets`, `vault_scopes`, `egress`,
`models`, `valid_until`; unique on `san`). Which database and namespace:
`knowledge {topic: "capability-bundles"}`. Stable services have permanent rows;
sub-agents get rows on spawn, deleted on destroy.

IaC source of truth: `stacks/<target>/<service>/capability-bundle.yaml`. The
`deploy-stack` playbook upserts it at deploy time — the only writer, so the two
should match.

```yaml
san: spiffe://<trust-domain>/<service>
tools: [<gateway-tool-name>, ...]
ssh_targets: {<ssh-tool>: []}
vault_scopes:
  - "vault.<surface>.<area>:read:*"
egress: [<exact-host>, "*.<sub-domain>"]
models: ["<family>-*-sonnet"]
```

## How a tool call enforces the bundle

1. Cloudflare Access validates the caller (service token, or interactive login).
2. The tunnel delivers the request to the proxy; off-LAN, the proxy terminates TLS.
3. LAN-direct, the proxy terminates mTLS and forwards the client-cert SAN in a header.
4. The gateway's tool handler reads the SAN, looks up the bundle, and checks the
   tool name and arguments against `tools[]` / `ssh_targets[]` / `vault_scopes[]`
   / `egress[]` / `models[]`.
5. Allow: the tool runs; an audit entry records caller SAN, tool, args hash,
   decision and reason.
6. Deny: `403 Forbidden` with a `fix_hint` naming the bundle entry needed.

A tool's behaviour at the gateway is determined **entirely** by the caller's
bundle. Adding the tool to the bundle is the only way to gain access.

## Sub-agent inheritance

On spawn: (1) validate that the child bundle is a subset of the parent's, with
wildcards expanded — otherwise `400`; (2) issue a certificate with a SAN of the
form `spiffe://<trust-domain>/agent/<role>/<uuid>`, 1h TTL (cap 4h with one
renewal); (3) write the spawn audit entry; (4) upsert the child row with
`parent_san` and a `valid_until` matching the TTL; (5) start the process with the
cert and key on a tmpfs mount. Destroy reverses it: revoke the cert, delete the
row, audit the reason (`completed`, `ttl_expired`, `revoked_manual`,
`parent_revoked`).

## Authoring a bundle

1. Identify the SAN (`spiffe://<trust-domain>/<service>`; the trust domain is
   `knowledge {topic: "identity"}`).
2. List the gateway tools needed — the minimum; add by PR as needs land.
3. List vault scopes as `vault.<surface>.<area>:<op>:<path-pattern>`.
4. List egress hosts — exact or `*.sub.domain`. The network firewall's egress
   rules are configured separately and should mirror it (bundle = application
   check, firewall = network check; defence in depth).
5. List the allowed models (family wildcards, or an endpoint URL for
   OpenAI-compatible backends).
6. Save the YAML next to the stack, then run `deploy-stack` so the row lands.

## When a denial happens

Quote the `fix_hint` verbatim — it is engineered to be actionable:

```
Bundle <caller-san> denies <tool-name>. To allow, add the tool name to
stacks/<target>/<caller>/capability-bundle.yaml under tools: and re-deploy.
Audit ID: <id>.
```

## Anti-patterns

- **Bundle drift.** The YAML must match the live row. If you must edit the row
  out of band in an emergency, update the YAML within the hour and run the
  `reconcile-bundles` playbook.
- **Wildcards that should be specific** (see rules above).
- **Child wider than parent.** Bypassing the subset check by inserting the row
  directly is a security regression with audit consequences.
