#!/usr/bin/env python3
"""Publish preset concepts to Extella without creating duplicates.

For each Markdown file in concepts/:
  1. Read `Concept_Slug: <Name>` from the file (required first-line pattern).
  2. POST /api/concept/list once (cached), then filter rows whose `concept_text` contains `Concept_Slug: <Name>`
     (full scan so **all** duplicates are found; semantic search alone can miss copies).
  3. If multiple matches: keep the **newest** (highest concept_id), POST /api/concept/remove for every older id.
  4. If at least one remains: POST /api/concept/update with full file text.
  5. If none: POST /api/concept/add.

Uses `POST /api/concept/list` for duplicate detection (full scan), then `POST /api/concept/update` / `remove` / `add` as in [Concept_update.md](../../Concept_update.md).

Environment: EXTELLA_TOKEN or EXTELLA_API_TOKEN, optional EXTELLA_API_URL, EXTELLA_PROFILE_ID, EXTELLA_AGENT_ID.

Usage:
  export EXTELLA_TOKEN=...
  python3 preset_linkedin_insights/scripts/publish_concepts.py
  python3 preset_linkedin_insights/scripts/publish_concepts.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError as e:  # pragma: no cover
    raise SystemExit("pip install -r preset_linkedin_insights/scripts/requirements-scripts.txt") from e


ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = ROOT / "concepts"

SLUG_LINE = re.compile(r"^\s*#\s*Concept_Slug:\s*(\S+)\s*$", re.MULTILINE)


def _headers() -> dict:
    token = os.environ.get("EXTELLA_TOKEN") or os.environ.get("EXTELLA_API_TOKEN")
    if not token:
        raise SystemExit("Missing EXTELLA_TOKEN (or EXTELLA_API_TOKEN)")
    base = os.environ.get("EXTELLA_API_URL", "https://api.extella.ai").rstrip("/")
    profile = os.environ.get("EXTELLA_PROFILE_ID", "default")
    agent = os.environ.get("EXTELLA_AGENT_ID", "agent_extella_default")
    return {
        "base": base,
        "headers": {
            "X-Auth-Token": token,
            "Content-Type": "application/json",
            "X-Profile-Id": profile,
            "X-Agent-Id": agent,
        },
    }


def extract_slug(text: str) -> str:
    m = SLUG_LINE.search(text)
    if not m:
        raise ValueError("Missing line '# Concept_Slug: <Name>' in concept file")
    return m.group(1).strip()


def concept_list_all(base: str, headers: dict) -> list[dict]:
    r = requests.post(
        f"{base}/api/concept/list",
        headers=headers,
        json={},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"concept/list HTTP {r.status_code}: {r.text[:400]}")
    data = r.json()
    if data.get("status") != "success":
        raise RuntimeError(f"concept/list bad payload: {data}")
    return list(data.get("results") or [])


def concept_add(base: str, headers: dict, text: str) -> dict:
    r = requests.post(
        f"{base}/api/concept/add",
        headers=headers,
        json={"text": text},
        timeout=60,
    )
    if r.status_code != 200:
        raise RuntimeError(f"concept/add HTTP {r.status_code}: {r.text[:400]}")
    return r.json()


def concept_update(base: str, headers: dict, concept_id: int, new_text: str) -> dict:
    r = requests.post(
        f"{base}/api/concept/update",
        headers=headers,
        json={"concept_id": int(concept_id), "new_text": new_text},
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"concept/update HTTP {r.status_code}: {r.text[:400]}")
    return r.json()


def concept_remove(base: str, headers: dict, concept_id: int) -> dict:
    r = requests.post(
        f"{base}/api/concept/remove",
        headers=headers,
        json={"concept_id": int(concept_id)},
        timeout=60,
    )
    if r.status_code != 200:
        raise RuntimeError(f"concept/remove HTTP {r.status_code}: {r.text[:400]}")
    return r.json()


def matching_rows(results: list[dict], slug: str) -> list[dict]:
    marker = f"Concept_Slug: {slug}"
    out = []
    for row in results:
        cid = row.get("concept_id")
        txt = row.get("concept_text") or ""
        if cid is None:
            continue
        if marker in txt:
            out.append(row)
    return out


def publish_file(base: str, headers: dict, path: Path, dry_run: bool, all_rows: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    slug = extract_slug(text)

    matches = matching_rows(all_rows, slug)
    matches.sort(key=lambda r: int(r["concept_id"]), reverse=True)

    if dry_run:
        print(f"[dry-run] {path.name} slug={slug} matches={len(matches)} ids={[r['concept_id'] for r in matches]}")
        return

    if len(matches) > 1:
        keep_id = int(matches[0]["concept_id"])
        remove_ids = [int(r["concept_id"]) for r in matches[1:]]
        print(f"{path.name}: dedupe slug={slug} keep_id={keep_id} remove_ids={remove_ids}")
        for rid in remove_ids:
            concept_remove(base, headers, rid)
        up = concept_update(base, headers, keep_id, text)
        if up.get("status") != "success":
            raise RuntimeError(f"concept/update failed: {up}")
        print(f"OK update {path.name} -> concept_id={keep_id}")
        return

    if len(matches) == 1:
        cid = int(matches[0]["concept_id"])
        up = concept_update(base, headers, cid, text)
        if up.get("status") != "success":
            raise RuntimeError(f"concept/update failed: {up}")
        print(f"OK update {path.name} -> concept_id={cid}")
        return

    add = concept_add(base, headers, text)
    if add.get("status") != "success":
        raise RuntimeError(f"concept/add failed: {add}")
    print(f"OK add {path.name} -> concept_id={add.get('id')}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print actions only")
    args = ap.parse_args()

    cfg = _headers()
    base, headers = cfg["base"], cfg["headers"]

    files = sorted(CONCEPT_DIR.glob("*.md"))
    if not files:
        print("No concepts found", file=sys.stderr)
        return 1

    print("Fetching concept/list …")
    all_rows = concept_list_all(base, headers)
    print("rows:", len(all_rows))

    for path in files:
        try:
            publish_file(base, headers, path, dry_run=args.dry_run, all_rows=all_rows)
        except Exception as e:
            print(f"FAIL {path.name}: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
