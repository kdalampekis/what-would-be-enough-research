"""Check model configuration and environment before a real run. No network, no API call.

    python experiments/check_config.py --models gpt-5.6-sol,claude-sonnet-5-5
"""

import argparse
import sys
from pathlib import Path

from msep.envfile import load_env
from msep.models.config_check import check_all
from msep.models.prompts import PROMPT_VERSION
from msep.models.runner import load_models
from msep.models.schemas import SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="gpt-5.6-sol,claude-sonnet-5-5")
    ap.add_argument("--models-config", default=str(ROOT / "configs" / "models.json"))
    ap.add_argument("--no-keys", action="store_true", help="do not require API keys (configuration only)")
    a = ap.parse_args(argv)
    loaded = load_env(ROOT / ".env")
    if loaded:
        print(f"loaded from .env: {sorted(loaded)}")
    errors, warnings = check_all(load_models(Path(a.models_config)), a.models.split(","), require_keys=not a.no_keys)
    print(f"prompt version {PROMPT_VERSION}; schema version {SCHEMA_VERSION}")
    for w in warnings:
        print("WARNING", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} error(s): fix before any real run")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
