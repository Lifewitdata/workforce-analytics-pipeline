# Workforce & Recruiting Analytics — KPI definitions

KPI contract | 26 October 2026 | Implemented workflow: Python; Alteryx removed at user request

**SYNTHETIC EDUCATIONAL PROJECT.** The supplied employee file is treated as synthetic teaching data; original provenance remains unconfirmed. The user approved simulated monthly employee history and synthetic recruiting data. Dates and recruiting events generated later will be invented for workflow demonstration, not recovered historical facts. Simulation and KPI computation are now implemented in src/pipeline.py; measured outputs are in data/output/.

## Reporting contract

- Demonstration period: January–December 2025. This is a chosen simulation window, not the source dataset's observation period.
- Fixed random seed: 42. Generation rules and distributions are documented in simulation_rules.md.
- Preserve the uploaded CSV and its original Attrition, YearsAtCompany, OverTime and satisfaction values. Store generated fields separately, with explicit simulated provenance. Do not treat original attributes as measured monthly history.
- Each date uses ISO `YYYY-MM-DD`; calculations use calendar days without time zones.
- Let S be the first day of a selected month and E its last day. `hire_date` is the first employed day. `exit_date` is the first day no longer employed (the last working day plus one); null means no recorded exit by the simulation cutoff.
- An employee is active at end of date D when `hire_date <= D AND (exit_date is null OR exit_date > D)`.
- Opening headcount O = active employees at the end of S−1. Closing headcount C = active employees at the end of E. Average headcount A = (O+C)/2. This is a two-point approximation, not average daily headcount.
- Monthly exits X = employees with S <= exit_date <= E. Monthly hires H = employees with S <= hire_date <= E. With no transfers or rehires, C must equal O+H−X. Same-month hires/exits contribute to both flows, even if absent from both boundary headcounts.
- The simple simulation will use one employment spell per employee and fixed department/location. Transfers and rehires are out of scope. Location labels will be fictional Site A, Site B and Site C, clearly identified as simulated.
- Monthly employee files must include anyone active at any time in the month, plus boundary exit events on S. Required record condition: `hire_date <= E AND (exit_date is null OR exit_date >= S)`. This retains exits needed for reconciliation. Employee-month uniqueness is required.
- Annual or multi-month attrition is NOT the sum or unweighted mean of monthly percentages. For a selected contiguous interval, recompute exits and opening/closing headcount at its boundaries. Label it as that interval's rate; do not annualize it.
- Zero denominators return null / N/A, never zero or infinity. Missing required values are reported as validation exceptions; do not silently impute. Round only for display: counts as integers, percentages to two decimal places, durations and income to two decimal places.

## Ten KPIs

All employee metrics may be grouped by department and fictional location. Exact source field names for generated inputs below form the implementation contract.

| # | KPI | Exact formula and population | Fields | Data status |
|---|---|---|---|---|
| 1 | Closing headcount | Distinct employee_id satisfying the active-at-E condition. Also show O and A as supporting measures. | employee_id, hire_date, exit_date | Simulated dates required |
| 2 | Attrition rate | 100 × X / A. X counts distinct employment exits in the selected period; A uses opening and closing headcount for the same period and group. | employee_id, hire_date, exit_date | Simulated period attrition; uses average headcount |
| 3 | Voluntary exit rate | 100 × V / A, where V is the distinct exits in-period with exit_type = Voluntary. Display V as a supporting count. | Above plus exit_type | Exit type is simulated, not inferred from Attrition |
| 4 | Involuntary exit rate | 100 × I / A, where I is the distinct exits in-period with exit_type = Involuntary. Display I as a supporting count. | Above plus exit_type | Exit type is simulated |
| 5 | Average active tenure | Sum of (E − hire_date).days / 365.25 over employees active at E, divided by C. Display in years. | employee_id, hire_date, exit_date | Derived from simulated dates; not the original YearsAtCompany |
| 6 | Time to hire | Mean of (acceptance_date − apply_date).days for distinct applications accepted during the selected period. This ends at acceptance, not employment start or requisition opening. | application_id, apply_date, acceptance_date, offer_decision | Synthetic recruiting; accepted applications only |
| 7 | Offer acceptance rate | 100 × accepted offers / (accepted offers + declined offers), counting offers whose decision_date falls in-period. Exclude pending offers; separately display their count as of E. | application_id, offer_date, decision_date, offer_decision | Synthetic recruiting; decision-based denominator |
| 8 | Average monthly income by level | Sum MonthlyIncome / number of employees with non-null MonthlyIncome, restricted to active-at-E employees and each JobLevel. Display valid-income count and flag missing income. | employee_id, JobLevel, MonthlyIncome, hire_date, exit_date | Source income reused in simulated active population; currency unspecified |
| 9 | Overtime share | 100 × active-at-E employees with OverTime = Yes / active-at-E employees with OverTime in {Yes, No}. Display valid-response count; flag missing/invalid values. | employee_id, OverTime, hire_date, exit_date | Source Yes/No attribute held fixed; no hours or historical overtime measurements |
| 10 | Application-to-offer conversion | 100 × distinct applications from the selected apply-date cohort with offer_date <= E / all distinct applications in that apply-date cohort. A cohort is the selected apply-date interval; outcomes are evaluated as of E. | application_id, apply_date, offer_date | Synthetic recruiting; recent cohorts have less time to progress |

