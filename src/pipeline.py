"""One command: python src/pipeline.py [--generate-demo] [--mode baseline]."""
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse,hashlib,json,logging,platform,statistics,shutil
from time import perf_counter
import pandas as pd
import numpy as np
from src.config import *
from src.load_data import read_union,log
from src.clean_data import clean_inputs
from src.quality_checks import checks,check,validation_doc,validate_inputs
from src.transform import derive,build_master,join_summaries
from src.build_kpis import recruiting_summary,rates
from src.generate_recruiting_data import generate
from src.analyze_attrition import insights
from src.build_excel import workbook
from optimization.baseline_pipeline import summarize_employees as baseline
from optimization.optimized_pipeline import summarize_employees as optimized

def summarize_employees(d,use_optimized):
    return optimized(d) if use_optimized else baseline(d)

def main(argv=None):
    checks.clear()
    parser=argparse.ArgumentParser();parser.add_argument('--generate-demo',action='store_true');parser.add_argument('--mode',choices=['baseline','optimized'],default='optimized');args=parser.parse_args(argv)
    for p in [INTERIM,LOGS,OPTIMIZATION,RAW/'source',RAW/'employees',RAW/'recruiting',OUT,DOC,ROOT/'excel',ROOT/'dashboard']:p.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s',handlers=[logging.FileHandler(LOGS/'pipeline_run.log',mode='w'),logging.StreamHandler()])
    began=perf_counter()
    # An old success marker must never survive a failed refresh.
    (OUT/'run_manifest.json').unlink(missing_ok=True)
    if args.generate_demo:generate()
    e_raw,r_raw=read_union('employees'),read_union('recruiting')
    e,r=clean_inputs(e_raw,r_raw)
    source,master,months=validate_inputs(e,r)
    check('Rows retained through cleaning',len(e)==len(e_raw) and len(r)==len(r_raw),f'employees {len(e)}; recruiting {len(r)}')
    for name,frame in [('employees_clean',e),('recruiting_clean',r)]:frame.to_csv(INTERIM/f'{name}.csv',index=False,date_format='%Y-%m-%d')
    d=derive(e);d.to_csv(INTERIM/'employee_months_derived.csv',index=False,date_format='%Y-%m-%d');log('derive employee fields',d)
    timings={k:[] for k in ['baseline','optimized']}
    # Warm both functions, alternate execution order across seven paired runs.
    summarize_employees(d,False);summarize_employees(d,True)
    for i in range(7):
        for name in (['baseline','optimized'] if i%2==0 else ['optimized','baseline']):
            st=perf_counter();s=summarize_employees(d,name=='optimized');timings[name].append(perf_counter()-st)
    base=summarize_employees(d,False);opt=summarize_employees(d,True)
    pd.testing.assert_frame_equal(base.sort_values(KEY).reset_index(drop=True),opt.sort_values(KEY).reset_index(drop=True))
    check('Baseline and optimized identical',True,'All grouped keys and numerical columns match')
    rs=recruiting_summary(r,months);log('recruiting aggregation',rs)
    departments=sorted(source.Department.unique());locations=LOCATIONS
    check('Department domain',e.Department.isin(departments).all() and r.Department.isin(departments).all())
    check('Location domain',e.location.isin(locations).all() and r.location.isin(locations).all())
    summary,scaffold=join_summaries(base if args.mode=='baseline' else opt,rs,months,departments,locations)
    summary=rates(summary);log('join aggregate tables',summary)
    from src.sql_validation import compare_sql
    compare_sql(d,r,scaffold,summary)

    check('Group headcount roll-forward',(summary.opening+summary.hires-summary.exits==summary.closing).all())
    check('Exit reasons reconcile',(summary.voluntary+summary.involuntary==summary.exits).all())
    dept=rates(summary.groupby(['report_month','Department'],as_index=False)[COUNTS+RCOUNTS].sum())
    total=rates(summary.groupby('report_month',as_index=False)[COUNTS+RCOUNTS].sum())
    for z in total.itertuples():
        t=pd.Period(z.report_month,freq='M').end_time.normalize()
        independent=int(((master.hire_date<=t)&(master.exit_date.isna()|(master.exit_date>t))).sum())
        check('Department closing reconciles '+z.report_month,int(z.closing)==independent,f'{int(z.closing)} summary / {independent} independent')
    check('Recruiting source totals',int(total.applications.sum())==len(r),f'{int(total.applications.sum())} / {len(r)}')
    check('Accepted decision totals',int(total.accepted.sum())==int(r.offer_decision.eq('Accepted').sum()))
    active=d[d.closing.eq(1)]
    tenure=active.groupby(['report_month','Department','tenure_band'],as_index=False).agg(headcount=('employee_id','size'),income_sum=('MonthlyIncome','sum'))
    tenure['avg_monthly_income']=tenure.income_sum/tenure.headcount
    level=active.groupby(['report_month','Department','JobLevel'],as_index=False).agg(headcount=('employee_id','size'),income_sum=('MonthlyIncome','sum'));level['avg_monthly_income']=level.income_sum/level.headcount
    for name,f in [('kpi_monthly',summary),('department_summary',dept),('monthly_totals',total),('tenure_summary',tenure),('income_by_level',level),('master_employees',build_master(e,months)),('recruiting_funnel',r)]:
        f.to_csv(OUT/f'{name}.csv',index=False,date_format='%Y-%m-%d');log('output '+name,f)
    finding,patterns=insights(source);workbook(summary,dept,total,tenure,level,source,patterns,finding)
    verification=OUT/'excel_verification.json'
    if verification.exists():verification.unlink()
    if shutil.which('soffice') or shutil.which('libreoffice'):
        from src.verify_excel import main as verify_excel
        verify_excel()
        check('External workbook recalculation',True,'LibreOffice; last-month and first-month selector checks; no formula errors')
    else:
        verification.write_text(json.dumps({'engine':'Unavailable','status':'Open in Excel to recalculate. Python/export checks passed; cached formula checks not executed.'},indent=2))
    metrics={name:{'median_seconds':statistics.median(v),'runs_seconds':v,'logical_steps':21 if name=='baseline' else 2,'output_bytes':len(f.to_csv(index=False).encode())} for (name,v),f in zip(timings.items(),[base,opt])}
    metrics['scope']='Employee aggregation only, excludes input/output, simulation, recruiting and Excel. Baseline: 11 groupbys + 10 joins. Optimized: column projection + 1 groupby.'
    (OUT/'benchmark.json').write_text(json.dumps(metrics,indent=2))
    pd.DataFrame([{'version':name,'scope':metrics['scope'],'median_seconds':metrics[name]['median_seconds'],'logical_steps':metrics[name]['logical_steps'],'output_bytes':metrics[name]['output_bytes'],'repetitions':7,'outputs_equal':True} for name in ['baseline','optimized']]).to_csv(OPTIMIZATION/'benchmark_results.csv',index=False)
    data_dict='# Data dictionary\n\n'+LABEL+'\n\nTypes and observed examples below describe generated input/output schemas. See KPI definitions and simulation rules for semantics. Source category labels are not decoded without an authoritative source dictionary.\n'
    data_dict+='\nOutput grains: master_employees.csv is one row per employee; recruiting_funnel.csv is one row per application; kpi_monthly.csv is one row per report_month + Department + location. Master exit_flag means exit on/before as_of_date; master tenure ends at exit for leavers and at the reporting cutoff otherwise.\n'
    for name,frame in [('Employee monthly input',e),('Employee master output',build_master(e,months)),('Recruiting input',r),('Monthly KPI output',summary)]:
        data_dict+=f'\n## {name}\n\n| Field | Type | Example |\n|---|---|---|\n'
        for c in frame:data_dict+=f'| {c} | {frame[c].dtype} | {frame[c].dropna().iloc[0] if frame[c].notna().any() else "nullable"} |\n'
    (DOC/'data_dictionary.md').write_text(data_dict,encoding='utf-8')
    from src.build_notebook import build_notebook
    from src.build_diagram import build_diagram
    executed_cells=build_notebook()
    check('EDA notebook cells executed',executed_cells>0,f'{executed_cells} code cells; no execution errors')
    build_diagram()
    validation_doc();elapsed=perf_counter()-began
    (OUT/'run_manifest.json').write_text(json.dumps({'label':LABEL,'seed':SEED,'execution_mode':args.mode,'source_sha256':hashlib.sha256((RAW/'source/HR-Employee-Attrition.csv').read_bytes()).hexdigest(),'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'employee_month_rows':len(e),'employees':len(master),'applications':len(r),'output_groups':len(summary),'checks_passed':len(checks),'pipeline_seconds':elapsed,'runtime_scope':'includes Python pipeline, benchmark, workbook generation and available LibreOffice recalculation; excludes documentation refresh, screenshots and packaging','finding':finding},indent=2))
    from src.documentation import write_docs
    write_docs()
    logging.info('COMPLETE: %s checks passed; total %.3f seconds',len(checks),elapsed)

if __name__=="__main__":main()
