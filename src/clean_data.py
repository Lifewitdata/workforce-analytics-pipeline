"""Strip labels, parse dates and reject duplicate keys; no invented imputation."""
import pandas as pd
from src.quality_checks import check

def clean_inputs(e,r):
    e,r=e.copy(),r.copy()
    for f in (e,r):
        for c in f.select_dtypes('object'): f[c]=f[c].str.strip()
    check('Employee-month keys unique',not e.duplicated(['employee_id','report_month']).any())
    check('Application keys unique',not r.application_id.duplicated().any())
    for f,cols in [(e,['hire_date','exit_date']),(r,['apply_date','screen_date','interview_date','offer_date','decision_date','acceptance_date'])]:
        for c in cols:
            before=f[c].notna();f[c]=pd.to_datetime(f[c],format='%Y-%m-%d',errors='coerce')
            check('Date parse '+c, not (before&f[c].isna()).any())
    return e,r
