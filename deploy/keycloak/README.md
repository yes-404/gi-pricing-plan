---
family: reference
title: Reference Keycloak deployment
status: active                  # active → retired (§1.2a)
created: 2026-10-11
owner: lead
corrected_by: []
relates: []                      # ids only
---

# Reference Keycloak deployment

An example identity provider deployment for a production stack (FR-437). **You operate it, you
patch it, and you are accountable for it.** This project does not ship an identity provider in
the production stack and does not secure this one on your behalf: one unpatched CVE in a bundled
identity provider would be every deployment's credential breach, and this project's release
cadence is nobody's SLA. This directory gives you the same starting point and leaves the
accountability where the deployment boundary already puts it.

It is **not** the local provider. `deploy/keycloak-local/` is the development realm behind the
`auth` compose profile: plain HTTP, `start-dev`, passwords in a committed file.

## What it is

Keycloak in production mode (`start`) with its own PostgreSQL database, TLS terminated at the
proxy in front of it, and no default credentials: every secret comes from the environment and
`docker compose` refuses to start without it.

```bash
export KC_DB_PASSWORD=… KC_HOSTNAME=login.example.com KC_ADMIN_USER=… KC_ADMIN_PASSWORD=…
docker compose -f deploy/keycloak/docker-compose.yml up -d --wait
```

## What you still do

- Put a TLS-terminating proxy in front of port 8080 (it is not published).
- Create the realm and a client for the SPA and the API audience. `deploy/keycloak-local/realm-gi-pricing.json`
  shows the shape of a public PKCE client with an audience mapper; do not import it as is.
- Point the platform at it with `GIP_OIDC_ISSUER`, `GIP_OIDC_AUDIENCE` and `GIP_OIDC_JWKS_URL`.
  `GIP_ENVIRONMENT=prod` refuses to start without an issuer.
- Pin, review and upgrade the image yourself, back up its database, and answer its CVEs.
