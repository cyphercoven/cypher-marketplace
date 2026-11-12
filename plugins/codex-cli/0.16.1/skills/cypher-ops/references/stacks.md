# Adding a docker-compose stack

PURPOSE: the end-to-end shape of adding a stack under `stacks/<target>/<service>/`
in cypherops, from authoring the compose file to landing the deploy. Load it from
the `cypher-ops` core when the task is "add or change a stack".

Rules that override everything below:

- Compose files never inline an image tag: `image: <registry>/<service>:${<SERVICE>_TAG}`,
  with the tag declared in `versions.yaml` (see `image-tags.md`).
- A first-party service's Dockerfile lives in `builds/<service>/`, never in the
  product repo.
- Sensitive-traffic services authenticate with a step-ca client certificate whose
  SAN identifies the service, never on network position (see `cloudflare-mtls.md`).
- Deploy with the `deploy-stack` Ansible playbook, never `docker compose up` by
  hand on the host — an imperative change outside the IaC loop breaks reproducibility.
- Read the closest sibling stack first; it already solves most of the shape.
  Differ from it only with a recorded reason.

## 1. Pick the target

Each target is a directory under `stacks/` that maps to one host. What runs on
which target, and which is the default landing zone for a new first-party
service: `knowledge {topic: "estate"}`.

| Kind of target | Land your service here when |
|---|---|
| infra | cross-cutting infrastructure other stacks consume (tunnel, proxy, CA, forge) |
| prod | production-grade always-on services — the default for a new first-party service |
| dev | pre-prod or experimental versions of services that will graduate to prod |
| media | anything that needs GPU passthrough |
| vault | vault-sensitive only; isolated network segment |
| interim | NAS-resident interim stacks (the live host until a stack is migrated) |

If the service fits none of them, that is the trigger for an ADR proposing a new
target — not a reason to invent a stack location ad hoc.

## 2. Lay out the directory

```
stacks/<target>/<service>/
├── docker-compose.yaml
├── .env.template           # values hydrated by sync-versions.sh + secret injection
├── README.md               # service-local notes, not a copy of the build
└── (optional) traefik/     # service-local Traefik labels if too long to inline
```

## 3. Wire the image tag

In `versions.yaml` add `<service>: {tag: "<initial-tag>"}` (Renovate datasource
hints live beside it). In the compose file reference `${<SERVICE>_TAG}`.
`scripts/sync-versions.sh` reads the manifest and writes the resolved tag into
`.env.template` for every stack that references it. Full flow: `image-tags.md`.

## 4. Extend the shared sidecars

Sensitive services take cross-cutting sidecars from `stacks/shared/` with
`extends:` — the certificate renewer (any service making mTLS calls, which is
almost all), the log shipper (any long-running service), and the audit shipper
(services that emit security-sensitive audit records). Template and the exact
`extends:` blocks: `sidecars.md`. A sidecar pattern that does not exist yet means
stop: it goes in the shared file, with an ADR if it is cross-cutting.

## 5. Wire routing (if user-facing)

Production services use **one hostname with split-horizon DNS**: LAN-direct with
mTLS at the proxy, off-LAN through the tunnel plus Cloudflare Access. The labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.<service>.rule=Host(`<service-hostname>`)"
  - "traefik.http.routers.<service>.tls=true"
  - "traefik.http.routers.<service>.tls.options=mtls-required@file"
  - "traefik.http.services.<service>.loadbalancer.server.port=<port>"
```

The hostname scheme: `knowledge {topic: "ingress"}`. The port comes from the
repo's `port-registry.md` — never invent a port; the registry is the canonical
assignment. The whole routing story: `cloudflare-mtls.md`.

## 6. Capability bundle (if it calls sensitive backends)

If the service calls gateway tools, the vault, or another sensitive backend,
write `stacks/<target>/<service>/capability-bundle.yaml`. See `capability-bundles.md`.

## 7. Deploy

```sh
ansible-playbook ansible/playbooks/deploy-stack.yaml -e target=<target> -e service=<service>
```

The playbook syncs versions, injects secrets, deploys, runs health checks and
rolls back on failure. For a merge that touches a ship-on-push stack, the merge
itself deploys (core §4).

## 8. Document

- A runbook if the service has operational procedures (rotation, restore,
  escalation): `runbooks.md`.
- An ADR if you made a binding decision (new tool, pattern, boundary).
- A row in `port-registry.md` for the service's port.
