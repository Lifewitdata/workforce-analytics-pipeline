# Workforce Operations Analytics — runnable demo

This adds a separate hourly contact-centre operations layer to the existing monthly HR/recruiting analytics project. It does not replace or blend into the monthly HR pack.

## Run from repository root

```bash
python -m pip install -r requirements.txt
python -m ops.build_operations --generate-demo
python -m unittest discover -s tests -p "test_*.py"
streamlit run dashboard/operations_app.py
```

Generated files are in `data/output/operations/`; source-like demo inputs are generated in `data/demo/operations/`. Demo date window defaults to 1 August–25 September 2026; adjust `--start` and `--end` as required.

To replace the deterministic generator with validated CSV imports, supply all five sources together. The code validates required columns, keys, dimensions, duration/score values, assignment intervals and time zones, and drops fields outside the documented allow-list:

```bash
python -m ops.build_operations \\
  --chat-source data/incoming/chat_interactions.csv \\
  --agents-source data/incoming/agents.csv \\
  --assignments-source data/incoming/agent_assignments.csv \\
  --qa-source data/incoming/qa_reviews.csv \\
  --training-source data/incoming/training_events.csv
```

See the complete schemas in [the data contract](docs/operations_data_contract.md). Never commit real employee or customer-level source files.

## Operational outputs

| Output | Grain / purpose |
|---|---|
| `chat_hourly_by_region_language_channel_market_team.csv` | Date-hour-region-language-channel-market-team interaction metrics |
| `hourly_demand_forecast.csv` | Seven-day weekday/hour demand projection by operational segment |
| `shift_allocation.csv` | Early/core/late shift-level required, available, allocated agents and gap |
| `daily_service_commercial_risk.csv` | Daily response, conversion, queue and coverage risk |
| `daily_tracker.csv` | Daily regional operating tracker |
| `weekly_capacity_brief.csv` | Weekly required capacity, allocation and uncovered shifts |
| `monthly_executive_summary.csv` | Monthly region-level service, contracted roster capacity, handling utilisation and conversion proxy |
| `agent_team_productivity.csv`, `team_productivity.csv` | Workload and resolution productivity using synthetic interaction-to-agent assignments |
| `qa_training_split.csv` | Separate QA review outcomes and agent training sessions by team |
| `reason_escalation_deep_dive.csv` | Contact reason and escalation analysis |
| `data_quality_checks.csv` | Executed contract assertions |
| `refresh_manifest.json` | Run ID, provenance, watermarks, row/null counts, checks and configuration |

## Model and limitations

Regions are AMER, EMEA and APAC, with language, channel, market, time zone and team dimensions. Effective-dated assignments resolve transfers using half-open date intervals. Site A/B/C is not used in this operational model. Forecasting is a deterministic weekday-hour baseline combining long-window and recent profiles (65/35); agent demand uses AHT, a 30-minute interval and 82% planning occupancy. Shift allocation is aggregate capacity allocation, not a published individual rota. Risk thresholds currently flag p90 first response above 10 minutes, conversion below 8%, queue wait above 8 minutes and any coverage gap; review them against real SLAs before use.

The revenue field is deliberately named a conversion proxy: no monetary transaction/revenue source exists in this demo. Team productivity is workload/resolution reporting, not a causal or individual quality score. QA and training are split so training time is not counted as productive handling.

See [the operational data contract](docs/operations_data_contract.md) for real HR/chat source schemas, refresh promotion, quality gates and responsible-AI boundaries. The daily GitHub Action only refreshes synthetic data and publishes its artifact; private source ingestion requires an approved adapter and credentials.

## Interactive dashboard and Tableau

Run `streamlit run dashboard/operations_app.py` after the demo build to open the interactive local Operations Command Centre. It includes date/region filters, service-risk segments, hourly forecast, shift allocation, monthly staffing/service summary, team productivity, QA/training and reason analysis.

The existing packaged Tableau workbook remains the monthly HR/recruiting dashboard. The publisher URL currently available in this repository is a Tableau Public profile rather than a confirmed direct workbook URL. See [the Tableau build guide](dashboard/OPERATIONS_TABLEAU_BUILD.md) to connect the operations CSVs as separate data sources. A live Tableau Public URL and genuine Tableau screenshots remain pending publication/exports from the owner's Tableau account; no fabricated links or screenshots are included.
