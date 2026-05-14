$extens("include.py")
include("from pathlib import Path", [])
include("import json", [])
include("import datetime", [])
include("import uuid", [])
include("from openpyxl import Workbook", ["extella-pip install openpyxl"])

def linkedin_insights_init_excel_workbook(
    output_path: str = "",
    query_spec_json: str = "{}",
    run_id: str = "",
) -> dict:
    """Create a new workbook with posts + run_meta sheets. See concept LinkedInInsights_PostRecordContract."""
    print("[1/3] init workbook...")
    rid = (run_id or "").strip() or str(uuid.uuid4())
    out = (output_path or "").strip()
    if not out:
        out = str(Path("/tmp") / f"linkedin_insights_{rid}.xlsx")

    path = Path(out).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = [
        "post_url",
        "post_text",
        "post_summary",
        "author_name",
        "author_profile_url",
        "published_at",
        "engagement_likes",
        "engagement_comments",
        "engagement_reposts",
        "source_adapter",
        "fetched_at",
        "dedupe_key",
    ]

    wb = Workbook()
    ws_posts = wb.active
    ws_posts.title = "posts"
    ws_posts.append(headers)

    ws_meta = wb.create_sheet("run_meta")
    ws_meta.append(["key", "value"])
    ws_meta.append(["run_id", rid])
    ws_meta.append(["created_at", datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"])
    ws_meta.append(["query_spec_json", query_spec_json])

    wb.save(str(path))
    print("[3/3] saved:", str(path))
    return {"status": "success", "output_path": str(path), "run_id": rid}
