"""Create and execute the transparent EDA notebook using its own Python cells.
No notebook server is needed during a pipeline run. Open the resulting .ipynb
in Jupyter or VS Code to rerun individual cells normally.
"""
from pathlib import Path
import base64, contextlib, io, json, uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.config import ROOT

def build_notebook():
    cells=[]
    def md(text):cells.append({'cell_type':'markdown','metadata':{},'id':uuid.uuid4().hex[:8],'source':text.splitlines(True)})
    def code(text):cells.append({'cell_type':'code','metadata':{},'id':uuid.uuid4().hex[:8],'source':text.splitlines(True),'execution_count':None,'outputs':[]})
    md('''# Workforce & Recruiting — exploratory analysis

**Synthetic educational data.** The uploaded employee sample is treated as teaching data; original provenance remains unconfirmed. Monthly history, locations, exit reasons and all recruiting records are simulated with seed 42. Original-sample comparisons below are separate from simulated monthly KPIs. No causation or real business impact is claimed.

This notebook profiles inputs, checks assumptions, explores distributions and attrition associations, then reconciles the simulated pipeline outputs. Each code cell has been executed; printed results and charts come from those executions.
''')
    code('''from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
ROOT = Path.cwd() if (Path.cwd() / 'data/raw').exists() else Path.cwd().parent
assert (ROOT / 'data/raw/source/HR-Employee-Attrition.csv').exists(), 'Run from project root or notebooks/'
employees = pd.read_csv(ROOT / 'data/raw/source/HR-Employee-Attrition.csv')
print('Rows, columns:', employees.shape)
print(employees.head(5).to_string(index=False))
''')
    md('## 1. Schema and missing values\nInteger-coded ratings are ordinal categories. EmployeeNumber is an identifier, not a quantitative predictor. Missing dates are absent fields, not null cells that can be filled.')
    code('''profile = pd.DataFrame({'dtype': employees.dtypes.astype(str), 'nulls': employees.isna().sum(), 'distinct': employees.nunique()})
print(profile.to_string())
print('Date-named columns:', [c for c in employees if 'date' in c.lower()])
''')
    md('## 2. Duplicate keys, blank strings and constant fields\nDo not silently drop conflicting employee records. The pipeline rejects duplicate employee-month keys and duplicate application IDs.')
    code('''text = employees.select_dtypes('object')
print('Duplicate rows:', employees.duplicated().sum())
print('Duplicate employee IDs:', employees.EmployeeNumber.duplicated().sum())
print('Blank text cells:', text.apply(lambda s: s.str.strip().eq('').sum()).sum())
print('Constant fields:', [c for c in employees if employees[c].nunique() == 1])
print('Whitespace differences:', text.apply(lambda s: s.ne(s.str.strip()).sum()).to_dict())
''')
    md('## 3. Categories and coded scales\nInspect exact labels before mapping them. A different recruitment or department label must not be assumed equivalent without a documented mapping.')
    code('''for col in ['Attrition', 'Department', 'JobRole', 'OverTime', 'BusinessTravel', 'JobSatisfaction', 'JobLevel']:
    print('\n' + col)
    print(employees[col].value_counts(dropna=False).to_string())
'''.replace("print('\n' + col)","print('\\n' + col)"))
    md('## 4. Numeric ranges and logical consistency\nUnusual values are not automatically incorrect. Company tenure must not exceed total experience; role, manager and promotion tenure must not exceed company tenure.')
    code('''cols = ['Age','MonthlyIncome','YearsAtCompany','TotalWorkingYears','DistanceFromHome']
print(employees[cols].describe().round(2).to_string())
for left, right in [('YearsAtCompany','TotalWorkingYears'), ('YearsInCurrentRole','YearsAtCompany'), ('YearsWithCurrManager','YearsAtCompany'), ('YearsSinceLastPromotion','YearsAtCompany')]:
    print(left, '>', right, ':', int((employees[left] > employees[right]).sum()))
''')
    md('## 5. Outlier flags\nTukey fences use Q1 − 1.5×IQR and Q3 + 1.5×IQR. Flagged values are retained because no evidence establishes that they are data errors. Currency is unspecified.')
    code('''flags=[]
for col in ['Age','MonthlyIncome','YearsAtCompany','TotalWorkingYears','YearsSinceLastPromotion']:
    q1,q3=employees[col].quantile([.25,.75]);iqr=q3-q1
    lower,upper=q1-1.5*iqr,q3+1.5*iqr
    flags.append({'field':col,'lower':lower,'upper':upper,'flagged':int(((employees[col]<lower)|(employees[col]>upper)).sum())})
print(pd.DataFrame(flags).to_string(index=False))
''')
    code('''fig, axes = plt.subplots(1,2,figsize=(11,4))
axes[0].hist(employees.Age,bins=14,color='#2B6F93',edgecolor='white'); axes[0].set(title='Age distribution',xlabel='Age',ylabel='Records')
axes[1].hist(employees.MonthlyIncome,bins=20,color='#2B6F93',edgecolor='white'); axes[1].set(title='Monthly income (currency unspecified)',xlabel='Income units',ylabel='Records')
fig.suptitle('Synthetic employee teaching sample');fig.tight_layout()
''')
    md('## 6. Attrition share — not a monthly rate\nThe original file has no observation dates. Use one row per employee and call this an attrition-label share, never an annual or monthly attrition rate.')
    code('''employees['exit_flag'] = employees.Attrition.eq('Yes').astype(int)
employees['tenure_band'] = pd.cut(employees.YearsAtCompany,[-np.inf,1,3,5,10,np.inf],right=False,labels=['<1 year','1–<3 years','3–<5 years','5–<10 years','10+ years'])
print('Attrition Yes:', employees.exit_flag.sum())
print('Records:', len(employees))
print('Dataset attrition share:', f'{employees.exit_flag.mean():.2%}')
''')
    md('## 7. Three descriptive pattern comparisons\nCompare overtime, tenure and department. Always show denominators. These are descriptive comparisons, not formal significance tests or causal effects.')
    code('''patterns=[]
for field in ['OverTime','tenure_band','Department']:
    table=employees.groupby(field,observed=True).exit_flag.agg(['size','sum','mean'])
    table.columns=['records','attrition_yes','attrition_share']
    print('\\n'+field);print(table.to_string())
    patterns.append(table)
''')
    code('''fig, axes=plt.subplots(1,3,figsize=(14,4))
for ax,field,table in zip(axes,['Overtime','Tenure','Department'],patterns):
    ax.bar(range(len(table)),table.attrition_share*100,color='#2B6F93')
    ax.set_xticks(range(len(table)),table.index.astype(str),rotation=30,ha='right')
    ax.set(title=field,ylabel='Attrition-label share (%)')
fig.suptitle('Synthetic sample: associations, not causes');fig.tight_layout()
''')
    md('## 8. Department × overtime: volume versus rate\nPrioritize workload investigation using the number of labelled exits within overtime groups, while also showing rates. This avoids ranking a small department solely by its percentage.')
    code('''cross = employees.groupby(['Department','OverTime']).exit_flag.agg(['size','sum','mean'])
cross.columns=['records','attrition_yes','attrition_share']
print(cross.to_string())
overtime = cross.xs('Yes',level='OverTime').sort_values('attrition_yes',ascending=False)
print('Highest overtime-group exit-label count:', overtime.index[0])
''')
    md('## 9. Simulated monthly files and their grain\nEmployee-month records repeat people across months. Recruiting records are independent application cohorts with no employee crosswalk. Do not join raw facts on department.')
    code('''master=pd.read_csv(ROOT/'data/output/master_employees.csv')
recruiting=pd.read_csv(ROOT/'data/output/recruiting_funnel.csv')
kpis=pd.read_csv(ROOT/'data/output/kpi_monthly.csv')
interim=pd.read_csv(ROOT/'data/interim/employee_months_derived.csv')
print('Unique employee master:',len(master))
print('Employee-month rows:',len(interim))
print('Applications:',len(recruiting))
print('Monthly department/site groups:',len(kpis))
assert master.employee_id.is_unique
assert recruiting.application_id.is_unique
assert not interim.duplicated(['employee_id','report_month']).any()
assert not kpis.duplicated(['report_month','Department','location']).any()
''')
    md('## 10. Monthly reconciliation and denominators\nAverage headcount is (opening + closing)/2. Same-month hires and exits are retained. Monthly stock counts cannot be summed to obtain annual headcount.')
    code('''total=pd.read_csv(ROOT/'data/output/monthly_totals.csv')
assert (total.opening+total.hires-total.exits==total.closing).all()
assert (total.voluntary+total.involuntary==total.exits).all()
assert np.allclose(total.attrition_rate,total.exits/((total.opening+total.closing)/2))
print(total[['report_month','opening','hires','exits','closing','attrition_rate']].to_string(index=False))
''')
    code('''fig,ax=plt.subplots(figsize=(10,3.8))
ax.plot(total.report_month,total.closing,marker='o',color='#2B6F93')
ax.set(title='SIMULATED closing headcount — not recovered history',ylabel='Employees',xlabel='Reporting month')
ax.tick_params(axis='x',rotation=35);fig.tight_layout()
''')
    md('## 11. Recruiting timing and cohort caveats\nTime to hire ends at acceptance. Offer acceptance excludes pending offers. Recent application cohorts have less follow-up time. These recruiting results are generated and do not explain employee hires.')
    code('''print(recruiting.offer_decision.value_counts().to_string())
print(total[['report_month','applications','accepted','declined','pending','time_to_hire_days','offer_acceptance_rate','funnel_conversion']].round(4).to_string(index=False))
print('Count of recorded applications:', total.applications.sum())
assert total.applications.sum()==len(recruiting)
''')
    md('## 12. SQL versus Python reconciliation\nThe SQL query separately aggregates employee flags and recruiting dates, then computes the same weighted ratios. It does not read Python KPI output as its source.')
    code('''sql=pd.read_csv(ROOT/'data/output/kpi_monthly_sql.csv')
keys=['report_month','Department','location']
numeric=[c for c in kpis if c not in keys]
a=kpis.sort_values(keys).reset_index(drop=True)
b=sql.sort_values(keys).reset_index(drop=True)
assert a[keys].equals(b[keys])
assert np.allclose(a[numeric].to_numpy(float),b[numeric].to_numpy(float),equal_nan=True,atol=1e-9)
print('SQL/Python group keys and all numerical output columns match.')
''')
    md('## Conclusion and next action\nInvestigate overtime workload in the department with the largest overtime-group exit-label count, supported by the cross-tab above. Validate using real dated records and exit interviews before a workload-management pilot. Tenure patterns suggest onboarding is another hypothesis. The teaching sample is synthetic, the monthly history is invented, and correlations do not establish causation. Read docs/insights.md for the evidence and recommendation.')
    env={'__name__':'__main__'}
    import os
    previous=Path.cwd()
    try:
        os.chdir(ROOT)
        number=0
        for cell in cells:
            if cell['cell_type']!='code':continue
            number+=1;stdout=io.StringIO()
            with contextlib.redirect_stdout(stdout):exec(compile(''.join(cell['source']),f'EDA cell {number}','exec'),env)
            cell['execution_count']=number
            if stdout.getvalue():cell['outputs'].append({'output_type':'stream','name':'stdout','text':stdout.getvalue().splitlines(True)})
            for fig_id in plt.get_fignums():
                buf=io.BytesIO();plt.figure(fig_id).savefig(buf,format='png',dpi=120,bbox_inches='tight')
                cell['outputs'].append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(buf.getvalue()).decode()}})
            plt.close('all')
    finally:os.chdir(previous)
    doc={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks').mkdir(exist_ok=True)
    (ROOT/'notebooks/01_eda.ipynb').write_text(json.dumps(doc,indent=1),encoding='utf-8')
    return number

if __name__=='__main__':build_notebook()
