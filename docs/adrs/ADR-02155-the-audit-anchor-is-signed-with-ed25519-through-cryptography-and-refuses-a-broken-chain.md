---
id: ADR-2155
family: decision
title: The audit anchor is signed with Ed25519 through cryptography, and refuses a chain that does not verify
status: active               # draft → active → superseded | retired (§1.2a)
created: 2026-11-15
owner: decision-maker          # creates via adr-write; maintainer accepts draft → active
tree: 4187a25e011ed69b47ef0a08bef94f42192d3146
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FR-372, FR-373, FR-424]   # ids only — the FR-/NFR-/ADR- this decision touches
---

# ADR-2155 — The audit anchor is signed with Ed25519 through cryptography, and refuses a chain that does not verify

- **Status:** Accepted (front matter `active`). Supersedes nothing.
- **Deciders:** the maintainer; the detail of the rule was decided on the maintainer's behalf by delegation, 15 Nov 2026.
- **Decision issue:** [#1839](https://github.com/yes-404/gi-pricing-plan/issues/1839) (Work #1497, slice 10, `06` FR-373)
- **Decision:** [comment of 2026-11-15](https://github.com/yes-404/gi-pricing-plan/issues/1839#issuecomment-6886339811), opening: "Decided by the maintainer, 2026-11-15: (i) option (a), and (ii) yes".
- **Enacted by:** the pull request that adds this record (the audit anchor, #1497 slice 10).

## Context

`06` FR-373 says the platform ships an explicit `POST /api/v1/audit/anchor` that exports a signed chain head for the customer to store somewhere the operator does not control. The hash chain (FR-372) detects an edit below the application, but not an operator who recomputes every later hash; a signed head that the customer holds outside the platform is what closes that gap, to the extent the customer automates it.

Two things the specification left open had to be decided before code. Which signature scheme, through which library, with the key held where. And what the anchor does when the chain it is asked to sign does not verify: `GET /audit/verify` reports a break as a finding (200 with `intact: false`), but a signature over a head is a statement that the chain up to it is sound.

`cryptography` was already in `uv.lock`, through `pyjwt[crypto]`; no backend module named it.

## Decision

1. **Ed25519 (RFC 8032, pure, no pre-hash), through `cryptography`, a new direct dependency of `backend`.** `pricing-core` and `model-schema` do not import it. The signing key is the setting `GIP_AUDIT_ANCHOR_SIGNING_KEY`, a `SecretStr` holding an unencrypted PKCS#8 PEM key, until `07` FR-424's secret backend exists; it then resolves through it. A key that is set and does not load as Ed25519 refuses start-up. An unset key starts the platform, and the route refuses with 503.
2. **The anchor refuses a chain that does not verify.** `POST /api/v1/audit/anchor` verifies the chain before it signs. A chain that does not verify is `409 AUDIT_CHAIN_BROKEN`: nothing is signed and no event is appended, because signing a tampered head would certify the tampering.

The detail of the rule, decided on the maintainer's behalf by delegation, 15 Nov 2026, and written in `06` FR-373's dated clauses:

| Question | Decided |
|---|---|
| Status for an unset key | 503 `AUDIT_ANCHOR_KEY_UNCONFIGURED`, a new code: the deployment lacks a capability, not a client error |
| Lock during the verify | Verify sequences `1..N` without the workspace lock; then under the lock re-read that row N's hash is the one verified, sign N and append. Never sign a later head than the one verified |
| Empty chain | Sign sequence 0 with a null head hash |
| A refused anchor | No event. An ERROR log with the sequence, and the 409 to the caller |
| Key rotation | `previous_key_id` inside the signed statement; the platform keeps no retired key. Rotation does not revoke |
| A public-key endpoint | None. The key arrives with each anchor and the customer pins it out of band |

It rules out a second serialiser for the signed bytes (the anchor reuses the chain's canonical JSON rule), a key in PostgreSQL (FR-424), and an anchor that signs a chain it has not verified.

## Consequences

- A customer verifies an anchor with any RFC 8032 implementation and needs the platform only to fetch it and, later, to export the log.
- A leaked key stays valid mathematically; what the customer relies on is the time it stored the anchor in a store the operator does not control. The rotation runbook says so.
- A new direct dependency is declared, and its licence (Apache-2.0 OR BSD-3-Clause) is compatible with the project's. `uv.lock` changes by `gi-backend`'s two lines only.
- The key is only as safe as the process environment until FR-424's backend exists. That is a limit of this decision, not a reason to defer the anchor.
- A refused anchor leaves no record in the chain. The ERROR log is the trace, so an operator who wants the refusals recorded durably needs the log pipeline to keep it.
