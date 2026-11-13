# Security and wrong-price policy

**Do not open a public issue** for either of these:

- a security vulnerability (authentication, roles, data exposure, code execution);
- a defect that could make the platform produce a **wrong price** or a wrong
  rating or scoring result.

Report it privately: **Security, then Report a vulnerability**
(https://github.com/yes-404/gi-pricing-plan/security/advisories/new).

Include the version or commit, a minimal reproduction, and the impact you think it
has. For a wrong price, give the inputs, the price you got and the price you expected.
If you used AI tools to find or write the report, say so, and check it yourself first.

What happens next:

1. Acknowledgement within three working days.
2. A probe. If it refutes the report, the advisory is closed with a short public note.
3. If confirmed, the fix is developed privately.
4. When the fix is merged, a public issue and a changelog entry describe the defect,
   the affected versions and the fix.

Reporters are credited in whatever record the fix produces, unless they ask not to be.

Only the latest release is supported. Everything else is a normal public finding:
open an issue with the finding form.

## Scope

This is an unreleased platform with no production deployment: no hosted service, no
customer data and no live endpoint. The scope is the code on `main` and any other branch
here. In scope: application code, the CI configuration under `.github/workflows/`, and
supply-chain issues in dependencies this repository pulls in. Out of scope: findings that
need a production deployment that does not exist yet, social-engineering or
physical-security reports, and third-party services (report those upstream).
There is no bug bounty.

The internal record of the repository's settings and workflow trust is
[`docs/process/security-posture.md`](docs/process/security-posture.md).
