$extens("include.py")
include("import json", [])
include("import re", [])

def linkedin_insights_rank_posts(
    posts_json: str = "[]",
    query_text: str = "",
) -> dict:
    """Lightweight keyword overlap scoring (no external ML). Descending score."""
    print("[1/2] rank_posts...")
    try:
        posts = json.loads(posts_json or "[]")
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid posts_json: {e}", "posts": []}

    if not isinstance(posts, list):
        return {"status": "error", "message": "posts_json must be a JSON array", "posts": []}

    tokens = _tokenize(query_text)
    if not tokens:
        return {"status": "success", "posts": posts, "note": "empty query_text; order unchanged"}

    def score(p: dict) -> int:
        blob = f"{p.get('post_text','')} {p.get('post_summary','')} {p.get('author_name','')}".lower()
        s = 0
        for t in tokens:
            if t in blob:
                s += blob.count(t)
        return s

    ranked = sorted(posts, key=lambda p: score(p) if isinstance(p, dict) else 0, reverse=True)
    print("[2/2] ranked:", len(ranked))
    return {"status": "success", "posts": ranked}


def _tokenize(q: str):
    q = (q or "").lower()
    return [t for t in re.split(r"[^a-z0-9_+-]+", q) if len(t) >= 3]
