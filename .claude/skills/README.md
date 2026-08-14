# Project skills

Procedures specific to **this** repository, versioned with it so they travel with the code.
Each captures something non-obvious that was learned the hard way — a convention that is
easy to break silently, or a trap that a passing check would hide.

Personal/global skills live in `~/.claude/skills/` and are **never** modified as part of
project work (`CLAUDE.md` §12).

## Index

| Skill | Purpose | Source | Last verified |
|---|---|---|---|
| [`spec-change`](spec-change/SKILL.md) | Add or modify a requirement, section, or open question in `docs/specs/` — append-only IDs, ten-section standard, both-direction cross-referencing | self-written | 2026-08-14 |
| [`docs-audit`](docs-audit/SKILL.md) | Verify suite integrity before a commit or PR, including the decision-gate invariant the script does not cover | self-written | 2026-08-14 |
| [`adr-write`](adr-write/SKILL.md) | Create, supersede, or annotate an architecture decision record — including the addendum-versus-edit rule that keeps accepted ADRs immutable | self-written | 2026-08-14 |
| [`contract-schema`](contract-schema/SKILL.md) | Add or modify a JSON Schema contract in `docs/contracts/` — money conventions, `invariants` annotation, duplicate-key and `$ref` traps | self-written | 2026-08-14 |
| [`library-spike`](library-spike/SKILL.md) | Empirically verify library behaviour where pip is unavailable, then land the finding across the suite | self-written | 2026-08-14 |

## External skills

**None installed.** A discovery pass against `anthropics/skills` (18 skills) and
`claude-plugins-official` on 2026-08-14 found no external skill that fits the project's
current state — Phase 0 is documentation-first with highly repo-specific conventions, and
the closest candidate (`doc-coauthoring`) overlaps `CLAUDE.md` §5/§10, which is more
specific and already binding.

Several become relevant in later phases and are recorded so the next gap analysis does not
have to rediscover them:

| Skill | Becomes relevant | For |
|---|---|---|
| `xlsx` | Phase 2 | Rate table CSV/XLSX import-export round-tripping (FR-RATE-20) |
| `pdf` | Phase 3 | Dossier PDF rendering, deterministic output (FR-GOV-29) |
| `webapp-testing` | Phase 1–2 | Frontend and DAG designer testing |
| `skill-creator` | when this library grows | Skill evals and description tuning; heavyweight (spawns nested `claude -p`) |

External skills are **never installed without the maintainer's approval** (`CLAUDE.md` §12).

## Conventions

- Kebab-case folder, one capability per skill, no overlap between skills.
- Frontmatter `name:` must equal the folder name; `description:` controls triggering, so
  it names the concrete artifacts and file paths involved, not just a topic.
- Every skill ends with a `## Verified` line: the date and **how** the procedure was
  confirmed — ideally citing a failure it actually caught.
