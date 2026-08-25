import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

markets = ['Dallas-Fort Worth', 'Austin', 'Houston', 'Phoenix', 'Denver']
asset_types = ['Multifamily', 'Industrial', 'Office', 'Retail']
statuses = ['Stabilized', 'Value-Add', 'Development']

market_coords = {
    'Dallas-Fort Worth': (32.7767, -96.7970),
    'Austin':            (30.2672, -97.7431),
    'Houston':           (29.7604, -95.3698),
    'Phoenix':           (33.4484, -112.0740),
    'Denver':            (39.7392, -104.9903),
}

properties = []

for i in range(1, 51):
    mkt             = random.choice(markets)
    atype           = random.choice(asset_types)
    sqft            = random.randint(20000, 200000)
    purchase_price  = random.randint(8_000_000, 80_000_000)
    cap_rate        = round(random.uniform(0.055, 0.075), 4)
    noi             = round(purchase_price * cap_rate, 0)
    ltv             = random.uniform(0.65, 0.75)
    loan_amount     = round(purchase_price * ltv, 0)
    interest_rate   = round(random.uniform(0.055, 0.072), 4)
    annual_debt_svc = round(loan_amount * interest_rate * 1.15, 0)
    dscr            = round(noi / annual_debt_svc, 2)
    occupancy       = round(random.uniform(0.88, 0.98), 3)
    current_value   = round(purchase_price * random.uniform(1.05, 1.35), 0)
    appreciation    = round((current_value - purchase_price) / purchase_price * 100, 1)
    unrealized_gain = round(current_value - purchase_price, 0)
    going_in_yield  = round(noi / current_value * 100, 2)

    # DSCR flag
    if dscr >= 1.30:
        dscr_flag = 'Healthy'
    elif dscr >= 1.15:
        dscr_flag = 'Watch'
    else:
        dscr_flag = 'At Risk'

    # Occupancy flag
    if occupancy >= 0.95:
        occupancy_flag = 'Strong'
    elif occupancy >= 0.90:
        occupancy_flag = 'Stable'
    else:
        occupancy_flag = 'Below Target'

    # Cap rate score
    if cap_rate >= 0.070:
        cap_score = 20
    elif cap_rate >= 0.065:
        cap_score = 15
    elif cap_rate >= 0.060:
        cap_score = 10
    elif cap_rate >= 0.055:
        cap_score = 5
    else:
        cap_score = 0

    # DSCR score
    if dscr >= 1.40:
        dscr_score = 20
    elif dscr >= 1.30:
        dscr_score = 15
    elif dscr >= 1.20:
        dscr_score = 10
    elif dscr >= 1.15:
        dscr_score = 5
    else:
        dscr_score = 0

    # Appreciation score
    if appreciation >= 25:
        appr_score = 20
    elif appreciation >= 15:
        appr_score = 15
    elif appreciation >= 10:
        appr_score = 10
    elif appreciation >= 5:
        appr_score = 5
    else:
        appr_score = 0

    # Occupancy score
    if occupancy >= 0.97:
        occ_score = 20
    elif occupancy >= 0.94:
        occ_score = 15
    elif occupancy >= 0.90:
        occ_score = 10
    elif occupancy >= 0.88:
        occ_score = 5
    else:
        occ_score = 0

    # Going-in yield score
    if going_in_yield >= 6.5:
        yield_score = 20
    elif going_in_yield >= 5.5:
        yield_score = 15
    elif going_in_yield >= 4.5:
        yield_score = 10
    elif going_in_yield >= 3.5:
        yield_score = 5
    else:
        yield_score = 0

    total_score = cap_score + dscr_score + appr_score + occ_score + yield_score

    # Decision
    if total_score >= 70:
        decision        = 'HOLD'
        decision_reason = 'Strong performer. Stable income and healthy debt coverage.'
    elif total_score >= 50:
        decision        = 'SELL'
        decision_reason = 'Underperforming. Consider exit and capital redeployment.'
    else:
        decision        = 'VALUE-ADD'
        decision_reason = 'Opportunity. Reposition or acquire at discount.'

    mkt_short = mkt.split('-')[0]

    properties.append({
        'property_id':         'PROP-' + str(i).zfill(3),
        'property_name':       mkt_short + ' ' + atype + ' ' + str(i).zfill(2),
        'market':              mkt,
        'asset_type':          atype,
        'status':              random.choice(statuses),
        'acquisition_date':    (datetime(2019,1,1) + timedelta(days=random.randint(0,1500))).strftime('%Y-%m-%d'),
        'purchase_price':      purchase_price,
        'current_value':       current_value,
        'sqft':                sqft,
        'noi_annual':          noi,
        'cap_rate':            cap_rate,
        'occupancy_rate':      occupancy,
        'loan_amount':         loan_amount,
        'interest_rate':       interest_rate,
        'annual_debt_service': annual_debt_svc,
        'dscr':                dscr,
        'ltv':                 round(ltv, 3),
        'latitude':            market_coords[mkt][0],
        'longitude':           market_coords[mkt][1],
        'unrealized_gain':     unrealized_gain,
        'appreciation_pct':    appreciation,
        'going_in_yield':      going_in_yield,
        'dscr_flag':           dscr_flag,
        'occupancy_flag':      occupancy_flag,
        'cap_score':           cap_score,
        'dscr_score':          dscr_score,
        'appr_score':          appr_score,
        'occ_score':           occ_score,
        'yield_score':         yield_score,
        'total_score':         total_score,
        'decision':            decision,
        'decision_reason':     decision_reason,
    })

