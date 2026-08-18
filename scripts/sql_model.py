import pandas as pd
import sqlite3

# Connect to (or create) the database file
# If re_portfolio.db doesn't exist, SQLite creates it automatically
conn = sqlite3.connect('data/re_portfolio.db')
print("✓ Connected to database")

# ── Load all 3 CSVs into database tables ──────────────────────
# if_exists='replace' drops and recreates the table each run
# so you always have fresh data — safe for a project like this

for table_name, csv_path in [
    ('properties',        'data/raw/properties.csv'),
    ('monthly_financials','data/raw/monthly_financials.csv'),
    ('scenarios',         'data/raw/scenarios.csv'),
]:
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"✓ Loaded {len(df):,} rows → table '{table_name}'")

# ── Verification queries ───────────────────────────────────────
# Run these to confirm the data looks correct before moving on

print("\n─── Market summary (should show 5 markets) ───")
q1 = pd.read_sql("""
    SELECT
        market,
        COUNT(*)                              AS properties,
        ROUND(AVG(cap_rate) * 100, 2)         AS avg_cap_rate_pct,
        ROUND(SUM(noi_annual) / 1000000, 1)   AS total_noi_mm
    FROM properties
    GROUP BY market
    ORDER BY total_noi_mm DESC
""", conn)
print(q1.to_string(index=False))

print("\n─── DSCR health check (flag = good / watch / risk) ───")
q2 = pd.read_sql("""
    SELECT
        CASE
            WHEN dscr >= 1.30 THEN 'Healthy'
            WHEN dscr >= 1.15 THEN 'Watch'
            ELSE 'At Risk'
        END AS dscr_flag,
        COUNT(*) AS properties,
        ROUND(AVG(dscr), 2) AS avg_dscr
    FROM properties
    GROUP BY dscr_flag
    ORDER BY avg_dscr DESC
""", conn)
print(q2.to_string(index=False))

conn.close()
print("\n✓ Database ready. File saved at: data/re_portfolio.db")