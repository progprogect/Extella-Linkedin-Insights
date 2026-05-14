# Concept_Slug: LinkedInInsights_PostRecordContract

Canonical English specification for row shape, Excel layout, deduplication, and batching. Other concepts and experts must reference this concept by **exact slug** `LinkedInInsights_PostRecordContract`.

## PostRecord (JSON object)

All string fields default to empty string if unknown. Numbers default to `0` or may be omitted when unknown (expert normalizes to `0`).

| Field | Type | Description |
|-------|------|-------------|
| `post_url` | string | Canonical post URL (used for dedupe). |
| `post_text` | string | Full post text when available. |
| `post_summary` | string | Short summary; may equal `post_text` if no summarization ran. |
| `author_name` | string | Display name. |
| `author_profile_url` | string | Profile URL. |
| `published_at` | string | ISO-8601 datetime or best-effort parseable date string. |
| `engagement_likes` | int | Like/reaction count if available. |
| `engagement_comments` | int | Comment count if available. |
| `engagement_reposts` | int | Repost/share count if available. |
| `source_adapter` | string | e.g. `manual`, `official`, `browser`. |
| `fetched_at` | string | ISO-8601 when the row was collected (set by experts). |
| `dedupe_key` | string | Normally equal to normalized `post_url`; experts may normalize (strip tracking query params). |

## Excel workbook layout

- Sheet **`posts`**: row 1 = headers, row 2+ = data.
- Header order (exact column order):

1. `post_url`
2. `post_text`
3. `post_summary`
4. `author_name`
5. `author_profile_url`
6. `published_at`
7. `engagement_likes`
8. `engagement_comments`
9. `engagement_reposts`
10. `source_adapter`
11. `fetched_at`
12. `dedupe_key`

- Optional sheet **`run_meta`** (created by `linkedin_insights_init_excel_workbook`): stores `query_spec_json`, `source_mode`, `run_id`, `created_at`.

## Deduplication rule (no external database)

Before appending, `linkedin_insights_append_posts_to_xlsx` reads all existing values in column **`post_url`** (sheet `posts`) and skips any incoming row whose `post_url` (after the same normalization) already exists.

## Checkpoint batch size

- Default **15** new rows maximum per `linkedin_insights_append_posts_to_xlsx` call (agent may split larger arrays across multiple calls).
- Configurable expert param: `max_rows_this_call` (int, default 15, cap 500).

## Expert parameters (additional)

### `linkedin_insights_collect_posts_batch`

- `rows_already` (int, default `0`): pass current total rows already persisted in the workbook (from the last `linkedin_insights_append_posts_to_xlsx` `rows_total`) so `max_posts` in `query_spec_json` can cap **total** rows across batches without a database.

## Exact expert names (do not rename without updating all concepts)

- `linkedin_insights_init_excel_workbook`
- `linkedin_insights_collect_posts_batch`
- `linkedin_insights_append_posts_to_xlsx`
- `linkedin_insights_rank_posts`