For generated exits, require exactly one of Voluntary or Involuntary, so V+I=X. With a real dataset, unknown exit reasons must remain Unknown and be shown separately rather than forced into either category.

## Recruiting timing and funnel rules

- Grain: one application per role per applicant; applicant_id identifies the person, application_id identifies the application. Even if the first generator creates one application per applicant, metrics use application_id.
- Ordered stages: Applied → Screened → Interviewed → Offered → Accepted. Stage reached records the furthest stage, while offer_decision records Accepted, Declined or Pending. A decline remains at Offered.
- Generate stage dates (screen_date, interview_date, offer_date) so each monthly as-of view can exclude future progress. A final stage_reached alone cannot reconstruct earlier funnel stages.
- Require apply_date <= screen_date <= interview_date <= offer_date <= decision_date whenever those dates exist. Accepted applications require acceptance_date = decision_date. Pending offers have no decision_date or acceptance_date; declined offers have no acceptance_date.
- For accepted applications: time to hire measures application-to-acceptance. Acceptance does not prove the applicant started work. A hire_date or actual_start_date is needed for employment starts.
- Monthly recruiting files are application cohorts partitioned by apply month, not repeated snapshots. Unioning them must retain unique application_id. Later decisions update the relevant cohort file; a refresh must not append a second copy of that application.
- If reporting supplementary stage conversion, use distinct applications reaching the later stage by E divided by those reaching the preceding stage by E, from the same apply-date cohort. Never divide a month's offers by unrelated applications received that month.
- Do not compare immature cohorts as if follow-up were equal. Display cohort age or use equally mature cohorts when interpreting conversion. The initial implementation uses the as-of cutoff and explicitly labels the maturity limitation.

## Join keys and grain safeguards

1. Employee source key: EmployeeNumber, renamed employee_id and treated as an identifier. Monthly employee key: (employee_id, snapshot_month). Repeated employees across different months are expected, not duplicate people to delete indiscriminately.
2. Recruiting key: application_id; applicant_id is not an employee ID. There is no source crosswalk connecting this synthetic recruiting population to the uploaded employee population.
3. Keep employee and recruiting facts separate. Aggregate each independently to (report_month, department, location), then join those summary tables one-to-one to a complete calendar/group scaffold, preserving every allowed group. Verify key uniqueness before joining. A reporting calendar/group scaffold should distinguish a known zero from absent source coverage.
4. Recruitment metrics use the role's department/location; employee metrics use the employee's fixed department/location. Validate both against shared allowed labels. Do not join raw employees to raw applicants using department or role: that creates many-to-many row multiplication.
5. The combined pack compares group-level workforce and recruiting metrics. It cannot claim applicants became particular employees, or that recruiting source predicts employee attrition. No random person-level matches will be created.
6. Keep numerator and denominator columns in outputs. Compute overall rates from summed counts, not averages of department rates. For average duration/income/tenure, retain sums and valid counts. Distinct people and closing headcounts cannot be summed across months.

## Tenure bands and interpretation

For monthly summaries, use exact elapsed days divided by 365.25: <1 year; 1–<3; 3–<5; 5–<10; 10+ years. For active headcount use tenure at E. For exits use tenure at exit_date. Label these populations separately: exit-band counts divided by closing active-band counts are not a valid tenure-band attrition rate.

For the later overtime/tenure/satisfaction attrition analysis, use each original uploaded employee row once. Define original dataset attrition share as count(Attrition = Yes) / count(valid Yes/No), with bands based on original YearsAtCompany. Do not pool repeated monthly records as independent employees. Do not use generated dates, exit types or locations as evidence of real attrition drivers. Associations in synthetic teaching data support a demonstration and hypotheses, not causal claims or real HR intervention evidence.

## Review checkpoint

Review average versus opening headcount, dataset attrition share versus period attrition rate, offer decision timing, cohort conversion and aggregation before joins. The Python implementation generates the simulation and verifies outputs. See validation_log.md and optimization_log.md for measured results. No Alteryx implementation is included.
