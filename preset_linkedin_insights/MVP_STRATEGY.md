# MVP strategy — LinkedIn Insights preset

## Default `source_mode` for v1

**Default: `manual`**

- The agent collects post data from the user (pasted URLs, exported snippets, or a JSON array produced by the agent from free text) and passes structured rows into `linkedin_insights_collect_posts_batch` / `linkedin_insights_append_posts_to_xlsx`.
- This avoids shipping LinkedIn Marketing API OAuth and browser automation in the first milestone while still delivering the full **chat → Excel** pipeline.

## Supported modes in the preset (documentation + hooks)

| Mode | v1 status | Notes |
|------|-----------|--------|
| `manual` | **Supported** | Agent + user supply `PostRecord`-shaped JSON; experts validate and append. |
| `official` | **Not implemented** | Requires approved LinkedIn Marketing API product, author/org scope, version headers. Reserved in `LinkedInInsights_FilterCatalog`. |
| `browser` | **Not implemented** | High ToS/account risk; only after explicit user consent flow in `LinkedInInsights_LegalNotice`. |

## Out of scope for v1

- OAuth for LinkedIn, token refresh, and org-wide post discovery.
- Playwright/Selenium flows inside experts (documented as future work behind `browser`).

## Incremental checkpoints

- Batch size **15** rows per append call (configurable via `batch_size` in `QuerySpec` / expert params).
- Single growing `.xlsx` file; dedupe by existing `post_url` column inside the workbook (no separate database).
