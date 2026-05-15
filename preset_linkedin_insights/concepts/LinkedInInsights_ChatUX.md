# Concept_Slug: LinkedInInsights_ChatUX

Chat-only UX templates for Extella agent. Referenced from `LinkedInInsights_Master` by **exact slug**. All user-visible prompts may be localized by the agent, but **machine tokens** below stay ASCII.

## Invocation (S0)

**Trigger:** user intends to run the preset and includes the exact slug **`LinkedInInsights_Master`** (see master concept for EN/RU verb examples: `run`, `start`, `запусти`, `старт`, …).

**Do not** require a fixed English-only phrase; Russian commands are first-class.

If the message matches the trigger, reply immediately with S0 below (no extra preamble).

Agent replies:

```
[LinkedInInsights] Starting preset run.
Scope: build one Excel workbook of LinkedIn post rows from your clarifications.
Reply CONFIRM to proceed to topic clarification, or CANCEL.
```

## Topic clarification (S1)

Ask for goal, niche, exclusions. If vague, propose examples:

```
Example queries you can copy/edit:
1) ...
2) ...
3) ...
Paste your final topic as one paragraph.
```

## Filters (S2)

Load filter menu from `LinkedInInsights_FilterCatalog` for the active `source_mode` (v1 default `manual`).

## Confirm QuerySpec (S3)

Agent must print a **RUN CONFIG** block every time after S3:

```
=== RUN CONFIG ===
output_path: /tmp/linkedin_insights_<run_id>.xlsx
source_mode: manual
query_spec_json: {...one line JSON...}
==================
Reply CONFIRM to start collection, or EDIT: <changes>
```

After user confirms, agent must repeat `output_path` at every progress message in S4.

## Execution progress (S4)

After each successful append:

```
[LinkedInInsights] checkpoint ok | batch=# | rows_total=NN | output_path=...
```

## Delivery (S5)

```
[LinkedInInsights] DONE | rows_total=NN | output_path=...
If your client supports file download from worker path, use that path; if using Desktop target, the path is on your machine.
```

## Failure partial success

```
[LinkedInInsights] FAILED after last good checkpoint.
Last known output_path=...
Error: <short message>
```