df = pd.DataFrame(properties)
df.to_csv('data/raw/properties.csv', index=False)
print('properties.csv: ' + str(len(df)) + ' rows, ' + str(len(df.columns)) + ' columns')
print(df[['property_name', 'total_score', 'decision']].head(10).to_string())


# MONTHLY FINANCIALS
monthly_dates   = pd.date_range('2022-01-01', periods=36, freq='MS')
monthly_records = []

for _, prop in df.iterrows():
    for month_offset, dt in enumerate(monthly_dates):
        seasonality = 1 + 0.08 * np.sin(2 * np.pi * (dt.month - 3) / 12)
        noise       = random.uniform(0.985, 1.015)
        trend       = 1 + 0.005 * month_offset
        noi_monthly = round(prop['noi_annual'] / 12 * seasonality * noise * trend, 0)
        revenue     = round(prop['noi_annual'] / 12 / 0.62 * noise * trend, 0)
        opex        = round(revenue * 0.38 * noise, 0)
        occ         = round(min(0.99, prop['occupancy_rate'] * (1 + 0.04 * np.sin(2 * np.pi * (dt.month - 3) / 12)) * noise), 3)
        qtr         = 'Q' + str((dt.month - 1) // 3 + 1)

        monthly_records.append({
            'property_id':          prop['property_id'],
            'property_name':        prop['property_name'],
            'market':               prop['market'],
            'asset_type':           prop['asset_type'],
            'status':               prop['status'],
            'month':                dt.strftime('%Y-%m'),
            'month_date':           dt.strftime('%Y-%m-%d'),
            'year':                 dt.year,
            'quarter':              qtr,
            'noi_monthly':          noi_monthly,
            'occupancy':            occ,
            'revenue':              revenue,
            'opex':                 opex,
            'debt_service_monthly': round(prop['annual_debt_service'] / 12, 0),
        })

monthly_df = pd.DataFrame(monthly_records)
monthly_df.to_csv('data/raw/monthly_financials.csv', index=False)
print('monthly_financials.csv: ' + str(len(monthly_df)) + ' rows')
print('Date range: ' + monthly_df['month'].min() + ' to ' + monthly_df['month'].max())


# SCENARIOS
scenarios = []

for _, prop in df.iterrows():
    for scenario, noi_mult, cap_adj in [
        ('Base',     1.00,  0.0000),
        ('Upside',   1.08, -0.0025),
        ('Downside', 0.90,  0.0050),
    ]:
        adj_noi   = round(prop['noi_annual'] * noi_mult, 0)
        adj_cap   = round(prop['cap_rate'] + cap_adj, 4)
        adj_value = round(adj_noi / adj_cap, 0)

        if scenario == 'Upside':
            sc = min(100, prop['total_score'] + 10)
        elif scenario == 'Downside':
            sc = max(0, prop['total_score'] - 15)
        else:
            sc = prop['total_score']

        if sc >= 70:
            sd = 'HOLD'
        elif sc >= 50:
            sd = 'SELL'
        else:
            sd = 'VALUE-ADD'

        scenarios.append({
            'property_id':       prop['property_id'],
            'property_name':     prop['property_name'],
            'market':            prop['market'],
            'asset_type':        prop['asset_type'],
            'scenario':          scenario,
            'noi_adjusted':      adj_noi,
            'cap_rate_adj':      adj_cap,
            'value_adjusted':    adj_value,
            'noi_delta_pct':     round((noi_mult - 1) * 100, 1),
            'scenario_score':    sc,
            'scenario_decision': sd,
        })

scenario_df = pd.DataFrame(scenarios)
scenario_df.to_csv('data/raw/scenarios.csv', index=False)
print('scenarios.csv: ' + str(len(scenario_df)) + ' rows')
print('ALL FILES GENERATED SUCCESSFULLY')