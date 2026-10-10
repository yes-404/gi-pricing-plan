# freMTPL2 rating fixture (measurement only)

Declarative JSON for WK-673 Slice 3 (SL-1387, PL-1452 Task 7): a baseline rating algorithm, a
full candidate, per-factor relativity tables and a catalogue of six changes. **It is measurement
only until the G2 exit-demo slice adopts it.** Nothing here is code or a pickle, and
`examples/fremtpl2/seed.py` is not changed.

The frequency model is **relativity tables, with no `model_call`** (dispatch record Ruling 1
(b')). Every table is exp(beta) from a real `glum` Poisson fit on the public freMTPL2 file:

    uv run python scripts/measure-attribution-cost.py fit

`fremtpl2-fit-record.json` holds the data checksum, both coefficient vectors and the decimal
places (8 for table values, 12 for the base frequency). `freq_v1` is the factor list of RS-1201's
`prep` (Area, VehPower, age band, VehBrand, Region, BonusMalus, log Density); `freq_v2` adds VehGas
and the VehAge band. Every term reads one field with a finite key domain; no interactions.

`fremtpl2-rate.changes.json` names, per member, the steps it takes from the full candidate
(`fremtpl2-rate.rating-algorithm.v2.json`), and the six RS-1201 change sets. Member 0 (the model
swap) is one group. The cap is an expression ahead of the minimum-premium clamp, with a factor too
large to bind in the baseline, because the engine allows one clamp per ladder rung.
