# Concept_Slug: LinkedInInsights_Master

English master concept for the Extella chat-only preset **LinkedIn Insights → Excel**.

## Invocation — treat as START (any language)

If the user message **contains the exact slug** `LinkedInInsights_Master` together with any common “run” intent, you MUST start this preset immediately (S0), without asking unrelated questions first.

**Recognized patterns (non-exhaustive; case-insensitive where noted):**

- English: `run LinkedInInsights_Master`, `start LinkedInInsights_Master`, `execute LinkedInInsights_Master`, `launch LinkedInInsights_Master`
- Russian: `запусти LinkedInInsights_Master`, `старт LinkedInInsights_Master`, `запуск LinkedInInsights_Master`, `выполни LinkedInInsights_Master`, `начни LinkedInInsights_Master`

**Minimum match rule:** substring `LinkedInInsights_Master` (exact spelling, PascalCase) **plus** a verb that reasonably means run/start, OR the user explicitly says this is the preset they want after you name it.

If the user writes a **different** master name by mistake, ask one short clarification listing the correct slug `LinkedInInsights_Master`.

## Agent MUST do on trigger

1. Confirm preset start using the S0 template in `LinkedInInsights_ChatUX`.
2. Load and follow (in full): `LinkedInInsights_PostRecordContract`, `LinkedInInsights_FilterCatalog`, `LinkedInInsights_LegalNotice`, `LinkedInInsights_ChatUX`.
3. Proceed S1→S5 and call experts by **exact** names listed below.

## Non-negotiable references (exact names)

Concepts (read in full before executing):

- `LinkedInInsights_PostRecordContract`
- `LinkedInInsights_FilterCatalog`
- `LinkedInInsights_LegalNotice`
- `LinkedInInsights_ChatUX`

Experts (call via Extella expert runner using **exact** `expert_name`):

- `linkedin_insights_init_excel_workbook`
- `linkedin_insights_collect_posts_batch`
- `linkedin_insights_append_posts_to_xlsx`
- `linkedin_insights_rank_posts`

Never use numeric `concept_id` as the only pointer to another concept.

## High-level behavior

1. Follow state machine templates in `LinkedInInsights_ChatUX` (S0–S5).
2. Default `source_mode` = `manual` (see repository `MVP_STRATEGY.md` in the preset folder for rationale).
3. Build **one** `.xlsx` path early (`run_id` UUID) and reuse it for all append calls. Always show `output_path` in progress messages.
4. For `manual` collection, the user (or agent from pasted content) supplies JSON arrays of `PostRecord` objects. Validate required keys against `LinkedInInsights_PostRecordContract`.
5. Optional: call `linkedin_insights_rank_posts` on each batch JSON **before** append when user asked for relevance sorting.
6. Incremental safety: never accumulate unbounded rows in chat. Pass at most **15** (or user `batch_size`) items per `linkedin_insights_append_posts_to_xlsx` call.

## Ordered execution recipe (happy path)

1. `linkedin_insights_init_excel_workbook` with params:
   - `output_path`: chosen absolute path (prefer Desktop folder when `target` device execution is used)
   - `query_spec_json`: compact JSON string of the agreed spec
   - `run_id`: UUID string
2. Loop until `max_posts` reached or user says STOP:
   - `linkedin_insights_collect_posts_batch` with `source_mode`, `query_spec_json`, `manual_posts_json`, and `rows_already` set to the last known `rows_total` from the previous append (use `0` on the first iteration).
   - If posts returned: optionally `linkedin_insights_rank_posts`.
   - `linkedin_insights_append_posts_to_xlsx` with same `output_path` and `posts_json` string.
3. Final chat message per `LinkedInInsights_ChatUX` S5.

## Failure handling

- If an expert returns `status != success`, stop the loop, surface the error, still print last `output_path`.
- Never print secrets (tokens) in chat.

## Extella CSPL / `fython` note

Experts are standard `fython` unless you intentionally ship a long-running collector; then use `nohup` only for that expert and keep Excel writes in a path shared with subsequent steps (document `output_path` in RUN CONFIG).

**`fython` entrypoint:** the **first** top-level `def` in the expert source must be the exported expert function (name matches `expert_name`). Helpers go **below** it — see `LinkedInInsights_PostRecordContract`.
