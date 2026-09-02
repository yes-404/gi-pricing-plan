# Roadmap (fixture)

Synthetic corpus for `tests/test_doc_index.py` (W37-3). Phase `P9` and works `WK-1200`/
`WK-1210` exist only here — chosen clear of any real phase or work number so this fixture
can never collide with a live id.

## P9 — Fixture phase
status: closed
opened: 2026-01-01
target: 2026-02-01
gates: plan freeze 2026-01-10 · code freeze 2026-01-20 · docs freeze 2026-01-25
exit criteria: WF-1400 delivered end to end
works: WK-1200, WK-1210

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

## Ruling 72 acceptance fixtures (not part of any phase report test)

Four minimal works, one per acceptance item in
`docs/plans/2026-09-02-w37-field-set-and-rollup-rulings.md`'s Ruling 72 §4. Tagged
`phase: P7`, which has no `## P7 — ...` section and is never queried by `--phase`, so
these cannot perturb the P8/P9 phase-report fixtures.

### WK-1500 — Ruling 72 item 1: the invisible slice

```yaml
id: WK-1500
family: work
title: Ruling 72 item 1 work
status: active
phase: P7
```

#### SL-1501 — closed, with a leaf plan

```yaml
id: SL-1501
family: slice
title: Ruling 72 item 1, closed slice
status: closed
phase: P7
work: WK-1500
```

#### SL-1502 — draft, no leaf plan

```yaml
id: SL-1502
family: slice
title: Ruling 72 item 1, unplanned slice A
status: draft
phase: P7
work: WK-1500
```

#### SL-1503 — draft, no leaf plan

```yaml
id: SL-1503
family: slice
title: Ruling 72 item 1, unplanned slice B
status: draft
phase: P7
work: WK-1500
```

### WK-1600 — Ruling 72 item 2: mid-flight

```yaml
id: WK-1600
family: work
title: Ruling 72 item 2 work
status: active
phase: P7
```

#### SL-1601 — closed, with a leaf plan

```yaml
id: SL-1601
family: slice
title: Ruling 72 item 2, closed slice
status: closed
phase: P7
work: WK-1600
```

#### SL-1602 — draft, no leaf plan

```yaml
id: SL-1602
family: slice
title: Ruling 72 item 2, unplanned slice
status: draft
phase: P7
work: WK-1600
```

### WK-1700 — Ruling 72 item 3: replanned then completed

```yaml
id: WK-1700
family: work
title: Ruling 72 item 3 work
status: active
phase: P7
```

#### SL-1701 — closed, two leaf plans across a replan

```yaml
id: SL-1701
family: slice
title: Ruling 72 item 3, closed slice
status: closed
phase: P7
work: WK-1700
```

### WK-1800 — Ruling 72 item 4: no catch-all, every slice retired

```yaml
id: WK-1800
family: work
title: Ruling 72 item 4 work
status: retired
phase: P7
```

#### SL-1801 — retired

```yaml
id: SL-1801
family: slice
title: Ruling 72 item 4, retired slice A
status: retired
phase: P7
work: WK-1800
```

#### SL-1802 — retired

```yaml
id: SL-1802
family: slice
title: Ruling 72 item 4, retired slice B
status: retired
phase: P7
work: WK-1800
```
