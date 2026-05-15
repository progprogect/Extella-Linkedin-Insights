$extens("include.py")
include("import json", [])
include("import datetime", [])
include("from urllib.parse import urlparse, urlunparse", [])

def linkedin_insights_collect_posts_batch(
    source_mode: str = "manual",
    query_spec_json: str = "{}",
    manual_posts_json: str = "[]",
    batch_cursor: str = "",
    rows_already: int = 0,
) -> dict:
    """Validate and filter posts for the current batch. v1 implements manual only."""
    print("[1/2] collect_posts_batch...")
    mode = (source_mode or "manual").strip().lower()
    if mode not in ("manual", "official", "browser"):
        return {"status": "error", "message": f"Unknown source_mode: {source_mode}"}

    if mode in ("official", "browser"):
        return {
            "status": "error",
            "message": f"source_mode '{mode}' is not implemented in v1. Use manual or see MVP_STRATEGY.md.",
            "posts": [],
            "batch_cursor": batch_cursor or "",
        }

    try:
        spec = json.loads(query_spec_json or "{}")
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid query_spec_json: {e}", "posts": []}

    try:
        raw_posts = json.loads(manual_posts_json or "[]")
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid manual_posts_json: {e}", "posts": []}

    if not isinstance(raw_posts, list):
        return {"status": "error", "message": "manual_posts_json must be a JSON array", "posts": []}

    max_posts = _safe_int(spec.get("max_posts"), 0)
    already = _safe_int(rows_already, 0)
    remaining_cap = 0
    if max_posts > 0:
        remaining_cap = max(0, max_posts - max(0, already))

    per_author_cap = _safe_int(spec.get("per_author_cap"), 0)
    date_from = (spec.get("date_from") or "").strip()
    date_to = (spec.get("date_to") or "").strip()

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    cleaned = []
    author_counts = {}

    for item in raw_posts:
        if not isinstance(item, dict):
            continue
        url = (item.get("post_url") or "").strip()
        if not url:
            continue
        norm = _normalize_post_url(url)
        author_url = (item.get("author_profile_url") or "").strip()

        if per_author_cap > 0 and author_url:
            c = author_counts.get(author_url, 0)
            if c >= per_author_cap:
                continue

        pub = (item.get("published_at") or "").strip()
        if date_from and len(pub) >= 10 and pub[:10] < date_from[:10]:
            continue
        if date_to and len(pub) >= 10 and pub[:10] > date_to[:10]:
            continue

        row = {
            "post_url": url,
            "post_text": (item.get("post_text") or "").strip(),
            "post_summary": (item.get("post_summary") or item.get("post_text") or "").strip(),
            "author_name": (item.get("author_name") or "").strip(),
            "author_profile_url": author_url,
            "published_at": pub,
            "engagement_likes": _safe_int(item.get("engagement_likes"), 0),
            "engagement_comments": _safe_int(item.get("engagement_comments"), 0),
            "engagement_reposts": _safe_int(item.get("engagement_reposts"), 0),
            "source_adapter": (item.get("source_adapter") or mode).strip(),
            "fetched_at": (item.get("fetched_at") or now).strip(),
            "dedupe_key": (item.get("dedupe_key") or norm or url).strip(),
        }
        cleaned.append(row)
        if author_url:
            author_counts[author_url] = author_counts.get(author_url, 0) + 1
        if remaining_cap > 0 and len(cleaned) >= remaining_cap:
            break

    print("[2/2] collect ok, rows:", len(cleaned))
    return {
        "status": "success",
        "posts": cleaned,
        "batch_cursor": batch_cursor or "",
        "source_mode": mode,
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
