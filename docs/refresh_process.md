# Refresh process

SYNTHETIC EDUCATIONAL DATA. This runbook refreshes the simulated portfolio project; it is not connected to an employer's HR systems.

## First use

1. Extract the project ZIP. Open a terminal in the workforce-analytics-pipeline folder.
2. Install Python 3.10 or newer, then run `python -m pip install -r requirements.txt`.
3. Run `python src/pipeline.py`. Inputs are already included. This command recreates CSV outputs, workbook, logs, the executed EDA notebook, workflow diagram and measured documentation.
4. Open `excel/workforce_summary.xlsx`. If LibreOffice is installed, the pipeline calculates and verifies formulas automatically. Otherwise Excel recalculates when opened; independent Python/output checks still run, and the verification status records that the external calculation engine was unavailable.

To deliberately regenerate the original synthetic demo, use `python src/pipeline.py --generate-demo`. Do not use that flag when adding your own monthly inputs.

## New files

- Put employee snapshots in `data/raw/employees/employees_YYYY-MM.csv`, using the existing schema. Each month must include boundary exit events and employees active during the month, as described in kpi_definitions.md. The key is employee_id + report_month.
- Put application cohorts in `data/raw/recruiting/recruiting_YYYY-MM.csv`. Update an existing cohort file when decisions arrive; do not append another copy of that application. Key: application_id. For a month with zero applications, include a header-only file.
- Cleaned monthly inputs are written to `data/interim/`; the final tables are `data/output/master_employees.csv`, `recruiting_funnel.csv` and `kpi_monthly.csv`. Runtime logs are written to `logs/pipeline_run.log`.

- A new employee must also exist in the source employee registry `data/raw/source/HR-Employee-Attrition.csv` for the strict coverage check. This source registry is also used for the original-sample insight analysis; with real data, redesign that analysis population and observation window rather than blindly appending mixed periods.
- Dates are YYYY-MM-DD. Keep blank optional dates empty, not literal strings. An exit date is the first day no longer employed. Use fixed department/location in this simple project; real transfers need an effective-dated dimension and revised checks.
- This version supports the fixed department/location domain. Updating the domains, multi-spell employment, true historical ratings or recruiting-to-employee linkage requires an explicit model revision.

## Checks to review

Read `logs/pipeline_run.log`, `data/output/run_manifest.json`, `docs/validation_log.md`, and `data/output/excel_verification.json`. Review source/union row counts, unique keys, valid dates, monthly membership, O+H−X=C, exit-type totals, independent headcount reconciliation, baseline-versus-optimized equality, and Excel reconciliation. `run_manifest.json` is written only after a successful pipeline run. The workbook's month dropdown uses a named range and includes all loaded months after regeneration. SQL/Python reconciliation and EDA execution also run automatically.

## If a check fails

The program raises an error and exits nonzero. Read the failed check and offending source file, correct or quarantine the source issue with an explanation in data_quality_log.md, and rerun. Never disable a check just to get a report. Do not use old outputs after a failed run; their presence is not evidence of success. Back up the previous complete output folder before a refresh. Verify the new successful-run timestamp/log before sharing. Empty/missing files and schema failures stop processing; they are not zero headcount.

## Reproducible checks

`python -m unittest discover -s tests -p "test_*.py"`

Optional explicit workbook recalculation: `python src/verify_excel.py` (requires LibreOffice). This checks cached formulas, changes the selected month in a disposable copy, checks a missing lookup ID, and preserves the original last-month view. It does not claim Microsoft Excel execution.

## Run time

The benchmark measures only the employee aggregation section, in seven alternating paired repetitions after a warm-up. The total pipeline time has a separate scope; do not confuse either with hand-preparation time saved. Timings depend on machine and load.
