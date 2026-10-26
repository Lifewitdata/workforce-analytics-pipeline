"""Validation gates; failed checks stop publication rather than drop rows silently."""
import pandas as pd
from src.config import DOC, LABEL, RAW

checks=[]

def check(name, ok, detail=''):
    checks.append((name, bool(ok), str(detail)))
    if not ok:
        validation_doc()
        raise ValueError(f'{name}: {detail}')

def validation_doc():
    DOC.mkdir(parents=True, exist_ok=True)
    text = '# Validation log\n\n'+LABEL+'\n\n| Check | Result | Detail |\n|---|---|---|\n'
    text += '\n'.join(f'| {n} | {"PASS" if o else "FAIL"} | {d} |' for n,o,d in checks)
    (DOC/'validation_log.md').write_text(text+'\n', encoding='utf-8')

def validate_inputs(e,r):
    check('Required employee fields',not e[['employee_id','report_month','hire_date','Department','location','MonthlyIncome','JobLevel','OverTime']].isna().any().any())
    check('Required recruiting fields',not r[['application_id','applicant_id','apply_date','Department','location','source','offer_decision']].isna().any().any())
    check('OverTime domain',e.OverTime.isin(['Yes','No']).all())
    check('Positive income',e.MonthlyIncome.gt(0).all())
    check('Exit on or after hire',(e.exit_date.isna()|(e.exit_date>=e.hire_date)).all())
    check('Exit type known',e.loc[e.exit_date.notna(),'exit_type'].isin(['Voluntary','Involuntary']).all())
    for a,b in [('apply_date','screen_date'),('screen_date','interview_date'),('interview_date','offer_date'),('offer_date','decision_date')]:
        check(f'{b} follows {a}',(r[b].isna()|(r[a].notna()&(r[b]>=r[a]))).all())
    check('Accepted dates consistent', (r.offer_decision.eq('Accepted')==r.acceptance_date.notna()).all() and (r.loc[r.offer_decision.eq('Accepted'),'acceptance_date']==r.loc[r.offer_decision.eq('Accepted'),'decision_date']).all())
    check('Recruiting decision domain',r.offer_decision.isin(['Not offered','Pending','Accepted','Declined']).all())
    check('Pending offer has no decision',r.loc[r.offer_decision.eq('Pending'),'decision_date'].isna().all())
    # One history record per employee; repeated snapshots must agree on fixed fields.
    fixed=['hire_date','exit_date','Department','location','exit_type','MonthlyIncome','JobLevel','OverTime']
    check('Fixed employee attributes consistent',e.groupby('employee_id')[fixed].nunique(dropna=False).le(1).all().all())
    master=e.drop_duplicates('employee_id')
    source=pd.read_csv(RAW/'source/HR-Employee-Attrition.csv')
    check('Source employee IDs unique',not source.EmployeeNumber.duplicated().any())
    check('Employee coverage vs uploaded source',set(master.employee_id)==set(source.EmployeeNumber),f'{len(master)} distinct employees / {len(source)} source records')
    months=sorted(e.report_month.unique())
    check('Continuous reporting months',months==list(map(str,pd.period_range(months[0],months[-1],freq='M'))))
    available={p.stem[-7:] for p in (RAW/'recruiting').glob('*.csv')}
    check('Recruiting cohort file coverage',set(months).issubset(available),'Header-only files required for zero-application months')
    for month in months:
        period=pd.Period(month,freq='M');s,t=period.start_time,period.end_time.normalize()
        expected=master.loc[(master.hire_date<=t)&(master.exit_date.isna()|(master.exit_date>=s)),'employee_id']
        actual=e.loc[e.report_month.eq(month),'employee_id']
        check('Monthly membership '+month,set(expected)==set(actual),f'{len(actual)} rows')
    return source,master,months
