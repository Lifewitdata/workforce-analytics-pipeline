# GenAI usage

SYNTHETIC EDUCATIONAL DATA. AI assisted in profiling the upload, drafting code, generating synthetic recruiting/history rules, writing KPI definitions, proposing validation checks and drafting the explanatory documents. Python executed the calculations; the code and output files provide the numerical evidence.

One design correction: the uploaded employee file has no dates. The initial project brief requested monthly attrition, but the file's Attrition=Yes share cannot be labeled monthly attrition. The implemented solution separates original-sample attrition share from explicitly simulated monthly rates using opening/closing headcount. It does not reconstruct historical dates as if known.

A second modeling safeguard: applicants have no employee crosswalk. Rather than fabricate person matches, the implementation aggregates both populations independently by month, department and fictional location before joining. Recruiting acceptances are not claimed to explain source employee hires.

The human selected the business problem and source file, authorized simulation, and later requested removing Alteryx from scope. No Alteryx or Tableau Prep workflow was built or executed. AI-generated insight text was checked against executed counts and includes correlation/causation and synthetic-data limitations. No external LLM API, paid API key or live HR system is required by this project.

The author should review the code and rerun it before discussing it in an interview. Explain the denominator and join grain; do not claim real company impact or measured manual time savings.

During SQL verification, SQLite rejected both source `OverTime` and derived `overtime` because SQL identifiers are case-insensitive. The SQL input was corrected to include only the keys and derived KPI fields it actually needs. SQL results are independently compared with pandas, rather than assuming the translation is correct.
