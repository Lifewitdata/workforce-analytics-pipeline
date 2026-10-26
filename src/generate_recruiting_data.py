"""Seeded demo generator: employee history plus independent recruiting cohorts.
Uses the shared seed stream to preserve the already-reviewed demo exactly.
"""
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import logging
import numpy as np
import pandas as pd
from src.config import RAW,SEED,REPORT_START,REPORT_END,APPLICATION_COUNT,LOCATIONS

def generate():
    """Only explicit --generate-demo creates/replaces synthetic input files."""
    rng = np.random.default_rng(SEED)
    e = pd.read_csv(RAW/'source/HR-Employee-Attrition.csv').rename(columns={'EmployeeNumber':'employee_id'})
    end = pd.Timestamp(REPORT_END); start = pd.Timestamp(REPORT_START)
    e['location'] = rng.choice(LOCATIONS, len(e))
    e['exit_date'] = pd.NaT
    mask = e.Attrition.eq('Yes')
    e.loc[mask,'exit_date'] = start + pd.to_timedelta(rng.integers(0,365,mask.sum()),unit='D')
    anchor = e.exit_date.fillna(end)
    # Duration anchored at exit for leavers and year-end for others. Not recovered dates.
    e['hire_date'] = anchor-pd.to_timedelta(e.YearsAtCompany*365+rng.integers(1,365,len(e)),unit='D')
    e['exit_type'] = 'Not applicable'
    e.loc[mask,'exit_type'] = rng.choice(['Voluntary','Involuntary'],mask.sum(),p=[.75,.25])
    e['is_synthetic'] = True
    for month in pd.period_range(REPORT_START[:7],REPORT_END[:7],freq='M'):
        s,t=month.start_time,month.end_time.normalize()
        m=e.loc[(e.hire_date<=t)&(e.exit_date.isna()|(e.exit_date>=s))].copy()
        m['report_month']=str(month)
        m.to_csv(RAW/f'employees/employees_{month}.csv',index=False,date_format='%Y-%m-%d')
    # Independent recruiting population. No invented applicant-to-employee crosswalk.
    roles=e[['Department','JobRole']].drop_duplicates().reset_index(drop=True)
    rows=[]
    for i in range(APPLICATION_COUNT):
        role=roles.iloc[int(rng.integers(len(roles)))]; apply=start+pd.Timedelta(days=int(rng.integers(365)))
        dates={}; current=apply; furthest='Applied'
        for col,stage,prob,low,high in [('screen_date','Screened',.78,1,11),('interview_date','Interviewed',.55,2,16),('offer_date','Offered',.55,1,11)]:
            if rng.random()>=prob: break
            current+=pd.Timedelta(days=int(rng.integers(low,high)))
            if current>end: break
            dates[col]=current; furthest=stage
        decision='Not offered'; dd=pd.NaT; ad=pd.NaT
        if 'offer_date' in dates:
            decision='Pending'; future=current+pd.Timedelta(days=int(rng.integers(1,15)))
            if future<=end:
                dd=future; decision='Accepted' if rng.random()<.78 else 'Declined'
                if decision=='Accepted': ad=dd;furthest='Accepted'
        rows.append(dict(application_id=f'APP{i+1:05}',applicant_id=f'P{i+1:05}',Department=role.Department,JobRole=role.JobRole,location=rng.choice(LOCATIONS),source=rng.choice(['Referral','Job board','Career site','Agency']),apply_date=apply,stage_reached=furthest,offer_decision=decision,decision_date=dd,acceptance_date=ad,is_synthetic=True,**dates))
    r=pd.DataFrame(rows)
    for month,g in r.groupby(r.apply_date.dt.to_period('M')):
        g.to_csv(RAW/f'recruiting/recruiting_{month}.csv',index=False,date_format='%Y-%m-%d')
    logging.info('Generated demo with seed 42: %s employees, %s applications',len(e),len(r))

if __name__=="__main__":
    for p in [RAW/"employees",RAW/"recruiting"]:p.mkdir(parents=True,exist_ok=True)
    generate()
