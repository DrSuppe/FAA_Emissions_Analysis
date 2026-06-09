"""Project-wide YAML loading utilities.

PyYAML follows YAML 1.1, which coerces bare ``NO``, ``YES``, ``ON``, etc.
to booleans.  This breaks species lists that contain ``NO`` (nitric oxide).
All YAML loading in this project should use :func:`safe_load` from this
module, which strips the boolean resolver before parsing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class _StrSafeLoader(yaml.SafeLoader):
    """SafeLoader variant that does not coerce YAML 1.1 boolean literals."""


# Remove the built-in boolean resolver so that NO, YES, ON, OFF, etc. are
# preserved as plain strings.
_StrSafeLoader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:bool"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def safe_load(source: str | bytes) -> Any:
    """Parse YAML without boolean coercion."""
    return yaml.load(source, Loader=_StrSafeLoader)  # noqa: S506


def load_yaml(path: Path) -> Any:
    """Open *path* and parse YAML without boolean coercion."""
    with path.open("r", encoding="utf-8") as fh:
        return yaml.load(fh, Loader=_StrSafeLoader)  # noqa: S506
