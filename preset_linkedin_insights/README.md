# LinkedIn Insights → Excel (Extella preset)

Chat-only workflow driven by the English master concept **`LinkedInInsights_Master`**. No separate UI and no intermediate database: a single growing `.xlsx` file is the durable artifact.

## Repository layout

| Path | Purpose |
|------|---------|
| [MVP_STRATEGY.md](MVP_STRATEGY.md) | MVP `source_mode` decision (`manual` default) and scope |
| [concepts/LinkedInInsights_Master.md](concepts/LinkedInInsights_Master.md) | Master concept (entry + orchestration) |
| [concepts/LinkedInInsights_PostRecordContract.md](concepts/LinkedInInsights_PostRecordContract.md) | Row schema, Excel columns, dedupe, batch size |
| [concepts/LinkedInInsights_FilterCatalog.md](concepts/LinkedInInsights_FilterCatalog.md) | Filter matrix by `source_mode` |
| [concepts/LinkedInInsights_LegalNotice.md](concepts/LinkedInInsights_LegalNotice.md) | Compliance + required API headers for nested calls |
| [concepts/LinkedInInsights_ChatUX.md](concepts/LinkedInInsights_ChatUX.md) | S0–S5 chat templates (`RUN CONFIG`, progress lines) |
| [experts/](experts/) | `fython` expert bodies (`*.py`) |
| [scripts/bootstrap_experts.py](scripts/bootstrap_experts.py) | Publishes experts to Extella |
| [scripts/upload_concepts.py](scripts/upload_concepts.py) | Uploads all `concepts/*.md` via `/api/concept/add` |
| [scripts/requirements-scripts.txt](scripts/requirements-scripts.txt) | `requests` for helper scripts |

## Expert names (exact)

- `linkedin_insights_init_excel_workbook`
- `linkedin_insights_collect_posts_batch`
- `linkedin_insights_append_posts_to_xlsx`
- `linkedin_insights_rank_posts`

## Publish to Extella

Install script dependencies once:

```bash
pip install -r preset_linkedin_insights/scripts/requirements-scripts.txt
```

Experts:

```bash
export EXTELLA_TOKEN="your-token"
# optional:
# export EXTELLA_API_URL="https://api.extella.ai"
# export EXTELLA_PROFILE_ID="default"
# export EXTELLA_AGENT_ID="agent_extella_default"

python3 preset_linkedin_insights/scripts/bootstrap_experts.py
```

Concepts (one API concept per Markdown file):

```bash
python3 preset_linkedin_insights/scripts/upload_concepts.py
```

## Concepts import notes

## Smoke test (manual mode)

1. Run `linkedin_insights_init_excel_workbook` with a chosen `output_path`.
2. Run `linkedin_insights_collect_posts_batch` with `manual_posts_json` containing 1–3 example `PostRecord` objects.
3. Run `linkedin_insights_append_posts_to_xlsx` with `posts_json` set to the JSON array returned in `result.posts` (stringify), repeat with `max_rows_this_call=15`.

## Notes

- `linkedin_insights_collect_posts_batch` returns an error for `official` and `browser` in v1 (reserved; see `MVP_STRATEGY.md`).
- For long-running collection on a user machine, use Extella Desktop `target` device UUID when calling `/api/expert/run` so `output_path` can point to a user-writable folder.
