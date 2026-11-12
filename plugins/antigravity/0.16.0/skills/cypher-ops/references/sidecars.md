# Sidecar composition via `stacks/shared/`

PURPOSE: how cypherops keeps cross-cutting sidecars (certificate renewal, log
shipping, audit forwarding, metrics) in one place and how a stack picks them up
with `extends:` instead of copy-pasting compose blocks. Load it from the
`cypher-ops` core when adding a sidecar or consuming one.

Rules:

- Cross-service concerns live in `stacks/shared/`, not duplicated per stack.
- A sidecar there is a **template**: it declares image, volumes, base env and
  entrypoint, and is never deployed directly. The consumer overrides the
  per-service variables (`SERVICE_NAME`, `SAN`, log labels).
- A new shared sidecar that introduces a new cross-cutting concern needs an ADR.
- Copy-pasting a sidecar into a second stack is the trigger to promote it to
  `stacks/shared/`. Extract on the second use, not the first.

## The shared file

`stacks/shared/cypher-sidecars.yaml` is a compose file whose `services:` entries
are the templates. Endpoints (CA, log store) are variables or `knowledge
{topic: "observability"}` / `knowledge {topic: "identity"}` answers — never copy
a real hostname into a skill.

```yaml
services:
  cert-renewer-base:
    image: <registry>/cert-renewer:${CERT_RENEWER_TAG}
    restart: unless-stopped
    volumes: [cert-shared:/certs]
    environment:
      STEP_CA_URL: ${STEP_CA_URL}
      RENEW_INTERVAL: 12h
      CERT_VALIDITY: 24h
    # SERVICE_NAME and SAN come from the consuming stack

  log-shipper-base:
    image: grafana/promtail:${PROMTAIL_TAG}
    restart: unless-stopped
    volumes: [/var/log:/var/log:ro]
    environment:
      LOKI_URL: ${LOKI_URL}
      LOG_TENANT: app

  audit-shipper-base:
    image: grafana/promtail:${PROMTAIL_TAG}
    restart: unless-stopped
    environment:
      LOKI_URL: ${LOKI_URL}
      LOG_TENANT: audit        # a SEPARATE tenant
```

## The pattern at the consumer

```yaml
services:
  <service>:
    image: <registry>/<service>:${<SERVICE>_TAG}

  <service>-cert-renewer:
    extends:
      file: ../../shared/cypher-sidecars.yaml
      service: cert-renewer-base
    environment:
      SERVICE_NAME: <service>
      SAN: spiffe://<trust-domain>/<service>

  <service>-log-shipper:
    extends:
      file: ../../shared/cypher-sidecars.yaml
      service: log-shipper-base
    environment:
      SERVICE_NAME: <service>
      LOG_LABELS: "service=<service>,env=prod"
```

`extends:` pulls in the template's `image`, `restart`, `volumes`, `environment`
(overridable per key) and `entrypoint`. The trust domain in the SAN:
`knowledge {topic: "identity"}`.

## The three sidecars

| Sidecar | What it does | Required for |
|---|---|---|
| `cert-renewer-base` | Requests a fresh step-ca client cert every 12h (24h validity) into a shared volume the consumer mounts | every service making mTLS calls (almost all) |
| `log-shipper-base` | Ships stdout/stderr to the `app` log tenant | every long-running service |
| `audit-shipper-base` | Ships audit-tier events to a **separate** `audit` tenant with different credentials and stricter retention | services emitting security-sensitive audit records |

Why audit is separate: the application service cannot write to the audit tenant.
The audit shipper runs as a different UID with its own credentials, so a process
compromise in the application container can alter the application logs but not
its own audit trail. That is the load-bearing security property — preserve it
when authoring an audit-emitting service.

## Adding a new shared sidecar

The bar is "genuinely cross-cutting", and an ADR is required for a new
observability surface (metrics exporter, trace shipper), identity surface
(token rotator, secret refresher) or auditable concern. Do not add one for a
concern only one service has (it stays in that service's compose) or for "we
might want this later" — wait for the second consumer.
