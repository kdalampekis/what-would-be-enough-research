"""Load KEY=VALUE lines from a local .env file into the environment (no dependency).

Variables already set in the environment win. The file is gitignored; never commit it.
Lines starting with # and blank lines are skipped; surrounding quotes are stripped.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env(path: Path) -> list[str]:
    """Return the names (never the values) of the variables set from the file."""
    path = Path(path)
    if not path.is_file():
        return []
    loaded = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        if name and name not in os.environ:
            os.environ[name] = value
            loaded.append(name)
    return loaded
