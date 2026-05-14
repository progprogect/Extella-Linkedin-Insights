#!/usr/bin/env python3
"""Upload preset concept Markdown files to Extella via POST /api/concept/add.

Each file body becomes one concept `text`. Slugs live inside the Markdown.

Environment: same as bootstrap_experts.py (EXTELLA_TOKEN, optional headers).

Usage:
  export EXTELLA_TOKEN=...
  python3 preset_linkedin_insights/scripts/upload_concepts.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import requests
except ImportError as e:  # pragma: no cover
    raise SystemExit("pip install -r preset_linkedin_insights/scripts/requirements-scripts.txt") from e


ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = ROOT / "concepts"


def main() -> int:
    token = os.environ.get("EXTELLA_TOKEN") or os.environ.get("EXTELLA_API_TOKEN")
    if not token:
        print("Missing EXTELLA_TOKEN", file=sys.stderr)
        return 1

    base = os.environ.get("EXTELLA_API_URL", "https://api.extella.ai").rstrip("/")
    profile = os.environ.get("EXTELLA_PROFILE_ID", "default")
    agent = os.environ.get("EXTELLA_AGENT_ID", "agent_extella_default")
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json",
        "X-Profile-Id": profile,
        "X-Agent-Id": agent,
    }

    files = sorted(CONCEPT_DIR.glob("*.md"))
    if not files:
        print("No concepts found", file=sys.stderr)
        return 1

    for path in files:
        text = path.read_text(encoding="utf-8")
        url = f"{base}/api/concept/add"
        r = requests.post(url, headers=headers, json={"text": text}, timeout=60)
        if r.status_code != 200:
            print(f"FAIL {path.name} HTTP {r.status_code}: {r.text[:300]}", file=sys.stderr)
            return 1
        print(f"OK {path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
