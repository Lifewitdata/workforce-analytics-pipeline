# Simulation rules

SYNTHETIC EDUCATIONAL DATA. The employee upload is treated as teaching data; original source provenance remains unconfirmed. All calendar history, locations, exit reasons and recruiting records below are simulated. The user authorized simulation. This is not real HR evidence.

- Seed: NumPy default_rng(42); reporting window January–December 2025.
- Keep the original 1,470 employee records and original fields unchanged in data/raw/source. EmployeeNumber becomes employee_id in generated monthly inputs.
- Attrition=Yes receives an exit date sampled uniformly across 2025. Attrition=No has no exit date. Exit date is the first day no longer employed.
- Anchor tenure at exit date for leavers and 31 December 2025 otherwise. Simulated hire date = anchor minus YearsAtCompany × 365 days minus a uniform integer from 1 through 364 days. This is an illustrative calendar, not recovered employment history. Original YearsAtCompany and derived tenure_years may differ slightly because the derived metric uses 365.25 days/year.
- Assign fictional Site A/B/C with equal probability, independently of attrition. For leavers, sample Voluntary/Involuntary with probabilities 75%/25%. These probabilities are design inputs, not findings. Non-leavers have exit_type=Not applicable.
- Hold department, role, monthly income, job level, overtime and satisfaction fixed across the simulated history. No transfers, rehires, pay changes or historical rating changes are modeled. Do not claim this is a realistic labor-force forecast.
- Employee monthly files include hire_date <= month-end and (exit_date is null or exit_date >= month-start). This includes month-start exits, needed for opening-headcount reconciliation.
- Generate 2,400 independent applications. Applicant and application IDs are unique in this demo. Sample department/role from distinct source combinations with equal probability, not employee-weighted probability. Site A/B/C and Referral/Job board/Career site/Agency are each uniform independent selections.
- Apply dates are uniform across 2025. Sequential conditional progression probabilities: screen 78%, interview 55%, offer 55%. Delays: screen 1–10 calendar days, interview 2–15 days, offer 1–10 days. Stop when a stage is not reached or its date would pass 31 December 2025.
- Offers receive a response after 1–14 days. Responses beyond year-end remain Pending; otherwise accept with probability 78% and decline with 22%. Accepted applications have acceptance_date=decision_date. All rules above are chosen simulation parameters, not real conversion benchmarks.
- Recruiting files are partitioned by application month. They contain final known outcomes by year-end; monthly computations explicitly exclude future outcomes at each reporting cutoff. Accepted applications are not linked to employee hires. Recruiting volume and employee hiring volume therefore will not reconcile and should not be presented as one population.
- Never directly join applicants and employees on department or role. Independently aggregate to report_month + Department + location, verify uniqueness, and join to a complete calendar/group scaffold. Zero-fill counts only after file coverage and schema checks pass.
- Re-running with the same seed, input file, library versions and script produces the same data. Benchmark runtimes vary. --generate-demo intentionally replaces the demo's same-named monthly files; ordinary runs preserve raw inputs.

## Source quality vs injected dirt

No artificial missing values, duplicates or invalid dates were injected into raw files. Their absence is reported honestly. Automated validation rejects those issues if they appear in later inputs. The meaningful work here is grain, dates, denominator consistency, aggregation, reproducibility and reconciliation, not pretending to have cleaned nonexistent errors.
