import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# These two lines ensure the same "random" numbers every time you run
# the script — so your data stays consistent across runs
np.random.seed(42)
random.seed(42)
market_coords = {
    'Dallas-Fort Worth': (32.7767, -96.7970),
    'Austin':            (30.2672, -97.7431),
    'Houston':           (29.7604, -95.3698),
    'Phoenix':           (33.4484, -112.0740),
    'Denver':            (39.7392, -104.9903),
}

# The 5 real Sun Belt markets your portfolio will cover
markets = ['Dallas-Fort Worth', 'Austin', 'Houston', 'Phoenix', 'Denver']

# 4 commercial real estate asset types
asset_types = ['Multifamily', 'Industrial', 'Office', 'Retail']

# 3 business plan statuses common in RE portfolios
statuses = ['Stabilized', 'Value-Add', 'Development']

properties = []

for i in range(1, 51):  # loops 50 times — creates 50 properties
    mkt   = random.choice(markets)
    atype = random.choice(asset_types)
    sqft  = random.randint(20000, 200000)

    # Purchase price: $8M to $80M — realistic mid-market CRE range
    purchase_price = random.randint(8_000_000, 80_000_000)

    # Cap rate: 5.5% to 7.5% — realistic Sun Belt cap rates
    cap_rate = round(random.uniform(0.055, 0.075), 4)

    # NOI = purchase price × cap rate — core CRE formula
    noi = round(purchase_price * cap_rate, 0)

    # Debt sizing: 65–75% LTV is standard acquisition financing
    ltv         = random.uniform(0.65, 0.75)
    loan_amount = round(purchase_price * ltv, 0)
    interest_rate = round(random.uniform(0.055, 0.072), 4)

    # Annual debt service = loan × rate × 1.15 (amortization factor)
    # DSCR = NOI / Debt Service — must be > 1.0 for lender to approve
    annual_debt_service = round(loan_amount * interest_rate * 1.15, 0)
    dscr = round(noi / annual_debt_service, 2)

    # Occupancy: 88% to 98% — realistic stabilized range
    occupancy = round(random.uniform(0.88, 0.98), 3)

    properties.append({
        'property_id'       : f'PROP-{i:03d}',
        'property_name'     : f'{mkt.split("-")[0]} {atype} {i:02d}',
        'market'            : mkt,
        'asset_type'        : atype,
        'status'            : random.choice(statuses),
        'acquisition_date'  : (datetime(2019,1,1) + timedelta(days=random.randint(0,1500))).strftime('%Y-%m-%d'),
        'purchase_price'    : purchase_price,
        'current_value'     : round(purchase_price * random.uniform(1.05, 1.35), 0),
        'sqft'              : sqft,
        'noi_annual'        : noi,
        'cap_rate'          : cap_rate,
        'occupancy_rate'    : occupancy,
        'loan_amount'       : loan_amount,
        'interest_rate'     : interest_rate,
        'annual_debt_service': annual_debt_service,
        'dscr'              : dscr,
        'ltv'               : round(ltv, 3),
        'latitude'          : market_coords[mkt][0],
        'longitude'         : market_coords[mkt][1]
    })

# Convert list of dicts to a table and save as CSV
df = pd.DataFrame(properties)
df.to_csv('data/raw/properties.csv', index=False)
print(f"✓ Created properties.csv — {len(df)} rows")
print(df[['property_name','market','noi_annual','cap_rate','dscr']].head(5))

# ── Monthly financial history ──────────────────────────────────
# 36 months × 50 properties = 1,800 rows
# Each row = one property's financials for one month

monthly_records = []

# FIX: use pd.date_range instead of timedelta arithmetic
# This guarantees exactly 36 monthly periods ending Dec 2024
monthly_dates = pd.date_range('2022-01-01', periods=36, freq='MS')

for _, prop in df.iterrows():
    for month_offset, dt in enumerate(monthly_dates):

        # FIX: increased seasonality amplitude from 0.03 to 0.08
        # and shifted peak to July/August (month 6-7) which is
        # realistic for multifamily and retail assets
        seasonality = 1 + 0.08 * np.sin(2 * np.pi * (dt.month - 3) / 12)

        # FIX: reduced noise from ±3% to ±1.5% so the seasonal
        # pattern is clearly visible rather than being drowned out
        noise = random.uniform(0.985, 1.015)

        # Small upward trend: 0.5% monthly growth = ~6% annual NOI growth
        # This makes the trend line visually interesting rather than flat
        trend = 1 + 0.005 * month_offset

        monthly_records.append({
            'property_id'         : prop['property_id'],
            'month'               : dt.strftime('%Y-%m'),
            'month_date'          : dt.strftime('%Y-%m-%d'),
            'noi_monthly'         : round(prop['noi_annual'] / 12 * seasonality * noise * trend, 0),
            'occupancy'           : round(min(0.99, prop['occupancy_rate'] * seasonality * noise), 3),
            'revenue'             : round(prop['noi_annual'] / 12 / 0.62 * noise * trend, 0),
            'opex'                : round(prop['noi_annual'] / 12 / 0.62 * 0.38 * noise, 0),
            'debt_service_monthly': round(prop['annual_debt_service'] / 12, 0),
        })

monthly_df = pd.DataFrame(monthly_records)
monthly_df.to_csv('data/raw/monthly_financials.csv', index=False)
print(f"✓ Created monthly_financials.csv — {len(monthly_df)} rows")
print(f"  Date range: {monthly_df['month'].min()} to {monthly_df['month'].max()}")
print(f"  Sample NOI trend for PROP-001:")
print(monthly_df[monthly_df['property_id']=='PROP-001'][['month','noi_monthly']].head(12).to_string(index=False))

# ── Scenario overlay table ──────────────────────────────────────
# 3 scenarios × 50 properties = 150 rows
# Each scenario adjusts NOI and cap rate differently

scenarios = []

for _, prop in df.iterrows():
    for scenario, noi_mult, cap_adj in [
        ('Base',     1.00,  0.0000),   # no change from actuals
        ('Upside',   1.08, -0.0025),   # 8% more NOI, cap rate compresses
        ('Downside', 0.90, +0.0050),   # 10% less NOI, cap rate expands
    ]:
        adj_noi   = round(prop['noi_annual'] * noi_mult, 0)
        adj_cap   = round(prop['cap_rate'] + cap_adj, 4)
        adj_value = round(adj_noi / adj_cap, 0)  # value = NOI / cap rate

        scenarios.append({
            'property_id'    : prop['property_id'],
            'scenario'       : scenario,
            'noi_adjusted'   : adj_noi,
            'cap_rate_adj'   : adj_cap,
            'value_adjusted' : adj_value,
        })

scenario_df = pd.DataFrame(scenarios)
scenario_df.to_csv('data/raw/scenarios.csv', index=False)
print(f"✓ Created scenarios.csv — {len(scenario_df)} rows")
print("\nAll 3 data files created. Check data/raw/ folder.")