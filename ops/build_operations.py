"""Build deterministic synthetic chat operations, WFM plans and service-risk packs.

All generated operational facts are synthetic. Forecasts use a transparent weekday/hour
seasonal-naive baseline and queueing approximation; they are planning signals, not truth.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "demo" / "operations"
OUT = ROOT / "data" / "output" / "operations"
SEED = 20261102
REGIONS = {"AMER": "America/New_York", "EMEA": "Europe/London", "APAC": "Asia/Singapore"}
LANGUAGES = ["English", "Spanish", "French", "German", "Japanese"]
REGION_LANGUAGES = {"AMER": ["English","Spanish","French"], "EMEA": ["English","French","German"], "APAC": ["English","Japanese"]}
CHANNELS = ["Chat", "Messaging", "Email"]
MARKETS = {"AMER": ["US", "CA", "MX"], "EMEA": ["UK", "DE", "FR"], "APAC": ["SG", "AU", "JP"]}
TEAMS = ["Core Support", "Billing", "Technical Support", "Retention"]


def make_demo(days: int = 56) -> None:
    """Create source-like, openly-labelled synthetic workload/agent/QA data."""
    rng = np.random.default_rng(SEED)
    RAW.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range("2026-08-01", periods=days, freq="D")
    agents = []
    for i in range(1, 91):
        region = ["AMER", "EMEA", "APAC"][(i - 1) % 3]
        lang = LANGUAGES[(i - 1) % len(LANGUAGES)]
        team = TEAMS[(i - 1) % len(TEAMS)]
        tz = REGIONS[region]
        agents.append({"agent_id": f"AG{i:03d}", "team": team, "home_region": region,
                       "home_language": lang, "time_zone": tz, "contract_hours_week": 40,
                       "employment_status": "Active", "is_synthetic": True})
    agent_frame=pd.DataFrame(agents)
    # Effective-dated changes; intervals are [effective_from, effective_to).
    transfers = pd.DataFrame([
        {"agent_id":"AG004","effective_from":"2026-09-01","effective_to":"","region":"EMEA","language":"French","channel":"Chat","team":"Billing","time_zone":"Europe/London"},
        {"agent_id":"AG011","effective_from":"2026-09-08","effective_to":"","region":"APAC","language":"Japanese","channel":"Messaging","team":"Technical Support","time_zone":"Asia/Singapore"},
        {"agent_id":"AG021","effective_from":"2026-09-15","effective_to":"","region":"AMER","language":"Spanish","channel":"Chat","team":"Retention","time_zone":"America/New_York"},
        {"agent_id":"AG030","effective_from":"2026-09-20","effective_to":"","region":"EMEA","language":"German","channel":"Email","team":"Core Support","time_zone":"Europe/London"},
    ])
    transfers.to_csv(RAW / "agent_assignments.csv", index=False)
    agent_frame.to_csv(RAW / "agents.csv", index=False)
    chats=[]; qa=[]; training=[]
    chat_id=1
    for day in dates:
        active_agents=apply_effective_assignments(agent_frame,transfers,day)
        if (day-dates[0]).days % 7 == 0:
            for agent in rng.choice(agent_frame.agent_id.to_numpy(), size=6, replace=False):
                training.append({"training_event_id":f"TR{len(training)+1:05d}","agent_id":str(agent),"training_date":str(day.date()),
                    "training_minutes":int(rng.choice([30,45,60,90])),"module":str(rng.choice(["Product update","De-escalation","Privacy refresher","Tooling workflow"])),
                    "completed":int(rng.random()<0.94),"is_synthetic":True})
        dow=day.dayofweek
        for region in REGIONS:
            for hour in range(24):
                # Distinct local-time operational demand pattern by region.
                local_peak = 14 if region=="AMER" else (10 if region=="EMEA" else 11)
                shape = 0.55 + 0.95*np.exp(-((hour-local_peak)/5.0)**2)
                day_factor = 0.72 if dow>=5 else 1.0
                for language in REGION_LANGUAGES[region]:
                    if (region=="AMER" and language not in ["English","Spanish","French"]) or (region=="EMEA" and language not in ["English","French","German"]) or (region=="APAC" and language not in ["English","Japanese"]):
                        continue
                    for channel in CHANNELS:
                        channel_factor={"Chat":1.0,"Messaging":0.55,"Email":0.30}[channel]
                        volume=max(0,int(rng.poisson(2.8*shape*day_factor*channel_factor)))
                        for _ in range(volume):
                            team=TEAMS[int(rng.integers(0,len(TEAMS)))]
                            eligible=active_agents[(active_agents.region==region)&(active_agents.language==language)&(active_agents.team==team)]
                            if eligible.empty: eligible=active_agents[active_agents.region==region]
                            agent_id=str(rng.choice(eligible.agent_id.tolist()))
                            offered=int(rng.random()<0.88)
                            resolved=int(offered and rng.random()<0.91)
                            response=float(np.clip(rng.gamma(2.0,1.8)+(0.7 if not offered else 0),0.2,40))
                            handle=float(rng.lognormal(2.55,0.38))
                            converted=int(resolved and rng.random() < (0.20 if team=="Retention" else 0.11))
                            chats.append({"interaction_id":f"CH{chat_id:07d}","created_at":f"{day.date()} {hour:02d}:00:00",
                                "region":region,"language":language,"channel":channel,"market":str(rng.choice(MARKETS[region])),
                                "time_zone":REGIONS[region],"agent_id":agent_id,"team":team,"offered":offered,"resolved":resolved,"first_response_minutes":round(response,2),
                                "handle_minutes":round(handle,2),"converted":converted,"queue_wait_minutes":round(float(rng.gamma(1.7,2.0)),2),
                                "reason":str(rng.choice(["How-to","Billing query","Technical issue","Cancellation","Order status","Account access"],p=[.22,.19,.20,.10,.17,.12])),
                                "escalated":int(rng.random()<(.16 if team=="Technical Support" else .07)), "is_synthetic":True})
                            if resolved:
                                qa.append({"interaction_id":f"CH{chat_id:07d}","qa_score":round(float(np.clip(rng.normal(88,8),50,100)),1),
                                           "reviewed":int(rng.random()<.72),"is_synthetic":True})
                            chat_id+=1
    pd.DataFrame(chats).to_csv(RAW/"chat_interactions.csv",index=False)
    pd.DataFrame(qa).to_csv(RAW/"qa_training.csv",index=False)
    pd.DataFrame(training).to_csv(RAW/"training_events.csv",index=False)


def apply_effective_assignments(agents: pd.DataFrame, assignments: pd.DataFrame, date: pd.Timestamp) -> pd.DataFrame:
    """Resolve one current assignment per agent using effective-dated transfer rows."""
    x=agents.rename(columns={"home_region":"region","home_language":"language"}).copy()
    x["channel"]="Chat"; x["effective_from"]="1900-01-01"; x["effective_to"]=""
    a=assignments.copy()
    if not a.empty:
        a["effective_from"]=pd.to_datetime(a["effective_from"])
        a["effective_to"]=pd.to_datetime(a["effective_to"],errors="coerce")
        a=a[(a.effective_from<=date)&(a.effective_to.isna()|(a.effective_to>date))]
        for row in a.to_dict("records"):
            m=x.agent_id.eq(row["agent_id"])
            for col in ["region","language","channel","team","time_zone"]: x.loc[m,col]=row[col]
    return x


CHAT_COLUMNS=["interaction_id","created_at","region","language","channel","market","team","time_zone","agent_id","offered","resolved","first_response_minutes","handle_minutes","converted","queue_wait_minutes","reason","escalated"]
AGENT_COLUMNS=["agent_id","team","home_region","home_language","time_zone","contract_hours_week","employment_status"]
ASSIGNMENT_COLUMNS=["agent_id","effective_from","effective_to","region","language","channel","team","time_zone"]
QA_COLUMNS=["interaction_id","qa_score","reviewed"]
TRAINING_COLUMNS=["training_event_id","agent_id","training_date","training_minutes","module","completed"]


def validate_source_contract(chats, agents, transfers, qa, training):
    """Fail closed on missing fields, invalid dimensions, keys or intervals."""
    for name, frame, columns in [("chat",chats,CHAT_COLUMNS),("agent roster",agents,AGENT_COLUMNS),
                                 ("agent assignments",transfers,ASSIGNMENT_COLUMNS),("QA",qa,QA_COLUMNS),
                                 ("training",training,TRAINING_COLUMNS)]:
        missing=sorted(set(columns)-set(frame.columns))
        if missing: raise ValueError(f"{name} source missing required columns: {missing}")
    if chats.interaction_id.isna().any() or chats.interaction_id.duplicated().any(): raise ValueError("chat interaction_id must be non-null and unique")
    if agents.agent_id.isna().any() or agents.agent_id.duplicated().any(): raise ValueError("agent_id must be non-null and unique in base roster")
    if chats.region.isna().any() or not chats.region.isin(REGIONS).all(): raise ValueError("chat region must be populated and use AMER, EMEA or APAC")
    if not pd.api.types.is_datetime64_any_dtype(chats.created_at): chats["created_at"]=pd.to_datetime(chats.created_at,errors="coerce")
    if chats.created_at.isna().any(): raise ValueError("chat created_at must be a valid local timestamp")
    for col in ["language","channel","market","team","time_zone","reason","agent_id"]:
        if chats[col].isna().any() or chats[col].astype(str).str.strip().eq("").any(): raise ValueError(f"chat {col} cannot be blank")
    if not set(chats.channel.dropna()) <= set(CHANNELS): raise ValueError("chat channel outside approved domain")
    for col in ["offered","resolved","converted","escalated"]:
        if not set(pd.to_numeric(chats[col],errors="coerce").dropna().unique()) <= {0,1}: raise ValueError(f"chat {col} must be binary")
    for col in ["first_response_minutes","handle_minutes","queue_wait_minutes"]:
        if pd.to_numeric(chats[col],errors="coerce").isna().any() or (pd.to_numeric(chats[col])<0).any(): raise ValueError(f"chat {col} must be numeric and non-negative")
    try:
        for tz in set(chats.time_zone)|set(agents.time_zone)|set(transfers.time_zone): ZoneInfo(str(tz))
    except (ZoneInfoNotFoundError, TypeError): raise ValueError("Every time_zone must be a valid IANA timezone")
    if set(chats.agent_id)-set(agents.agent_id): raise ValueError("chat agent_id is not present in the base roster")
    if set(transfers.agent_id)-set(agents.agent_id): raise ValueError("assignment agent_id is not present in the base roster")
    if set(qa.interaction_id)-set(chats.interaction_id): raise ValueError("QA interaction_id does not resolve to chat source")
    if set(training.agent_id)-set(agents.agent_id): raise ValueError("training agent_id does not resolve to base roster")
    if qa.interaction_id.isna().any() or qa.interaction_id.duplicated().any(): raise ValueError("QA interaction_id must be non-null and unique")
    if training.training_event_id.isna().any() or training.training_event_id.duplicated().any(): raise ValueError("training_event_id must be non-null and unique")
    if pd.to_numeric(qa.qa_score,errors="coerce").isna().any() or not pd.to_numeric(qa.qa_score).between(0,100).all(): raise ValueError("QA scores must be numeric in [0,100]")
    if pd.to_numeric(training.training_minutes,errors="coerce").isna().any() or (pd.to_numeric(training.training_minutes)<=0).any(): raise ValueError("training_minutes must be positive")
    if not set(pd.to_numeric(training.completed,errors="coerce").dropna().unique()) <= {0,1}: raise ValueError("training completed must be binary")
    for col in ["region","language","channel","team","time_zone"]:
        if transfers[col].isna().any() or transfers[col].astype(str).str.strip().eq("").any(): raise ValueError(f"assignment {col} cannot be blank")
    for col in ["home_region","home_language","team","time_zone"]:
        if agents[col].isna().any() or agents[col].astype(str).str.strip().eq("").any(): raise ValueError(f"agent roster {col} cannot be blank")
    if transfers.effective_from.isna().any(): raise ValueError("assignment effective_from is required")
    if (pd.to_numeric(agents.contract_hours_week,errors="coerce")<=0).any(): raise ValueError("contract_hours_week must be positive")
    intervals=transfers.copy(); intervals["effective_from"]=pd.to_datetime(intervals.effective_from,errors="coerce"); intervals["effective_to"]=pd.to_datetime(intervals.effective_to,errors="coerce")
    if intervals.effective_from.isna().any(): raise ValueError("assignment effective_from must be a valid date")
    for _, group in intervals.groupby("agent_id"):
        group=group.sort_values("effective_from").reset_index(drop=True)
        for i in range(1,len(group)):
            prior_end=group.loc[i-1,"effective_to"]
            if pd.isna(prior_end) or prior_end>group.loc[i,"effective_from"]: raise ValueError("effective-dated assignment intervals overlap")


def build(start: str="2026-08-01", end: str="2026-09-25", regenerate: bool=False, source_files: dict | None=None) -> dict:
    if source_files is None:
        if regenerate or not (RAW/"chat_interactions.csv").exists(): make_demo()
        source_files={"chat":RAW/"chat_interactions.csv","agents":RAW/"agents.csv","assignments":RAW/"agent_assignments.csv",
                      "qa":RAW/"qa_training.csv","training":RAW/"training_events.csv"}
    expected={"chat","agents","assignments","qa","training"}
    if set(source_files)!=expected: raise ValueError(f"Supply all five sources together: {sorted(expected)}")
    chats=pd.read_csv(source_files["chat"],parse_dates=["created_at"])
    agents=pd.read_csv(source_files["agents"])
    transfers=pd.read_csv(source_files["assignments"])
    qa=pd.read_csv(source_files["qa"])
    training_source=pd.read_csv(source_files["training"],parse_dates=["training_date"])
    validate_source_contract(chats,agents,transfers,qa,training_source)
    chats=chats[CHAT_COLUMNS+([ "is_synthetic" ] if "is_synthetic" in chats.columns else [])].copy()
    agents=agents[AGENT_COLUMNS+([ "is_synthetic" ] if "is_synthetic" in agents.columns else [])].copy()
    qa=qa[QA_COLUMNS+([ "is_synthetic" ] if "is_synthetic" in qa.columns else [])].copy()
    training_source=training_source[TRAINING_COLUMNS+([ "is_synthetic" ] if "is_synthetic" in training_source.columns else [])].copy()
    if "is_synthetic" not in chats: chats["is_synthetic"]=False
    OUT.mkdir(parents=True,exist_ok=True)
    chats=chats[(chats.created_at.dt.date>=pd.Timestamp(start).date())&(chats.created_at.dt.date<=pd.Timestamp(end).date())].copy()
    if chats.empty: raise ValueError("No chat interactions in requested reporting window")
    chats["date"]=chats.created_at.dt.strftime("%Y-%m-%d")
    chats["hour"]=chats.created_at.dt.hour
    # Real regional dimensions; there are no Site A/B/C values in this model.
    dims=["date","hour","region","language","channel","market","team","time_zone"]
    hourly=chats.groupby(dims,dropna=False).agg(contacts=("interaction_id","count"),offered=("offered","sum"),resolved=("resolved","sum"),
       conversions=("converted","sum"),avg_response_minutes=("first_response_minutes","mean"),p90_response_minutes=("first_response_minutes",lambda s:s.quantile(.9)),
       avg_handle_minutes=("handle_minutes","mean"),avg_queue_wait_minutes=("queue_wait_minutes","mean"),escalations=("escalated","sum")).reset_index()
    hourly["service_level_5m"]=chats.groupby(dims).first_response_minutes.apply(lambda s:(s<=5).mean()).values
    hourly.to_csv(OUT/"chat_hourly_by_region_language_channel_market_team.csv",index=False)
    # Hour-of-week profile with trend-adjusted last 14 days; forecast next seven days.
    chats["weekday"]=chats.created_at.dt.dayofweek
    hist=chats.groupby(["region","language","channel","team","time_zone","weekday","hour"],as_index=False).agg(actual_contacts=("interaction_id","count"))
    recent_cut=chats.created_at.max()-pd.Timedelta(days=14)
    recent=chats[chats.created_at>=recent_cut].groupby(["region","language","channel","team","time_zone","weekday","hour"]).size().rename("recent_contacts").reset_index()
    hist=hist.merge(recent,on=["region","language","channel","team","time_zone","weekday","hour"],how="left").fillna({"recent_contacts":0})
    hist["forecast_contacts_per_hour"]=(0.65*hist.actual_contacts/max(1,chats.date.nunique())+0.35*hist.recent_contacts/max(1,(chats.created_at.max().normalize()-recent_cut.normalize()).days+1))
    hist["forecast_contacts_per_hour"]=hist.forecast_contacts_per_hour.clip(lower=0).round(2)
    future=pd.date_range(pd.Timestamp(end)+pd.Timedelta(days=1),periods=7,freq="D")
    f=[]
    for d in future:
        tmp=hist[hist.weekday.eq(d.dayofweek)].copy(); tmp["forecast_date"]=d.strftime("%Y-%m-%d"); f.append(tmp)
    forecast=pd.concat(f,ignore_index=True)
    # Erlang-style workload approximation: workload hours / interval hours / occupancy.
    forecast["workload_hours"]=forecast.forecast_contacts_per_hour*forecast.channel.map({"Chat":7.5,"Messaging":6.5,"Email":9.0})/60
    forecast["required_agents"]=np.ceil(forecast.workload_hours/(0.5*0.82)).astype(int)
    forecast["forecast_method"]="weekday-hour seasonal baseline (65% full-window profile, 35% recent profile)"
    forecast.to_csv(OUT/"hourly_demand_forecast.csv",index=False)
    # Build a transparent 8h shift plan; shift windows in local timezone, assignment effective at forecast date.
    shift_rows=[]
    for d in future:
        active=apply_effective_assignments(agents,transfers,d)
        for region in REGIONS:
            for language in REGION_LANGUAGES[region]:
              for team in TEAMS:
                for channel in CHANNELS:
                    for shift,start_hour in [("Early",6),("Core",14),("Late",22)]:
                        local_hours={(start_hour+i)%24 for i in range(8)}
                        demand=forecast[(forecast.forecast_date==d.strftime("%Y-%m-%d"))&(forecast.region==region)&(forecast.language==language)&(forecast.team==team)&(forecast.channel==channel)&(forecast.hour.isin(local_hours))]
                        req=int(demand.required_agents.max()) if not demand.empty else 0
                        eligible=active[(active.region==region)&(active.language==language)&(active.team==team)&((active.channel==channel)|(active.channel=="Chat"))]
                        # Allocated agents capped by available headcount; this is capacity planning, not a roster.
                        allocated=min(len(eligible),req)
                        shift_rows.append({"date":d.strftime("%Y-%m-%d"),"region":region,"language":language,"team":team,"channel":channel,"shift":shift,
                          "local_start_hour":start_hour,"local_end_hour":(start_hour+8)%24,"required_agents":req,"available_agents":len(eligible),
                          "allocated_agents":allocated,"coverage_gap":max(0,req-allocated),"time_zone":REGIONS[region],"is_synthetic":True})
    shifts=pd.DataFrame(shift_rows); shifts.to_csv(OUT/"shift_allocation.csv",index=False)
    # Daily service/commercial risk table. Thresholds documented and configurable in code.
    daily=chats.groupby(["date","region","language","channel","market","team","time_zone"],as_index=False).agg(contacts=("interaction_id","count"),
      avg_response_minutes=("first_response_minutes","mean"),p90_response_minutes=("first_response_minutes",lambda s:s.quantile(.9)),
      conversion_rate=("converted","mean"),avg_queue_wait_minutes=("queue_wait_minutes","mean"),escalations=("escalated","sum"),offered=("offered","sum"))
    gap=shifts.groupby(["date","region","language","team","channel","time_zone"],as_index=False).agg(uncovered_shift_hours=("coverage_gap",lambda s:int((s>0).sum())*8),max_agent_gap=("coverage_gap","max"))
    daily=daily.merge(gap,on=["date","region","language","team","channel","time_zone"],how="left").fillna({"uncovered_shift_hours":0,"max_agent_gap":0})
    daily["risk_reasons"]=daily.apply(lambda r:"; ".join([x for x,v in [("coverage gap",r.max_agent_gap>0),("slow response",r.p90_response_minutes>10),("low conversion",r.conversion_rate<.08),("queue saturation",r.avg_queue_wait_minutes>8)] if v]) or "none",axis=1)
    daily["risk_level"]=daily.risk_reasons.map(lambda x:"HIGH" if sum(k in x for k in ["coverage gap","slow response","queue saturation"])>=2 else ("MEDIUM" if x!="none" else "LOW"))
    daily.to_csv(OUT/"daily_service_commercial_risk.csv",index=False)
    # Daily tracker, weekly capacity brief, monthly exec summary.
    tracker=daily.groupby(["date","region"],as_index=False).agg(contacts=("contacts","sum"),avg_response_minutes=("avg_response_minutes","mean"),
      conversion_rate=("conversion_rate","mean"),high_risk_segments=("risk_level",lambda s:int((s=="HIGH").sum())))
    coverage=shifts.groupby(["date","region"],as_index=False).agg(uncovered_shift_hours=("coverage_gap",lambda s:int((s>0).sum())*8))
    tracker=tracker.merge(coverage,on=["date","region"],how="left").fillna({"uncovered_shift_hours":0})
    tracker.to_csv(OUT/"daily_tracker.csv",index=False)
    weekly=shifts.assign(week=pd.to_datetime(shifts.date).dt.to_period("W").astype(str)).groupby(["week","region","language","team","channel","time_zone"],as_index=False).agg(required_agent_shifts=("required_agents","sum"),allocated_agent_shifts=("allocated_agents","sum"),coverage_gap_shifts=("coverage_gap",lambda s:int((s>0).sum())),peak_gap=("coverage_gap","max"))
    weekly.to_csv(OUT/"weekly_capacity_brief.csv",index=False)
    chats["month"]=chats.created_at.dt.to_period("M").astype(str)
    monthly=chats.groupby(["month","region"],as_index=False).agg(contacts=("interaction_id","count"),resolved=("resolved","sum"),conversions=("converted","sum"),
      avg_response_minutes=("first_response_minutes","mean"),revenue_proxy_conversions=("converted","sum"),productive_handling_hours=("handle_minutes",lambda s:s.sum()/60))
    roster_rows=[]
    for month,region in monthly[["month","region"]].drop_duplicates().itertuples(index=False):
        month_end=pd.Period(month,freq="M").end_time.normalize()
        roster=apply_effective_assignments(agents,transfers,month_end)
        roster=roster[(roster.region==region)&(roster.employment_status=="Active")]
        month_days=pd.Period(month,freq="M").days_in_month
        roster_rows.append({"month":month,"region":region,"roster_agents":roster.agent_id.nunique(),
            "estimated_contract_capacity_hours":roster.contract_hours_week.sum()*month_days/7})
    monthly=monthly.merge(pd.DataFrame(roster_rows),on=["month","region"],how="left")
    monthly["handling_utilisation"]=monthly.productive_handling_hours/monthly.estimated_contract_capacity_hours.replace(0,np.nan)
    monthly["resolution_rate"]=monthly.resolved/monthly.contacts
    monthly["conversion_rate"]=monthly.conversions/monthly.contacts
    monthly.to_csv(OUT/"monthly_executive_summary.csv",index=False)
    # Team/agent productivity uses the synthetic agent assignment stored on each generated interaction.
    ids=chats[["interaction_id","agent_id","team","resolved","handle_minutes","escalated"]].copy()
    prod=ids.groupby(["agent_id","team"],as_index=False).agg(handled=("interaction_id","count"),resolved=("resolved","sum"),handle_minutes=("handle_minutes","sum"),escalations=("escalated","sum"))
    prod["resolution_rate"]=prod.resolved/prod.handled
    prod.to_csv(OUT/"agent_team_productivity.csv",index=False)
    team=prod.groupby("team",as_index=False).agg(agents=("agent_id","nunique"),handled=("handled","sum"),resolved=("resolved","sum"),avg_handle_minutes=("handle_minutes",lambda s:s.sum()/max(1,prod.loc[s.index,"handled"].sum())),escalations=("escalations","sum"))
    team["resolution_rate"]=team.resolved/team.handled
    team.to_csv(OUT/"team_productivity.csv",index=False)
    q=qa.merge(chats[["interaction_id","team","reason","escalated"]],on="interaction_id",how="inner")
    qa_summary=q.groupby("team",as_index=False).agg(events=("interaction_id","count"),avg_qa_score=("qa_score","mean"),review_rate=("reviewed","mean"))
    qa_summary["event_type"]="QA"; qa_summary["training_minutes"]=np.nan; qa_summary["completion_rate"]=np.nan
    training=training_source.copy()
    training["team"]=None
    for training_date, idx in training.groupby("training_date").groups.items():
        active=apply_effective_assignments(agents,transfers,pd.Timestamp(training_date))
        lookup=active.set_index("agent_id").team
        training.loc[idx,"team"]=training.loc[idx,"agent_id"].map(lookup)
    training_summary=training.groupby("team",as_index=False).agg(events=("training_event_id","count"),training_minutes=("training_minutes","sum"),completion_rate=("completed","mean"))
    training_summary["event_type"]="Training"; training_summary["avg_qa_score"]=np.nan; training_summary["review_rate"]=np.nan
    pd.concat([qa_summary,training_summary],ignore_index=True)[["team","event_type","events","avg_qa_score","review_rate","training_minutes","completion_rate"]].to_csv(OUT/"qa_training_split.csv",index=False)
    chats.groupby(["reason","escalated"],as_index=False).agg(interactions=("interaction_id","count"),avg_response_minutes=("first_response_minutes","mean"),conversion_rate=("converted","mean")).to_csv(OUT/"reason_escalation_deep_dive.csv",index=False)
    # Data quality audit results, with hard fails for critical source contract violations.
    dq=[]
    def add(check,passed,detail): dq.append({"check":check,"passed":bool(passed),"detail":str(detail)})
    add("unique interaction_id",chats.interaction_id.is_unique,f"rows={len(chats)}")
    add("non-negative volumes",bool((hourly.contacts>=0).all()),f"segments={len(hourly)}")
    add("allowed region dimension",set(chats.region)<=set(REGIONS),str(sorted(chats.region.unique())))
    add("required operational dimensions populated",bool(chats[["language","channel","market","team","time_zone"]].notna().all().all()),"language/channel/market/team/time_zone must be populated")
    add("agent keys resolve",set(chats.agent_id)<=set(agents.agent_id),"chat agent IDs must exist in roster")
    add("language/channel/timezone complete",bool(chats[["language","channel","time_zone"]].notna().all().all()),"required coverage dimensions populated")
    add("no fictional site labels",not chats.region.astype(str).str.match(r"Site [ABC]").any(),"region must be AMER/EMEA/APAC")
    add("response-time valid",bool(chats.first_response_minutes.ge(0).all()),"minutes >= 0")
    add("QA interaction referential integrity",set(qa.interaction_id)<=set(pd.read_csv(source_files["chat"]).interaction_id),"QA rows reference chat IDs")
    add("effective-dated assignments valid",pd.to_datetime(transfers.effective_from).notna().all(),"effective_from required")
    overlap_ok=True
    for _, group in transfers.assign(effective_from=pd.to_datetime(transfers.effective_from),effective_to=pd.to_datetime(transfers.effective_to,errors="coerce")).groupby("agent_id"):
        group=group.sort_values("effective_from").reset_index(drop=True)
        for i in range(1,len(group)):
            prior_end=group.loc[i-1,"effective_to"]
            if pd.isna(prior_end) or prior_end>group.loc[i,"effective_from"]: overlap_ok=False
    add("assignment intervals do not overlap",overlap_ok,"effective intervals use [from,to) semantics")
    add("forecast nonnegative",bool(forecast.forecast_contacts_per_hour.ge(0).all()),"forecast >= 0")
    add("capacity allocation bounded",bool((shifts.allocated_agents<=shifts.available_agents).all()),"allocated <= available")
    pd.DataFrame(dq).to_csv(OUT/"data_quality_checks.csv",index=False)
    if not all(x["passed"] for x in dq): raise ValueError("Operational data-quality checks failed")
    return {"chat_rows":len(chats),"hourly_segments":len(hourly),"forecast_rows":len(forecast),"shift_rows":len(shifts),"risk_rows":len(daily),"checks":len(dq)}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--generate-demo",action="store_true"); p.add_argument("--start",default="2026-08-01"); p.add_argument("--end",default="2026-09-25")
    for key in ["chat","agents","assignments","qa","training"]: p.add_argument("--"+key+"-source")
    a=p.parse_args(); supplied={k:getattr(a,k+"_source") for k in ["chat","agents","assignments","qa","training"]}
    source_files=None if all(v is None for v in supplied.values()) else {k:v for k,v in supplied.items() if v is not None}
    print(build(a.start,a.end,a.generate_demo,source_files))
