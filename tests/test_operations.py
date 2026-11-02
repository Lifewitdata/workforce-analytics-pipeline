import unittest
import pandas as pd
from ops.build_operations import apply_effective_assignments, REGIONS

class OperationsTests(unittest.TestCase):
    def test_effective_dated_transfer(self):
        agents=pd.DataFrame([{"agent_id":"AG001","team":"A","home_region":"AMER","home_language":"English","time_zone":"America/New_York","contract_hours_week":40,"employment_status":"Active"}])
        transfers=pd.DataFrame([{"agent_id":"AG001","effective_from":"2026-09-01","effective_to":"","region":"EMEA","language":"French","channel":"Chat","team":"B","time_zone":"Europe/Paris"}])
        before=apply_effective_assignments(agents,transfers,pd.Timestamp("2026-08-31"))
        after=apply_effective_assignments(agents,transfers,pd.Timestamp("2026-09-01"))
        self.assertEqual(before.region.iloc[0],"AMER"); self.assertEqual(after.region.iloc[0],"EMEA")
    def test_operating_regions(self): self.assertEqual(set(REGIONS),{"AMER","EMEA","APAC"})

if __name__=="__main__": unittest.main()
