"""Analysis 35: Industry Employment Shifts"""
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
OUTPUT_DIR = Path('results/35_industry_employment_shifts')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("="*70)
    print("Analysis 35: Industry Employment Shifts")
    print("="*70)

    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()
    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')

    # Fetch industry employment
    industries = {
        'Manufacturing': 'MANEMP',
        'Construction': 'USCONS',
        'Leisure_Hospitality': 'CES7000000001'
    }

    for name, series_id in industries.items():
        try:
            data = fred.get_series(series_id, observation_start='2012-01-01', observation_end='2023-12-31')
            annual_data = data.resample('Y').mean()
            annual_data.index = annual_data.index.year
            annual_deaths[name] = annual_deaths['Year'].map(dict(zip(annual_data.index, annual_data.values)))
            print(f"✓ Fetched {name}")
        except:
            print(f"✗ Could not fetch {name}")

    annual_deaths.to_csv(OUTPUT_DIR / 'industry_employment_trends.csv', index=False)
    print("✓ Saved: industry_employment_trends.csv")

    # Correlations
    corrs = []
    for industry in industries.keys():
        if industry in annual_deaths.columns:
            valid = annual_deaths[[industry, 'Deaths']].dropna()
            if len(valid) >= 5:
                corr, pval = stats.pearsonr(valid[industry], valid['Deaths'])
                corrs.append({'Industry': industry, 'Correlation': corr, 'P_Value': pval})

    if corrs:
        pd.DataFrame(corrs).to_csv(OUTPUT_DIR / 'industry_correlations.csv', index=False)
        print("✓ Saved: industry_correlations.csv")
        print("\nCorrelations:")
        for c in corrs:
            print(f"  {c['Industry']}: r={c['Correlation']:.3f}, p={c['P_Value']:.4f}")

    # Plot indexed trends
    if 'Manufacturing' in annual_deaths.columns:
        fig, ax = plt.subplots(figsize=(14, 8))
        for industry in industries.keys():
            if industry in annual_deaths.columns:
                baseline = annual_deaths[annual_deaths['Year'] == 2012][industry].iloc[0]
                indexed = (annual_deaths[industry] / baseline) * 100
                ax.plot(annual_deaths['Year'], indexed, '-o', linewidth=2.5,
                       markersize=7, label=industry.replace('_', ' '))

        ax.axhline(100, color='black', linestyle='--', linewidth=1)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Employment Index (2012 = 100)', fontsize=12, fontweight='bold')
        ax.set_title('Industry Employment Trends (Indexed to 2012)',
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'industry_employment_indexed.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: industry_employment_indexed.png")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

if __name__ == '__main__':
    main()
