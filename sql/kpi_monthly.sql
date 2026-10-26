-- Synthetic educational data. SQLite dialect; executed by src/sql_validation.py.
WITH employee AS (
 SELECT report_month,Department,location,
 SUM(opening) opening,SUM(closing) closing,SUM(hires) hires,SUM(exits) exits,
 SUM(voluntary) voluntary,SUM(involuntary) involuntary,SUM(tenure_sum) tenure_sum,
 SUM(income_sum) income_sum,SUM(income_count) income_count,
 SUM(overtime) overtime,SUM(overtime_count) overtime_count
 FROM employee_months GROUP BY report_month,Department,location
), calendar AS (
 SELECT *,date(report_month||'-01') month_start,
 date(report_month||'-01','+1 month','-1 day') month_end FROM group_grid
), recruiting AS (
 SELECT g.report_month,g.Department,g.location,
 SUM(CASE WHEN date(a.apply_date) BETWEEN g.month_start AND g.month_end THEN 1 ELSE 0 END) applications,
 SUM(CASE WHEN date(a.apply_date) BETWEEN g.month_start AND g.month_end AND date(a.offer_date)<=g.month_end THEN 1 ELSE 0 END) offers_in_cohort,
 SUM(CASE WHEN date(a.decision_date) BETWEEN g.month_start AND g.month_end AND a.offer_decision='Accepted' THEN 1 ELSE 0 END) accepted,
 SUM(CASE WHEN date(a.decision_date) BETWEEN g.month_start AND g.month_end AND a.offer_decision='Declined' THEN 1 ELSE 0 END) declined,
 SUM(CASE WHEN date(a.offer_date)<=g.month_end AND (a.decision_date IS NULL OR date(a.decision_date)>g.month_end) THEN 1 ELSE 0 END) pending,
 SUM(CASE WHEN date(a.decision_date) BETWEEN g.month_start AND g.month_end AND a.offer_decision='Accepted' THEN julianday(a.acceptance_date)-julianday(a.apply_date) ELSE 0 END) hire_days_sum
 FROM calendar g LEFT JOIN applications a ON a.Department=g.Department
 AND a.location=g.location AND date(a.apply_date)<=g.month_end
 GROUP BY g.report_month,g.Department,g.location
), combined AS (
 SELECT g.report_month,g.Department,g.location,
 COALESCE(e.opening,0) opening,COALESCE(e.closing,0) closing,
 COALESCE(e.hires,0) hires,COALESCE(e.exits,0) exits,
 COALESCE(e.voluntary,0) voluntary,COALESCE(e.involuntary,0) involuntary,
 COALESCE(e.tenure_sum,0) tenure_sum,COALESCE(e.income_sum,0) income_sum,
 COALESCE(e.income_count,0) income_count,COALESCE(e.overtime,0) overtime,
 COALESCE(e.overtime_count,0) overtime_count,
 COALESCE(r.applications,0) applications,COALESCE(r.offers_in_cohort,0) offers_in_cohort,
 COALESCE(r.accepted,0) accepted,COALESCE(r.declined,0) declined,
 COALESCE(r.pending,0) pending,COALESCE(r.hire_days_sum,0) hire_days_sum
 FROM group_grid g LEFT JOIN employee e USING(report_month,Department,location)
 LEFT JOIN recruiting r USING(report_month,Department,location)
), denominators AS (
 SELECT *,(opening+closing)/2.0 average_headcount FROM combined
)
SELECT *,exits*1.0/NULLIF(average_headcount,0) attrition_rate,
 voluntary*1.0/NULLIF(average_headcount,0) voluntary_rate,
 involuntary*1.0/NULLIF(average_headcount,0) involuntary_rate,
 tenure_sum*1.0/NULLIF(closing,0) avg_tenure_years,
 income_sum*1.0/NULLIF(income_count,0) avg_monthly_income,
 overtime*1.0/NULLIF(overtime_count,0) overtime_share,
 hire_days_sum*1.0/NULLIF(accepted,0) time_to_hire_days,
 offers_in_cohort*1.0/NULLIF(applications,0) funnel_conversion,
 accepted*1.0/NULLIF(accepted+declined,0) offer_acceptance_rate
FROM denominators ORDER BY report_month,Department,location;
