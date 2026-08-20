# Real Estate Portfolio Performance Dashboard

## What this is
Power BI executive dashboard tracking NOI, cap rate, DSCR, and 
occupancy across a 50-property simulated portfolio spanning 5 
Sun Belt markets, with scenario analysis and property drill-down.

## Dashboard pages
- **Portfolio Overview** — 4 KPI cards, NOI by market/asset type, 
  geographic bubble map, risk/return scatter plot
- **Property Drill-Down** — 50-property table with DSCR health 
  flags, 36-month NOI and occupancy trend charts per property
- **Scenario Analysis** — Base / Upside / Downside toggle updating 
  all KPIs and charts live

## Tech stack
Python (pandas, numpy) · SQLite · Power BI Desktop · DAX

## How to run it yourself
1. Clone this repo
2. pip install pandas numpy faker openpyxl
3. python scripts/generate_data.py
4. python scripts/sql_model.py
5. python scripts/etl_pipeline.py
6. Open powerbi/re_dashboard.pbix

## Finance skills demonstrated
Real estate finance · Asset management · Portfolio analytics · 
NOI/cap rate/DSCR modeling · Scenario planning · Power BI · DAX · 
Python ETL