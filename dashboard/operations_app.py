"""Local interactive dashboard for the separate synthetic operations mart.
Run after generating the demo: streamlit run dashboard/operations_app.py
"""
from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ops.build_operations import build, OUT

st.set_page_config(page_title="Workforce Operations Command Centre", page_icon="📊", layout="wide")
st.title("Workforce Operations Command Centre")
st.caption("Synthetic educational demo • operational chat model is separate from the monthly HR pack")
required = ["daily_tracker.csv", "hourly_demand_forecast.csv", "shift_allocation.csv", "daily_service_commercial_risk.csv", "monthly_executive_summary.csv"]
if not all((OUT / f).exists() for f in required):
    with st.spinner("Building the reproducible synthetic operations demo…"):
        build()

def load(name):
    return pd.read_csv(OUT / name)

daily = load("daily_tracker.csv")
risks = load("daily_service_commercial_risk.csv")
forecast = load("hourly_demand_forecast.csv")
shifts = load("shift_allocation.csv")
monthly = load("monthly_executive_summary.csv")
productivity = load("team_productivity.csv")
qa = load("qa_training_split.csv")
reasons = load("reason_escalation_deep_dive.csv")

st.sidebar.header("Filters")
regions = ["All"] + sorted(daily.region.dropna().unique().tolist())
region = st.sidebar.selectbox("Region", regions)
dates = sorted(daily.date.dropna().unique().tolist())
selected_date = st.sidebar.selectbox("Operating date", dates, index=len(dates)-1)
view = daily[daily.date.eq(selected_date)]
if region != "All":
    view = view[view.region.eq(region)]
    risks = risks[(risks.date.eq(selected_date)) & risks.region.eq(region)]
    forecast = forecast[forecast.region.eq(region)]
    shifts = shifts[(shifts.date.isin(sorted(shifts.date.unique())[:7])) & shifts.region.eq(region)]
    monthly = monthly[monthly.region.eq(region)]
else:
    risks = risks[risks.date.eq(selected_date)]

contacts = int(view.contacts.sum()) if not view.empty else 0
response = float(view.avg_response_minutes.mean()) if not view.empty else 0
conversion = float(view.conversion_rate.mean()) if not view.empty else 0
gaps = int(view.uncovered_shift_hours.sum()) if not view.empty else 0
c1,c2,c3,c4 = st.columns(4)
c1.metric("Contacts", f"{contacts:,}")
c2.metric("Avg first response", f"{response:.1f} min")
c3.metric("Conversion proxy", f"{conversion:.1%}")
c4.metric("Uncovered shift hours", f"{gaps:,}")

left,right = st.columns(2)
with left:
    st.subheader("Daily contact volume by region")
    trend = daily[daily.date.le(selected_date)]
    if region != "All": trend = trend[trend.region.eq(region)]
    chart = trend.pivot_table(index="date", columns="region", values="contacts", aggfunc="sum").tail(21)
    st.line_chart(chart)
with right:
    st.subheader("Service and commercial risk")
    risk_counts = risks.groupby("risk_level").size().rename("segments")
    st.bar_chart(risk_counts)
    st.dataframe(risks[["date","region","language","channel","market","team","p90_response_minutes","conversion_rate","max_agent_gap","risk_level","risk_reasons"]].sort_values(["risk_level","p90_response_minutes"],ascending=[True,False]), use_container_width=True, hide_index=True)

st.subheader("Hourly demand forecast and shift capacity")
t1,t2,t3 = st.tabs(["Demand forecast","Shift allocation","Monthly executive view"])
with t1:
    f=forecast.copy()
    f["forecast_timestamp"]=pd.to_datetime(f.forecast_date)+pd.to_timedelta(f.hour,unit="h")
    series=f.groupby("forecast_timestamp",as_index=True).forecast_contacts_per_hour.sum()
    st.line_chart(series)
    st.dataframe(f[["forecast_date","hour","region","language","channel","team","forecast_contacts_per_hour","required_agents","forecast_method"]].head(250),use_container_width=True,hide_index=True)
with t2:
    st.dataframe(shifts[["date","region","language","team","channel","shift","time_zone","required_agents","available_agents","allocated_agents","coverage_gap"]],use_container_width=True,hide_index=True)
with t3:
    st.dataframe(monthly,use_container_width=True,hide_index=True)
    st.caption("Revenue is represented only by a conversion-count proxy; no transaction value is supplied in the demo.")

st.subheader("Team productivity, QA and root causes")
a,b = st.columns(2)
with a:
    st.dataframe(productivity,use_container_width=True,hide_index=True)
    st.dataframe(qa,use_container_width=True,hide_index=True)
with b:
    st.bar_chart(reasons.set_index("reason")[["interactions"]])
    st.dataframe(reasons,use_container_width=True,hide_index=True)
st.caption("Agent assignments, volumes, service metrics, staffing estimates and QA events are generated demo data. Forecasts are planning estimates, not validated predictions or employee decisions.")
