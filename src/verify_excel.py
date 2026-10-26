"""Optional LibreOffice recalculation plus independent cached-value checks.
Excel itself has not been automated. A disposable first-month selector test is included.
"""
from pathlib import Path
import json, shutil, subprocess, tempfile
import pandas as pd
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]

def recalc(path,outdir):
    exe=shutil.which('soffice') or shutil.which('libreoffice')
    if not exe: raise RuntimeError('LibreOffice not installed. Open the workbook in Excel to calculate formulas.')
    with tempfile.TemporaryDirectory() as profile:
        p=subprocess.run([exe,'-env:UserInstallation='+Path(profile).as_uri(),'--headless','--convert-to','xlsx','--outdir',str(outdir),str(path)],capture_output=True,text=True,timeout=60)
        target=Path(outdir)/path.name
        if p.returncode or not target.exists():raise RuntimeError(p.stdout+p.stderr)
        return target

def verify(path,month):
    cached=load_workbook(path,data_only=True)
    errors=[f'{w.title}!{c.coordinate}: {c.value}' for w in cached for row in w for c in row if c.data_type=='e']
    if errors:raise AssertionError(errors[:10])
    total=pd.read_csv(ROOT/'data/output/monthly_totals.csv').set_index('report_month').loc[month]
    fields={8:'closing',9:'attrition_rate',10:'offer_acceptance_rate',11:'time_to_hire_days',12:'overtime_share',13:'avg_tenure_years'}
    differences={}
    for row,field in fields.items():
        actual=cached['Summary'].cell(row,2).value
        if pd.isna(total[field]):
            assert actual=='N/A', (field,actual)
            differences[field]=0
        else:differences[field]=abs(float(actual)-float(total[field]))
    if max(differences.values())>1e-9:raise AssertionError(differences)
    dept=pd.read_csv(ROOT/'data/output/department_summary.csv');dept=dept[dept.report_month.eq(month)].set_index('Department')
    for row in range(17,20):
        name=cached['Summary'].cell(row,1).value
        for col,field in [(2,'opening'),(3,'closing'),(4,'exits'),(5,'attrition_rate')]:
            expected=dept.loc[name,field];actual=cached['Summary'].cell(row,col).value
            if pd.isna(expected):
                assert actual=='N/A';difference=0
            else:difference=abs(float(actual)-float(expected))
            differences[name+' '+field]=difference
            if difference>1e-9:raise AssertionError((name,field,difference))
    return differences

def main():
    path=ROOT/'excel/workforce_summary.xlsx'
    available=pd.read_csv(ROOT/'data/output/monthly_totals.csv').report_month
    selected_month=available.iloc[-1];first_month=available.iloc[0]
    with tempfile.TemporaryDirectory() as temp:
        t=Path(temp);out=t/'calc';out.mkdir()
        result=recalc(path,out);dec=verify(result,selected_month)
        # Save recalculated final workbook with formula caches intact.
        shutil.copy2(result,path)
        w=load_workbook(path);w['Summary']['B5']=first_month;w['Summary']['B28']=999999
        test=t/'selector_test.xlsx';w.save(test)
        january=recalc(test,out);jan=verify(january,first_month)
        assert load_workbook(january,data_only=True)['Summary']['E28'].value=='Not found'
        original=load_workbook(path,data_only=False)
        assert len(original['Summary'].data_validations.dataValidation)==2
        assert len(original['Summary'].conditional_formatting)>0
        assert len(original['Summary']._charts)==1
        assert 'INDEX(' in original['Summary']['E28'].value
    result={'engine':'LibreOffice headless; Microsoft Excel not executed','formula_error_cells':0,'selected_month':selected_month,'selected_month_max_absolute_difference':max(dec.values()),'alternate_month':first_month,'alternate_month_max_absolute_difference':max(jan.values()),'missing_employee_lookup':'Not found','dropdowns_preserved':2,'conditional_formatting_preserved':True,'chart_preserved':True}
    (ROOT/'data/output/excel_verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
