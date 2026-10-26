# Workforce & Recruiting Tableau Dashboard

**Synthetic educational data.** Monthly history, recruiting records and fictional locations are simulated. Original employee-source provenance remains unconfirmed. Recruiting and employee populations are independent.

## Open the dashboard

- [Download Workforce_Recruiting_Dashboard.twbx](Workforce_Recruiting_Dashboard.twbx)
- [Isfaque Ansari on Tableau Public](https://public.tableau.com/app/profile/isfaque.ansari5273/vizzes)

The web link opens the supplied Tableau Public profile, not a specific visualization. Open the packaged workbook in Tableau and select **Workforce & Recruiting Overview**. Its embedded Hyper extract is included; the supplied workbook bytes are preserved unchanged.

This delivered workbook replaces the previous optional build specification.

## Contents

One dashboard and 12 worksheets:

- Six KPI cards: closing headcount, monthly attrition, time to hire, offer acceptance, overtime share and average tenure.
- Headcount change versus the previous month.
- Headcount and attrition trends.
- Department attrition comparison.
- Department/location heatmap.
- Recruiting summary.

Controls include the reporting month, an illustrative attrition threshold, and department/location filters. Default selection: December 2025, all departments and locations, threshold 2.0%. The threshold is a demonstration setting, not an industry benchmark.

Layout: 1400 × 1600. Scroll vertically to reach the recruiting table.

## Review in Tableau

1. Open the workbook and check that labels, cards and table values are visible.
2. Select December 2025 with all departments and locations.
3. Compare the dashboard with the CSV-derived checkpoints below.
4. Switch the reporting month to March and check that both trend charts retain the full history.
5. Change department, location and threshold controls.
6. Select January; the prior-month headcount comparison should be undefined because December 2024 is absent.

| December 2025 checkpoint | Expected |
|---|---:|
| Closing headcount | 1,233 |
| Monthly attrition | 1.53% |
| Time to hire | 26.1 days |
| Offer acceptance | 87.23% |
| Overtime share | 23.44% |
| Average tenure | 7.9 years |
| Headcount change vs November | -19 |

These are reference results calculated from the project CSV, not a claim of independently executing this workbook in Tableau.

## Data and interpretation

The reference output is [kpi_monthly.csv](../data/output/kpi_monthly.csv), at month + department + fictional location grain. See [KPI definitions](../docs/kpi_definitions.md).

Compute overall rates from summed numerators and denominators. Do not sum headcount across months or average department percentages. Time to hire ends at offer acceptance. Application cohorts and offer decisions have different time bases, so the summary is not a complete sequential recruiting funnel. Undefined ratios should remain null.

The dashboard describes simulated monthly patterns. It cannot establish why employees leave or demonstrate that an intervention reduces attrition.

## Verification scope

The uploaded package opens as a ZIP, its workbook XML parses, and it contains one dashboard, 12 worksheets and Data/workforce.hyper. The supplied workbook was added unchanged. Native Tableau rendering, action execution and exact displayed KPI values have not been independently verified in this environment.
