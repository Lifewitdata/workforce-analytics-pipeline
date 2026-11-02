# Operational data contract and governance

## Scope and separation

The operational model is a separate product from the monthly HR/recruiting pack. It does not join operational chat interactions to employee attrition records or claim to be the same workforce. All committed demo records are synthetic and marked `is_synthetic=true`.

## Required source contracts

### Chat interactions (one row per interaction)
Required: `interaction_id` (stable unique key), `created_at` (ISO-8601 timestamp with offset or explicitly documented source timezone), `region` (AMER/EMEA/APAC), `language`, `channel`, `market`, `team`, `offered`, `resolved`, `first_response_minutes`, `handle_minutes`, `converted`, `queue_wait_minutes`, `reason`, `escalated`. Optional: customer pseudonymous key and product/intent fields. Never ingest message bodies or direct identifiers into the analytics mart.

### HR/agent roster (one row per agent per effective interval)
Required: `agent_id` (pseudonymous stable key), `team`, `region`, `language`, `channel`, `time_zone`, `effective_from`, `effective_to` (exclusive, nullable), `contract_hours_week`, `employment_status`. Dates are ISO-8601; each agent must have at most one active assignment on any date. Use effective-dated transfer records; never overwrite history.

### QA/training (one row per reviewed interaction or training event)
Required: event key, interaction or agent key, `event_type` (QA/Training), event timestamp, reviewer/training cohort pseudonymous key, and score/result fields appropriate to event type. Do not conflate training time with productive handling time.

## Validation gates

Reject duplicate keys, missing event timestamps, invalid region/channel/language dimensions, negative durations, invalid status flags, unresolvable agent/interaction keys and overlapping effective assignment intervals. Missing language or region is a failed dimension check, not a catch-all business category. Record row counts, null counts, quarantine counts, source watermark and run ID for each refresh.

## Refresh

GitHub Actions runs the deterministic demo refresh daily at 05:17 UTC and on demand. The workflow uploads outputs as a run artifact; it does not connect to private HR/chat systems. For production, configure approved source credentials as GitHub Actions secrets or a managed identity, replace the demo source adapters, retain least privilege, and never commit credentials. A production refresh should be idempotent by source watermark and partition date, write to a staging area, pass all gates, then atomically promote outputs.

## Responsible AI

AI assistance was used to draft the design, code and documentation. Every published metric is calculated by deterministic Python transformations and checked by automated assertions. Synthetic data is explicitly labelled. Forecasts are a transparent seasonal baseline and planning approximation; they are not presented as model-validated predictions. Staffing outputs are aggregate decision support, not automatic individual scheduling or performance decisions. No AI-generated statement is treated as verified evidence without source-backed validation. A human owner must approve thresholds, inspect exceptions and validate performance before operational use.
