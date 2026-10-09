"""The `dislocation.run` Job handler (03 §5.1, FR-263, FR-265, FR-266; PL-1501 Tasks 3-4).

`pricing-core` computes (`dislocation_frame`, `select_movers`, `summarise_dislocation`,
`derive_changes`, `attribute`); this module owns what it may not: the Job identity, the
output location (a content-addressed movers blob and one `dislocation_runs` row) and
resumability. The attribution runs on the worker thread with no database I/O, because
`attribute` is `async` only for its resolver and a long coroutine inside `run_on_loop`
hangs (the 30 s `JobProgress` timeout `scoring_handlers.py` documents): the handler first
resolves every artifact the two versions need into a `PreloadedResolver`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from model_schema import ArtifactRef, RatingVersion
from pricing_core.rating.compile import ArtifactResolver, ResolvedArtifact, compile_bundle

__all__ = ["PreloadedResolver", "preload"]


class PreloadedResolver:
    """Serves artifacts already resolved, with no I/O (DP-S4-4).

    A ref that was not preloaded raises `ValueError("NOT_FOUND: …")`, the form
    `compile_bundle`'s callers read as a named code.
    """

    def __init__(self, artifacts: Mapping[ArtifactRef, ResolvedArtifact]) -> None:
        self._artifacts = dict(artifacts)

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        try:
            return self._artifacts[ref]
        except KeyError:
            raise ValueError(f"NOT_FOUND: {ref} was not preloaded for this run") from None


class _Recorder:
    """Passes every resolution to `inner` and keeps what it returned."""

    def __init__(self, inner: ArtifactResolver) -> None:
        self._inner = inner
        self.seen: dict[ArtifactRef, ResolvedArtifact] = {}

    async def resolve(self, ref: ArtifactRef) -> ResolvedArtifact:
        resolved = await self._inner.resolve(ref)
        self.seen[ref] = resolved
        return resolved


async def preload(base: ArtifactResolver, versions: Iterable[RatingVersion]) -> PreloadedResolver:
    """Every artifact a compile of each of `versions` resolves, held in memory.

    The refs are those `compile_bundle` itself asks `base` for (the algorithm, every pin and
    the Factors a model pin reads), so no list of pin kinds is kept here to drift from it.
    Run inside the one `run_on_loop` call that has the database session.
    """
    recorder = _Recorder(base)
    for version in versions:
        await compile_bundle(version, recorder)
    return PreloadedResolver(recorder.seen)
