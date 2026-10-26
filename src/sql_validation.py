"""Execute the optional SQLite KPI query and reconcile all columns with pandas."""
import sqlite3
import numpy as np
import pandas as pd
from src.config import ROOT,OUT,KEY,COUNTS
from src.quality_checks import check

def compare_sql(employee_months,applications,grid,expected):
    with sqlite3.connect(':memory:') as db:
        # SQLite identifiers ignore case: exclude source OverTime when exporting
        # the derived overtime count. Only KPI input fields belong in this table.
        employee_months[KEY+COUNTS].to_sql('employee_months',db,index=False)
        applications.to_sql('applications',db,index=False)
        grid.to_sql('group_grid',db,index=False)
        actual=pd.read_sql_query((ROOT/'sql/kpi_monthly.sql').read_text(),db)
    a=actual.sort_values(KEY).reset_index(drop=True)
    b=expected.sort_values(KEY).reset_index(drop=True)
    check('SQL group keys reconcile',a[KEY].equals(b[KEY]))
    numeric=[c for c in expected if c not in KEY]
    check('SQL all KPI values reconcile',np.allclose(a[numeric].to_numpy(float),b[numeric].to_numpy(float),rtol=1e-10,atol=1e-9,equal_nan=True),'All counts, sums, denominators and KPI rates; SQLite vs pandas')
    actual.to_csv(OUT/'kpi_monthly_sql.csv',index=False)
