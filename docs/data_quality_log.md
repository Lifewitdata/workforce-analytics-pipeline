# Data quality log

**Project update:** this section records the initial source-only profile. The completed Python project subsequently generated explicitly simulated inputs with user approval; see simulation_rules.md and validation_log.md. Alteryx was removed from scope.

Project: Workforce & Recruiting Analytics Pipeline
Profile date: 26 October 2026

**Data status: treat as synthetic educational data, not real workforce evidence.** The schema resembles the IBM HR Attrition teaching dataset; the uploaded CSV itself does not establish original provenance. Please confirm the source URL. At the initial source-profile stage, no dates, months or recruiting records had been generated. Source file remains unchanged.

Source: `HR-Employee-Attrition.csv`; SHA-256: `df7985d643392e2a09fd66a1833d9bb1fc4a6525ffd3934cb61926b4590201e2`.
Profiled using Python/pandas 2.2.3. Row count: 1,470; columns: 35.

## Checks and decisions

| Issue/check | Observed result | Decision | Reason |
|---|---|---|---|
| Nulls | 0 null cells | No imputation needed | No parsed missing values |
| Blank text | 0 blank cells | No blank replacement needed | Checked empty and whitespace-only values |
| Duplicate rows | 0 | Retain all rows | No exact duplicates |
| EmployeeNumber | 1470 unique; 0 duplicate IDs | Candidate employee key; retain as identifier | Unique in this file; future months require employee ID plus snapshot month and duplicate checks |
| Categorical labels | No leading/trailing whitespace or case-only collisions in text columns | Preserve source labels | Different punctuation is not itself an error; document any later display mapping |
| Constant fields | EmployeeCount=1, Over18=Y, StandardHours=80 | Propose dropping from analytical output only; keep raw | No variation; StandardHours cannot measure actual overtime hours |
| Attrition | Yes=237; No=1233; Yes share=16.1224% | Use only as dataset attrition share for now | Unknown observation window; this is not a monthly or annual attrition rate |
| Date formats | No date columns | Not testable; do not reconstruct dates from tenure | YearsAtCompany is a duration, not a dated event |
| Monthly headcount / attrition | No snapshot date, hire date or exit date | Blocked pending dated data or explicit simulation approval | Splitting rows into files does not create monthly workforce history |
| Location / exit type | No location or voluntary/involuntary field | Unavailable; do not infer | Department and distance are not location; Attrition does not describe exit reason |
| Recruiting | No applicant, application, offer or acceptance data | Await recruiting file or synthetic generation approval | Hiring speed, offer acceptance and funnel conversion cannot be measured here |
| Income semantics | MonthlyIncome present; currency unspecified; MonthlyRate is separate | Keep units unspecified until source confirmed; do not substitute MonthlyRate | Currency and rate meanings are not established by CSV |
| Tenure consistency | 0 records with company tenure above total experience; 0 with role, promotion or manager tenure above company tenure | Retain | These basic logical checks pass; zero years can represent less than a year |
| Join risks | No employee-to-applicant crosswalk | No person-level recruiting join is currently possible | Do not equate applicant ID and EmployeeNumber; department/role joins between raw tables can multiply rows. Consider separately aggregated tables only after agreeing grain, dates and keys |

## Column profile

Types are pandas-inferred storage types; integer category codes and IDs are not continuous measures. Rating meanings require a source dictionary.

