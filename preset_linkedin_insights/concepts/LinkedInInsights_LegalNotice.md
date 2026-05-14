# Concept_Slug: LinkedInInsights_LegalNotice

Legal, compliance, and API hygiene. Referenced from `LinkedInInsights_Master` by **exact slug**.

## LinkedIn data access

- LinkedIn User Agreement and help articles prohibit unauthorized scraping, bots, and certain automation. Users must not use `browser` mode to violate LinkedIn rules.
- Official Marketing APIs require approved applications and member/organization scopes. Do not store member secrets inside concepts.

## `browser` mode (future)

If implemented later:

- Require explicit user text: `I_ACCEPT_LINKEDIN_AUTOMATION_RISK`.
- Enforce conservative rate limits in the expert (e.g. max 1 navigation every N seconds, max pages per run) — exact numbers must live in the browser expert code comments.
- Prefer headful automation on user device via Extella `target` (Desktop) so credentials stay local.

## Nested REST calls to Extella API

When an expert calls `https://api.extella.ai` (or env `EXTELLA_API_URL`), include headers:

- `X-Auth-Token`: token value
- `Content-Type`: `application/json`
- `X-Profile-Id`: profile id (commonly `default` unless account uses multiple profiles)
- `X-Agent-Id`: agent id (commonly `agent_extella_default` unless customized)

Omitting `X-Profile-Id` / `X-Agent-Id` may break profile-scoped routes.

## Privacy

- Excel may contain PII. Do not echo full spreadsheets back into chat; only counts and `output_path`.
