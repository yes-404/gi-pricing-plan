# Roadmap (fixture)

A worked example of the legacy roadmap shape the migration script restructures into
milestone sections with fenced work/slice rows. This fixture's own grammar
(`## Phase <id> — <title>`, `### <work-key> — <title>` + `status:`, and
`- **<slice-key>** <title> — status: <status>`) is this corpus's own reasonable, minimal
reading of "phase sections and work rows" — the migration spec does not pin the legacy
shape, only the post-migration one.

## Phase 1a — Example workbench

### W1 — Example workstream
status: active

- **W1-1** Example slice, closed — status: closed
- **W1-2** Another slice, still open — status: draft
