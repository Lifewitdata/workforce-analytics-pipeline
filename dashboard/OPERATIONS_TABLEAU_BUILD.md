# Operations dashboard — Tableau build and publishing guide

The operational pipeline publishes Tableau-ready CSV data marts under `data/output/operations/`. Keep them as a separate Tableau data source/model from `kpi_monthly.csv`; do not join agent interactions to the monthly employee attrition population.

## Data sources

Connect to these files after running `python -m ops.build_operations --generate-demo`:

- `chat_hourly_by_region_language_channel_market_team.csv` — operational volume and service trends.
- `hourly_demand_forecast.csv` — future hourly contact demand and staffing requirement.
- `shift_allocation.csv` — shift-level required/available/allocated capacity, including coverage gaps.
- `daily_service_commercial_risk.csv` — risk drivers and priority by operational segment.
- `daily_tracker.csv`, `weekly_capacity_brief.csv`, `monthly_executive_summary.csv` — reporting packs.
- `team_productivity.csv`, `agent_team_productivity.csv`, `qa_training_split.csv`, `reason_escalation_deep_dive.csv` — performance and root-cause views.

## Suggested dashboard layout

1. **Operations overview:** total contacts, average first response, conversion proxy, uncovered shift hours and high-risk segments.
2. **Demand and capacity:** hourly actual/forecast demand, required versus available agents, heatmap by region/language/shift.
3. **Service/commercial risk:** daily risk trend and drill-down by market, language, channel, team, reason and escalation.
4. **People and quality:** team/agent workload, resolution, QA review score and training minutes as separate measures.
5. **Executive pack:** monthly contacts, service levels, roster capacity, handling utilisation and conversion-count proxy.

Use weighted rates from numerators/denominators wherever possible. Treat conversion counts as a proxy, not monetary revenue. Do not publish agent-level views as employee assessments; the demo agent assignments are synthetic.

## Publishing and evidence status

The repository currently contains an existing packaged Tableau workbook for the monthly HR/recruiting pack, not a published operations workbook. The available Tableau Public URL in the README is a profile URL, not a direct workbook URL. Publishing requires the owner to sign in to Tableau Desktop/Public, open the built workbook, publish it, and copy the resulting visualization URL. Export genuine dashboard screenshots from Tableau after checking filters and KPI values. Until those owner-side steps are complete, do not label the profile URL as a direct dashboard link or add mock screenshots.
