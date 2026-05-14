# Concept_Slug: LinkedInInsights_FilterCatalog

Filter matrix for chat selection. Referenced from `LinkedInInsights_Master` by **exact slug**.

Legend: Supported = user may set in S2. Disabled = show in chat as disabled with reason.

## Rows

| filter_key | description | manual | official | browser |
|------------|-------------|--------|----------|---------|
| `language` | BCP-47 language code filter for ranking/display (e.g. `en`, `ru`, `any`). | Supported | Disabled (API scope not in v1) | Planned (fragile) |
| `date_from` | ISO date inclusive lower bound on `published_at`. | Supported (client-side filter in expert) | Disabled (v1) | Planned |
| `date_to` | ISO date inclusive upper bound on `published_at`. | Supported | Disabled (v1) | Planned |
| `max_posts` | Hard cap on total rows for this run. | Supported | Disabled (v1) | Supported (when implemented) |
| `per_author_cap` | Max rows per unique `author_profile_url`. | Supported | Disabled (v1) | Planned |
| `min_engagement` | Minimum `engagement_likes` threshold (0 = off). | Supported (if user provides metrics) | Disabled (v1) | Planned |
| `author_allowlist` | Newline or comma separated profile URLs to restrict to. | Supported | Supported (primary official path when implemented) | Planned |
| `company_allowlist` | Newline separated company page URLs (official only, future). | Disabled | Planned | Disabled |
| `include_reposts` | Boolean string `true`/`false`. | Supported | Disabled (v1) | Planned |
| `batch_size` | Rows per append checkpoint (default 15, max 500). | Supported | Supported | Supported |

## Chat UX for S2

Agent must print a numbered menu. Example:

```
Filters (reply with lines like: language=en; date_from=2025-01-01; max_posts=120)
1) language: en | ru | any (default any)
2) date_from: YYYY-MM-DD or empty
3) date_to: YYYY-MM-DD or empty
4) max_posts: integer (default 200)
5) per_author_cap: integer (default 0 = unlimited)
6) batch_size: integer (default 15)
```

For `official` / `browser` when still not implemented, agent answers: "This source_mode is reserved; switching to manual for v1 or cancel."
