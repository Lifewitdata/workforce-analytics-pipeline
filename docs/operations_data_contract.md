# Operational data contract and governance

## Scope and separation

The operational model is a separate product from the monthly HR/recruiting pack. It does not join operational chat interactions to employee attrition records or claim to be the same workforce. All committed demo records are synthetic and marked `is_synthetic=true`.

## Required source contracts

### Chat interactions (one row per interaction)
Required: `interaction_id` (stable unique key), `created_at` (ISO-8601 local wall-clock timestamp), `time_zone` (valid IANA timezone for that local timestamp), `region` (AMER/EMEA/APAC), `language`, `channel`, `market`, `team`, `offered`, `resolved`, `first_response_minutes`, `handle_minutes`, `converted`, `queue_wait_minutes`, `reason`, `escalated`. No free-text message content or direct customer identifiers are accepted. The ingestion allow-list deliberately drops extra columns; source-specific optional fields must be separately reviewed and added to the contract before use.

### HR/agent roster and effective-dated assignment history
The base roster (`agents.csv`) has one row per pseudonymous agent: `agent_id`, `team`, `home_region`, `home_language`, `time_zone`, `contract_hours_week`, `employment_status`. The assignment history (`agent_assignments.csv`) has `agent_id`, `effective_from`, `effective_to` (exclusive, nullable), `region`, `language`, `channel`, `team`, `time_zone`. Dates are ISO-8601; each agent must have at most one active assignment on any date. Use half-open intervals [from,to); never overwrite history.

### QA and training (separate source tables)
QA review rows use a unique `interaction_id`, `qa_score` (0–100), and review status (`reviewed` binary). Training event rows use a unique `training_event_id`, pseudonymous `agent_id`, training date, duration in minutes, module/category and completion status. Do not conflate training time with productive handling time. The demo uses separate `qa_training.csv` and `training_events.csv` sources. The CLI accepts `--chat-source`, `--agents-source`, `--assignments-source`, `--qa-source` and `--training-source`; all five must be supplied together. Fields outside the required schema are dropped before transformation to avoid carrying unapproved source columns into the mart.

## Validation gates

Reject duplicate keys, missing event timestamps, invalid region/channel/language dimensions, negative durations, invalid status flags, unresolvable agent/interaction keys and overlapping effective assignment intervals. Missing language or region is a failed dimension check, not a catch-all business category. Record row counts, null counts, quarantine counts, source watermark and run ID for each refresh.

## Refresh

GitHub Actions runs the deterministic demo refresh daily at 05:17 UTC, on pull requests and on demand. The workflow uploads outputs as a run artifact; it does not connect to private HR/chat systems. Each successful run writes `refresh_manifest.json` with a unique run ID, refresh timestamp, requested/actual time window, latest local event watermark by region/time zone, source/output row counts, null counts, provenance, check totals and model configuration. The current quarantine policy is fail-fast: invalid input aborts before a successful manifest is promoted. For production, configure approved source credentials as GitHub Actions secrets or a managed identity, replace the demo source adapters, retain least privilege, and never commit credentials. A production refresh should be idempotent by source watermark and partition date, write to a staging area, pass all gates, then atomically promote outputs.

## Responsible AI

AI assistance was used to draft the design, code and documentation. Every published metric is calculated by deterministic Python transformations and checked by automated assertions. Synthetic data is explicitly labelled. Forecasts are a transparent seasonal baseline and planning approximation; they are not presented as model-validated predictions. Staffing outputs are aggregate decision support, not automatic individual scheduling or performance decisions. No AI-generated statement is treated as verified evidence without source-backed validation. A human owner must approve thresholds, inspect exceptions and validate performance before operational use.
