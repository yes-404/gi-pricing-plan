# Moved

The working notes that used to live in this directory moved to
[`docs/notes/`](../../docs/notes/README.md) on 2026-09-01 (NT-0016 Slice 4, Ruling 56 —
`docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md`). This is a tombstone, not a
symlink: `scripts/audit-docs.py` globs its notes root for `*.md`, so a symlink here would
keep resolving and both paths would stay "real" to every tool that checks — exactly the
two-homes ambiguity the move exists to end (Ruling 57). Cite a note by its `NT-00NN` id
going forward (Ruling 58), not by path; each id resolves via the index at
[`docs/notes/README.md`](../../docs/notes/README.md).

A frozen plan filed under `docs/plans/` before this move keeps its original
`.claude/notes/...` citation unedited (NT-0016 C4, `docs/plans/README.md`'s write-once
rule) — this file is what makes that citation still resolve to something.

## Old path → new path

| Old | New |
|---|---|
| `.claude/notes/0001-phase-boundary-plan-review.md` | `docs/notes/0001-phase-boundary-plan-review.md` |
| `.claude/notes/0002-demo-entrance-and-guide.md` | `docs/notes/0002-demo-entrance-and-guide.md` |
| `.claude/notes/0003-duplicated-status-goes-stale.md` | `docs/notes/0003-duplicated-status-goes-stale.md` |
| `.claude/notes/0004-a-reference-that-resolves-only-for-the-writer.md` | `docs/notes/0004-a-reference-that-resolves-only-for-the-writer.md` |
| `.claude/notes/0005-deferred-items-with-no-durable-custody.md` | `docs/notes/0005-deferred-items-with-no-durable-custody.md` |
| `.claude/notes/0006-two-rules-for-reading-an-artifact.md` | `docs/notes/0006-two-rules-for-reading-an-artifact.md` |
| `.claude/notes/0007-context-bound-measures-cap-not-discipline.md` | `docs/notes/0007-context-bound-measures-cap-not-discipline.md` |
| `.claude/notes/0008-project-closure-audit-structure.md` | `docs/notes/0008-project-closure-audit-structure.md` |
| `.claude/notes/0009-slim-the-roadmap.md` | `docs/notes/0009-slim-the-roadmap.md` |
| `.claude/notes/0010-layered-slice-based-workflow.md` | `docs/notes/0010-layered-slice-based-workflow.md` |
| `.claude/notes/0011-per-agent-model-and-skill-settings.md` | `docs/notes/0011-per-agent-model-and-skill-settings.md` |
| `.claude/notes/0012-a-credential-is-borrowed-not-stored.md` | `docs/notes/0012-a-credential-is-borrowed-not-stored.md` |
| `.claude/notes/0013-the-lead-is-the-highest-error-node.md` | `docs/notes/0013-the-lead-is-the-highest-error-node.md` |
| `.claude/notes/0014-machine-readable-process-core.md` | `docs/notes/0014-machine-readable-process-core.md` |
| `.claude/notes/0015-the-register-is-a-ledger-evidence-is-a-file.md` | `docs/notes/0015-the-register-is-a-ledger-evidence-is-a-file.md` |
| `.claude/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md` | `docs/notes/0016-file-taxonomy-reference-coding-and-custody-investigation.md` |
| `.claude/notes/0017-a-public-repository-needs-a-public-face.md` | `docs/notes/0017-a-public-repository-needs-a-public-face.md` |
| `.claude/notes/0018-a-turn-that-ends-strands-what-it-started.md` | `docs/notes/0018-a-turn-that-ends-strands-what-it-started.md` |
| `.claude/notes/README.md` (the working index) | `docs/notes/README.md` |
