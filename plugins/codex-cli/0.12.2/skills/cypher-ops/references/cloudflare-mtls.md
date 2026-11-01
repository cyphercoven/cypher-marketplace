# Cloudflare Tunnel, Access and mTLS

PURPOSE: how the tunnel, Cloudflare Access, the proxy (LAN-direct mTLS
terminator), the certificate authority and the LAN resolver fit together end to
end. Load it from the `cypher-ops` core when wiring a new service's hostname or
debugging why one path (LAN or off-LAN) works and the other does not. The
decisions live in the repo's ADRs and win over this narrative.

Rules:

- **One hostname per service.** Split-horizon DNS resolves it differently for LAN
  and off-LAN clients. There is no second-alias scheme.
- A service is reachable through the tunnel **or** LAN-direct depending on where
  the client resolves; the split is at DNS resolution.
- mTLS at the proxy is the trust boundary on the LAN-direct path. The application
  trusts the forwarded client-cert-info header and **does not terminate TLS itself.**
- Cloudflare Access is the trust boundary off-LAN: it validates identity and
  device posture before forwarding to the tunnel.
- The actual hostnames, zones and addresses are never in a skill:
  `knowledge {topic: "ingress"}`; trust domain and CA facts:
  `knowledge {topic: "identity"}`.

## The two paths

LAN client → the LAN resolver returns the proxy's LAN address → the proxy
terminates mTLS and checks the client SAN against the route → the app container
trusts the forwarded header.

Off-LAN client → public DNS returns a CNAME to the tunnel → Cloudflare Access
(identity + device posture) → the tunnel client on the infra guest → the same
proxy, on a separate listener that does **not** require client mTLS (Access has
already authenticated) but routes identically by Host header.

## Tunnel (off-LAN)

`stacks/<infra>/cloudflared/` runs the tunnel client; the Cloudflare side is
OpenTofu under `cloudflare/tunnels/`. Each public hostname is a CNAME to the
tunnel's hostname. For a service reachable off-LAN you add the hostname to the
tunnel config (Cloudflare side) **and** the proxy labels (cypherops side, in the
service's compose).

## Access (off-LAN identity gate)

An Access policy sits in front of every off-LAN-reachable service and checks
(1) identity — a login confirming the user is the owner or a whitelisted
household member, and (2) device posture — the WARP client running, enrolled,
posture checks passing. Service-to-service callers from agent surfaces use
Access **service tokens** (client-id + client-secret headers) rather than the
interactive flow; issuance and rotation are in the repo's rotate-service-token
runbook. Read an application and its policies with `cf_access`; change them
through the OpenTofu root with `cf_tofu` (plan first).

## Proxy (LAN-direct mTLS)

`stacks/<infra>/traefik/`: listens on the LAN-direct address, terminates TLS with
its own step-ca-issued server cert, **requires a valid client cert** for any
route flagged `tls.options=mtls-required@file` (verified against the CA), sets
the forwarded client-cert-info header, and routes by Host.

## Certificate authority

`stacks/<infra>/step-ca/`. Two cert kinds, both 24h validity renewed by the
`cert-renewer` sidecar every 12h (see `sidecars.md`): server certs (the proxy,
anything serving mTLS) and client certs (every service that makes mTLS calls).
SAN format: `spiffe://<trust-domain>/<service>` for stable services,
`spiffe://<trust-domain>/agent/<role>/<uuid>` for sub-agents. The CA's root key
sits on a hardware token in physical custody — without it the CA cannot issue,
and it cannot be compromised remotely, so a CA root rotation is a runbook for the
owner, not something an agent completes.

## LAN resolver

The firewall's resolver answers LAN clients with LAN addresses for the suite's
hostnames and falls back to the public records for everything else. The WARP
client puts an off-LAN device on the LAN resolver, so a phone on cellular still
takes the LAN-direct path while WARP is on.

## When you add a service

1. Pick the hostname and add it to the zone in `cloudflare/zones/` (OpenTofu).
2. Reachable off-LAN? Add it to the tunnel config in `cloudflare/tunnels/` **and**
   an Access policy in `cloudflare/access/`.
3. Sensitive (mTLS-required on the LAN path)? Add the proxy route with
   `mtls-required@file` and a `cert-renewer` sidecar for outbound client certs.
4. Reserve its container port in `port-registry.md`.
5. Makes cross-service calls? Write its capability bundle (`capability-bundles.md`).

Cloudflare changes ship through `cf_tofu` plan → apply (one-off `cf_api` only as
a planned exception), and anything that touches a public zone is a B-lane ask
first (core §4). The broader walkthrough: `stacks.md`.
