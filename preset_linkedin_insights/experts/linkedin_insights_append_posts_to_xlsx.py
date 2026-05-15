$extens("include.py")
include("from pathlib import Path", [])
include("import json", [])
include("import datetime", [])
include("from urllib.parse import urlparse, urlunparse", [])
include("from openpyxl import load_workbook", ["extella-pip install openpyxl"])

def linkedin_insights_append_posts_to_xlsx(
    output_path: str = "",
    posts_json: str = "[]",
    max_rows_this_call: int = 15,
) -> dict:
    """Append PostRecord rows with dedupe by existing post_url column. See LinkedInInsights_PostRecordContract."""
    print("[1/3] append_posts_to_xlsx...")
    out = (output_path or "").strip()
    if not out:
        return {"status": "error", "message": "output_path is required"}

    path = Path(out).expanduser().resolve()
    if not path.exists():
        return {"status": "error", "message": f"Workbook not found: {path}"}

    cap = _safe_int(max_rows_this_call, 15)
    if cap <= 0:
        cap = 15
    if cap > 500:
        cap = 500

    try:
        posts = json.loads(posts_json or "[]")
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid posts_json: {e}"}

    if not isinstance(posts, list):
        return {"status": "error", "message": "posts_json must be a JSON array"}

    wb = load_workbook(filename=str(path))
    if "posts" not in wb.sheetnames:
        return {"status": "error", "message": "Sheet 'posts' missing; run linkedin_insights_init_excel_workbook first"}

    ws = wb["posts"]
    existing = set()
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1, values_only=True):
        val = row[0]
        if val:
            existing.add(_normalize_post_url(str(val)))

    appended = 0
    skipped_dup = 0
    skipped_cap = 0
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    for item in posts:
        if appended >= cap:
            skipped_cap += 1
            continue
        if not isinstance(item, dict):
            continue
        url = (item.get("post_url") or "").strip()
        if not url:
            continue
        key = _normalize_post_url(url)
        if key in existing:
            skipped_dup += 1
            continue

        row = [
            url,
            (item.get("post_text") or "").strip(),
            (item.get("post_summary") or item.get("post_text") or "").strip(),
            (item.get("author_name") or "").strip(),
            (item.get("author_profile_url") or "").strip(),
            (item.get("published_at") or "").strip(),
            _safe_int(item.get("engagement_likes"), 0),
            _safe_int(item.get("engagement_comments"), 0),
            _safe_int(item.get("engagement_reposts"), 0),
            (item.get("source_adapter") or "manual").strip(),
            (item.get("fetched_at") or now).strip(),
            (item.get("dedupe_key") or key or url).strip(),
        ]
        ws.append(row)
        existing.add(key)
        appended += 1

    wb.save(str(path))
    total_rows = ws.max_row - 1
    print("[3/3] saved:", str(path), "appended:", appended, "total_data_rows:", total_rows)
    return {
        "status": "success",
        "output_path": str(path),
        "appended": appended,
        "skipped_duplicate": skipped_dup,
        "skipped_due_to_cap": skipped_cap,
        "rows_total": max(total_rows, 0),
    }


def _normalize_post_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    p = urlparse(u)
    netloc = (p.netloc or "").lower()
    path = (p.path or "").rstrip("/") or "/"
    scheme = (p.scheme or "https").lower()
    return urlunparse((scheme, netloc, path, "", "", ""))


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
