"""Pure data functions: ingestion helpers, preparation, validation, profiling (`01` §5.2).

No I/O and no database. Files are read by the caller and passed in as frames, so every
function here runs in a notebook against a CSV the actuary already has — which is ADR-703's
promise and the reason a reviewer can reproduce a number without the platform.
"""
