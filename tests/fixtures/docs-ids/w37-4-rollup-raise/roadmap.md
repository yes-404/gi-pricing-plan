# Roadmap (fixture)

`scripts/audit-docs.py` check 33's own fixture: a single work with one slice that carries
**two** live (non-superseded, non-retired) leaf plans at once — a data-entry error
`_slice_child_state` (`scripts/doc-index.py`, Ruling 72) refuses to resolve silently.
Phase `P6` and work `WK-1900` exist only here, chosen clear of any real or other-fixture
number so this corpus can never collide.

## P6 — Fixture phase (check 33 rollup-raise only)

```yaml
status: active
opened: 2026-01-01
target: 2026-02-01
gates: plan freeze 2026-01-10 · code freeze 2026-01-20 · docs freeze 2026-01-25
exit criteria: not read by any test
works: WK-1900
```

### WK-1900 — Rollup-raise fixture work

```yaml
id: WK-1900
family: work
title: Rollup-raise fixture work
status: active
phase: P6
```

#### SL-1901 — the slice with two live leaf plans

```yaml
id: SL-1901
family: slice
title: Two live leaf plans
status: active
phase: P6
work: WK-1900
```
