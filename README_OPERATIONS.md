# Workforce Operations Analytics — runnable demo

This adds a separate hourly contact-centre operations layer to the existing monthly HR/recruiting analytics project. It does not replace or blend into the monthly HR pack.

## Run from repository root

```bash
python -m pip install -r requirements.txt
python -m ops.build_operations --generate-demo
python -m unittest discover -s tests -p "test_*.py"
```

Generated files are in `data/output/operations/`; source-like demo inputs are in `data/demo/operations/`. Demo date window defaults to 1 August–25 September 2026; adjust `--start` and `--end` as required.

## Operational outputs

| Output | Grain / purpose |
|---|---|
| `chat_hourly_by_region_language_channel_market_team.csv` | Date-hour-region-language-channel-market-team interaction metrics |
| `hourly_demand_forecast.csv` | Seven-day weekday/hour demand projection by operational segment |
| `shift_allocation.csv` | Early/core/late shift-level required, available, allocated agents and gap |
| `daily_service_commercial_risk.csv` | Daily response, conversion, queue and coverage risk |
| `daily_tracker.csv` | Daily regional operating tracker |
| `weekly_capacity_brief.csv` | Weekly required capacity, allocation and uncovered shifts |
| `monthly_executive_summary.csv` | Monthly region-level service and conversion proxy summary |
| `agent_team_productivity.csv`, `team_productivity.csv` | Workload and resolution productivity (synthetic agent mapping) |
| `qa_training_split.csv` | QA score/review split by training flag and team |
| `reason_escalation_deep_dive.csv` | Contact reason and escalation analysis |
| `data_quality_checks.csv` | Executed contract assertions |

## Model and limitations

Regions are AMER, EMEA and APAC, with language, channel, market, time zone and team dimensions. Effective-dated assignments resolve transfers using half-open date intervals. Site A/B/C is not used in this operational model. Forecasting is a deterministic weekday-hour baseline combining long-window and recent profiles (65/35); agent demand uses AHT, a 30-minute interval and 82% planning occupancy. Shift allocation is aggregate capacity allocation, not a published individual rota. Risk thresholds currently flag p90 first response above 10 minutes, conversion below 8%, queue wait above 8 minutes and any coverage gap; review them against real SLAs before use.

The revenue field is deliberately named a conversion proxy: no monetary transaction/revenue source exists in this demo. Team productivity is workload/resolution reporting, not a causal or individual quality score. QA and training are split so training time is not counted as productive handling.

See [the operational data contract](docs/operations_data_contract.md) for real HR/chat source schemas, refresh promotion, quality gates and responsible-AI boundaries. The daily GitHub Action only refreshes synthetic data and publishes its artifact; private source ingestion requires an approved adapter and credentials.

## Tableau

The existing packaged workbook remains the monthly HR/recruiting dashboard; its publisher link is only a Tableau Public profile, not a verified direct workbook URL. This change does not claim to have published a new Tableau visualization or generated genuine Tableau screenshots. The operational CSV outputs are Tableau-ready and can be connected as separate data sources. A direct Tableau URL can only be added after the owner publishes the workbook to Tableau Public and confirms its URL.
