#!/usr/bin/env python3
"""Publish preset experts to Extella via POST /api/expert/save.

Environment:
  EXTELLA_TOKEN or EXTELLA_API_TOKEN (required)
  EXTELLA_API_URL (optional, default https://api.extella.ai)
  EXTELLA_PROFILE_ID (optional, default default)
  EXTELLA_AGENT_ID (optional, default agent_extella_default)

Usage (from repo root):
  export EXTELLA_TOKEN=...
  python3 preset_linkedin_insights/scripts/bootstrap_experts.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError as e:  # pragma: no cover
    raise SystemExit("Install requests: pip install requests") from e


ROOT = Path(__file__).resolve().parents[1]
EXPERT_DIR = ROOT / "experts"


def _load_code(name: str) -> str:
    p = EXPERT_DIR / f"{name}.py"
    return p.read_text(encoding="utf-8")


EXPERTS: list[dict] = [
    {
        "name": "linkedin_insights_init_excel_workbook",
        "description": (
            "Creates a new LinkedIn Insights Excel workbook with sheets posts and run_meta. "
            "Parameters: output_path — absolute or ~/ path (optional, defaults under /tmp); "
            "query_spec_json — JSON string stored in run_meta; run_id — optional UUID string."
        ),
        "kwargs": {
            "output_path": "",
            "query_spec_json": "{}",
            "run_id": "",
        },
    },
    {
        "name": "linkedin_insights_collect_posts_batch",
        "description": (
            "Validates and filters a batch of PostRecord objects. v1 supports source_mode=manual only. "
            "Parameters: source_mode — manual|official|browser; query_spec_json — filters including max_posts; "
            "manual_posts_json — JSON array of PostRecord dicts; batch_cursor — reserved string; "
            "rows_already — rows already persisted in workbook for max_posts cap."
        ),
        "kwargs": {
            "source_mode": "manual",
            "query_spec_json": "{}",
            "manual_posts_json": "[]",
            "batch_cursor": "",
            "rows_already": 0,
        },
    },
    {
        "name": "linkedin_insights_append_posts_to_xlsx",
        "description": (
            "Appends up to max_rows_this_call PostRecord rows to sheet posts with dedupe by post_url. "
            "Parameters: output_path — workbook path; posts_json — JSON array string; "
            "max_rows_this_call — default 15, max 500."
        ),
        "kwargs": {
            "output_path": "",
            "posts_json": "[]",
            "max_rows_this_call": 15,
        },
    },
    {
        "name": "linkedin_insights_rank_posts",
        "description": (
            "Keyword overlap rerank for a JSON posts array. "
            "Parameters: posts_json — JSON array; query_text — free-text query for scoring."
        ),
        "kwargs": {
            "posts_json": "[]",
            "query_text": "",
        },
    },
]


def main() -> int:
    token = os.environ.get("EXTELLA_TOKEN") or os.environ.get("EXTELLA_API_TOKEN")
    if not token:
        print("Missing EXTELLA_TOKEN (or EXTELLA_API_TOKEN)", file=sys.stderr)
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

    for spec in EXPERTS:
        name = spec["name"]
        code = _load_code(name)
        payload = {
            "name": name,
            "description": spec["description"],
            "code": code,
            "kwargs": spec["kwargs"],
            "cspl": "fython",
        }
        url = f"{base}/api/expert/save"
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        if r.status_code != 200:
            print(f"FAIL {name} HTTP {r.status_code}: {r.text[:500]}", file=sys.stderr)
            return 1
        try:
            data = r.json()
        except json.JSONDecodeError:
            print(f"OK {name} (non-json body)", file=sys.stderr)
            continue
        if data.get("status") != "success":
            print(f"FAIL {name}: {data}", file=sys.stderr)
            return 1
        print(f"OK {name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
