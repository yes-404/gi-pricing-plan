"""The GIT_* variables that point git at another repository or rewrite what it reads, as a git
hook exports them, and the environment every script under scripts/ runs git with (#1900, #1913).

`git -C` does not override them. Each git call in a script passes `env=clean_env()`, so the script
reads the checkout it names, never one the caller's environment names. Named, not a GIT_ prefix
match: `tests/test_gitenv.py` holds this tuple to `git rev-parse --local-env-vars`.
"""

import os

REDIRECTS: tuple[str, ...] = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE",
    "GIT_CONFIG",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_COUNT",
    "GIT_IMPLICIT_WORK_TREE",
    "GIT_GRAFT_FILE",
    "GIT_NO_REPLACE_OBJECTS",
    "GIT_REPLACE_REF_BASE",
    "GIT_PREFIX",
    "GIT_SHALLOW_FILE",
)


def clean_env() -> dict[str, str]:
    """`os.environ` without `REDIRECTS`, read at call time (never cached)."""
    return {k: v for k, v in os.environ.items() if k not in REDIRECTS}
