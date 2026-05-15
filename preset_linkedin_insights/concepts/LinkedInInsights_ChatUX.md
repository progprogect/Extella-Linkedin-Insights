# Concept_Slug: LinkedInInsights_ChatUX

Chat-only UX templates for Extella agent. Referenced from `LinkedInInsights_Master` by **exact slug**. All user-visible prompts may be localized by the agent, but **machine tokens** below stay ASCII.

## Formatting rules (critical)

- **Do not** wrap user-facing status lines in markdown **fenced code blocks** (no triple backticks). Extella chat may mislabel fences as `sql` or other languages and it looks broken.
- Use **plain paragraphs**, optional **bold labels**, or markdown **blockquotes** (`>`) for multi-line templates.

## Invocation + topic (S0 + S1 in one assistant turn)

**Trigger:** user message contains the exact slug **`LinkedInInsights_Master`** plus run intent (`run`, `start`, `запусти`, `старт`, …). See `LinkedInInsights_Master` for examples.

**On trigger, in the SAME reply (no waiting step):**

1. Acknowledge the preset is running (2–4 short lines, plain text).
2. **Immediately** continue with the S1 topic questions below. **Do not** ask for `CONFIRM` / `CANCEL` before topic clarification — the user already started the preset with the run command.
3. Only if the message is ambiguous (slug typo, no run intent), ask **one** short clarification instead of starting.

**Example opening (adapt wording; keep structure, no code fences):**

> **[LinkedInInsights]** Preset **LinkedInInsights_Master** is running.  
> I will build one Excel workbook of post rows (manual mode in v1: you paste or we structure post data together).  
> **What should we look for?** Describe the topic, goal, niche, and exclusions in one message.  
> If unsure, pick one of the example lines below or edit it.

Then continue with S1 examples (same message).

## Topic clarification (S1) — examples block

If the user’s topic is vague, append **numbered example queries** (plain lines, not fenced):

Example queries you can copy/edit:

1. …  
2. …  
3. …  

Ask them to reply with one paragraph as the final topic.

## Filters (S2)

Load filter menu from `LinkedInInsights_FilterCatalog` for the active `source_mode` (v1 default `manual`). Plain text or blockquotes only.

## Confirm QuerySpec (S3)

Only **here** (after topic + filters are agreed) ask for confirmation before calling experts that write files.

Print a **RUN CONFIG** summary as **plain lines** (no triple backticks), for example:

**RUN CONFIG**  
output_path: /tmp/linkedin_insights_<run_id>.xlsx  
source_mode: manual  
query_spec_json: {…single-line JSON…}  

Then ask: reply **CONFIRM** to start collection, or **EDIT:** followed by changes.

After the user confirms, repeat `output_path` in every progress line in S4.

## Execution progress (S4)

After each successful append, one plain line, for example:

**[LinkedInInsights]** checkpoint ok | batch=3 | rows_total=45 | output_path=/path/to/file.xlsx

## Delivery (S5)

**[LinkedInInsights]** DONE | rows_total=NN | output_path=…  
If the client cannot download from the worker path, explain where the file lives for Desktop `target` runs.

## Failure partial success

**[LinkedInInsights]** FAILED after last good checkpoint.  
Last known output_path=…  
Error: short message
