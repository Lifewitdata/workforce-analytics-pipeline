"""As-of recruiting counts and weighted KPI ratios; zero denominators remain null."""
import numpy as np
import pandas as pd
from src.config import KEY,RCOUNTS

def recruiting_summary(r,months):
    blocks=[]
    for month in months:
        period=pd.Period(month,freq='M');s,t=period.start_time,period.end_time.normalize()
        q=r[r.apply_date<=t].copy()
        q['report_month']=month;q['applications']=q.apply_date.between(s,t).astype(int)
        q['offers_in_cohort']=(q.applications.eq(1)&q.offer_date.le(t)).astype(int)
        q['accepted']=(q.decision_date.between(s,t)&q.offer_decision.eq('Accepted')).astype(int)
        q['declined']=(q.decision_date.between(s,t)&q.offer_decision.eq('Declined')).astype(int)
        q['pending']=(q.offer_date.le(t)&(q.decision_date.isna()|q.decision_date.gt(t))).astype(int)
        q['hire_days_sum']=((q.acceptance_date-q.apply_date).dt.days.fillna(0)*q.accepted)
        blocks.append(q.groupby(KEY,as_index=False)[RCOUNTS].sum())
    return pd.concat(blocks,ignore_index=True)

def rates(s):
    s=s.copy();s['average_headcount']=(s.opening+s.closing)/2
    for target,num,den in [('attrition_rate','exits','average_headcount'),('voluntary_rate','voluntary','average_headcount'),('involuntary_rate','involuntary','average_headcount'),('avg_tenure_years','tenure_sum','closing'),('avg_monthly_income','income_sum','income_count'),('overtime_share','overtime','overtime_count'),('time_to_hire_days','hire_days_sum','accepted'),('funnel_conversion','offers_in_cohort','applications')]:
        s[target]=s[num]/s[den].replace(0,np.nan)
    s['offer_acceptance_rate']=s.accepted/(s.accepted+s.declined).replace(0,np.nan)
    return s
