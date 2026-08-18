import pandas as pd
import sqlite3
import os

conn = sqlite3.connect('data/re_portfolio.db')
os.makedirs('data/processed', exist_ok=True)

# ── 1. MASTER PORTFOLIO TABLE ──────────────────────────────────
# Adds calculated columns Power BI will use for colors and flags
master = pd.read_sql("""
    SELECT
        p.*,

        -- Appreciation: how much value has grown since purchase
        ROUND(p.current_value - p.purchase_price, 0)
            AS unrealized_gain,
        ROUND((p.current_value - p.purchase_price)
            / p.purchase_price * 100, 1)
            AS appreciation_pct,

        -- Going-in yield: current NOI as % of current value
        ROUND(p.noi_annual / p.current_value * 100, 2)
            AS going_in_yield,

        -- DSCR flag: Green / Amber / Red for conditional formatting
        CASE
            WHEN p.dscr >= 1.30 THEN 'Healthy'
            WHEN p.dscr >= 1.15 THEN 'Watch'
            ELSE                     'At Risk'
        END AS dscr_flag,

        -- Occupancy flag: same idea for occupancy health
        CASE
            WHEN p.occupancy_rate >= 0.95 THEN 'Strong'
            WHEN p.occupancy_rate >= 0.90 THEN 'Stable'
            ELSE                               'Below Target'
        END AS occupancy_flag

    FROM properties p
""", conn)

master.to_csv('data/processed/portfolio_master.csv', index=False)
print(f"✓ portfolio_master.csv — {len(master)} rows, {len(master.columns)} columns")

# ── 2. MONTHLY TRENDS TABLE ────────────────────────────────────
# Joins monthly financials with property metadata
# Power BI uses this for trend charts on the drill-down page
monthly = pd.read_sql("""
    SELECT
        m.*,
        p.market,
        p.asset_type,
        p.status,
        p.property_name
    FROM monthly_financials m
    JOIN properties p ON m.property_id = p.property_id
""", conn)

monthly.to_csv('data/processed/monthly_trends.csv', index=False)
print(f"✓ monthly_trends.csv — {len(monthly)} rows")

# ── 3. PORTFOLIO MONTHLY AGGREGATE ─────────────────────────────
# Rolls up all 50 properties into one monthly portfolio view
# Used for the top-level trend chart on the overview page
agg = monthly.groupby('month').agg(
    total_noi             = ('noi_monthly',          'sum'),
    avg_occupancy         = ('occupancy',             'mean'),
    total_revenue         = ('revenue',               'sum'),
    total_debt_service    = ('debt_service_monthly',  'sum'),
    active_properties     = ('property_id',           'nunique'),
).reset_index()

# Portfolio DSCR = total NOI / total debt service
agg['portfolio_dscr'] = (agg['total_noi'] / agg['total_debt_service']).round(2)
agg['avg_occupancy']  = agg['avg_occupancy'].round(3)

agg.to_csv('data/processed/portfolio_monthly_agg.csv', index=False)
print(f"✓ portfolio_monthly_agg.csv — {len(agg)} rows")

# ── 4. MARKET SUMMARY TABLE ────────────────────────────────────
# One row per market — used for the bar chart and map
market_summary = pd.read_sql("""
    SELECT
        market,
        COUNT(*)                          AS property_count,
        SUM(noi_annual)                   AS total_noi,
        ROUND(AVG(cap_rate) * 100, 2)     AS avg_cap_rate_pct,
        ROUND(AVG(dscr), 2)               AS avg_dscr,
        ROUND(AVG(occupancy_rate) * 100,1)AS avg_occupancy_pct,
        SUM(current_value)                AS total_portfolio_value
    FROM properties
    GROUP BY market
    ORDER BY total_noi DESC
""", conn)

market_summary.to_csv('data/processed/market_summary.csv', index=False)
print(f"✓ market_summary.csv — {len(market_summary)} rows")

conn.close()
print("\n✓ ETL complete — 4 processed files ready for Power BI")