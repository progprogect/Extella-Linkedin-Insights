#!/usr/bin/env python3
"""Backward-compatible entry: delegates to publish_concepts.py."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "publish_concepts.py"), run_name="__main__")
