"""Project paths and explicit demo settings; synthetic educational data."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW, OUT, DOC = ROOT/'data/raw', ROOT/'data/output', ROOT/'docs'
KEY = ['report_month', 'Department', 'location']
COUNTS = ['opening','closing','hires','exits','voluntary','involuntary','tenure_sum','income_sum','income_count','overtime','overtime_count']
RCOUNTS = ['applications','offers_in_cohort','accepted','declined','pending','hire_days_sum']
BANDS = ['<1 year','1–<3 years','3–<5 years','5–<10 years','10+ years']
LABEL = 'SYNTHETIC EDUCATIONAL DATA — monthly history and recruiting are simulated.'

INTERIM = ROOT/"data/interim"
LOGS = ROOT/"logs"
OPTIMIZATION = ROOT/"optimization"
SEED = 42
REPORT_START = "2025-01-01"
REPORT_END = "2025-12-31"
APPLICATION_COUNT = 2400
LOCATIONS = ["Site A", "Site B", "Site C"]
ATTRITION_THRESHOLD = 0.02
