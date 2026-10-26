"""Boundary tests: python -m unittest discover -s workflow -p 'test_*.py'"""
import unittest
import pandas as pd
from src.transform import derive,join_summaries,build_master
from src.pipeline import summarize_employees
from src.build_kpis import rates,recruiting_summary
from src.config import COUNTS,RCOUNTS

class BoundaryTests(unittest.TestCase):
    def test_summary_join_rejects_duplicate_keys(self):
        keys={'report_month':'2025-01','Department':'D','location':'A'}
        e=pd.DataFrame([{**keys,**{c:0 for c in COUNTS}}]*2)
        r=pd.DataFrame([{**keys,**{c:0 for c in RCOUNTS}}])
        with self.assertRaises(pd.errors.MergeError):
            join_summaries(e,r,['2025-01'],['D'],['A'])

    def test_master_has_one_employee_and_exit_flag(self):
        e=pd.DataFrame({'employee_id':[1,1], 'report_month':['2025-01','2025-02'], 'hire_date':pd.to_datetime(['2024-01-01']*2), 'exit_date':pd.to_datetime(['2025-02-15']*2)})
        m=build_master(e,['2025-01','2025-02'])
        self.assertEqual(len(m),1);self.assertEqual(m.exit_flag.iloc[0],1)
        self.assertNotIn('report_month',m.columns)

    def test_month_boundaries(self):
        d=pd.DataFrame({'employee_id':[1,2,3,4], 'report_month':['2025-01']*4,'Department':['D']*4,'location':['A']*4,'hire_date':pd.to_datetime(['2024-01-01','2025-01-01','2025-01-10','2024-01-01']),'exit_date':pd.to_datetime(['2025-01-01',None,'2025-01-20','2025-01-31']),'exit_type':['Voluntary','Not applicable','Involuntary','Voluntary'],'MonthlyIncome':[100]*4,'OverTime':['No']*4})
        z=derive(d)
        self.assertEqual(z.opening.tolist(),[1,0,0,1])
        self.assertEqual(z.closing.tolist(),[0,1,0,0])
        self.assertEqual(z.hires.sum(),2);self.assertEqual(z.exits.sum(),3)
        self.assertEqual(z.opening.sum()+z.hires.sum()-z.exits.sum(),z.closing.sum())
        pd.testing.assert_frame_equal(summarize_employees(z,True),summarize_employees(z,False))

    def test_zero_denominators(self):
        r=rates(pd.DataFrame([{c:0 for c in COUNTS+RCOUNTS}]))
        self.assertTrue(pd.isna(r.attrition_rate.iloc[0]));self.assertTrue(pd.isna(r.offer_acceptance_rate.iloc[0]))

    def test_recruitment_future_decision(self):
        r=pd.DataFrame({'Department':['D'],'location':['A'],'apply_date':pd.to_datetime(['2025-01-01']),'offer_date':pd.to_datetime(['2025-01-20']),'decision_date':pd.to_datetime(['2025-02-02']),'acceptance_date':pd.to_datetime(['2025-02-02']),'offer_decision':['Accepted']})
        q=recruiting_summary(r,['2025-01','2025-02'])
        self.assertEqual(q.pending.tolist(),[1,0]);self.assertEqual(q.accepted.tolist(),[0,1]);self.assertEqual(q.applications.tolist(),[1,0]);self.assertEqual(q.hire_days_sum.tolist(),[0,32])

if __name__=='__main__':unittest.main()
