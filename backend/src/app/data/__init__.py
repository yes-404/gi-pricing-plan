"""Data management: ingestion, preparation, validation, profiling (`01`).

Orchestration and I/O only. The deterministic parts — column normalisation, schema
inference, quarantine partitioning — live in `pricing_core.data` so they are callable
without the platform (ADR-703, `01` §5.2).
"""
