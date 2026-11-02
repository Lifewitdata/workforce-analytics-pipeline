import unittest
import pandas as pd
from ops.build_operations import apply_effective_assignments, REGIONS, build, OUT

class OperationsTests(unittest.TestCase):
    def test_effective_dated_transfer(self):
        agents=pd.DataFrame([{"agent_id":"AG001","team":"A","home_region":"AMER","home_language":"English","time_zone":"America/New_York","contract_hours_week":40,"employment_status":"Active"}])
        transfers=pd.DataFrame([{"agent_id":"AG001","effective_from":"2026-09-01","effective_to":"","region":"EMEA","language":"French","channel":"Chat","team":"B","time_zone":"Europe/Paris"}])
        before=apply_effective_assignments(agents,transfers,pd.Timestamp("2026-08-31"))
        after=apply_effective_assignments(agents,transfers,pd.Timestamp("2026-09-01"))
        self.assertEqual(before.region.iloc[0],"AMER"); self.assertEqual(after.region.iloc[0],"EMEA")
    def test_operating_regions(self): self.assertEqual(set(REGIONS),{"AMER","EMEA","APAC"})
    def test_demo_build_writes_separate_operational_marts(self):
        result=build("2026-08-01","2026-08-07",regenerate=True)
        self.assertGreater(result["chat_rows"],0)
        self.assertGreater(result["forecast_rows"],0)
        hourly=pd.read_csv(OUT/"chat_hourly_by_region_language_channel_market_team.csv")
        shifts=pd.read_csv(OUT/"shift_allocation.csv")
        monthly=pd.read_csv(OUT/"monthly_executive_summary.csv")
        self.assertTrue({"region","language","channel","market","team","time_zone"}<=set(hourly.columns))
        self.assertTrue({"language","required_agents","allocated_agents","coverage_gap"}<=set(shifts.columns))
        self.assertIn("estimated_contract_capacity_hours",monthly.columns)
        self.assertTrue(set(hourly.region)<=set(REGIONS))

if __name__=="__main__": unittest.main()
