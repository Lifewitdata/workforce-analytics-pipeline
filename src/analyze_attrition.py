"""Original-sample descriptive analysis; never treat repeated months as people."""
import pandas as pd
from src.config import OUT,DOC,LABEL
from src.transform import band

def insights(source):
    x=source.copy();x['exit_flag']=x.Attrition.eq('Yes').astype(int);x['tenure_band']=band(x.YearsAtCompany)
    tables=[]
    for field in ['OverTime','tenure_band','Department']:
        t=x.groupby(field).agg(records=('exit_flag','size'),exits=('exit_flag','sum')).reset_index().rename(columns={field:'segment'})
        t['attrition_share']=t.exits/t.records;t.insert(0,'pattern',field);tables.append(t)
    allp=pd.concat(tables,ignore_index=True);allp.to_csv(OUT/'attrition_patterns.csv',index=False)
    cross=x.groupby(['Department','OverTime']).agg(records=('exit_flag','size'),exits=('exit_flag','sum')).reset_index();cross['attrition_share']=cross.exits/cross.records
    cross.to_csv(OUT/'department_overtime.csv',index=False)
    yes=allp.query("pattern == 'OverTime' and segment == 'Yes'").iloc[0];no=allp.query("pattern == 'OverTime' and segment == 'No'").iloc[0]
    priority=cross[cross.OverTime.eq('Yes')].sort_values('exits',ascending=False).iloc[0]
    finding=f'Investigate overtime workload in {priority.Department} first: {priority.exits}/{priority.records} overtime employees have Attrition=Yes ({priority.attrition_share:.1%}).'
    md='# Where should HR act first?\n\n'+LABEL+'\n\n## Finding\n\n'+finding+' This prioritizes the number of flagged exits among overtime groups, not just the highest percentage. It is a demonstration recommendation, not evidence about a real employer.\n\n'
    md+=f'Across the original file, overtime employees have {yes.exits}/{yes.records} attrition labels ({yes.attrition_share:.1%}), compared with {no.exits}/{no.records} ({no.attrition_share:.1%}) without overtime. Difference: {(yes.attrition_share-no.attrition_share)*100:.1f} percentage points.\n\n'
    md+='## Three descriptive patterns\n\n| Pattern | Segment | Records | Attrition Yes | Share |\n|---|---|---|---|---|\n'
    for z in allp.itertuples():md+=f'| {z.pattern} | {z.segment} | {z.records} | {z.exits} | {z.attrition_share:.2%} |\n'
    md+='\n## Department × overtime evidence\n\n| Department | Overtime | Records | Attrition Yes | Share |\n|---|---|---|---|---|\n'
    for z in cross.itertuples():md+=f'| {z.Department} | {z.OverTime} | {z.records} | {z.exits} | {z.attrition_share:.2%} |\n'
    md+='\n## Recommendation\n\nReview staffing coverage, workload allocation and manager check-ins in the priority group. Validate with real dated records and exit interviews before a small workload-management pilot. Monitor overtime and period attrition against a comparable group; do not promise an improvement percentage. Use early-tenure onboarding support as a second hypothesis where the tenure table shows elevated share.\n\n## Caveats\n\nThese are descriptive comparisons, not significance tests or causal estimates. The file is synthetic teaching data with an unspecified observation window. No employee is counted more than once. Role, pay, tenure and other confounders could explain differences. Small groups produce unstable percentages. Generated months, locations and exit reasons are excluded from this evidence. No individual risk scores or employment decisions are produced.\n'
    (DOC/'insights.md').write_text(md,encoding='utf-8');return finding,allp