| Column | Type | Nulls | Distinct | Range / labels |
|---|---|---|---|---|
| Age | int64 | 0 | 43 | 18 to 60 |
| Attrition | object | 0 | 2 | No; Yes |
| BusinessTravel | object | 0 | 3 | Non-Travel; Travel_Frequently; Travel_Rarely |
| DailyRate | int64 | 0 | 886 | 102 to 1499 |
| Department | object | 0 | 3 | Human Resources; Research & Development; Sales |
| DistanceFromHome | int64 | 0 | 29 | 1 to 29 |
| Education | int64 | 0 | 5 | 1 to 5 |
| EducationField | object | 0 | 6 | Human Resources; Life Sciences; Marketing; Medical; Other; Technical Degree |
| EmployeeCount | int64 | 0 | 1 | 1 to 1 |
| EmployeeNumber | int64 | 0 | 1470 | 1 to 2068 |
| EnvironmentSatisfaction | int64 | 0 | 4 | 1 to 4 |
| Gender | object | 0 | 2 | Female; Male |
| HourlyRate | int64 | 0 | 71 | 30 to 100 |
| JobInvolvement | int64 | 0 | 4 | 1 to 4 |
| JobLevel | int64 | 0 | 5 | 1 to 5 |
| JobRole | object | 0 | 9 | Healthcare Representative; Human Resources; Laboratory Technician; Manager; Manufacturing Director; Research Director; Research Scientist; Sales Executive; Sales Representative |
| JobSatisfaction | int64 | 0 | 4 | 1 to 4 |
| MaritalStatus | object | 0 | 3 | Divorced; Married; Single |
| MonthlyIncome | int64 | 0 | 1349 | 1009 to 19999 |
| MonthlyRate | int64 | 0 | 1427 | 2094 to 26999 |
| NumCompaniesWorked | int64 | 0 | 10 | 0 to 9 |
| Over18 | object | 0 | 1 | Y |
| OverTime | object | 0 | 2 | No; Yes |
| PercentSalaryHike | int64 | 0 | 15 | 11 to 25 |
| PerformanceRating | int64 | 0 | 2 | 3 to 4 |
| RelationshipSatisfaction | int64 | 0 | 4 | 1 to 4 |
| StandardHours | int64 | 0 | 1 | 80 to 80 |
| StockOptionLevel | int64 | 0 | 4 | 0 to 3 |
| TotalWorkingYears | int64 | 0 | 40 | 0 to 40 |
| TrainingTimesLastYear | int64 | 0 | 7 | 0 to 6 |
| WorkLifeBalance | int64 | 0 | 4 | 1 to 4 |
| YearsAtCompany | int64 | 0 | 37 | 0 to 40 |
| YearsInCurrentRole | int64 | 0 | 19 | 0 to 18 |
| YearsSinceLastPromotion | int64 | 0 | 16 | 0 to 15 |
| YearsWithCurrManager | int64 | 0 | 18 | 0 to 17 |

## Outlier screening

Exploratory rule: values strictly below Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR, using pandas default linear quantiles. Exclude identifiers, constant fields and ordinal category codes. Counts below are per column, not distinct employee totals. Flags are not proven errors: retain values pending business context; no removal or winsorization performed.

| Field | Lower fence | Upper fence | Flagged rows |
|---|---|---|---|
| Age | 10.5 | 62.5 | 0 |
| DailyRate | -573 | 2195 | 0 |
| DistanceFromHome | -16 | 32 | 0 |
| HourlyRate | -5.625 | 137.375 | 0 |
| MonthlyIncome | -5291 | 16581 | 114 |
| MonthlyRate | -10574.8 | 39083.2 | 0 |
| NumCompaniesWorked | -3.5 | 8.5 | 52 |
| PercentSalaryHike | 3 | 27 | 0 |
| TotalWorkingYears | -7.5 | 28.5 | 63 |
| TrainingTimesLastYear | 0.5 | 4.5 | 238 |
| YearsAtCompany | -6 | 18 | 104 |
| YearsInCurrentRole | -5.5 | 14.5 | 21 |
| YearsSinceLastPromotion | -4.5 | 7.5 | 107 |
| YearsWithCurrManager | -5.5 | 14.5 | 14 |

## Department coverage

| Department | Records |
|---|---|
| Research & Development | 961 |
| Sales | 446 |
| Human Resources | 63 |

## Initial review decisions (resolved where noted)

- Confirm the data source and synthetic status; provide a source dictionary if available.
- Alteryx Designer Cloud access was confirmed from user screenshots, then Alteryx was removed from project scope at the user’s request.
- User approved a seeded synthetic recruiting dataset; implemented with seed 42.
- User approved simulated monthly history; dates, locations and exit types are explicitly labelled and documented in simulation_rules.md.
- Learn the distinction between a dataset attrition share and a period attrition rate using opening or average headcount.

The source-only profile above is preserved as the initial audit. Later input/output validation, measured optimization and workbook verification are recorded separately. No Alteryx workflow has been run.
