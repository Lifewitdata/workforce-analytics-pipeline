"""Employee-month flags, tenure bands and one-to-one summary joins."""
import numpy as np
import pandas as pd
from src.config import BANDS,KEY,COUNTS,RCOUNTS

def band(s):
    return pd.cut(s, [-np.inf,1,3,5,10,np.inf], right=False, labels=BANDS).astype(str)

def derive(e):
    d=e.copy();s=pd.to_datetime(d.report_month+'-01');t=s+pd.offsets.MonthEnd(0)
    d['opening']=((d.hire_date<s)&(d.exit_date.isna()|(d.exit_date>=s))).astype(int)
    d['closing']=((d.hire_date<=t)&(d.exit_date.isna()|(d.exit_date>t))).astype(int)
    d['hires']=d.hire_date.between(s,t).astype(int);d['exits']=d.exit_date.between(s,t).astype(int)
    d['voluntary']=(d.exits.eq(1)&d.exit_type.eq('Voluntary')).astype(int)
    d['involuntary']=(d.exits.eq(1)&d.exit_type.eq('Involuntary')).astype(int)
    d['tenure_years']=(t-d.hire_date).dt.days/365.25
    d['tenure_band']=band(d.tenure_years)
    d['tenure_sum']=d.tenure_years*d.closing;d['income_sum']=d.MonthlyIncome*d.closing
    d['income_count']=d.closing;d['overtime']=(d.OverTime.eq('Yes')&d.closing.eq(1)).astype(int);d['overtime_count']=d.closing
    return d

def join_summaries(employee_summary,recruiting_summary,months,departments,locations):
    grid=pd.MultiIndex.from_product([months,departments,locations],names=KEY).to_frame(index=False)
    summary=grid.merge(employee_summary,on=KEY,how='left',validate='one_to_one').merge(recruiting_summary,on=KEY,how='left',validate='one_to_one')
    summary[COUNTS+RCOUNTS]=summary[COUNTS+RCOUNTS].fillna(0)
    return summary,grid

def build_master(e,months):
    master=e.drop(columns='report_month').drop_duplicates('employee_id').copy()
    cutoff=pd.Period(months[-1],freq='M').end_time.normalize()
    master['as_of_date']=cutoff
    master['exit_flag']=(master.exit_date.notna() & master.exit_date.le(cutoff)).astype(int)
    anchor=master.exit_date.where(master.exit_flag.eq(1),cutoff)
    master['tenure_years']=(anchor-master.hire_date).dt.days/365.25
    master['tenure_band']=band(master.tenure_years)
    return master
