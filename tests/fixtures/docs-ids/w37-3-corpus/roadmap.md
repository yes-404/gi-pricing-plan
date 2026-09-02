# Roadmap (fixture)

Synthetic corpus for `tests/test_doc_index.py` (W37-3). Phase `P9` and works `WK-1200`/
`WK-1210` exist only here — chosen clear of any real phase or work number so this fixture
can never collide with a live id.

## P9 — Fixture phase

```yaml
status: closed
opened: 2026-01-01
target: 2026-02-01
gates: plan freeze 2026-01-10 · code freeze 2026-01-20 · docs freeze 2026-01-25
exit criteria: WF-1400 delivered end to end
works: WK-1200, WK-1210
```

### WK-1200 — Alpha work

```yaml
id: WK-1200
family: work
title: Alpha work
status: closed
phase: P9
```

#### SL-1201 — Alpha, closed slice

```yaml
id: SL-1201
family: slice
title: Alpha, closed slice
status: closed
phase: P9
work: WK-1200
```

#### SL-1202 — Alpha, active slice

```yaml
id: SL-1202
family: slice
title: Alpha, active slice
status: active
phase: P9
work: WK-1200
```

#### SL-1203 — Alpha, draft slice

```yaml
id: SL-1203
family: slice
title: Alpha, draft slice
status: draft
phase: P9
work: WK-1200
```

#### SL-1204 — Alpha, executed-not-closed slice

```yaml
id: SL-1204
family: slice
title: Alpha, executed-not-closed slice
status: active
phase: P9
work: WK-1200
```

### WK-1210 — Beta work

```yaml
id: WK-1210
family: work
title: Beta work
status: retired
phase: P9
```

#### SL-1211 — Beta, retired slice

```yaml
id: SL-1211
family: slice
title: Beta, retired slice
status: retired
phase: P9
work: WK-1210
```

## P8 — Fixture phase, roll-up only

Deliberately given no `works:` line and never read by any phase-report test: `WK-1220`
below exists only to back the map-plan "all closed → closed" roll-up fixture
(`PL-1329`/`PL-1330`/`PL-1331`), kept off `P9` so it cannot perturb that phase's
hand-counted totals.

### WK-1220 — Gamma work

```yaml
id: WK-1220
family: work
title: Gamma work
status: closed
phase: P8
```

#### SL-1221 — Gamma, closed slice A

```yaml
id: SL-1221
family: slice
title: Gamma, closed slice A
status: closed
phase: P8
work: WK-1220
```

#### SL-1222 — Gamma, closed slice B

```yaml
id: SL-1222
family: slice
title: Gamma, closed slice B
status: closed
phase: P8
work: WK-1220
```
