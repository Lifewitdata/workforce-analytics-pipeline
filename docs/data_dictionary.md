# Data dictionary

SYNTHETIC EDUCATIONAL DATA — monthly history and recruiting are simulated.

Types and observed examples below describe generated input/output schemas. See KPI definitions and simulation rules for semantics. Source category labels are not decoded without an authoritative source dictionary.

Output grains: master_employees.csv is one row per employee; recruiting_funnel.csv is one row per application; kpi_monthly.csv is one row per report_month + Department + location. Master exit_flag means exit on/before as_of_date; master tenure ends at exit for leavers and at the reporting cutoff otherwise.

## Employee monthly input

| Field | Type | Example |
|---|---|---|
| Age | int64 | 41 |
| Attrition | object | Yes |
| BusinessTravel | object | Travel_Rarely |
| DailyRate | int64 | 1102 |
| Department | object | Sales |
| DistanceFromHome | int64 | 1 |
| Education | int64 | 2 |
| EducationField | object | Life Sciences |
| EmployeeCount | int64 | 1 |
| employee_id | int64 | 1 |
| EnvironmentSatisfaction | int64 | 2 |
| Gender | object | Female |
| HourlyRate | int64 | 94 |
| JobInvolvement | int64 | 3 |
| JobLevel | int64 | 2 |
| JobRole | object | Sales Executive |
| JobSatisfaction | int64 | 4 |
| MaritalStatus | object | Single |
| MonthlyIncome | int64 | 5993 |
| MonthlyRate | int64 | 19479 |
| NumCompaniesWorked | int64 | 8 |
| Over18 | object | Y |
| OverTime | object | Yes |
| PercentSalaryHike | int64 | 11 |
| PerformanceRating | int64 | 3 |
| RelationshipSatisfaction | int64 | 1 |
| StandardHours | int64 | 80 |
| StockOptionLevel | int64 | 0 |
| TotalWorkingYears | int64 | 8 |
| TrainingTimesLastYear | int64 | 0 |
| WorkLifeBalance | int64 | 1 |
| YearsAtCompany | int64 | 6 |
| YearsInCurrentRole | int64 | 4 |
| YearsSinceLastPromotion | int64 | 0 |
| YearsWithCurrManager | int64 | 5 |
| location | object | Site A |
| exit_date | datetime64[ns] | 2025-11-24 00:00:00 |
| hire_date | datetime64[ns] | 2018-12-28 00:00:00 |
| exit_type | object | Voluntary |
| is_synthetic | bool | True |
| report_month | object | 2025-01 |

## Employee master output

| Field | Type | Example |
|---|---|---|
| Age | int64 | 41 |
| Attrition | object | Yes |
| BusinessTravel | object | Travel_Rarely |
| DailyRate | int64 | 1102 |
| Department | object | Sales |
| DistanceFromHome | int64 | 1 |
| Education | int64 | 2 |
| EducationField | object | Life Sciences |
| EmployeeCount | int64 | 1 |
| employee_id | int64 | 1 |
| EnvironmentSatisfaction | int64 | 2 |
| Gender | object | Female |
| HourlyRate | int64 | 94 |
| JobInvolvement | int64 | 3 |
| JobLevel | int64 | 2 |
| JobRole | object | Sales Executive |
| JobSatisfaction | int64 | 4 |
| MaritalStatus | object | Single |
| MonthlyIncome | int64 | 5993 |
| MonthlyRate | int64 | 19479 |
| NumCompaniesWorked | int64 | 8 |
| Over18 | object | Y |
| OverTime | object | Yes |
| PercentSalaryHike | int64 | 11 |
| PerformanceRating | int64 | 3 |
| RelationshipSatisfaction | int64 | 1 |
| StandardHours | int64 | 80 |
| StockOptionLevel | int64 | 0 |
| TotalWorkingYears | int64 | 8 |
| TrainingTimesLastYear | int64 | 0 |
| WorkLifeBalance | int64 | 1 |
| YearsAtCompany | int64 | 6 |
| YearsInCurrentRole | int64 | 4 |
| YearsSinceLastPromotion | int64 | 0 |
| YearsWithCurrManager | int64 | 5 |
| location | object | Site A |
| exit_date | datetime64[ns] | 2025-11-24 00:00:00 |
| hire_date | datetime64[ns] | 2018-12-28 00:00:00 |
| exit_type | object | Voluntary |
| is_synthetic | bool | True |
| as_of_date | datetime64[ns] | 2025-12-31 00:00:00 |
| exit_flag | int64 | 1 |
| tenure_years | float64 | 6.907597535934292 |
| tenure_band | object | 5–<10 years |

## Recruiting input

| Field | Type | Example |
|---|---|---|
| application_id | object | APP00011 |
| applicant_id | object | P00011 |
| Department | object | Research & Development |
| JobRole | object | Laboratory Technician |
| location | object | Site A |
| source | object | Career site |
| apply_date | datetime64[ns] | 2025-01-14 00:00:00 |
| stage_reached | object | Screened |
| offer_decision | object | Not offered |
| decision_date | datetime64[ns] | 2025-02-06 00:00:00 |
| acceptance_date | datetime64[ns] | 2025-02-06 00:00:00 |
| is_synthetic | bool | True |
| screen_date | datetime64[ns] | 2025-01-18 00:00:00 |
| interview_date | datetime64[ns] | 2025-02-13 00:00:00 |
| offer_date | datetime64[ns] | 2025-02-03 00:00:00 |

## Monthly KPI output

| Field | Type | Example |
|---|---|---|
| report_month | object | 2025-01 |
| Department | object | Human Resources |
| location | object | Site A |
| opening | int64 | 12 |
| closing | int64 | 12 |
| hires | int64 | 0 |
| exits | int64 | 0 |
| voluntary | int64 | 0 |
| involuntary | int64 | 0 |
| tenure_sum | float64 | 135.93702943189595 |
| income_sum | int64 | 121164 |
| income_count | int64 | 12 |
| overtime | int64 | 4 |
| overtime_count | int64 | 12 |
| applications | int64 | 14 |
| offers_in_cohort | int64 | 1 |
| accepted | int64 | 0 |
| declined | int64 | 0 |
| pending | int64 | 1 |
| hire_days_sum | float64 | 0.0 |
| average_headcount | float64 | 12.0 |
| attrition_rate | float64 | 0.0 |
| voluntary_rate | float64 | 0.0 |
| involuntary_rate | float64 | 0.0 |
| avg_tenure_years | float64 | 11.328085785991329 |
| avg_monthly_income | float64 | 10097.0 |
| overtime_share | float64 | 0.3333333333333333 |
| time_to_hire_days | float64 | 27.0 |
| funnel_conversion | float64 | 0.07142857142857142 |
| offer_acceptance_rate | float64 | 1.0 |
