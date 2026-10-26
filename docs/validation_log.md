# Validation log

SYNTHETIC EDUCATIONAL DATA — monthly history and recruiting are simulated.

| Check | Result | Detail |
|---|---|---|
| File month employees_2025-01.csv | PASS |  |
| File month employees_2025-02.csv | PASS |  |
| File month employees_2025-03.csv | PASS |  |
| File month employees_2025-04.csv | PASS |  |
| File month employees_2025-05.csv | PASS |  |
| File month employees_2025-06.csv | PASS |  |
| File month employees_2025-07.csv | PASS |  |
| File month employees_2025-08.csv | PASS |  |
| File month employees_2025-09.csv | PASS |  |
| File month employees_2025-10.csv | PASS |  |
| File month employees_2025-11.csv | PASS |  |
| File month employees_2025-12.csv | PASS |  |
| File cohort recruiting_2025-01.csv | PASS |  |
| File cohort recruiting_2025-02.csv | PASS |  |
| File cohort recruiting_2025-03.csv | PASS |  |
| File cohort recruiting_2025-04.csv | PASS |  |
| File cohort recruiting_2025-05.csv | PASS |  |
| File cohort recruiting_2025-06.csv | PASS |  |
| File cohort recruiting_2025-07.csv | PASS |  |
| File cohort recruiting_2025-08.csv | PASS |  |
| File cohort recruiting_2025-09.csv | PASS |  |
| File cohort recruiting_2025-10.csv | PASS |  |
| File cohort recruiting_2025-11.csv | PASS |  |
| File cohort recruiting_2025-12.csv | PASS |  |
| Employee-month keys unique | PASS |  |
| Application keys unique | PASS |  |
| Date parse hire_date | PASS |  |
| Date parse exit_date | PASS |  |
| Date parse apply_date | PASS |  |
| Date parse screen_date | PASS |  |
| Date parse interview_date | PASS |  |
| Date parse offer_date | PASS |  |
| Date parse decision_date | PASS |  |
| Date parse acceptance_date | PASS |  |
| Required employee fields | PASS |  |
| Required recruiting fields | PASS |  |
| OverTime domain | PASS |  |
| Positive income | PASS |  |
| Exit on or after hire | PASS |  |
| Exit type known | PASS |  |
| screen_date follows apply_date | PASS |  |
| interview_date follows screen_date | PASS |  |
| offer_date follows interview_date | PASS |  |
| decision_date follows offer_date | PASS |  |
| Accepted dates consistent | PASS |  |
| Recruiting decision domain | PASS |  |
| Pending offer has no decision | PASS |  |
| Fixed employee attributes consistent | PASS |  |
| Source employee IDs unique | PASS |  |
| Employee coverage vs uploaded source | PASS | 1470 distinct employees / 1470 source records |
| Continuous reporting months | PASS |  |
| Recruiting cohort file coverage | PASS | Header-only files required for zero-application months |
| Monthly membership 2025-01 | PASS | 1439 rows |
| Monthly membership 2025-02 | PASS | 1422 rows |
| Monthly membership 2025-03 | PASS | 1401 rows |
| Monthly membership 2025-04 | PASS | 1383 rows |
| Monthly membership 2025-05 | PASS | 1363 rows |
| Monthly membership 2025-06 | PASS | 1352 rows |
| Monthly membership 2025-07 | PASS | 1333 rows |
| Monthly membership 2025-08 | PASS | 1321 rows |
| Monthly membership 2025-09 | PASS | 1304 rows |
| Monthly membership 2025-10 | PASS | 1287 rows |
| Monthly membership 2025-11 | PASS | 1274 rows |
| Monthly membership 2025-12 | PASS | 1252 rows |
| Rows retained through cleaning | PASS | employees 16131; recruiting 2400 |
| Baseline and optimized identical | PASS | All grouped keys and numerical columns match |
| Department domain | PASS |  |
| Location domain | PASS |  |
| SQL group keys reconcile | PASS |  |
| SQL all KPI values reconcile | PASS | All counts, sums, denominators and KPI rates; SQLite vs pandas |
| Group headcount roll-forward | PASS |  |
| Exit reasons reconcile | PASS |  |
| Department closing reconciles 2025-01 | PASS | 1418 summary / 1418 independent |
| Department closing reconciles 2025-02 | PASS | 1398 summary / 1398 independent |
| Department closing reconciles 2025-03 | PASS | 1379 summary / 1379 independent |
| Department closing reconciles 2025-04 | PASS | 1361 summary / 1361 independent |
| Department closing reconciles 2025-05 | PASS | 1348 summary / 1348 independent |
| Department closing reconciles 2025-06 | PASS | 1331 summary / 1331 independent |
| Department closing reconciles 2025-07 | PASS | 1314 summary / 1314 independent |
| Department closing reconciles 2025-08 | PASS | 1303 summary / 1303 independent |
| Department closing reconciles 2025-09 | PASS | 1284 summary / 1284 independent |
| Department closing reconciles 2025-10 | PASS | 1273 summary / 1273 independent |
| Department closing reconciles 2025-11 | PASS | 1252 summary / 1252 independent |
| Department closing reconciles 2025-12 | PASS | 1233 summary / 1233 independent |
| Recruiting source totals | PASS | 2400 / 2400 |
| Accepted decision totals | PASS |  |
| Excel exported counts reconcile | PASS | max absolute headcount/exit difference 0 |
| Excel requested controls | PASS |  |
| External workbook recalculation | PASS | LibreOffice; last-month and first-month selector checks; no formula errors |
| EDA notebook cells executed | PASS | 16 code cells; no execution errors |
