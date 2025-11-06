"""Analysis 31: Labor Force Participation"""
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
OUTPUT_DIR = Path('results/31_labor_force_participation')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("="*70)
    print("Analysis 31: Labor Force Participation")
    print("="*70)

    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()
    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')

    # Fetch LFPR
    try:
        lfpr = fred.get_series('CIVPART', observation_start='2012-01-01', observation_end='2023-12-31')
        annual_lfpr = lfpr.resample('Y').mean()
        annual_lfpr.index = annual_lfpr.index.year
        annual_deaths['LFPR'] = annual_deaths['Year'].map(dict(zip(annual_lfpr.index, annual_lfpr.values)))
        print("✓ Fetched labor force participation data")
    except:
        print("✗ Could not fetch LFPR data")

    if 'LFPR' in annual_deaths.columns:
        annual_deaths.to_csv(OUTPUT_DIR / 'lfpr_deaths_annual.csv', index=False)
        print("✓ Saved: lfpr_deaths_annual.csv")

        corr, pval = stats.pearsonr(annual_deaths['LFPR'], annual_deaths['Deaths'])
        pd.DataFrame([{'Correlation': corr, 'P_Value': pval}]).to_csv(
            OUTPUT_DIR / 'lfpr_correlation.csv', index=False)
        print(f"✓ Correlation: {corr:.3f}, p={pval:.4f}")

        # Plot
        fig, ax1 = plt.subplots(figsize=(14, 8))
        ax1.plot(annual_deaths['Year'], annual_deaths['LFPR'],
                'b-o', linewidth=3, markersize=8)
        ax1.set_ylabel('Labor Force Participation Rate (%)', color='b',
                      fontsize=12, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='b')

        ax2 = ax1.twinx()
        ax2.plot(annual_deaths['Year'], annual_deaths['Deaths'],
                'r-s', linewidth=3, markersize=8)
        ax2.set_ylabel('Annual Deaths', color='r', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='r')

        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_title('Labor Force Participation vs Overdose Deaths',
                      fontsize=14, fontweight='bold', pad=20)
        ax1.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'lfpr_deaths_timeseries.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: lfpr_deaths_timeseries.png")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

if __name__ == '__main__':
    main()
