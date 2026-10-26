# Optional one-page Tableau specification

SYNTHETIC EDUCATIONAL DATA. Specification only; no Tableau workbook was built or executed. Excel is the delivered dashboard.

Input: data/output/kpi_monthly.csv, one row per report_month + Department + location. Connect this single fact table without joining the raw employee and recruiting tables.

- Top row: selected-month closing headcount = SUM(closing); attrition = SUM(exits)/((SUM(opening)+SUM(closing))/2); acceptance = SUM(accepted)/(SUM(accepted)+SUM(declined)); time to hire = SUM(hire_days_sum)/SUM(accepted). Guard zero denominators with NULL.
- Middle: closing headcount by report_month as a line. Department and location filters apply to all views. A month parameter controls the KPI cards without truncating the line's full history.
- Bottom: department bar chart for period attrition, with exits and average headcount in the tooltip. Calculate aggregate rates, never average row percentages.
- Label title: Workforce & Recruiting — Synthetic Demo. Add: 2025 history, locations and recruiting simulated; employee and recruiting populations are independent.
- Show pending offers and note that funnel conversion uses application-month cohorts as of each month-end. Do not plot synthetic locations as real geographical sites.
- Export a screenshot only after building and validating in Tableau. Compare the selected-month KPI cards against monthly_totals.csv and Excel.
