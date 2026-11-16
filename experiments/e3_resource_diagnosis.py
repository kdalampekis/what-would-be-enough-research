"""E3 only. Same options as run_pilot.py; shares its cached raw responses."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_pilot import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(["--experiments", "e3", *sys.argv[1:]]))
