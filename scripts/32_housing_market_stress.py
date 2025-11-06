"""Analysis 32: Housing Market Stress Index"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fredapi import Fred
from scipy import stats
from pathlib import Path
import os, sys

sys.path.append(str(Path(__file__).parent.parent))
from scripts.utils import load_overdose_data

fred = Fred(api_key=os.getenv('FRED_API_KEY'))
OUTPUT_DIR = Path('results/32_housing_market_stress')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("="*70)
    print("Analysis 32: Housing Market Stress")
    print("="*70)

    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()
    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')

    # Fetch housing data
    try:
        mortgage = fred.get_series('MORTGAGE30US', observation_start='2012-01-01', observation_end='2023-12-31')
        annual_mortgage = mortgage.resample('Y').mean()
        annual_mortgage.index = annual_mortgage.index.year
        annual_deaths['Mortgage_Rate'] = annual_deaths['Year'].map(dict(zip(annual_mortgage.index, annual_mortgage.values)))
        print("✓ Fetched mortgage rate data")
    except:
        print("✗ Could not fetch mortgage data")

    try:
        hpi = fred.get_series('CSUSHPISA', observation_start='2012-01-01', observation_end='2023-12-31')
        annual_hpi = hpi.resample('Y').mean()
        annual_hpi.index = annual_hpi.index.year
        annual_deaths['Home_Price_Index'] = annual_deaths['Year'].map(dict(zip(annual_hpi.index, annual_hpi.values)))
        print("✓ Fetched home price index")
    except:
        print("✗ Could not fetch home price data")

    annual_deaths.to_csv(OUTPUT_DIR / 'housing_market_stress.csv', index=False)
    print("✓ Saved: housing_market_stress.csv")

    # Correlations
    corrs = []
    for col in ['Mortgage_Rate', 'Home_Price_Index']:
        if col in annual_deaths.columns:
            valid = annual_deaths[[col, 'Deaths']].dropna()
            if len(valid) >= 5:
                corr, pval = stats.pearsonr(valid[col], valid['Deaths'])
                corrs.append({'Metric': col, 'Correlation': corr, 'P_Value': pval})

    if corrs:
        pd.DataFrame(corrs).to_csv(OUTPUT_DIR / 'housing_correlations.csv', index=False)
        print("✓ Saved: housing_correlations.csv")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

if __name__ == '__main__':
    main()
