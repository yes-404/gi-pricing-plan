# Security Policy

## Scope

This is an **unreleased platform with no production deployment**. There is no hosted
service, no customer data, and no live endpoint to attack — the scope is the codebase as
published on `main` and any other branch in this repository. Once the platform is
deployed (Phase 2's `W14`, per [`docs/roadmap.md`](docs/roadmap.md)), this file will be
updated to describe the deployed surface; until then, treat every finding as a codebase
finding.

In scope: vulnerabilities in the application code, the CI/CD configuration under
`.github/workflows/`, and dependency supply-chain issues (a malicious or compromised
dependency this repository pulls in).

Out of scope: findings that require a production deployment that does not exist yet;
social-engineering or physical-security reports; anything about a third-party service
this project merely depends on (report those upstream).

## Reporting a vulnerability

**Use GitHub's private vulnerability reporting** — the "Report a vulnerability" button
under this repository's Security tab. This is the only reporting channel; **please do not
open a public issue for a security finding.**

We will acknowledge a report **within 7 days**. This is a part-time-maintained project
with no on-call rotation, so 7 days is a commitment we can actually keep rather than an
aspirational number that slips. There is no bug bounty.

## What happens next

A validated report is triaged into the project's internal delivery process
(`docs/process/delivery-process.md`) like any other piece of work, and tracked to a fix.
Reporters are credited in whatever record the fix produces, unless they ask not to be.

## Repository security posture

This file is the outward-facing summary. The internal record of what is configured on
this repository — settings, rulesets, workflow trust — and why, is
[`docs/audit/security-posture.md`](docs/audit/security-posture.md).
