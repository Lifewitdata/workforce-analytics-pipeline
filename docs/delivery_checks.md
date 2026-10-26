# Delivery checks

SYNTHETIC EDUCATIONAL DATA.

- 90 pipeline checks and five boundary tests passed.
- Sixteen EDA code cells executed; three charts are embedded in the notebook.
- Baseline and optimized standalone entry points ran to completion; their KPI outputs are identical to each other and the pre-refactor outputs.
- The SQL query reconciles every group key and numerical KPI column with pandas.
- All 24 monthly raw files regenerate byte-identically using the modular seeded generator.
- LibreOffice recalculated the Excel workbook with no formula errors. The last-month and first-month selectors reconcile with Python within 1e-9. The missing-ID lookup, dropdowns, formatting and chart were checked. Microsoft Excel itself was not automated.
- Evidence: data/output/refactor_verification.json, excel_verification.json, reproducibility_check.json and unit_test_results.txt.
- Summary render: dashboard/screenshots/summary_preview.png.
- Optional Tableau workbook is not included; only its specification is supplied.
